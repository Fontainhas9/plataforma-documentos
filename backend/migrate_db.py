# migrate_db.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, SessionLocal
from sqlalchemy import text
from models import Base

def migrar():
    db = SessionLocal()
    try:
        # Verificar se a coluna empresa_id já existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='documentos' AND column_name='empresa_id'
        """))
        coluna_existe = result.fetchone() is not None
        
        if not coluna_existe:
            print("📦 A adicionar coluna empresa_id...")
            db.execute(text("""
                ALTER TABLE documentos 
                ADD COLUMN empresa_id VARCHAR NOT NULL DEFAULT 'empresa_padrao'
            """))
            db.commit()
            print("✅ Coluna empresa_id adicionada com sucesso!")
        else:
            print("✅ Coluna empresa_id já existe.")
            
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar()