from sqlalchemy.orm import Session
from models import Notificacao, Documento, Utilizador, PerfilUtilizador
from typing import List, Dict, Optional

def criar_notificacao(
    db: Session,
    username: str,
    titulo: str,
    mensagem: str,
    link: Optional[str] = None,
    icone: str = "📄"
) -> Notificacao:
    """
    Cria uma nova notificação para um utilizador.
    """
    notificacao = Notificacao(
        username=username,
        titulo=titulo,
        mensagem=mensagem,
        link=link,
        icone=icone
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    return notificacao

def criar_notificacao_para_empresa(
    db: Session,
    documento: Documento,
    titulo: str,
    mensagem: str,
    icone: str = "📄"
):
    """
    Cria notificação para todos os utilizadores com perfil empresa e admin.
    """
    empresas = db.query(Utilizador).filter(
        Utilizador.perfil.in_([PerfilUtilizador.EMPRESA, PerfilUtilizador.ADMIN])
    ).all()
    
    for empresa in empresas:
        criar_notificacao(
            db=db,
            username=empresa.username,
            titulo=titulo,
            mensagem=mensagem,
            link=f"/documentos?doc_id={documento.id}",
            icone=icone
        )

def criar_notificacao_para_parceiro(
    db: Session,
    documento: Documento,
    titulo: str,
    mensagem: str,
    icone: str = "📄"
):
    """
    Cria notificação para o parceiro do documento.
    """
    criar_notificacao(
        db=db,
        username=documento.parceiro_id,
        titulo=titulo,
        mensagem=mensagem,
        link=f"/documentos?doc_id={documento.id}",
        icone=icone
    )

def get_notificacoes_utilizador(db: Session, username: str, limit: int = 50) -> List[Dict]:
    """
    Obtém as notificações de um utilizador.
    """
    notificacoes = db.query(Notificacao).filter(
        Notificacao.username == username
    ).order_by(Notificacao.created_at.desc()).limit(limit).all()
    
    return [n.to_dict() for n in notificacoes]

def get_notificacoes_nao_lidas_count(db: Session, username: str) -> int:
    """
    Conta as notificações não lidas de um utilizador.
    """
    return db.query(Notificacao).filter(
        Notificacao.username == username,
        Notificacao.lida == False
    ).count()