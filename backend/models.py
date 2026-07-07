from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from database import Base

class PerfilUtilizador(str, enum.Enum):
    PARCEIRO = "parceiro"
    EMPRESA = "empresa"
    ADMIN = "admin"

class EstadoDocumento(str, enum.Enum):
    RASCUNHO = "Rascunho"
    SUBMETIDO = "Submetido"
    EM_REVISAO = "Em Revisão"
    ALTERACOES = "Alterações"
    APROVADO = "Aprovado"
    ARQUIVADO = "Arquivado"

class Utilizador(Base):
    __tablename__ = "utilizadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    perfil = Column(Enum(PerfilUtilizador), nullable=False)
    nome_completo = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    parceiro_id = Column(String, nullable=False)  # username do parceiro
    estado = Column(Enum(EstadoDocumento), default=EstadoDocumento.RASCUNHO)
    versao_atual = Column(Integer, default=1)
    dados = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    versoes = relationship("VersaoDocumento", back_populates="documento", order_by="VersaoDocumento.numero_versao")

class VersaoDocumento(Base):
    __tablename__ = "versoes_documento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documentos.id"))
    numero_versao = Column(Integer, nullable=False)
    dados = Column(JSON, nullable=False)
    estado = Column(Enum(EstadoDocumento), nullable=False)
    comentario = Column(Text, default="")
    criado_por = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documento = relationship("Documento", back_populates="versoes")