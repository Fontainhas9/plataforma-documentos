# backend/migrate_db.py
import sys
import os

from database import engine, SessionLocal
from sqlalchemy import text
from models import Base

def migrar():
    print("📦 A criar tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    migrar()