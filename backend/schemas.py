# backend/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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
    parceiros_ids: List[str]
    empresa_id: str
    dados: Dict[str, Any] = {}
    imagem_url: Optional[str] = None

class DocumentoCreate(DocumentoBase):
    pass

class DocumentoUpdate(BaseModel):
    dados: Dict[str, Any]
    imagem_url: Optional[str] = None

class MudancaEstado(BaseModel):
    comentario: Optional[str] = ""

class DocumentoOut(BaseModel):
    id: int
    titulo: str
    parceiro_id: Optional[str] = None
    parceiros_ids: List[str] = []
    empresa_id: str
    estado: EstadoDocumento
    versao_atual: int
    dados: Dict[str, Any]
    imagem_url: Optional[str] = None
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

# ---------- Comentários ----------
class ComentarioCreate(BaseModel):
    mensagem: str

class ComentarioOut(BaseModel):
    id: int
    documento_id: int
    username: str
    mensagem: str
    created_at: str

    class Config:
        from_attributes = True