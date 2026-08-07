# fix_db_imagem.py
from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Verificar se a coluna já existe
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'documentos' 
        AND column_name = 'imagem_url'
    """))
    
    if result.fetchone() is None:
        print("📌 Adicionando coluna imagem_url...")
        conn.execute(text("""
            ALTER TABLE documentos 
            ADD COLUMN imagem_url VARCHAR
        """))
        conn.commit()
        print("✅ Coluna imagem_url adicionada com sucesso!")
    else:
        print("✅ Coluna imagem_url já existe!")