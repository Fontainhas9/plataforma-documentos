from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
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
    RASCUNHO = "rascunho"
    SUBMETIDO = "submetido"
    EM_REVISAO = "em_revisao"
    ALTERACOES = "alteracoes"
    APROVADO = "aprovado"
    ARQUIVADO = "arquivado"

class Utilizador(Base):
    __tablename__ = "utilizadores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    perfil = Column(Enum(PerfilUtilizador), nullable=False)
    nome_completo = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    documento_id = Column(UUID(as_uuid=True), ForeignKey("documentos.id"))
    numero_versao = Column(Integer, nullable=False)
    dados = Column(JSON, nullable=False)
    estado = Column(Enum(EstadoDocumento), nullable=False)
    comentario = Column(Text, default="")
    criado_por = Column(String)  # username de quem criou a versão
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documento = relationship("Documento", back_populates="versoes")