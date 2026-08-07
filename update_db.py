# update_db.py
import sys
import os

# Adicionar o caminho do backend ao sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine
from sqlalchemy import text, inspect
from models import Base

print("📦 A verificar e atualizar a base de dados...")

def column_exists(table_name, column_name):
    """Verifica se uma coluna existe numa tabela."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_column_if_not_exists(table_name, column_name, column_type):
    """Adiciona uma coluna se ela não existir."""
    if not column_exists(table_name, column_name):
        print(f"📌 A adicionar coluna '{column_name}' à tabela '{table_name}'...")
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            conn.commit()
        print(f"✅ Coluna '{column_name}' adicionada com sucesso!")
    else:
        print(f"✅ Coluna '{column_name}' já existe na tabela '{table_name}'")

def verify_table_exists(table_name):
    """Verifica se uma tabela existe."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# ============================================================
# 1. ADICIONAR COLUNA imagem_url NA TABELA documentos
# ============================================================
print("\n🔍 A verificar tabela 'documentos'...")
if verify_table_exists('documentos'):
    add_column_if_not_exists('documentos', 'imagem_url', 'VARCHAR')
else:
    print("⚠️ Tabela 'documentos' não encontrada!")

# ============================================================
# 2. ADICIONAR COLUNA tipo NA TABELA comentarios_documento
# ============================================================
print("\n🔍 A verificar tabela 'comentarios_documento'...")
if verify_table_exists('comentarios_documento'):
    add_column_if_not_exists('comentarios_documento', 'tipo', 'VARCHAR DEFAULT \'geral\'')
    
    # ✅ Atualizar registos existentes que tenham tipo NULL
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM comentarios_documento WHERE tipo IS NULL"))
        count = result.scalar()
        if count > 0:
            print(f"📌 A atualizar {count} registos com tipo NULL para 'geral'...")
            conn.execute(text("UPDATE comentarios_documento SET tipo = 'geral' WHERE tipo IS NULL"))
            conn.commit()
            print(f"✅ {count} registos atualizados!")
else:
    print("⚠️ Tabela 'comentarios_documento' não encontrada!")

# ============================================================
# 3. VERIFICAR E CRIAR TABELAS FALTANTES
# ============================================================
print("\n🔍 A verificar se todas as tabelas existem...")

# Lista de todas as tabelas que devem existir
tables_to_check = [
    'utilizadores',
    'documentos',
    'versoes_documento',
    'notificacoes',
    'comentarios_documento',
    'documento_parceiros'
]

for table in tables_to_check:
    if verify_table_exists(table):
        print(f"✅ Tabela '{table}' existe")
    else:
        print(f"⚠️ Tabela '{table}' NÃO existe - a criar...")
        # Criar todas as tabelas que faltam
        Base.metadata.create_all(bind=engine)
        print(f"✅ Tabelas criadas!")

# ============================================================
# 4. VERIFICAR ESTRUTURA DA TABELA documentos
# ============================================================
print("\n🔍 A verificar estrutura da tabela 'documentos'...")
if verify_table_exists('documentos'):
    inspector = inspect(engine)
    columns = inspector.get_columns('documentos')
    print("📋 Colunas da tabela 'documentos':")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
else:
    print("⚠️ Tabela 'documentos' não encontrada!")

# ============================================================
# 5. VERIFICAR ESTRUTURA DA TABELA comentarios_documento
# ============================================================
print("\n🔍 A verificar estrutura da tabela 'comentarios_documento'...")
if verify_table_exists('comentarios_documento'):
    inspector = inspect(engine)
    columns = inspector.get_columns('comentarios_documento')
    print("📋 Colunas da tabela 'comentarios_documento':")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
else:
    print("⚠️ Tabela 'comentarios_documento' não encontrada!")

# ============================================================
# 6. CONTAR REGISTOS
# ============================================================
print("\n📊 Contagem de registos:")

with engine.connect() as conn:
    tables_count = [
        'utilizadores',
        'documentos',
        'versoes_documento',
        'notificacoes',
        'comentarios_documento'
    ]
    
    for table in tables_count:
        if verify_table_exists(table):
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"   - {table}: {count} registos")
        else:
            print(f"   - {table}: tabela não encontrada")

print("\n✅ Base de dados atualizada com sucesso!")

# ============================================================
# 7. SUGESTÃO PARA CRIAR UTILIZADORES DE TESTE
# ============================================================
print("\n📌 Para criar utilizadores de teste, execute:")
print("   python create_test_users.py")