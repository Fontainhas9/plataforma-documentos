import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuração para Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "ccgcenas@gmail.com"  # O teu email
SMTP_PASSWORD = "badz gxcs ubcb zefa"  # <-- App Password do Gmail

# Endereço fixo para receber notificações
DESTINATARIO_PADRAO = "ccgcenas@gmail.com"  # O teu email

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
        print(f"✅ Email enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False