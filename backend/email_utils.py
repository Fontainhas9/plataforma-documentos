import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuração – SUBSTITUIR PELAS TUAS CREDENCIAIS
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "teuemail@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "tuapassword")

# Endereço fixo para receber notificações (podes mudar)
DESTINATARIO_PADRAO = "andre.fontainhas@holoss.pt"

def enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    """Envia email usando as credenciais configuradas."""
    if not destinatario:
        return False

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False