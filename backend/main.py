from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import SessionLocal, engine
from models import Base, Documento, VersaoDocumento, EstadoDocumento
from schemas import DocumentoCreate, DocumentoUpdate, DocumentoOut, VersaoOut, MudancaEstado

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

@app.post("/documentos/", response_model=DocumentoOut)
def criar_documento(doc: DocumentoCreate, db: Session = Depends(get_db)):
    documento = Documento(
        titulo=doc.titulo,
        parceiro_id=doc.parceiro_id,
        dados=doc.dados,
        estado=EstadoDocumento.RASCUNHO,
        versao_atual=1
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    criar_versao(db, documento, EstadoDocumento.RASCUNHO, criado_por=doc.parceiro_id)
    return documento

@app.get("/documentos/{doc_id}", response_model=DocumentoOut)
def obter_documento(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return doc

@app.put("/documentos/{doc_id}/editar", response_model=DocumentoOut)
def editar_documento(doc_id: uuid.UUID, update: DocumentoUpdate, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if doc.estado != EstadoDocumento.RASCUNHO:
        raise HTTPException(400, detail="Documento não está em edição")
    doc.dados = update.dados
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/submeter", response_model=DocumentoOut)
def submeter_documento(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.RASCUNHO:
        raise HTTPException(400, detail="Só pode submeter a partir de rascunho")
    doc.versao_atual += 1
    doc.estado = EstadoDocumento.SUBMETIDO
    criar_versao(db, doc, EstadoDocumento.SUBMETIDO, criado_por=doc.parceiro_id, comentario="Submissão para validação")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/iniciar-revisao", response_model=DocumentoOut)
def iniciar_revisao(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.SUBMETIDO:
        raise HTTPException(400, detail="Documento não está submetido")
    doc.estado = EstadoDocumento.EM_REVISAO
    criar_versao(db, doc, EstadoDocumento.EM_REVISAO, criado_por="empresa", comentario="Revisão iniciada")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/pedir-alteracoes", response_model=DocumentoOut)
def pedir_alteracoes(doc_id: uuid.UUID, motivo: MudancaEstado, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.EM_REVISAO:
        raise HTTPException(400, detail="Só pode pedir alterações durante a revisão")
    doc.estado = EstadoDocumento.ALTERACOES
    criar_versao(db, doc, EstadoDocumento.ALTERACOES, criado_por="empresa", comentario=motivo.comentario or "Alterações solicitadas")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/editar-novamente", response_model=DocumentoOut)
def editar_novamente(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.ALTERACOES:
        raise HTTPException(400, detail="Ação permitida apenas no estado 'Alterações'")
    doc.estado = EstadoDocumento.RASCUNHO
    doc.versao_atual += 1
    criar_versao(db, doc, EstadoDocumento.RASCUNHO, criado_por=doc.parceiro_id, comentario="Iniciada correção após pedido de alterações")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/aprovar", response_model=DocumentoOut)
def aprovar_documento(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.EM_REVISAO:
        raise HTTPException(400, detail="Só pode aprovar durante a revisão")
    doc.estado = EstadoDocumento.APROVADO
    criar_versao(db, doc, EstadoDocumento.APROVADO, criado_por="empresa", comentario="Documento aprovado")
    db.commit()
    db.refresh(doc)
    return doc

@app.post("/documentos/{doc_id}/reabrir", response_model=DocumentoOut)
def reabrir_documento(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404)
    if doc.estado != EstadoDocumento.APROVADO:
        raise HTTPException(400, detail="Só pode reabrir um documento aprovado")
    doc.estado = EstadoDocumento.RASCUNHO
    doc.versao_atual += 1
    criar_versao(db, doc, EstadoDocumento.RASCUNHO, criado_por="empresa", comentario="Documento reaberto para nova edição")
    db.commit()
    db.refresh(doc)
    return doc

@app.get("/documentos/{doc_id}/versoes", response_model=List[VersaoOut])
def listar_versoes(doc_id: uuid.UUID, db: Session = Depends(get_db)):
    versoes = db.query(VersaoDocumento).filter(VersaoDocumento.documento_id == doc_id).order_by(VersaoDocumento.numero_versao).all()
    return versoes