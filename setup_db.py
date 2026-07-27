# setup_db.py
import sys
import os

# Adicionar o caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, SessionLocal
from models import Base, Utilizador, PerfilUtilizador
from auth import hash_password

def setup_database():
    print("📦 A criar as tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    
    db = SessionLocal()
    
    # Criar utilizadores de teste
    users = [
        {"username": "empresa1", "password": "123", "perfil": PerfilUtilizador.EMPRESA, "nome_completo": "Empresa Teste"},
        {"username": "parceiro1", "password": "123", "perfil": PerfilUtilizador.PARCEIRO, "nome_completo": "Parceiro Teste"},
        {"username": "admin1", "password": "123", "perfil": PerfilUtilizador.ADMIN, "nome_completo": "Admin Teste"},
    ]
    
    for user_data in users:
        existing = db.query(Utilizador).filter(Utilizador.username == user_data["username"]).first()
        if existing:
            print(f"⚠️ User {user_data['username']} already exists")
        else:
            user = Utilizador(
                username=user_data["username"],
                password_hash=hash_password(user_data["password"]),
                perfil=user_data["perfil"],
                nome_completo=user_data["nome_completo"]
            )
            db.add(user)
            print(f"✅ User {user_data['username']} created")
    
    db.commit()
    db.close()
    print("✅ Setup concluído!")

if __name__ == "__main__":
    setup_database()