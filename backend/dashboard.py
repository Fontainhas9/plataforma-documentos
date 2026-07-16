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
    
    # Tempo médio de revisão (em dias)
    # Para documentos aprovados, calcular tempo entre submissão e aprovação
    tempo_revisao = []
    docs_aprovados = query.filter(Documento.estado == EstadoDocumento.APROVADO).all()
    for doc in docs_aprovados:
        versoes = db.query(VersaoDocumento).filter(
            VersaoDocumento.documento_id == doc.id
        ).order_by(VersaoDocumento.numero_versao).all()
        
        data_submissao = None
        data_aprovacao = None
        
        for v in versoes:
            if v.estado == EstadoDocumento.SUBMETIDO and not data_submissao:
                data_submissao = v.created_at
            if v.estado == EstadoDocumento.APROVADO and not data_aprovacao:
                data_aprovacao = v.created_at
                break
        
        if data_submissao and data_aprovacao:
            delta = data_aprovacao - data_submissao
            tempo_revisao.append(delta.total_seconds() / 86400)  # em dias
    
    tempo_medio_revisao = sum(tempo_revisao) / len(tempo_revisao) if tempo_revisao else 0
    
    return {
        "total_documentos": total_documentos,
        "documentos_por_estado": documentos_por_estado,
        "aprovados": aprovados,
        "taxa_aprovacao": round(taxa_aprovacao, 1),
        "tempo_medio_revisao": round(tempo_medio_revisao, 1)
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

def get_documentos_recentes(db: Session, current_user_username: str, perfil: str, limit: int = 10) -> List[Dict]:
    """
    Obtém os documentos mais recentes.
    """
    query = db.query(Documento)
    if perfil == PerfilUtilizador.PARCEIRO:
        query = query.filter(Documento.parceiro_id == current_user_username)
    
    documentos = query.order_by(Documento.created_at.desc()).limit(limit).all()
    
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