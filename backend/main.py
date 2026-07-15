from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from io import BytesIO
import json
import traceback

from database import SessionLocal, engine
from models import Base, Documento, VersaoDocumento, EstadoDocumento, Utilizador, PerfilUtilizador, Notificacao  # <-- ADICIONAR Notificacao
from schemas import (
    DocumentoCreate, DocumentoUpdate, DocumentoOut,
    VersaoOut, MudancaEstado, UtilizadorCreate, Token,
    PasswordUpdate
)
from auth import (
    hash_password,
    verificar_password,
    criar_token_acesso,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Importar funções do dashboard
from dashboard import (
    get_dashboard_kpis,
    get_evolucao_mensal,
    get_top_parceiros,
    get_tempo_medio_por_estado,
    get_documentos_recentes
)

# Importar funções de notificações
from notificacoes import (
    criar_notificacao_para_empresa,
    criar_notificacao_para_parceiro,
    get_notificacoes_utilizador,
    get_notificacoes_nao_lidas_count
)

# EMAIL DESATIVADO - manter para futuro
# from email_utils import enviar_email, DESTINATARIO_PADRAO

# Criar tabelas (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def criar_versao(db: Session, documento: Documento, estado: EstadoDocumento, criado_por: str, comentario: str = ""):
    versao = VersaoDocumento(
        documento_id=documento.id,
        numero_versao=documento.versao_atual,
        dados=documento.dados.copy(),
        estado=estado,
        comentario=comentario,
        criado_por=criado_por
    )
    db.add(versao)
    db.commit()

# -------------------- Autenticação --------------------
@app.post("/registar", response_model=Token)
def registar(utilizador: UtilizadorCreate, db: Session = Depends(get_db)):
    user_existente = db.query(Utilizador).filter(Utilizador.username == utilizador.username).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="Username já existe")

    user = Utilizador(
        username=utilizador.username,
        password_hash=hash_password(utilizador.password),
        perfil=utilizador.perfil,
        nome_completo=utilizador.nome_completo
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = criar_token_acesso(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilizador).filter(Utilizador.username == form_data.username).first()
    if not user or not verificar_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Username ou password incorretos")

    access_token = criar_token_acesso(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=dict)
def quem_sou_eu(current_user: Utilizador = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "perfil": current_user.perfil.value,
        "nome_completo": current_user.nome_completo
    }

# -------------------- Documentos --------------------
@app.get("/documentos", response_model=List[DocumentoOut])
def listar_documentos(
    estado: Optional[EstadoDocumento] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    query = db.query(Documento)
    if estado:
        query = query.filter(Documento.estado == estado)

    if current_user.perfil == PerfilUtilizador.PARCEIRO:
        query = query.filter(Documento.parceiro_id == current_user.username)
    documentos = query.order_by(Documento.id.desc()).all()
    return documentos

# -------------------- Pesquisa e Filtros --------------------
@app.get("/documentos/pesquisar", response_model=List[DocumentoOut])
def pesquisar_documentos(
    q: Optional[str] = Query(None, description="Texto para pesquisar (título, parceiro, ID)"),
    estados: Optional[str] = Query(None, description="Filtrar por estados (separados por vírgula)"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    order_by: Optional[str] = Query("id", description="Campo para ordenar"),
    order_dir: Optional[str] = Query("desc", description="Direção da ordenação (asc/desc)"),
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Endpoint de pesquisa avançada de documentos.
    """
    query = db.query(Documento)

    # -------------------- Filtro por pesquisa de texto --------------------
    if q:
        q = f"%{q}%"
        # Tenta converter para inteiro para pesquisar por ID
        try:
            id_int = int(q.replace("%", ""))
            query = query.filter(
                or_(
                    Documento.id == id_int,
                    Documento.titulo.ilike(q),
                    Documento.parceiro_id.ilike(q)
                )
            )
        except ValueError:
            query = query.filter(
                or_(
                    Documento.titulo.ilike(q),
                    Documento.parceiro_id.ilike(q)
                )
            )

    # -------------------- Filtro por estados --------------------
    if estados:
        estados_lista = [e.strip() for e in estados.split(",") if e.strip()]
        if estados_lista:
            query = query.filter(Documento.estado.in_(estados_lista))

    # -------------------- Filtro por data --------------------
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Documento.created_at >= data_inicio_dt)
        except ValueError:
            pass  # Ignora data inválida

    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            # Adicionar um dia para incluir todo o dia
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Documento.created_at <= data_fim_dt)
        except ValueError:
            pass  # Ignora data inválida

    # -------------------- Filtro por perfil --------------------
    if current_user.perfil == PerfilUtilizador.PARCEIRO:
        query = query.filter(Documento.parceiro_id == current_user.username)

    # -------------------- Ordenação --------------------
    # Mapeamento de campos para ordenação segura
    order_map = {
        "id": Documento.id,
        "titulo": Documento.titulo,
        "parceiro_id": Documento.parceiro_id,
        "estado": Documento.estado,
        "created_at": Documento.created_at,
        "updated_at": Documento.updated_at,
        "versao_atual": Documento.versao_atual
    }
    
    campo_ordem = order_map.get(order_by, Documento.id)
    if order_dir.lower() == "asc":
        query = query.order_by(campo_ordem.asc())
    else:
        query = query.order_by(campo_ordem.desc())

    documentos = query.all()
    return documentos

@app.post("/documentos/", response_model=DocumentoOut)
def criar_documento(
    doc: DocumentoCreate,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    if current_user.perfil != PerfilUtilizador.PARCEIRO:
        raise HTTPException(status_code=403, detail="Apenas parceiros podem criar documentos")
    documento = Documento(
        titulo=doc.titulo,
        parceiro_id=current_user.username,
        dados=doc.dados,
        estado=EstadoDocumento.RASCUNHO,
        versao_atual=1
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    criar_versao(db, documento, EstadoDocumento.RASCUNHO, criado_por=current_user.username)
    return documento

@app.get("/documentos/{doc_id}", response_model=DocumentoOut)
def obter_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    if current_user.perfil == PerfilUtilizador.PARCEIRO and doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return doc

@app.put("/documentos/{doc_id}/editar", response_model=DocumentoOut)
def editar_documento(
    doc_id: int,
    update: DocumentoUpdate,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    try:
        doc = db.query(Documento).filter(Documento.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        if current_user.perfil != PerfilUtilizador.PARCEIRO or doc.parceiro_id != current_user.username:
            raise HTTPException(status_code=403, detail="Apenas o parceiro pode editar")
        if doc.estado != EstadoDocumento.RASCUNHO:
            raise HTTPException(400, detail=f"Documento está em estado '{doc.estado}'. Só é possível editar em Rascunho.")
        doc.dados = update.dados
        db.commit()
        db.refresh(doc)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/documentos/{doc_id}/submeter", response_model=DocumentoOut)
def submeter_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil != PerfilUtilizador.PARCEIRO or doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.RASCUNHO:
        raise HTTPException(400, detail="Só pode submeter a partir de rascunho")
    doc.versao_atual += 1
    doc.estado = EstadoDocumento.SUBMETIDO
    criar_versao(db, doc, EstadoDocumento.SUBMETIDO, criado_por=current_user.username, comentario="Submissão para validação")
    db.commit()
    db.refresh(doc)
    
    # Criar notificação para a empresa
    criar_notificacao_para_empresa(
        db=db,
        documento=doc,
        titulo="📤 Documento submetido",
        mensagem=f"O documento '{doc.titulo}' foi submetido por {current_user.username} para validação.",
        icone="📤"
    )
    
    return doc

@app.post("/documentos/{doc_id}/iniciar-revisao", response_model=DocumentoOut)
def iniciar_revisao(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil not in [PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN]:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.SUBMETIDO:
        raise HTTPException(400, detail="Documento não está submetido")
    doc.estado = EstadoDocumento.EM_REVISAO
    criar_versao(db, doc, EstadoDocumento.EM_REVISAO, criado_por=current_user.username, comentario="Revisão iniciada")
    db.commit()
    db.refresh(doc)
    
    # Criar notificação para o parceiro
    criar_notificacao_para_parceiro(
        db=db,
        documento=doc,
        titulo="🔍 Revisão iniciada",
        mensagem=f"O documento '{doc.titulo}' está em revisão pela empresa.",
        icone="🔍"
    )
    
    return doc


@app.post("/documentos/{doc_id}/pedir-alteracoes", response_model=DocumentoOut)
def pedir_alteracoes(
    doc_id: int,
    motivo: MudancaEstado,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil not in [PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN]:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.EM_REVISAO:
        raise HTTPException(400, detail="Só pode pedir alterações durante a revisão")
    doc.estado = EstadoDocumento.ALTERACOES
    criar_versao(db, doc, EstadoDocumento.ALTERACOES, criado_por=current_user.username, comentario=motivo.comentario or "Alterações solicitadas")
    db.commit()
    db.refresh(doc)
    
    # Criar notificação para o parceiro
    criar_notificacao_para_parceiro(
        db=db,
        documento=doc,
        titulo="🔄 Alterações solicitadas",
        mensagem=f"A empresa pediu alterações no documento '{doc.titulo}': {motivo.comentario or 'Ver detalhes'}",
        icone="🔄"
    )
    
    return doc

@app.post("/documentos/{doc_id}/editar-novamente", response_model=DocumentoOut)
def editar_novamente(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil != PerfilUtilizador.PARCEIRO or doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.ALTERACOES:
        raise HTTPException(400, detail="Ação permitida apenas no estado 'Alterações'")
    doc.estado = EstadoDocumento.RASCUNHO
    doc.versao_atual += 1
    criar_versao(db, doc, EstadoDocumento.RASCUNHO, criado_por=current_user.username, comentario="Iniciada correção após pedido de alterações")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/aprovar", response_model=DocumentoOut)
def aprovar_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil not in [PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN]:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.EM_REVISAO:
        raise HTTPException(400, detail="Só pode aprovar durante a revisão")
    doc.estado = EstadoDocumento.APROVADO
    criar_versao(db, doc, EstadoDocumento.APROVADO, criado_por=current_user.username, comentario="Documento aprovado")
    db.commit()
    db.refresh(doc)
    
    # Criar notificação para o parceiro
    criar_notificacao_para_parceiro(
        db=db,
        documento=doc,
        titulo="✅ Documento aprovado",
        mensagem=f"O documento '{doc.titulo}' foi aprovado por {current_user.username}.",
        icone="✅"
    )

    # EMAIL DESATIVADO - manter para futuro
    # assunto = f"Documento '{doc.titulo}' aprovado (ID {doc.id})"
    # corpo = (
    #     f"O documento '{doc.titulo}' (ID {doc.id}) foi aprovado.\n\n"
    #     f"Parceiro: {doc.parceiro_id}\n"
    #     f"Última versão: {doc.versao_atual}\n"
    #     f"Aprovado por: {current_user.username}\n"
    #     f"Data: {doc.updated_at or doc.created_at}\n\n"
    #     "Aceda à plataforma para consultar os detalhes."
    # )
    # enviar_email(DESTINATARIO_PADRAO, assunto, corpo)

    return doc

@app.post("/documentos/{doc_id}/reabrir", response_model=DocumentoOut)
def reabrir_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil not in [PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN]:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.APROVADO:
        raise HTTPException(400, detail="Só pode reabrir um documento aprovado")
    doc.estado = EstadoDocumento.RASCUNHO
    doc.versao_atual += 1
    criar_versao(db, doc, EstadoDocumento.RASCUNHO, criado_por=current_user.username, comentario="Documento reaberto para nova edição")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/arquivar", response_model=DocumentoOut)
def arquivar_documento(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil not in [PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN]:
        raise HTTPException(status_code=403, detail="Apenas a empresa pode arquivar documentos")
    if doc.estado not in [EstadoDocumento.RASCUNHO, EstadoDocumento.APROVADO]:
        raise HTTPException(400, detail="Só é possível arquivar documentos em rascunho ou aprovados")
    doc.estado = EstadoDocumento.ARQUIVADO
    criar_versao(db, doc, EstadoDocumento.ARQUIVADO, criado_por=current_user.username, comentario="Documento arquivado")
    db.commit()
    db.refresh(doc)
    
    # Criar notificação para o parceiro
    criar_notificacao_para_parceiro(
        db=db,
        documento=doc,
        titulo="📁 Documento arquivado",
        mensagem=f"O documento '{doc.titulo}' foi arquivado por {current_user.username}.",
        icone="📁"
    )

    # EMAIL DESATIVADO - manter para futuro
    # assunto = f"Documento '{doc.titulo}' arquivado (ID {doc.id})"
    # corpo = (
    #     f"O documento '{doc.titulo}' (ID {doc.id}) foi arquivado.\n\n"
    #     f"Parceiro: {doc.parceiro_id}\n"
    #     f"Última versão: {doc.versao_atual}\n"
    #     f"Arquivado por: {current_user.username}\n"
    #     f"Data: {doc.updated_at or doc.created_at}\n\n"
    #     "O documento está disponível apenas para consulta na plataforma."
    # )
    # enviar_email(DESTINATARIO_PADRAO, assunto, corpo)

    return doc

@app.get("/documentos/{doc_id}/versoes", response_model=List[VersaoOut])
def listar_versoes(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil == PerfilUtilizador.PARCEIRO and doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403)
    versoes = db.query(VersaoDocumento).filter(VersaoDocumento.documento_id == doc_id).order_by(VersaoDocumento.numero_versao).all()
    return versoes

# -------------------- Admin: gestão de utilizadores --------------------
@app.get("/admin/usuarios", response_model=List[dict])
def listar_utilizadores(
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    if current_user.perfil != PerfilUtilizador.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas admin")
    users = db.query(Utilizador).all()
    return [
        {
            "username": u.username,
            "perfil": u.perfil.value,
            "nome_completo": u.nome_completo,
            "created_at": u.created_at
        }
        for u in users
    ]

@app.delete("/admin/usuarios/{username}")
def eliminar_utilizador(
    username: str,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    if current_user.perfil != PerfilUtilizador.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas admin")
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Não pode eliminar a si próprio")
    user = db.query(Utilizador).filter(Utilizador.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    db.delete(user)
    db.commit()
    return {"ok": True}

@app.put("/admin/usuarios/{username}/password")
def alterar_password(
    username: str,
    dados: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    if current_user.perfil != PerfilUtilizador.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas admin")
    user = db.query(Utilizador).filter(Utilizador.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    user.password_hash = hash_password(dados.nova_password)
    db.commit()
    return {"ok": True}

# -------------------- Dashboard --------------------
@app.get("/dashboard/kpis")
def dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Obtém os KPIs principais para o dashboard.
    """
    return get_dashboard_kpis(db, current_user.username, current_user.perfil)

@app.get("/dashboard/evolucao")
def dashboard_evolucao(
    meses: int = 12,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Obtém a evolução mensal de documentos.
    """
    return get_evolucao_mensal(db, current_user.username, current_user.perfil, meses)

@app.get("/dashboard/top-parceiros")
def dashboard_top_parceiros(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Obtém os parceiros com mais documentos (apenas para empresa/admin).
    """
    if current_user.perfil == PerfilUtilizador.PARCEIRO:
        raise HTTPException(status_code=403, detail="Apenas empresa/admin podem ver top parceiros")
    return get_top_parceiros(db, limit)

@app.get("/dashboard/tempo-medio-estado")
def dashboard_tempo_medio_estado(
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Obtém o tempo médio em cada estado.
    """
    return get_tempo_medio_por_estado(db, current_user.username, current_user.perfil)

@app.get("/dashboard/documentos-recentes")
def dashboard_documentos_recentes(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Obtém os documentos mais recentes.
    """
    return get_documentos_recentes(db, current_user.username, current_user.perfil, limit)

# -------------------- Notificações --------------------
@app.get("/notificacoes")
def listar_notificacoes(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Lista as notificações do utilizador atual.
    """
    return get_notificacoes_utilizador(db, current_user.username, limit)

@app.get("/notificacoes/nao-lidas")
def contar_notificacoes_nao_lidas(
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Conta as notificações não lidas do utilizador atual.
    """
    count = get_notificacoes_nao_lidas_count(db, current_user.username)
    return {"count": count}

@app.put("/notificacoes/{notificacao_id}/ler")
def marcar_notificacao_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Marca uma notificação como lida.
    """
    try:
        # Verificar se a notificação existe e pertence ao utilizador
        notificacao = db.query(Notificacao).filter(
            Notificacao.id == notificacao_id,
            Notificacao.username == current_user.username
        ).first()
        
        if not notificacao:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        
        notificacao.lida = True
        db.commit()
        
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao marcar notificação como lida: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notificacoes/ler-todas")
def marcar_todas_notificacoes_lidas(
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    """
    Marca todas as notificações como lidas.
    """
    try:
        count = db.query(Notificacao).filter(
            Notificacao.username == current_user.username,
            Notificacao.lida == False
        ).update({"lida": True})
        
        db.commit()
        return {"ok": True, "count": count}
    except Exception as e:
        print(f"❌ Erro ao marcar todas notificações como lidas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# -------------------- Exportar Excel --------------------
@app.get("/documentos/{doc_id}/exportar-excel")
def exportar_versoes_excel(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    try:
        doc = db.query(Documento).filter(Documento.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        if current_user.perfil == PerfilUtilizador.PARCEIRO and doc.parceiro_id != current_user.username:
            raise HTTPException(status_code=403, detail="Acesso negado")

        dados = doc.dados
        wb = openpyxl.Workbook()
        processos = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]

        # ---------- Folha LCA ----------
        ws_lca = wb.active
        ws_lca.title = "LCA"
        row = 1

        # INPUTS
        ws_lca.cell(row=row, column=1, value="INPUTS").font = Font(bold=True, size=12)
        row += 1
        cab_inputs = ["Processo", "Material", "QTY", "Unit", "Material Description", "CAS/Comments", "Distance (km)", "Country", "Data Source"]
        for col, header in enumerate(cab_inputs, start=1):
            ws_lca.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lca", {}).get("inputs", {}).get(proc, []):
                ws_lca.cell(row=row, column=1, value=proc)
                ws_lca.cell(row=row, column=2, value=item.get("material", ""))
                ws_lca.cell(row=row, column=3, value=item.get("qty", ""))
                ws_lca.cell(row=row, column=4, value=item.get("unit", ""))
                ws_lca.cell(row=row, column=5, value=item.get("description", ""))
                ws_lca.cell(row=row, column=6, value=item.get("cas", ""))
                ws_lca.cell(row=row, column=7, value=item.get("distance", ""))
                ws_lca.cell(row=row, column=8, value=item.get("country", ""))
                ws_lca.cell(row=row, column=9, value=item.get("datasource", ""))
                row += 1
        row += 1

        # PROCESSES
        ws_lca.cell(row=row, column=1, value="PROCESSES").font = Font(bold=True, size=12)
        row += 1
        cab_proc = ["Processo", "Tipo", "QTY", "Unit", "Description", "Comments", "Data Source"]
        for col, header in enumerate(cab_proc, start=1):
            ws_lca.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lca", {}).get("processes", {}).get(proc, []):
                ws_lca.cell(row=row, column=1, value=proc)
                ws_lca.cell(row=row, column=2, value=item.get("tipo", ""))
                ws_lca.cell(row=row, column=3, value=item.get("qty", ""))
                ws_lca.cell(row=row, column=4, value=item.get("unit", ""))
                ws_lca.cell(row=row, column=5, value=item.get("description", ""))
                ws_lca.cell(row=row, column=6, value=item.get("comments", ""))
                ws_lca.cell(row=row, column=7, value=item.get("datasource", ""))
                row += 1
        row += 1

        # OUTPUTS LCA
        ws_lca.cell(row=row, column=1, value="OUTPUTS").font = Font(bold=True, size=12)
        row += 1
        cab_out = ["Processo", "Etapa", "Tipo", "Sub-tipo", "QTY", "Unit", "Material description", "Comments", "Data Source"]
        for col, header in enumerate(cab_out, start=1):
            ws_lca.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lca", {}).get("outputs", {}).get(proc, []):
                ws_lca.cell(row=row, column=1, value=proc)
                ws_lca.cell(row=row, column=2, value=item.get("etapa", ""))
                ws_lca.cell(row=row, column=3, value=item.get("tipo", ""))
                ws_lca.cell(row=row, column=4, value=item.get("sub_tipo", ""))
                ws_lca.cell(row=row, column=5, value=item.get("qty", ""))
                ws_lca.cell(row=row, column=6, value=item.get("unit", ""))
                ws_lca.cell(row=row, column=7, value=item.get("description", ""))
                ws_lca.cell(row=row, column=8, value=item.get("comments", ""))
                ws_lca.cell(row=row, column=9, value=item.get("datasource", ""))
                row += 1

        # Ajustar colunas LCA
        for col in ws_lca.columns:
            max_length = 0
            for cell in col:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            col_letter = get_column_letter(cell.column)
            ws_lca.column_dimensions[col_letter].width = min(max_length + 2, 40)

        # ---------- Folha LCC ----------
        ws_lcc = wb.create_sheet("LCC")
        row = 1

        # MATERIALS
        ws_lcc.cell(row=row, column=1, value="COST BREAKDOWN MATERIAL").font = Font(bold=True, size=12)
        row += 1
        cab_mat = ["Processo", "Material", "Price €", "Qty", "Unit", "Material Description", "Comments", "Distance (km)", "Country", "Data Source"]
        for col, header in enumerate(cab_mat, start=1):
            ws_lcc.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lcc", {}).get("materials", {}).get(proc, []):
                ws_lcc.cell(row=row, column=1, value=proc)
                ws_lcc.cell(row=row, column=2, value=item.get("material", ""))
                ws_lcc.cell(row=row, column=3, value=item.get("price", ""))
                ws_lcc.cell(row=row, column=4, value=item.get("qty", ""))
                ws_lcc.cell(row=row, column=5, value=item.get("unit", ""))
                ws_lcc.cell(row=row, column=6, value=item.get("description", ""))
                ws_lcc.cell(row=row, column=7, value=item.get("comments", ""))
                ws_lcc.cell(row=row, column=8, value=item.get("distance", ""))
                ws_lcc.cell(row=row, column=9, value=item.get("country", ""))
                ws_lcc.cell(row=row, column=10, value=item.get("datasource", ""))
                row += 1
        row += 1

        # EQUIPMENT
        ws_lcc.cell(row=row, column=1, value="EQUIPMENT").font = Font(bold=True, size=12)
        row += 1
        cab_eq = ["Processo", "Equipment", "Process", "Unit Cost (€)", "Lifespan (Years)", "Maintenance €/Year", "Industrial Equivalent", "Comments", "Data Source"]
        for col, header in enumerate(cab_eq, start=1):
            ws_lcc.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lcc", {}).get("equipment", {}).get(proc, []):
                ws_lcc.cell(row=row, column=1, value=proc)
                ws_lcc.cell(row=row, column=2, value=item.get("equipment", ""))
                ws_lcc.cell(row=row, column=3, value=item.get("process", ""))
                ws_lcc.cell(row=row, column=4, value=item.get("unit_cost", ""))
                ws_lcc.cell(row=row, column=5, value=item.get("lifespan", ""))
                ws_lcc.cell(row=row, column=6, value=item.get("maintenance", ""))
                ws_lcc.cell(row=row, column=7, value=item.get("industrial_equiv", ""))
                ws_lcc.cell(row=row, column=8, value=item.get("comments", ""))
                ws_lcc.cell(row=row, column=9, value=item.get("datasource", ""))
                row += 1
        row += 1

        # LABOUR
        ws_lcc.cell(row=row, column=1, value="LABOUR").font = Font(bold=True, size=12)
        row += 1
        cab_lab = ["Processo", "Name of the process", "Total Labour - Number", "Total Labour - Cost €",
                   "Number - High Skilled", "Number - Moderated skilled", "Number - Unskilled",
                   "Rate - High Skilled (€/h)", "Rate - Moderated skilled (€/h)", "Rate - Unskilled (€/h)",
                   "Comments", "Data Source"]
        for col, header in enumerate(cab_lab, start=1):
            ws_lcc.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lcc", {}).get("labour", {}).get(proc, []):
                ws_lcc.cell(row=row, column=1, value=proc)
                ws_lcc.cell(row=row, column=2, value=item.get("process", ""))
                ws_lcc.cell(row=row, column=3, value=item.get("total_number", ""))
                ws_lcc.cell(row=row, column=4, value=item.get("total_cost", ""))
                ws_lcc.cell(row=row, column=5, value=item.get("high_skilled", ""))
                ws_lcc.cell(row=row, column=6, value=item.get("moderate_skilled", ""))
                ws_lcc.cell(row=row, column=7, value=item.get("unskilled", ""))
                ws_lcc.cell(row=row, column=8, value=item.get("high_rate", ""))
                ws_lcc.cell(row=row, column=9, value=item.get("moderate_rate", ""))
                ws_lcc.cell(row=row, column=10, value=item.get("unskilled_rate", ""))
                ws_lcc.cell(row=row, column=11, value=item.get("comments", ""))
                ws_lcc.cell(row=row, column=12, value=item.get("datasource", ""))
                row += 1
        row += 1

        # OUTPUTS LCC
        ws_lcc.cell(row=row, column=1, value="OUTPUTS").font = Font(bold=True, size=12)
        row += 1
        cab_out_lcc = ["Processo", "Material", "Market Price €", "Quantity", "Unit", "Amount of product produced", "Comments", "Data Source"]
        for col, header in enumerate(cab_out_lcc, start=1):
            ws_lcc.cell(row=row, column=col, value=header).font = Font(bold=True)
        row += 1
        for proc in processos:
            for item in dados.get("lcc", {}).get("outputs", {}).get(proc, []):
                ws_lcc.cell(row=row, column=1, value=proc)
                ws_lcc.cell(row=row, column=2, value=item.get("material", ""))
                ws_lcc.cell(row=row, column=3, value=item.get("market_price", ""))
                ws_lcc.cell(row=row, column=4, value=item.get("quantity", ""))
                ws_lcc.cell(row=row, column=5, value=item.get("unit", ""))
                ws_lcc.cell(row=row, column=6, value=item.get("amount_produced", ""))
                ws_lcc.cell(row=row, column=7, value=item.get("comments", ""))
                ws_lcc.cell(row=row, column=8, value=item.get("datasource", ""))
                row += 1

        for col in ws_lcc.columns:
            max_length = 0
            for cell in col:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            col_letter = get_column_letter(cell.column)
            ws_lcc.column_dimensions[col_letter].width = min(max_length + 2, 40)

        # ---------- Histórico ----------
        ws_hist = wb.create_sheet("Historico")
        versoes = db.query(VersaoDocumento).filter(VersaoDocumento.documento_id == doc_id).order_by(VersaoDocumento.numero_versao).all()
        cab_hist = ["Nº Versão", "Estado", "Criado por", "Data", "Comentário"]
        for col, header in enumerate(cab_hist, start=1):
            ws_hist.cell(row=1, column=col, value=header).font = Font(bold=True)
        for idx, v in enumerate(versoes, start=2):
            ws_hist.cell(row=idx, column=1, value=v.numero_versao)
            ws_hist.cell(row=idx, column=2, value=v.estado.value if v.estado else "")
            ws_hist.cell(row=idx, column=3, value=v.criado_por or "")
            ws_hist.cell(row=idx, column=4, value=v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else "")
            ws_hist.cell(row=idx, column=5, value=v.comentario or "")
        for col in ws_hist.columns:
            max_length = 0
            for cell in col:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            col_letter = get_column_letter(cell.column)
            ws_hist.column_dimensions[col_letter].width = min(max_length + 2, 40)

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        headers = {"Content-Disposition": f"attachment; filename=documento_{doc_id}_completo.xlsx"}
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Erro ao gerar Excel: {str(e)}"})