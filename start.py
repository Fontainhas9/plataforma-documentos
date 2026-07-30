# start.py
import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    print(f"\n🔄 Executando: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

def main():
    print("🚀 A iniciar a plataforma de documentos...")
    
    # 1. Instalar dependências
    print("\n📦 A instalar dependências...")
    run_command("pip install -r backend/requirements.txt")
    
    # 2. Criar tabelas
    print("\n🗄️ A criar tabelas...")
    run_command('python -c "import sys; sys.path.insert(0, \\"backend\\"); from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print(\\"✅ Tabelas criadas!\\")"')
    
    # 3. Criar utilizadores de teste
    print("\n👤 A criar utilizadores de teste...")
    run_command("python create_test_users.py")
    
    # 4. Iniciar o backend
    print("\n🚀 A iniciar o backend na porta 8000...")
    print("Pressiona Ctrl+C para parar")
    run_command("cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()