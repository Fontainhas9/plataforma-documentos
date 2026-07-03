from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import timedelta

from database import SessionLocal, engine
from models import Base, Documento, VersaoDocumento, EstadoDocumento, Utilizador, PerfilUtilizador
from schemas import (
    DocumentoCreate, DocumentoUpdate, DocumentoOut,
    VersaoOut, MudancaEstado, UtilizadorCreate, Token
)
from auth import (
    hash_password,
    verificar_password,
    criar_token_acesso,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

# -------------------- Documentos (protegidos) --------------------
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
        parceiro_id=current_user.username,  # usa o username do token
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
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    # Parceiro só vê os seus próprios documentos; empresa vê todos
    if current_user.perfil == PerfilUtilizador.PARCEIRO and doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return doc

@app.put("/documentos/{doc_id}/editar", response_model=DocumentoOut)
def editar_documento(
    doc_id: uuid.UUID,
    update: DocumentoUpdate,
    db: Session = Depends(get_db),
    current_user: Utilizador = Depends(get_current_user)
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.perfil != PerfilUtilizador.PARCEIRO or doc.parceiro_id != current_user.username:
        raise HTTPException(status_code=403)
    if doc.estado != EstadoDocumento.RASCUNHO:
        raise HTTPException(400, detail="Documento não está em edição")
    doc.dados = update.dados
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/submeter", response_model=DocumentoOut)
def submeter_documento(
    doc_id: uuid.UUID,
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
    return doc

@app.post("/documentos/{doc_id}/iniciar-revisao", response_model=DocumentoOut)
def iniciar_revisao(
    doc_id: uuid.UUID,
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
    return doc

@app.post("/documentos/{doc_id}/pedir-alteracoes", response_model=DocumentoOut)
def pedir_alteracoes(
    doc_id: uuid.UUID,
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
    return doc

@app.post("/documentos/{doc_id}/editar-novamente", response_model=DocumentoOut)
def editar_novamente(
    doc_id: uuid.UUID,
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
    doc_id: uuid.UUID,
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
    return doc

@app.post("/documentos/{doc_id}/reabrir", response_model=DocumentoOut)
def reabrir_documento(
    doc_id: uuid.UUID,
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

@app.get("/documentos/{doc_id}/versoes", response_model=List[VersaoOut])
def listar_versoes(
    doc_id: uuid.UUID,
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