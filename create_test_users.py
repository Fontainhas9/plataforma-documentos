# create_test_users.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import Utilizador, PerfilUtilizador
from auth import hash_password

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
print("✅ Done!")