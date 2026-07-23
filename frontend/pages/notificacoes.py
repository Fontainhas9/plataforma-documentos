import streamlit as st
import requests
from datetime import datetime
import os

# ============================================================
# API URL CONFIGURATION
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

st.set_page_config(
    page_title="Notifications",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# LOAD CSS
# ============================================================
def load_css():
    try:
        css_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style.css'),
            'style.css',
            os.path.join(os.getcwd(), 'style.css'),
        ]
        css_content = None
        for path in css_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    css_content = f.read()
                break
        if css_content:
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none !important; }
                .main > div { padding: 0 !important; }
                .block-container { padding: 0 !important; }
                body { background: #032949; color: #e8edf3; font-family: "Inter", "Segoe UI", Arial, sans-serif; }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error loading CSS: {e}")

load_css()

# ============================================================
# CHECK AUTH
# ============================================================
if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Please login first.")
    st.stop()

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_notificacoes_nao_lidas():
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except:
        pass
    return 0

def get_notificacoes(limit=100):
    try:
        resp = requests.get(f"{API_URL}/notificacoes?limit={limit}", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Error loading notifications: {resp.status_code}")
            return []
    except Exception as e:
        st.error(f"Error loading notifications: {e}")
        return []

def marcar_todas_lidas():
    try:
        resp = requests.put(f"{API_URL}/notificacoes/ler-todas", headers=headers_auth())
        if resp.status_code == 200:
            count = resp.json().get("count", 0)
            st.success(f"✅ {count} notifications marked as read!")
            return True
        else:
            st.error(f"Error marking all as read: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Error marking all as read: {e}")
        return False

def marcar_como_lida(notificacao_id):
    try:
        resp = requests.put(f"{API_URL}/notificacoes/{notificacao_id}/ler", headers=headers_auth())
        if resp.status_code == 200:
            st.success("✅ Notification marked as read!")
            return True
        else:
            st.error(f"Error marking as read: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Error marking as read: {e}")
        return False

# ============================================================
# RENDER TOPBAR
# ============================================================
def render_topbar():
    username = st.session_state.get("username", "User")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    topbar_html = f'''
    <header class="dashboard-topbar">
        <div class="dashboard-topbar__inner">
            <h1 class="dashboard-topbar__title" onclick="window.location.href='?page=home'">📄 DocPlatform</h1>
            <nav class="dashboard-topbar__nav">
                <a class="dashboard-topbar__link" onclick="window.location.href='?page=home'">Home</a>
                <a class="dashboard-topbar__link" onclick="window.location.href='?page=dashboard'">Dashboard</a>
                <a class="dashboard-topbar__link active" onclick="window.location.href='?page=notificacoes'">
                    🔔 {notif_count if notif_count > 0 else ''}
                </a>
                <span style="color: rgba(255,255,255,0.3); font-size:14px;">|</span>
                <span style="color: rgba(255,255,255,0.7); font-size:14px; font-weight:500;">{username}</span>
                <button class="dashboard-topbar__link" onclick="window.location.href='?logout=true'" style="background:none;border:none;cursor:pointer;">Logout</button>
            </nav>
        </div>
    </header>
    <div class="dashboard-shell">
    '''
    st.markdown(topbar_html, unsafe_allow_html=True)
    
    if st.query_params.get("page") == "home":
        st.switch_page("app.py")
    elif st.query_params.get("page") == "dashboard":
        st.switch_page("pages/dashboard.py")
    
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        from app import logout
        logout()
        st.rerun()

render_topbar()

# ============================================================
# NOTIFICATIONS CONTENT
# ============================================================
st.title("Notifications")

# Count unread
try:
    resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
    if resp.status_code == 200:
        count = resp.json().get("count", 0)
        if count > 0:
            st.info(f"📌 You have {count} unread notification{'s' if count > 1 else ''}.")
        else:
            st.info("📌 All notifications are read.")
except:
    pass

# Action buttons
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("← Back", use_container_width=True, key="notificacoes_voltar_principal"):
        st.switch_page("app.py")
with col2:
    if st.button("Mark all as read", use_container_width=True, key="notificacoes_marcar_todas"):
        if marcar_todas_lidas():
            st.rerun()

st.divider()

# List notifications
notificacoes = get_notificacoes(100)

if not notificacoes:
    st.info("No notifications found.")
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
                    if st.button("✓ Mark read", key=f"notificacao_marcar_lida_{notif['id']}"):
                        if marcar_como_lida(notif['id']):
                            st.rerun()
                else:
                    st.write("✅ Read")
            
            if notif.get("link"):
                link = notif['link'].replace("/documentos?doc_id=", "")
                if link:
                    try:
                        doc_id = int(link)
                        if st.button("View Document", key=f"notificacao_ver_doc_{notif['id']}"):
                            st.session_state.doc_selecionado = doc_id
                            st.query_params["doc_id"] = str(doc_id)
                            st.query_params["from_notification"] = "true"
                            st.switch_page("app.py")
                    except ValueError:
                        pass
            
            st.divider()

# ============================================================
# CLOSE DASHBOARD-SHELL
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)