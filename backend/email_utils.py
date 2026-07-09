import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import json
import os

# ---------- CONFIGURAÇÃO OAuth2 (Microsoft Graph API) ----------
# Obtém estas informações do Azure AD:
TENANT_ID = "o-teu-tenant-id"  # ID do diretório (inquilino)
CLIENT_ID = "o-teu-client-id"  # ID da aplicação (cliente)
CLIENT_SECRET = "o-teu-client-secret"  # O segredo do cliente que criaste

# Quem vai receber os emails 
DESTINATARIO_PADRAO = "andre.fontainhas@holoss.com"

# Endereço que vai aparecer como remetente (tem de ser um email válido do teu domínio)
FROM_EMAIL = "andre.fontainhas@holoss.com"

def obter_token_oauth2():
    """
    Obtém um token de acesso OAuth2 usando as credenciais da aplicação.
    """
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        print("✅ Token OAuth2 obtido com sucesso!")
        return token_data.get("access_token")
    except Exception as e:
        print(f"❌ Erro ao obter token OAuth2: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Detalhes: {e.response.text}")
        return None

def enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    """
    Envia um email usando a Microsoft Graph API com OAuth2.
    """
    try:
        # Obter token OAuth2
        token = obter_token_oauth2()
        if not token:
            print("❌ Não foi possível obter token OAuth2")
            return False
        
        # Construir o email no formato da Graph API
        email_data = {
            "message": {
                "subject": assunto,
                "body": {
                    "contentType": "Text",
                    "content": corpo
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": destinatario
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }
        
        # Enviar usando a Graph API
        url = "https://graph.microsoft.com/v1.0/users/andre.fontainhas@holoss.com/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"📧 A enviar email para {destinatario}...")
        response = requests.post(url, json=email_data, headers=headers)
        
        if response.status_code == 202:
            print(f"✅ Email enviado com sucesso para {destinatario}")
            return True
        else:
            print(f"❌ Erro ao enviar email: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

# Função de teste para verificar configuração
def testar_email():
    """Função de teste para verificar se o email está a funcionar."""
    resultado = enviar_email(
        "andre.fontainhas@holoss.com",
        "🧪 Teste de configuração OAuth2",
        "Este é um email de teste da plataforma de documentos.\n\n"
        "Se recebeste este email, a configuração OAuth2 está correta!\n\n"
        "Data: " + __import__('datetime').datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )
    return resultado

if __name__ == "__main__":
    print("🔧 A testar configuração de email...")
    testar_email()