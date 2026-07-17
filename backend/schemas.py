from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from models import EstadoDocumento, PerfilUtilizador

# ---------- Autenticação ----------
class UtilizadorCreate(BaseModel):
    username: str
    password: str
    perfil: PerfilUtilizador
    nome_completo: Optional[str] = ""

class PasswordUpdate(BaseModel):
    nova_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ---------- Documentos ----------
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
    id: int
    titulo: str
    parceiro_id: str
    estado: EstadoDocumento
    versao_atual: int
    dados: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class VersaoOut(BaseModel):
    id: int
    numero_versao: int
    estado: EstadoDocumento
    comentario: Optional[str]
    criado_por: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True