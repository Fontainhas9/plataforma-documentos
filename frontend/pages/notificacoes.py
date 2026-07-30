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
            return True
    except Exception as e:
        print(f"Error loading CSS: {e}")
    return False

# Tentar carregar CSS, se falhar usar inline
css_loaded = load_css()

if not css_loaded:
    st.markdown("""
    <style>
        .stApp { background: radial-gradient(circle at top left, rgba(67, 116, 170, 0.18), transparent 28%), linear-gradient(180deg, #032949 0%, #083b67 100%) !important; }
        .stAppViewContainer { background: transparent !important; overflow: hidden !important; height: 100vh !important; }
        .stMain { background: transparent !important; overflow: hidden !important; }
        .st-emotion-cache-1r6slb0 { background: transparent !important; overflow: hidden !important; padding: 0 !important; margin: 0 !important; }
        .st-emotion-cache-16idsys { background: transparent !important; overflow: hidden !important; padding: 0 !important; margin: 0 !important; }
        [data-testid="stAppViewContainer"] > div:first-child { display: none !important; }
        [data-testid="stAppViewBlockContainer"] { overflow: hidden !important; background: transparent !important; padding: 0 !important; margin: 0 !important; }
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        .main > div { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
        
        .dashboard-topbar { width: 100%; background: linear-gradient(180deg, rgba(2, 28, 53, 0.96) 0%, rgba(3, 41, 73, 0.96) 100%); border-bottom: 1px solid rgba(255, 255, 255, 0.06); box-sizing: border-box; position: fixed !important; top: 0 !important; left: 0 !important; right: 0 !important; z-index: 999999 !important; padding: 0 clamp(20px, 2.2vw, 56px); min-height: 74px; display: flex !important; align-items: center; height: 74px; margin: 0 !important; }
        .dashboard-topbar__inner { width: 100%; max-width: none; margin: 0 auto; display: flex !important; align-items: center; justify-content: space-between; gap: 24px; box-sizing: border-box; height: 74px; }
        .dashboard-topbar__title { margin: 0; color: #ffffff !important; font-family: "Inter", "Segoe UI", Arial, sans-serif; font-size: 24px; line-height: 1.1; font-weight: 700; letter-spacing: -0.02em; position: relative; cursor: pointer; text-decoration: none !important; padding-left: 0 !important; background: none !important; }
        .dashboard-topbar__title::after { content: ""; position: absolute; left: 2px; bottom: -6px; width: 60%; height: 2px; background: linear-gradient(90deg, rgb(254, 200, 0), rgba(254, 200, 0, 0.3)); border-radius: 2px; }
        .dashboard-topbar__nav { display: flex !important; align-items: center; justify-content: flex-end; gap: 22px; flex-wrap: wrap; }
        .dashboard-topbar__link { color: rgba(255, 255, 255, 0.94) !important; text-decoration: none !important; font-family: "Inter", "Segoe UI", Arial, sans-serif !important; font-size: 15px !important; line-height: 1.2 !important; font-weight: 600 !important; transition: color 0.18s ease, opacity 0.18s ease !important; cursor: pointer !important; background: none !important; border: none !important; padding: 8px 4px !important; display: inline-block !important; }
        .dashboard-topbar__link:hover { color: #ffffff !important; opacity: 0.82 !important; }
        .dashboard-topbar__link.hidden { display: none !important; }
        .dashboard-topbar__nav .dashboard-topbar__link + .dashboard-topbar__link { position: relative; }
        .dashboard-topbar__nav .dashboard-topbar__link + .dashboard-topbar__link::before { content: ""; position: absolute; left: -11px; top: 50%; width: 1px; height: 14px; background: rgb(254, 200, 0); transform: translateY(-50%); }
        .dashboard-topbar__link:empty { display: none !important; }
        
        .dashboard-shell { position: fixed !important; top: 74px !important; left: 0 !important; right: 0 !important; bottom: 0 !important; overflow-y: auto !important; overflow-x: hidden !important; padding: 20px clamp(20px, 2.2vw, 56px) 42px !important; background: transparent !important; box-sizing: border-box; width: 100% !important; margin: 0 !important; }
        .dashboard-shell::-webkit-scrollbar { width: 6px; }
        .dashboard-shell::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); border-radius: 3px; }
        .dashboard-shell::-webkit-scrollbar-thumb { background: rgba(254, 200, 0, 0.4); border-radius: 3px; }
        .dashboard-shell::-webkit-scrollbar-thumb:hover { background: rgba(254, 200, 0, 0.6); }
        
        [data-testid="stSidebar"] { display: none !important; }
        .stApp > header { display: none !important; }
        .stAppHeader, .stDecoration { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

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

def logout():
    st.session_state.token = None
    st.session_state.perfil = None
    st.session_state.username = None
    st.session_state.doc_selecionado = None
    st.session_state.success_message = None
    st.session_state.menu_parceiro_widget = "My Documents"
    st.session_state.redirect_to_docs = False
    st.session_state.edit_data = None
    st.session_state.new_data = None
    st.session_state.refresh_counter = 0
    st.session_state.ultimo_count = 0
    st.session_state.expander_aberto = False
    st.session_state.show_create_user_form = False
    st.session_state.processos_do_documento = []
    st.session_state.empresa_mostrar_form = False
    st.session_state.admin_mostrar_form = False
    st.query_params.clear()
    st.rerun()

def render_topbar():
    """Renders the topbar with navigation and user info."""
    username = st.session_state.get("username", "User")
    perfil = st.session_state.get("perfil", "")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    current_page = st.query_params.get("page", "notificacoes")
    is_home = current_page == "home"
    is_dashboard = current_page == "dashboard"
    is_notifications = current_page in ["notificacoes", ""] or current_page is None
    
    notif_display = f'({notif_count})' if notif_count > 0 else ''
    
    dashboard_btn = ''
    if perfil == "admin":
        if is_dashboard:
            dashboard_btn = '<span class="topbar-link active">Dashboard</span>'
        else:
            dashboard_btn = f'<a class="topbar-link" href="?page=dashboard">Dashboard</a>'
    
    topbar_html = f'''
    <style>
        .topbar-container {{
            width: 100%;
            background: linear-gradient(180deg, rgba(2, 28, 53, 0.96) 0%, rgba(3, 41, 73, 0.96) 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
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
            box-sizing: border-box;
        }}
        .topbar-inner {{
            width: 100%;
            max-width: none;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            height: 74px;
            box-sizing: border-box;
        }}
        .topbar-title {{
            margin: 0;
            color: #ffffff !important;
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
            font-size: 24px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: -0.02em;
            text-decoration: none;
            position: relative;
            background: none !important;
            border: none !important;
            padding: 0 !important;
            cursor: pointer;
        }}
        .topbar-title::after {{
            content: "";
            position: absolute;
            left: 2px;
            bottom: -6px;
            width: 60%;
            height: 2px;
            background: linear-gradient(90deg, rgb(254, 200, 0), rgba(254, 200, 0, 0.3));
            border-radius: 2px;
        }}
        .topbar-title:hover {{
            color: #ffffff !important;
            opacity: 0.82 !important;
        }}
        .topbar-nav {{
            display: flex;
            align-items: center;
            gap: 22px;
            flex-wrap: wrap;
        }}
        .topbar-link {{
            color: rgba(255, 255, 255, 0.94) !important;
            text-decoration: none !important;
            font-family: "Inter", "Segoe UI", Arial, sans-serif !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 8px 4px !important;
            transition: color 0.18s ease, opacity 0.18s ease !important;
            cursor: pointer !important;
            background: none !important;
            border: none !important;
            display: inline-block !important;
            position: relative;
        }}
        .topbar-link:hover {{
            color: #ffffff !important;
            opacity: 0.82 !important;
        }}
        .topbar-link.active {{
            color: rgba(255, 255, 255, 0.4) !important;
            cursor: default !important;
        }}
        .topbar-link.active:hover {{
            opacity: 1 !important;
        }}
        .topbar-nav .topbar-link + .topbar-link::before,
        .topbar-nav .topbar-link + .topbar-divider::before {{
            content: "";
            position: absolute;
            left: -11px;
            top: 50%;
            width: 1px;
            height: 14px;
            background: rgb(254, 200, 0);
            transform: translateY(-50%);
        }}
        .topbar-nav .topbar-link + .topbar-divider,
        .topbar-nav .topbar-divider + .topbar-link {{
            position: relative;
        }}
        .topbar-divider {{
            color: rgba(255, 255, 255, 0.3);
            font-size: 14px;
            padding: 0 4px;
        }}
        .topbar-user {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 500;
        }}
        .topbar-perfil {{
            color: rgba(255, 255, 255, 0.4);
            font-size: 13px;
            font-weight: 400;
        }}
        .dashboard-shell {{
            margin-top: 90px;
            padding: 20px clamp(20px, 2.2vw, 56px) 42px;
            background: transparent !important;
        }}
        @media (max-width: 640px) {{
            .topbar-container {{ padding: 14px 10px; height: auto; min-height: auto; flex-wrap: wrap; }}
            .topbar-inner {{ flex-wrap: wrap; gap: 10px; height: auto; }}
            .topbar-title {{ font-size: 20px; }}
            .topbar-nav {{ gap: 12px; flex-wrap: wrap; }}
            .topbar-link {{ font-size: 13px !important; padding: 6px 2px !important; }}
            .dashboard-shell {{ margin-top: 120px; padding: 14px 10px 24px; }}
        }}
    </style>
    
    <div class="topbar-container">
        <div class="topbar-inner">
            <a class="topbar-title" href="?page=home">📄 DocPlatform</a>
            <nav class="topbar-nav">
                <a class="topbar-link {'active' if is_home else ''}" href="?page=home">Home</a>
                {dashboard_btn}
                <a class="topbar-link {'active' if is_notifications else ''}" href="?page=notificacoes">Notifications {notif_display}</a>
                <span class="topbar-divider">|</span>
                <span class="topbar-user">{username}</span>
                <span class="topbar-perfil">({perfil})</span>
                <a class="topbar-link" href="?logout=true">Logout</a>
            </nav>
        </div>
    </div>
    <div class="dashboard-shell">
    '''
    
    st.markdown(topbar_html, unsafe_allow_html=True)
    
    page = st.query_params.get("page", "notificacoes")
    logout_param = st.query_params.get("logout", "false")
    
    if logout_param == "true" or page == "logout":
        st.query_params.clear()
        logout()
        st.rerun()
        return
    
    if page == "home":
        try:
            st.switch_page("app.py")
            return
        except:
            st.query_params.clear()
            st.rerun()
            return
    
    if page == "dashboard":
        try:
            st.switch_page("pages/dashboard.py")
            return
        except:
            st.query_params.clear()
            st.rerun()
            return


        
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