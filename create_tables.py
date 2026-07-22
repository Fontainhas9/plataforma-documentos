# create_tables.py
import sys
import os

# Adicionar o caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine
from models import Base

print("📦 A criar todas as tabelas...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")