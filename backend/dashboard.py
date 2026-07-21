from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import Documento, VersaoDocumento, Utilizador, EstadoDocumento, PerfilUtilizador
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd

def get_dashboard_kpis(db: Session, current_user_username: str, perfil: str) -> Dict[str, Any]:
    """
    Obtém os KPIs principais para o dashboard.
    """
    # Query base - se for parceiro, só vê os seus documentos
    query = db.query(Documento)
    if perfil == PerfilUtilizador.PARCEIRO:
        query = query.filter(Documento.parceiro_id == current_user_username)
    
    total_documentos = query.count()
    
    # Documentos por estado
    documentos_por_estado = {}
    for estado in EstadoDocumento:
        count = query.filter(Documento.estado == estado).count()
        documentos_por_estado[estado.value] = count
    
    # Documentos aprovados
    aprovados = query.filter(Documento.estado == EstadoDocumento.APROVADO).count()
    
    # Taxa de aprovação (aprovados / total submetidos)
    submetidos = query.filter(
        or_(
            Documento.estado == EstadoDocumento.SUBMETIDO,
            Documento.estado == EstadoDocumento.EM_REVISAO,
            Documento.estado == EstadoDocumento.ALTERACOES,
            Documento.estado == EstadoDocumento.APROVADO
        )
    ).count()
    
    taxa_aprovacao = (aprovados / submetidos * 100) if submetidos > 0 else 0
    
    return {
        "total_documentos": total_documentos,
        "documentos_por_estado": documentos_por_estado,
        "aprovados": aprovados,
        "taxa_aprovacao": round(taxa_aprovacao, 1)
    }


def get_top_parceiros(db: Session, limit: int = 10) -> List[Dict]:
    """
    Obtém os parceiros com mais documentos.
    """
    resultados = db.query(
        Documento.parceiro_id,
        func.count(Documento.id).label('total')
    ).group_by(Documento.parceiro_id).order_by(
        func.count(Documento.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "parceiro": r[0],
            "total": r[1]
        }
        for r in resultados
    ]

def get_documentos_recentes(db: Session, current_user_username: str, perfil: str, limit: int = None) -> List[Dict]:
    """
    Obtém os documentos mais recentes.
    Se limit for None, retorna todos os documentos.
    """
    query = db.query(Documento)
    if perfil == PerfilUtilizador.PARCEIRO:
        query = query.filter(Documento.parceiro_id == current_user_username)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(Documento.created_at.desc())
    
    # Aplicar limite se especificado
    if limit is not None:
        query = query.limit(limit)
    
    documentos = query.all()
    
    return [
        {
            "id": doc.id,
            "titulo": doc.titulo,
            "estado": doc.estado.value,
            "parceiro_id": doc.parceiro_id,
            "created_at": doc.created_at.strftime("%d/%m/%Y %H:%M") if doc.created_at else ""
        }
        for doc in documentos
    ]