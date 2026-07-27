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
    """Renders the topbar with navigation and user info."""
    username = st.session_state.get("username", "User")
    perfil = st.session_state.get("perfil", "")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    current_page = st.query_params.get("page", "notificacoes")
    is_home = current_page == "home"
    is_dashboard = current_page == "dashboard"
    is_notifications = current_page in ["notificacoes", ""] or current_page is None
    
    home_hidden = 'hidden' if is_home else ''
    dashboard_hidden = 'hidden' if is_dashboard else ''
    notifications_hidden = 'hidden' if is_notifications else ''
    
    notif_display = f'{notif_count}' if notif_count > 0 else ''
    
    dashboard_link = ''
    if perfil == "admin":
        dashboard_link = f'<a class="dashboard-topbar__link {dashboard_hidden}" href="?page=dashboard">Dashboard</a>'
    
    topbar_html = f'''
    <style>
        .dashboard-topbar {{
            width: 100%;
            background: linear-gradient(180deg, rgba(2, 28, 53, 0.96) 0%, rgba(3, 41, 73, 0.96) 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            box-sizing: border-box;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999999;
            padding: 0 clamp(20px, 2.2vw, 56px);
            min-height: 74px;
            display: flex;
            align-items: center;
            height: 74px;
        }}
        .dashboard-topbar__inner {{
            width: 100%;
            max-width: none;
            min-height: 74px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            box-sizing: border-box;
            height: 74px;
        }}
        .dashboard-topbar__title {{
            margin: 0;
            color: #ffffff !important;
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
            font-size: 24px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: -0.02em;
            position: relative;
            cursor: pointer;
            text-decoration: none;
        }}
        .dashboard-topbar__title::after {{
            content: "";
            position: absolute;
            left: 2px;
            bottom: -6px;
            width: 60%;
            height: 2px;
            background: linear-gradient(90deg, rgb(254, 200, 0), rgba(254, 200, 0, 0.3));
            border-radius: 2px;
        }}
        .dashboard-topbar__nav {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 22px;
            flex-wrap: wrap;
        }}
        .dashboard-topbar__link {{
            color: rgba(255, 255, 255, 0.94) !important;
            text-decoration: none !important;
            font-family: "Inter", "Segoe UI", Arial, sans-serif !important;
            font-size: 15px !important;
            line-height: 1.2 !important;
            font-weight: 600 !important;
            transition: color 0.18s ease, opacity 0.18s ease !important;
            cursor: pointer !important;
            background: none !important;
            border: none !important;
            padding: 8px 4px !important;
        }}
        .dashboard-topbar__link:hover {{
            color: #ffffff !important;
            opacity: 0.82 !important;
        }}
        .dashboard-topbar__link.hidden {{
            display: none !important;
        }}
        .dashboard-topbar__divider {{
            color: rgba(255,255,255,0.3);
            font-size: 14px;
        }}
        .dashboard-topbar__username {{
            color: rgba(255,255,255,0.7);
            font-size: 14px;
            font-weight: 500;
        }}
        .dashboard-topbar__perfil {{
            color: rgba(255,255,255,0.4);
            font-size: 13px;
            font-weight: 400;
        }}
        @media (max-width: 900px) {{
            .dashboard-topbar {{ min-height: 70px; height: 70px; padding: 0 36px; }}
            .dashboard-topbar__title {{ font-size: 22px; }}
            .dashboard-topbar__nav {{ gap: 18px; }}
            .dashboard-topbar__link {{ font-size: 14px !important; }}
        }}
        @media (max-width: 640px) {{
            .dashboard-topbar {{ min-height: auto; height: auto; padding: 14px 10px; flex-wrap: wrap; }}
            .dashboard-topbar__inner {{ flex-wrap: wrap; gap: 10px; height: auto; }}
            .dashboard-topbar__title {{ font-size: 20px; }}
            .dashboard-topbar__nav {{ gap: 12px; flex-wrap: wrap; }}
            .dashboard-topbar__link {{ font-size: 13px !important; padding: 6px 2px !important; }}
        }}
        [data-testid="stSidebar"] {{ display: none !important; }}
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        [data-testid="stSidebarUserContent"] {{ display: none !important; }}
        .main > div {{ padding: 0 !important; max-width: 100% !important; }}
        .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        .stButton {{ display: none !important; }}
        
        .stDataFrame {{
            width: 80% !important;
            max-width: 80% !important;
            margin: 0 auto !important;
            overflow: visible !important;
            display: block !important;
            background: #ffffff !important;
            border-radius: 14px !important;
            border: 1px solid rgba(15, 23, 42, 0.06) !important;
        }}
        .stDataFrame > div {{
            max-width: 100% !important;
            overflow: visible !important;
            margin: 0 auto !important;
        }}
        .stDataFrame table {{
            width: 100% !important;
            table-layout: auto !important;
            margin: 0 auto !important;
        }}
        .stDataFrame thead tr th {{
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
            max-width: none !important;
            min-width: auto !important;
            background: #f0f2f5 !important;
            color: #17345a !important;
            font-weight: 600 !important;
            padding: 10px 14px !important;
            font-size: 13px !important;
        }}
        .stDataFrame tbody tr td {{
            word-break: break-word !important;
            max-width: none !important;
            min-width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
            color: #1c2f50 !important;
            padding: 8px 14px !important;
            font-size: 14px !important;
        }}
        [data-testid="stDataFrameResizable"] {{
            overflow: visible !important;
            max-width: 100% !important;
            margin: 0 auto !important;
        }}
        .element-container:has(.stDataFrame) {{
            max-width: 100% !important;
            overflow: visible !important;
            margin: 0 auto !important;
        }}
        .streamlit-expanderContent .stDataFrame {{
            width: 80% !important;
            max-width: 80% !important;
            margin: 0 auto !important;
            overflow: visible !important;
        }}
        [data-testid="column"] {{ overflow: visible !important; }}
        [data-testid="stVerticalBlock"] {{ overflow: visible !important; }}
        div[data-testid="stDataFrame"] {{
            overflow: visible !important;
            max-width: 100% !important;
            width: 80% !important;
            margin: 0 auto !important;
        }}
        .stDataFrame tbody {{
            overflow-y: auto !important;
            display: block !important;
            max-height: 500px !important;
        }}
        .stDataFrame thead,
        .stDataFrame tbody tr {{
            display: table !important;
            width: 100% !important;
            table-layout: fixed !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            padding-left: 3em !important;
        }}
        .stCaption, .stMarkdown p, .stMarkdown li, .stMarkdown div {{
            padding-left: 3em !important;
        }}
        .stAlert .stAlertContent {{
            padding-left: 3em !important;
        }}
        .element-container {{
            padding-left: 0 !important;
        }}
        .dashboard-topbar__title {{
            padding-left: 0 !important;
        }}
        .streamlit-expanderHeader {{
            padding-left: 16px !important;
        }}
        [data-testid="stMetricLabel"] {{
            padding-left: 0 !important;
        }}
        .stTextInput label, .stSelectbox label, .stTextArea label, .stCheckbox label {{
            padding-left: 0 !important;
        }}
    </style>
    
    <header class="dashboard-topbar">
        <div class="dashboard-topbar__inner">
            <a class="dashboard-topbar__title" href="?page=home">📄 DocPlatform</a>
            <nav class="dashboard-topbar__nav">
                <a class="dashboard-topbar__link {home_hidden}" href="?page=home">Home</a>
                {dashboard_link}
                <a class="dashboard-topbar__link {notifications_hidden}" href="?page=notificacoes">🔔 {notif_display}</a>
                <span class="dashboard-topbar__divider">|</span>
                <span class="dashboard-topbar__username">{username}</span>
                <span class="dashboard-topbar__perfil">({perfil})</span>
                <a class="dashboard-topbar__link" href="?logout=true">Logout</a>
            </nav>
        </div>
    </header>
    <div class="dashboard-shell" style="margin-top:90px;padding:0 clamp(20px,2.2vw,56px) 42px;max-width:none;">
    '''
    
    st.markdown(topbar_html, unsafe_allow_html=True)
    
    page = st.query_params.get("page", "notificacoes")
    if page == "home":
        st.switch_page("app.py")
    elif page == "dashboard":
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
# CLOSE MAIN CONTENT
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)