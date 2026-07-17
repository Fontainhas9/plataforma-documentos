import streamlit as st
import requests
from datetime import datetime
import os

# ============================================================
# CONFIGURAÇÃO DA API_URL
# ============================================================
def get_api_url():
    try:
        if hasattr(st, 'secrets') and st.secrets and 'API_URL' in st.secrets:
            return st.secrets['API_URL']
    except Exception:
        pass
    
    api_url = os.getenv('API_URL')
    if api_url:
        return api_url
    
    return "http://127.0.0.1:8000"

API_URL = get_api_url()

# ============================================================
# TRADUÇÕES
# ============================================================
TRADUCOES = {
    "pt": {
        "app_title": "Notificações",
        "logout": "Sair",
        "back": "← Voltar",
        "logged_as": "Logado como:",
        "no_notifications_found": "Nenhuma notificação encontrada.",
        "all_notifications_read": "📌 Todas as notificações estão lidas.",
        "unread_notifications": "📌 Você tem {count} notificação(ões) não lida(s).",
        "mark_all_read": "Marcar todas como lidas",
        "mark_read": "✓ Marcar lida",
        "read": "✅ Lida",
        "view_document": "Ver Documento",
        "notifications": "Notificações",
        "unread_notifications_one": "🔔 {count} notificação não lida",
        "unread_notifications_other": "🔔 {count} notificações não lidas"
    },
    "en": {
        "app_title": "Notifications",
        "logout": "Logout",
        "back": "← Back",
        "logged_as": "Logged as:",
        "no_notifications_found": "No notifications found.",
        "all_notifications_read": "📌 All notifications are read.",
        "unread_notifications": "📌 You have {count} unread notification(s).",
        "mark_all_read": "Mark all as read",
        "mark_read": "✓ Mark as read",
        "read": "✅ Read",
        "view_document": "View Document",
        "notifications": "Notifications",
        "unread_notifications_one": "🔔 {count} unread notification",
        "unread_notifications_other": "🔔 {count} unread notifications"
    }
}

def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("idioma", "pt")
    texto = TRADUCOES.get(lang, TRADUCOES["pt"]).get(key, key)
    if kwargs:
        try:
            return texto.format(**kwargs)
        except KeyError:
            return texto
    return texto

st.set_page_config(
    page_title=t("app_title"),
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        min-width: 270px !important;
        width: 270px !important;
    }
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Por favor, faça login primeiro.")
    st.stop()

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_notificacoes(limit=100):
    try:
        resp = requests.get(f"{API_URL}/notificacoes?limit={limit}", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Erro ao carregar notificações: {resp.status_code}")
            return []
    except Exception as e:
        st.error(f"Erro ao carregar notificações: {e}")
        return []

def marcar_todas_lidas():
    try:
        resp = requests.put(f"{API_URL}/notificacoes/ler-todas", headers=headers_auth())
        if resp.status_code == 200:
            count = resp.json().get("count", 0)
            st.success(f"✅ {count} notificações marcadas como lidas!")
            return True
        else:
            st.error(f"Erro ao marcar todas como lidas: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Erro ao marcar todas como lidas: {e}")
        return False

def marcar_como_lida(notificacao_id):
    try:
        resp = requests.put(f"{API_URL}/notificacoes/{notificacao_id}/ler", headers=headers_auth())
        if resp.status_code == 200:
            st.success("✅ Notificação marcada como lida!")
            return True
        else:
            st.error(f"Erro ao marcar como lida: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Erro ao marcar como lida: {e}")
        return False

with st.sidebar:
    st.write(f"{t('logged_as')} **{st.session_state.username}**")
    st.divider()
    
    if st.button(t("back"), use_container_width=True, key="notificacoes_sidebar_voltar"):
        st.switch_page("app.py")
    
    if st.button(t("logout"), key="notificacoes_sidebar_logout"):
        st.session_state.token = None
        st.session_state.perfil = None
        st.session_state.username = None
        st.session_state.doc_selecionado = None
        st.session_state.success_message = None
        st.session_state.menu_parceiro_widget = "Meus Documentos"
        st.session_state.redirect_to_docs = False
        st.session_state.edit_data = None
        st.session_state.new_data = None
        st.session_state.refresh_counter = 0
        st.rerun()

st.title(t("notifications"))

try:
    resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
    if resp.status_code == 200:
        count = resp.json().get("count", 0)
        if count > 0:
            if count == 1:
                st.info(t("unread_notifications_one", count=count))
            else:
                st.info(t("unread_notifications_other", count=count))
        else:
            st.info(t("all_notifications_read"))
except:
    pass

col1, col2 = st.columns([1, 5])
with col1:
    if st.button(t("back"), use_container_width=True, key="notificacoes_voltar_principal"):
        st.switch_page("app.py")
with col2:
    if st.button(t("mark_all_read"), use_container_width=True, key="notificacoes_marcar_todas"):
        if marcar_todas_lidas():
            st.rerun()

st.divider()

notificacoes = get_notificacoes(100)

if not notificacoes:
    st.info(t("no_notifications_found"))
else:
    for notif in notificacoes:
        with st.container():
            col1, col2, col3 = st.columns([0.5, 8, 1.5])
            with col1:
                st.write(notif.get("icone", "📄"))
            with col2:
                if not notif.get("lida", False):
                    st.markdown(f"**🔵 {notif['titulo']}**")
                else:
                    st.markdown(f"**{notif['titulo']}**")
                st.write(notif['mensagem'])
                st.caption(f"📅 {notif['created_at']}")
            with col3:
                if not notif.get("lida", False):
                    if st.button(t("mark_read"), key=f"notificacao_marcar_lida_{notif['id']}"):
                        if marcar_como_lida(notif['id']):
                            st.rerun()
                else:
                    st.write(t("read"))
            
            if notif.get("link"):
                link = notif['link'].replace("/documentos?doc_id=", "")
                if link:
                    try:
                        doc_id = int(link)
                        if st.button(t("view_document"), key=f"notificacao_ver_doc_{notif['id']}"):
                            st.session_state.doc_selecionado = doc_id
                            st.query_params["doc_id"] = str(doc_id)
                            st.query_params["from_notification"] = "true"
                            st.switch_page("app.py")
                    except ValueError:
                        pass
            
            st.divider()