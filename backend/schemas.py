from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models import EstadoDocumento

class DocumentoBase(BaseModel):
    titulo: str
    parceiro_id: str
    dados: Dict[str, Any] = {}

class DocumentoCreate(DocumentoBase):
    pass

class DocumentoUpdate(BaseModel):
    dados: Dict[str, Any]

class MudancaEstado(BaseModel):
    comentario: Optional[str] = ""

class DocumentoOut(BaseModel):
    id: UUID
    titulo: str
    parceiro_id: str
    estado: EstadoDocumento
    versao_atual: int
    dados: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class VersaoOut(BaseModel):
    id: UUID
    numero_versao: int
    estado: EstadoDocumento
    comentario: Optional[str]
    criado_por: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True