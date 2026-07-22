import streamlit as st
import requests
import pandas as pd
import copy
from datetime import datetime
import os
import sys

# ============================================================
# ADD FRONTEND DIRECTORY TO PATH FOR IMPORTS
# ============================================================
frontend_dir = os.path.dirname(os.path.abspath(__file__))
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

# ============================================================
# LOAD CSS - FROM EXTERNAL FILE
# ============================================================
def load_css():
    """Loads the external CSS file."""
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'style.css')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css = f.read()
                st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
                print(f"✅ CSS loaded from: {css_path}")
                return
    except Exception as e:
        print(f"Error loading CSS from file: {e}")
    
    # Fallback minimal CSS
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        .main > div { padding: 0 !important; max-width: 100% !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        .main-content { margin-top: 80px; padding: 0 2rem 2rem 2rem; max-width: 1100px; margin-left: auto; margin-right: auto; }
        .stat-card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.05); }
        .stat-value { font-size: 2rem; font-weight: 700; color: white; }
        .stat-label { font-size: 0.8rem; color: #80809a; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

load_css()

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

# Default processes
PROCESSOS_PADRAO = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = ["Measured", "Calculated", "Estimated", "Literature"]

# ============================================================
# FUNCTION TO FORMAT DATE/TIME
# ============================================================
def formatar_data_hora(data_str):
    if not data_str:
        return ""
    try:
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y %H:%M")
        data_str = str(data_str).replace('Z', '').replace('T', ' ')
        formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
        for fmt in formats:
            try:
                dt = datetime.strptime(data_str, fmt)
                return dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        return data_str
    except Exception:
        return str(data_str)

# Page configuration
st.set_page_config(
    page_title="Document Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import notification component
try:
    from componentes.notificacoes import get_notificacoes_nao_lidas
except ImportError:
    def get_notificacoes_nao_lidas():
        return 0

# ============================================================
# JAVASCRIPT FOR AUTO SCROLL
# ============================================================
st.markdown("""
<script>
    function checkScrollParam() {
        var urlParams = new URLSearchParams(window.location.search);
        var targetId = urlParams.get('scroll_to');
        if (targetId) {
            setTimeout(function() {
                var element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
            setTimeout(function() {
                var element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 400);
            setTimeout(function() {
                var element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 800);
            setTimeout(function() {
                urlParams.delete('scroll_to');
                var newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState({}, '', newUrl);
            }, 1000);
        }
    }
    window.addEventListener('load', function() {
        setTimeout(checkScrollParam, 200);
    });
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(checkScrollParam, 300);
    });
</script>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if "token" not in st.session_state:
    st.session_state.token = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "username" not in st.session_state:
    st.session_state.username = None
if "doc_selecionado" not in st.session_state:
    st.session_state.doc_selecionado = None
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "redirect_to_docs" not in st.session_state:
    st.session_state.redirect_to_docs = False
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None
if "new_data" not in st.session_state:
    st.session_state.new_data = None
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0
if "pw_input_counter" not in st.session_state:
    st.session_state.pw_input_counter = 0
if "parceiro_dropdown_key" not in st.session_state:
    st.session_state.parceiro_dropdown_key = 0
if "empresa_dropdown_key" not in st.session_state:
    st.session_state.empresa_dropdown_key = 0
if "admin_dropdown_key" not in st.session_state:
    st.session_state.admin_dropdown_key = 0
if "admin_user_dropdown_key" not in st.session_state:
    st.session_state.admin_user_dropdown_key = 0
if "ultimo_count" not in st.session_state:
    st.session_state.ultimo_count = 0
if "show_create_user_form" not in st.session_state:
    st.session_state.show_create_user_form = False
if "close_doc_after_action" not in st.session_state:
    st.session_state.close_doc_after_action = False
if "expander_aberto" not in st.session_state:
    st.session_state.expander_aberto = False
if "processos_do_documento" not in st.session_state:
    st.session_state.processos_do_documento = []
if "empresa_form_key" not in st.session_state:
    st.session_state.empresa_form_key = 0
if "admin_form_key" not in st.session_state:
    st.session_state.admin_form_key = 0
if "empresa_mostrar_form" not in st.session_state:
    st.session_state.empresa_mostrar_form = False
if "admin_mostrar_form" not in st.session_state:
    st.session_state.admin_mostrar_form = False

# Filter state
if "filtros_widget_key" not in st.session_state:
    st.session_state.filtros_widget_key = 0
if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "q": "", "estados": [], "data_inicio": None, "data_fim": None,
        "order_by": "id", "order_dir": "desc"
    }
if "filtros_temporarios" not in st.session_state:
    st.session_state.filtros_temporarios = {
        "q": "", "estados": [], "data_inicio": None, "data_fim": None,
        "order_by": "id", "order_dir": "desc"
    }

# ============================================================
# HEADER COMPONENT
# ============================================================
def render_header():
    username = st.session_state.get("username", "User")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    current_page = st.query_params.get("page", "home")
    is_home = current_page == "home" or current_page == ""
    is_dashboard = current_page == "dashboard"
    is_notifications = current_page == "notificacoes"
    
    badge_html = f'<span class="badge">{notif_count}</span>' if notif_count > 0 else ''
    
    header_html = f'''
    <header class="main-header">
        <div class="header-logo" onclick="window.location.href='?page=home'">
            <div class="logo-icon">📄</div>
            <span>DocPlatform</span>
        </div>
        <nav class="header-nav">
            <a class="{'active' if is_home else ''}" onclick="window.location.href='?page=home'">Home</a>
            <a class="{'active' if is_dashboard else ''}" onclick="window.location.href='?page=dashboard'">Dashboard</a>
            <span class="nav-divider"></span>
            <a class="{'active' if is_notifications else ''}" onclick="window.location.href='?page=notificacoes'">Notifications</a>
        </nav>
        <div class="header-user">
            <span class="user-name">{username}</span>
            <button class="notification-bell" onclick="window.location.href='?page=notificacoes'">
                🔔{badge_html}
            </button>
            <div class="user-avatar">{username[0].upper() if username else 'U'}</div>
            <button class="logout-btn" onclick="window.location.href='?logout=true'">Logout</button>
        </div>
    </header>
    <div class="main-content">
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        logout()
        st.rerun()
    
    if st.query_params.get("page") == "dashboard":
        st.switch_page("pages/dashboard.py")
    elif st.query_params.get("page") == "notificacoes":
        st.switch_page("pages/notificacoes.py")
    
    return username

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def safe_copy(data):
    return copy.deepcopy(data)

def get_processos_from_data(data):
    if data and "lca" in data and "inputs" in data["lca"]:
        processos = list(data["lca"]["inputs"].keys())
        if processos:
            return processos
    return PROCESSOS_PADRAO

def ensure_new_structure(data, processos=None):
    if processos is None:
        processos = PROCESSOS_PADRAO
    if not data:
        return {
            "lca": {"inputs": {p: [] for p in processos}, "processes": {p: [] for p in processos}, "outputs": {p: [] for p in processos}},
            "lcc": {"materials": {p: [] for p in processos}, "equipment": {p: [] for p in processos}, "labour": {p: [] for p in processos}, "outputs": {p: [] for p in processos}}
        }
    if "lca" in data and "lcc" in data:
        for secao in ["lca", "lcc"]:
            for campo in data[secao].keys():
                if not isinstance(data[secao][campo], dict):
                    data[secao][campo] = {}
                for p in processos:
                    if p not in data[secao][campo]:
                        data[secao][campo][p] = []
        return data
    new_data = {
        "lca": {"inputs": {p: [] for p in processos}, "processes": {p: [] for p in processos}, "outputs": {p: [] for p in processos}},
        "lcc": {"materials": {p: [] for p in processos}, "equipment": {p: [] for p in processos}, "labour": {p: [] for p in processos}, "outputs": {p: [] for p in processos}}
    }
    if "lca" in data:
        for campo in ["inputs", "processes", "outputs"]:
            if campo in data["lca"] and isinstance(data["lca"][campo], dict):
                for p in processos:
                    if p in data["lca"][campo]:
                        new_data["lca"][campo][p] = data["lca"][campo][p]
    if "lcc" in data:
        for campo in ["materials", "equipment", "labour", "outputs"]:
            if campo in data["lcc"] and isinstance(data["lcc"][campo], dict):
                for p in processos:
                    if p in data["lcc"][campo]:
                        new_data["lcc"][campo][p] = data["lcc"][campo][p]
    return new_data

# ============================================================
# API FUNCTIONS
# ============================================================
def login(username, password):
    resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
    if resp.status_code == 200:
        dados = resp.json()
        st.session_state.token = dados["access_token"]
        headers = {"Authorization": f"Bearer {dados['access_token']}"}
        me = requests.get(f"{API_URL}/me", headers=headers)
        if me.status_code == 200:
            user_info = me.json()
            st.session_state.perfil = user_info["perfil"]
            st.session_state.username = user_info["username"]
        return True
    else:
        st.error("Invalid credentials")
        return False

def logout():
    st.session_state.token = None
    st.session_state.perfil = None
    st.session_state.username = None
    st.session_state.doc_selecionado = None
    st.session_state.success_message = None
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

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def listar_documentos(estado=None):
    if st.session_state.token is None:
        return []
    params = {}
    if estado:
        params["estado"] = estado
    resp = requests.get(f"{API_URL}/documentos", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def listar_documentos_com_filtros(filtros):
    if st.session_state.token is None:
        return []
    params = {}
    if filtros.get("q"):
        params["q"] = filtros["q"]
    if filtros.get("estados"):
        params["estados"] = ",".join(filtros["estados"])
    if filtros.get("data_inicio"):
        params["data_inicio"] = filtros["data_inicio"]
    if filtros.get("data_fim"):
        params["data_fim"] = filtros["data_fim"]
    if filtros.get("order_by"):
        params["order_by"] = filtros["order_by"]
    if filtros.get("order_dir"):
        params["order_dir"] = filtros["order_dir"]
    resp = requests.get(f"{API_URL}/documentos/pesquisar", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def criar_documento(titulo, parceiro_id, dados):
    payload = {"titulo": titulo, "parceiro_id": parceiro_id, "empresa_id": st.session_state.username, "dados": dados}
    resp = requests.post(f"{API_URL}/documentos/", json=payload, headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            erro = resp.json().get("detail", "Unknown error")
        except:
            erro = resp.text
        st.error(f"Error creating document: {erro}")
        return None

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Error fetching document: {resp.text}")
        return None

def editar_documento(doc_id, dados):
    resp = requests.put(f"{API_URL}/documentos/{doc_id}/editar", json={"dados": dados}, headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Error editing: {resp.text}")
        return None

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error submitting: {resp.text}")
        return None
    st.success("Document submitted successfully!")
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.expander_aberto = False
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error starting review: {resp.text}")
        return None
    st.success("Review started successfully!")
    st.session_state.doc_selecionado = doc_id
    st.session_state.expander_aberto = True
    st.rerun()
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/pedir-alteracoes", json={"comentario": comentario}, headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error requesting changes: {resp.text}")
        return None
    st.success("Changes requested successfully!")
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error reopening: {resp.text}")
        return None
    st.success("Document reopened for editing!")
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.expander_aberto = False
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error approving: {resp.text}")
        return None
    st.success("Document approved successfully!")
    st.session_state.doc_selecionado = None
    st.session_state.expander_aberto = False
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error reopening: {resp.text}")
        return None
    st.success("Document reopened successfully!")
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def arquivar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/arquivar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Error archiving: {resp.text}")
        return None
    st.success("Document archived successfully!")
    st.session_state.doc_selecionado = None
    st.session_state.expander_aberto = False
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def listar_versoes(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/versoes", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    return []

def exportar_excel(doc_id, titulo):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/exportar-excel", headers=headers_auth())
    if resp.status_code == 200:
        content = resp.content
        filename = f"{titulo}.xlsx"
        filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
        return content, filename
    else:
        try:
            erro = resp.json().get("detail", "Unknown error")
        except:
            erro = "Error exporting"
        st.error(f"Export failed: {erro}")
        return None, None

# ============================================================
# UI FUNCTIONS
# ============================================================
def get_notificacoes_nao_lidas():
    if st.session_state.token is None:
        return 0
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception as e:
        print(f"Error getting notifications: {e}")
    return 0

def show_document_summary(documentos):
    if not documentos:
        st.info("No documents found.")
        return
    estado_groups = {
        "Draft": ["Draft", "Rascunho"],
        "Submitted": ["Submitted", "Submetido"],
        "In Review": ["In Review", "Em Revisão"],
        "Changes Requested": ["Changes Requested", "Alterações"],
        "Approved": ["Approved", "Aprovado"],
        "Archived": ["Archived", "Arquivado"]
    }
    contagens = {group: 0 for group in estado_groups.keys()}
    for doc in documentos:
        estado = doc.get("estado", "")
        for group, values in estado_groups.items():
            if estado in values:
                contagens[group] += 1
                break
    cols = st.columns(len(contagens))
    for i, (estado, count) in enumerate(contagens.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{count}</div>
                <div class="stat-label">{estado}</div>
            </div>
            """, unsafe_allow_html=True)

def display_dataframe(df):
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [col.title() for col in df.columns]
        df = df.reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("(no data)")

def render_filtros():
    with st.expander("Search Filters", expanded=False):
        col1, col2 = st.columns(2)
        key_suffix = st.session_state.filtros_widget_key
        with col1:
            q = st.text_input("Search", value=st.session_state.filtros_temporarios.get("q", ""), placeholder="Title, partner or ID...", key=f"filtro_q_{key_suffix}")
            st.session_state.filtros_temporarios["q"] = q
            estados_disponiveis = ["Draft", "Submitted", "In Review", "Changes Requested", "Approved", "Archived"]
            estados_selecionados = st.multiselect("Status", options=estados_disponiveis, default=st.session_state.filtros_temporarios.get("estados", []), key=f"filtro_estados_{key_suffix}")
            st.session_state.filtros_temporarios["estados"] = estados_selecionados
        with col2:
            data_inicio = st.date_input("Start Date", value=st.session_state.filtros_temporarios.get("data_inicio"), format="DD/MM/YYYY", key=f"filtro_data_inicio_{key_suffix}")
            st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
            data_fim = st.date_input("End Date", value=st.session_state.filtros_temporarios.get("data_fim"), format="DD/MM/YYYY", key=f"filtro_data_fim_{key_suffix}")
            st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
        col5, col6 = st.columns(2)
        with col5:
            if st.button("Apply Filters", use_container_width=True):
                st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                st.rerun()
        with col6:
            if st.button("Clear Filters", use_container_width=True):
                st.session_state.filtros_temporarios = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                st.session_state.filtros_aplicados = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                st.session_state.filtros_widget_key += 1
                st.rerun()

# ============================================================
# RENDER FUNCTIONS - LCA/LCC FORMS
# ============================================================
# (As funções render_lca_* e render_lcc_* permanecem iguais ao código anterior)
# Para não repetir todo o código, mantenha as funções existentes.

# ============================================================
# FUNCTION TO CREATE ANCHOR AND TRIGGER SCROLL
# ============================================================
def create_document_anchor(doc_id):
    st.markdown(f'<div id="doc-{doc_id}" class="doc-anchor"></div>', unsafe_allow_html=True)

def trigger_scroll(doc_id):
    st.query_params["scroll_to"] = str(doc_id)

# ============================================================
# FUNCTION TO LIST AVAILABLE PARTNERS
# ============================================================
def listar_parceiros_disponiveis():
    try:
        resp = requests.get(f"{API_URL}/parceiros/disponiveis", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Error loading partners: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        st.error(f"Error loading partners: {e}")
        return []

# ============================================================
# FUNCTION TO RENDER PROCESS SELECTION
# ============================================================
def render_processos_selecao(key_prefix="empresa"):
    processos_disponiveis = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
    session_key = f"processos_selecionados_{key_prefix}"
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    input_key = f"{key_prefix}_novo_processo_input"
    processos_selecionados = st.session_state[session_key]
    st.write("**Default processes:**")
    col1, col2 = st.columns(2)
    with col1:
        for i, proc in enumerate(processos_disponiveis[:2]):
            checked = st.checkbox(proc, key=f"{key_prefix}_proc_{i}", value=proc in processos_selecionados)
            if checked and proc not in processos_selecionados:
                processos_selecionados.append(proc)
            elif not checked and proc in processos_selecionados:
                processos_selecionados.remove(proc)
    with col2:
        for i, proc in enumerate(processos_disponiveis[2:]):
            checked = st.checkbox(proc, key=f"{key_prefix}_proc_{i+2}", value=proc in processos_selecionados)
            if checked and proc not in processos_selecionados:
                processos_selecionados.append(proc)
            elif not checked and proc in processos_selecionados:
                processos_selecionados.remove(proc)
    st.divider()
    st.write("**Add new process:**")
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        novo_processo = st.text_input("New process name", placeholder="Ex: Drying, Milling, etc.", key=input_key)
    with col_add2:
        if st.button("Add new process", key=f"{key_prefix}_add_processo_btn"):
            if novo_processo and novo_processo.strip():
                if novo_processo not in processos_selecionados:
                    processos_selecionados.append(novo_processo.strip())
                    st.success(f"✅ Process '{novo_processo}' added!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Process '{novo_processo}' is already in the list.")
                    st.rerun()
            else:
                st.warning("⚠️ Please enter a name for the process.")
    if processos_selecionados:
        st.divider()
        st.write("**Selected processes:**")
        cols = st.columns(min(len(processos_selecionados), 4))
        for i, proc in enumerate(processos_selecionados):
            col_idx = i % len(cols) if len(cols) > 0 else 0
            with cols[col_idx]:
                if st.button(f"✖ {proc}", key=f"{key_prefix}_remover_{proc}_{i}"):
                    processos_selecionados.remove(proc)
                    st.rerun()
        if st.button("🗑️ Clear all", key=f"{key_prefix}_limpar_processos"):
            st.session_state[session_key] = []
            st.rerun()
    else:
        st.info("No process selected. Select the checkboxes above or add a new process.")
    st.session_state[session_key] = processos_selecionados
    return processos_selecionados

# ============================================================
# MAIN INTERFACE
# ============================================================

# Check if user is authenticated
if st.session_state.token is None:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login(username, password):
                st.session_state.success_message = "Login successful!"
                st.rerun()
    st.stop()

# ============================================================
# FROM HERE, USER IS AUTHENTICATED - RENDER HEADER
# ============================================================

# Render the fixed header
username = render_header()

# Show success message with toast
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

# Process document opening from notifications
if "doc_id" in st.query_params and st.query_params["doc_id"]:
    try:
        doc_id = int(st.query_params["doc_id"])
        st.session_state.doc_selecionado = doc_id
        st.query_params.clear()
    except ValueError:
        pass

if st.session_state.redirect_to_docs:
    st.session_state.redirect_to_docs = False

# If close_doc_after_action is active, close the document
if st.session_state.get("close_doc_after_action", False):
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False

# ============================================================
# MAIN CONTENT
# ============================================================

st.title("📄 Document Management Platform")

# ---------- Document summary ----------
if st.session_state.perfil != "admin":
    documentos = listar_documentos()
    if documentos:
        st.subheader("📊 Document Summary")
        show_document_summary(documentos)
        st.divider()
    else:
        st.info("No documents found. Start by creating a new document.")

# ---------- Partner Area ----------
if st.session_state.perfil == "parceiro":
    st.header("👤 Partner Area")
    st.caption("Documents are created by the company. You only fill in the data and submit.")
    
    st.subheader("📋 My Documents")
    
    if st.button("🔄 Refresh list", key="refresh_list_parceiro"):
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
        st.session_state.parceiro_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos()
    if not documentos:
        st.info("No documents found. Wait for the company to create a document for you.")
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Title", "Status", "Version", "Last Update"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]
        id_selecionado = st.selectbox(
            "Select a document:",
            ids,
            format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
            key=f"parceiro_selectbox_{st.session_state.parceiro_dropdown_key}",
            placeholder="Choose an option"
        )

        if st.button("📂 Load document", key="parceiro_carregar_doc"):
            if not id_selecionado:
                st.warning("Please select a document.")
            else:
                st.session_state.doc_selecionado = id_selecionado
                st.session_state.expander_aberto = False
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']}")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")
            st.caption(f"Created by: {doc.get('empresa_id', 'N/A')}")
            
            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            with st.expander("📊 View data in tables", expanded=st.session_state.get("expander_aberto", False)):
                st.subheader("LCA")
                lca = dados.get("lca", {})
                for proc in processos:
                    st.write(f"**{proc}**")
                    if lca.get("inputs", {}).get(proc):
                        st.write("Inputs")
                        display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                    if lca.get("processes", {}).get(proc):
                        st.write("Processes")
                        display_dataframe(pd.DataFrame(lca["processes"][proc]))
                    if lca.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                st.subheader("LCC")
                lcc = dados.get("lcc", {})
                for proc in processos:
                    st.write(f"**{proc}**")
                    if lcc.get("materials", {}).get(proc):
                        st.write("Cost Breakdown Material")
                        display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                    if lcc.get("equipment", {}).get(proc):
                        st.write("Equipment")
                        display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                    if lcc.get("labour", {}).get(proc):
                        st.write("Labour")
                        display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                    if lcc.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

            with st.expander("🔍 View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            estado_doc = doc.get('estado', '')
            is_draft = estado_doc in ["Draft", "Rascunho"]
            
            if is_draft:
                st.subheader("✏️ Edit Document")
                st.info("Fill in the data below and submit for validation.")
                
                if st.session_state.edit_data is None:
                    st.session_state.edit_data = ensure_new_structure(safe_copy(dados), processos)
                render_full_form("edit_data", prefix="edit_", processos=processos)
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("💾 Save Draft", key="parceiro_save_edit", use_container_width=True):
                        try:
                            novos_dados = st.session_state.edit_data
                            resultado = editar_documento(doc['id'], novos_dados)
                            if resultado:
                                st.session_state.edit_data = None
                                st.session_state.doc_selecionado = None
                                st.session_state.expander_aberto = False
                                st.session_state.close_doc_after_action = True
                                st.success("✅ Document updated successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {str(e)}")
                with col_btn2:
                    if st.button("📤 Submit for Review", key="parceiro_submeter", use_container_width=True):
                        try:
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                resultado_sub = submeter(doc['id'])
                                if resultado_sub:
                                    st.session_state.edit_data = None
                                    st.session_state.doc_selecionado = None
                                    st.session_state.expander_aberto = False
                                    st.session_state.close_doc_after_action = True
                                    st.success("✅ Document submitted successfully!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting: {str(e)}")
                with col_btn3:
                    if st.button("✖ Close", key="parceiro_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.edit_data = None
                        st.session_state.expander_aberto = False
                        st.rerun()
            else:
                st.subheader("📄 View Document")
                st.info(f"This document is in status: **{estado_doc}**")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                if estado_doc in ["Changes Requested", "Alterações"]:
                    with col_btn1:
                        st.warning("⚠️ The company has requested changes.")
                        versoes = listar_versoes(doc['id'])
                        if versoes:
                            ultima = versoes[-1]
                            if ultima['comentario']:
                                st.info(f"Reason: {ultima['comentario']}")
                        if st.button("✏️ Edit again", key="parceiro_editar_novamente", use_container_width=True):
                            if editar_novamente(doc['id']):
                                st.rerun()
                elif estado_doc in ["Approved", "Aprovado"]:
                    with col_btn1:
                        st.success("✅ Document approved. Cannot be edited.")
                elif estado_doc in ["Submitted", "Submetido", "In Review", "Em Revisão"]:
                    with col_btn1:
                        st.info("📋 Document under review by the company.")
                elif estado_doc in ["Archived", "Arquivado"]:
                    with col_btn1:
                        st.warning("📁 Document archived (view only).")
                else:
                    with col_btn1:
                        st.info(f"Document is in status: {estado_doc}")
                
                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label="📊 Export History",
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_parceiro_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )
                
                with col_btn3:
                    if st.button("✖ Close", key="parceiro_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.edit_data = None
                        st.session_state.expander_aberto = False
                        st.rerun()

            st.markdown("---")

            with st.expander("📜 Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} by {v['criado_por']} at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ---------- Company Area ----------
elif st.session_state.perfil == "empresa":
    st.header("🏢 Company Area (Validation)")
    
    if "empresa_mostrar_form" not in st.session_state:
        st.session_state.empresa_mostrar_form = False
    
    if not st.session_state.empresa_mostrar_form:
        if st.button("➕ Create new document for partner", use_container_width=True, key="empresa_abrir_form"):
            st.session_state.empresa_mostrar_form = True
            st.rerun()
    else:
        with st.container():
            st.subheader("Create Document")
            st.info("The company creates the document skeleton. The partner will fill in the data later.")
            
            form_key = st.session_state.get("empresa_form_key", 0)
            titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"empresa_titulo_{form_key}")
            
            parceiros = listar_parceiros_disponiveis()
            
            if not parceiros:
                st.warning("No partners available. Create a partner first in the Admin area.")
                if st.button("🔄 Reload partner list"):
                    st.rerun()
                if st.button("✖ Close", key="empresa_fechar_sem_parceiros"):
                    st.session_state.empresa_mostrar_form = False
                    st.rerun()
            else:
                parceiro_selecionado = st.selectbox(
                    "Select Partner",
                    options=[""] + [p["username"] for p in parceiros],
                    format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                    placeholder="Select a partner from the list",
                    key=f"empresa_parceiro_{form_key}"
                )
                
                st.info("Select the processes that will be available in this document for the partner to fill in.")
                processos_selecionados = render_processos_selecao(key_prefix=f"empresa_{form_key}")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn1:
                    if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                        if st.button("✅ Create Document", key=f"empresa_create_doc_btn_{form_key}", use_container_width=True):
                            if not titulo.strip():
                                st.error("Title is required.")
                            else:
                                try:
                                    dados = ensure_new_structure({}, processos_selecionados)
                                    novo = criar_documento(titulo, parceiro_selecionado, dados)
                                    if novo:
                                        st.session_state.empresa_form_key = form_key + 1
                                        session_key = f"processos_selecionados_empresa_{form_key}"
                                        if session_key in st.session_state:
                                            del st.session_state[session_key]
                                        st.session_state.empresa_mostrar_form = False
                                        st.session_state.success_message = f"Document created successfully! ID: {novo['id']}"
                                        st.session_state.new_data = None
                                        st.session_state.doc_selecionado = None
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating document: {str(e)}")
                    elif processos_selecionados and (not parceiro_selecionado or parceiro_selecionado == ""):
                        st.warning("Please select a partner to continue.")
                    elif parceiro_selecionado and parceiro_selecionado != "" and not processos_selecionados:
                        st.warning("Please select at least one process to continue.")
                
                with col_btn2:
                    if st.button("❌ Cancel", key=f"empresa_cancel_btn_{form_key}", use_container_width=True):
                        session_key = f"processos_selecionados_empresa_{form_key}"
                        if session_key in st.session_state:
                            del st.session_state[session_key]
                        st.session_state.empresa_mostrar_form = False
                        st.rerun()
                
                with col_btn3:
                    if st.button("✖ Close", key=f"empresa_fechar_btn_{form_key}", use_container_width=True):
                        session_key = f"processos_selecionados_empresa_{form_key}"
                        if session_key in st.session_state:
                            del st.session_state[session_key]
                        st.session_state.empresa_mostrar_form = False
                        st.rerun()
        
        st.divider()
    
    st.divider()
    
    st.subheader("📋 Available Documents")
    render_filtros()
    
    if st.button("🔄 Refresh list", key="refresh_list_empresa"):
        st.session_state.doc_selecionado = None
        st.session_state.empresa_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
    if not documentos:
        st.info("No documents found with the current filters.")
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Title", "Partner", "Status", "Version", "Last Update"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]
        id_selecionado = st.selectbox(
            "Select a document:",
            ids,
            format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
            key=f"empresa_selectbox_{st.session_state.empresa_dropdown_key}",
            placeholder="Choose an option"
        )

        if st.button("📂 Load document", key="empresa_carregar_doc"):
            if not id_selecionado:
                st.warning("Please select a document.")
            else:
                st.session_state.doc_selecionado = id_selecionado
                st.session_state.expander_aberto = False
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            with st.expander("📊 View document data", expanded=st.session_state.get("expander_aberto", False)):
                st.subheader("LCA")
                lca = dados.get("lca", {})
                for proc in processos:
                    st.write(f"**{proc}**")
                    if lca.get("inputs", {}).get(proc):
                        st.write("Inputs")
                        display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                    if lca.get("processes", {}).get(proc):
                        st.write("Processes")
                        display_dataframe(pd.DataFrame(lca["processes"][proc]))
                    if lca.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                st.subheader("LCC")
                lcc = dados.get("lcc", {})
                for proc in processos:
                    st.write(f"**{proc}**")
                    if lcc.get("materials", {}).get(proc):
                        st.write("Cost Breakdown Material")
                        display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                    if lcc.get("equipment", {}).get(proc):
                        st.write("Equipment")
                        display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                    if lcc.get("labour", {}).get(proc):
                        st.write("Labour")
                        display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                    if lcc.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

            with st.expander("🔍 View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            if doc['estado'] in ["Submitted", "Submetido"]:
                with col_btn1:
                    if st.button("🔍 Start Review", key="empresa_iniciar_revisao", use_container_width=True):
                        if iniciar_revisao(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["In Review", "Em Revisão"]:
                comentario = st.text_area("Comment (required if requesting changes)", key="empresa_comentario")
                col_aprov, col_alt = st.columns(2)
                with col_aprov:
                    if st.button("✅ Approve", key="empresa_aprovar", use_container_width=True):
                        if aprovar(doc['id']):
                            st.rerun()
                with col_alt:
                    if st.button("🔄 Request Changes", key="empresa_pedir_alteracoes", use_container_width=True):
                        if not comentario.strip():
                            st.error("A comment is required to request changes")
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.rerun()
            elif doc['estado'] in ["Approved", "Aprovado"]:
                with col_btn1:
                    if st.button("🔁 Reopen", key="empresa_reabrir", use_container_width=True):
                        if reabrir(doc['id']):
                            st.rerun()
                with col_btn2:
                    if st.button("📁 Archive", key="empresa_arquivar", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Draft", "Rascunho"]:
                with col_btn1:
                    if st.button("📁 Archive (draft)", key="empresa_arquivar_rascunho", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Changes Requested", "Alterações"]:
                with col_btn1:
                    st.info("⏳ Waiting for partner to edit again.")
            elif doc['estado'] in ["Archived", "Arquivado"]:
                with col_btn1:
                    st.warning("📁 Document archived (view only).")

            with col_btn2:
                conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                if conteudo:
                    st.download_button(
                        label="📊 Export History",
                        data=conteudo,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_empresa_{doc['id']}_{st.session_state.refresh_counter}",
                        use_container_width=True
                    )

            with col_btn3:
                if st.button("✖ Close details", key="empresa_fechar_detalhes", use_container_width=True):
                    st.session_state.doc_selecionado = None
                    st.session_state.expander_aberto = False
                    st.rerun()

            st.markdown("---")

            with st.expander("📜 Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']}) at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ---------- Admin Area ----------
elif st.session_state.perfil == "admin":
    st.header("⚙️ Administrative Panel")
    
    menu_admin = st.radio("Admin", ["Users", "Documents (company)"], key="admin_menu", horizontal=True)

    if menu_admin == "Users":
        st.subheader("👥 User Management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔄 Load users", use_container_width=True, key="admin_carregar_users"):
                st.session_state.doc_selecionado = None
                st.session_state.admin_user_dropdown_key += 1
                st.session_state.refresh_counter += 1
                st.rerun()
        with col2:
            if st.button("➕ New User", use_container_width=True, key="admin_novo_user"):
                st.session_state.show_create_user_form = not st.session_state.show_create_user_form
                st.rerun()
        
        st.write("")
        
        if st.session_state.show_create_user_form:
            st.divider()
            st.subheader("Create New User")
            
            with st.form("create_user_form"):
                new_username = st.text_input("Username *", placeholder="Ex: new_partner")
                new_password = st.text_input("Password *", type="password", placeholder="Minimum 3 characters")
                new_nome = st.text_input("Full Name", placeholder="Ex: John Doe")
                new_perfil = st.selectbox(
                    "Profile *",
                    options=["parceiro", "empresa", "admin"],
                    format_func=lambda x: {
                        "parceiro": "Partner",
                        "empresa": "Company",
                        "admin": "Admin"
                    }.get(x, x),
                    placeholder="Choose an option"
                )
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    submit_create = st.form_submit_button("Create User", use_container_width=True)
                with col2:
                    cancel_create = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancel_create:
                    st.session_state.show_create_user_form = False
                    st.rerun()
                
                if submit_create:
                    if not new_username.strip():
                        st.error("Username is required")
                    elif not new_password.strip() or len(new_password.strip()) < 3:
                        st.error("Password is required and must be at least 3 characters")
                    elif not new_perfil:
                        st.error("Profile is required")
                    else:
                        resp_check = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
                        if resp_check.status_code == 200:
                            users_existentes = resp_check.json()
                            if any(u["username"] == new_username for u in users_existentes):
                                st.error(f"Username '{new_username}' already exists!")
                            else:
                                try:
                                    resp_create = requests.post(
                                        f"{API_URL}/registar",
                                        json={
                                            "username": new_username.strip(),
                                            "password": new_password.strip(),
                                            "perfil": new_perfil,
                                            "nome_completo": new_nome.strip() if new_nome.strip() else new_username.strip()
                                        }
                                    )
                                    if resp_create.status_code == 200:
                                        st.toast(f"User '{new_username}' created successfully!", icon="✅")
                                        st.session_state.show_create_user_form = False
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_create.json().get("detail", "Unknown error")
                                        except:
                                            erro = resp_create.text
                                        st.error(f"Error creating user: {erro}")
                                except Exception as e:
                                    st.error(f"Error creating user: {str(e)}")
                        else:
                            st.error("Error checking existing users")
            
            st.divider()
        
        resp = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
        if resp.status_code == 200:
            users = resp.json()
            if users:
                for user in users:
                    if user["perfil"] == "empresa":
                        user["perfil"] = "Company"
                    elif user["perfil"] == "parceiro":
                        user["perfil"] = "Partner"
                    elif user["perfil"] == "admin":
                        user["perfil"] = "Admin"
                
                df = pd.DataFrame(users)
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_disponiveis = df.columns.tolist()
                colunas_desejadas = ["username", "perfil", "nome_completo", "created_at"]
                colunas_existentes = [col for col in colunas_desejadas if col in cols_disponiveis]
                df = df[colunas_existentes]
                df.columns = ["Username", "Profile", "Name", "Created At"]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                st.subheader("Manage User")
                
                usernames = [""] + [u["username"] for u in users]
                sel_user = st.selectbox(
                    "Select user to manage",
                    usernames,
                    format_func=lambda x: "Select a user..." if x == "" else x,
                    key=f"admin_user_selectbox_{st.session_state.admin_user_dropdown_key}",
                    placeholder="Choose an option"
                )

                if sel_user:
                    user_data = next((u for u in users if u["username"] == sel_user), None)
                    if user_data:
                        st.info(f"**Username:** {user_data['username']} | **Profile:** {user_data['perfil']} | **Name:** {user_data['nome_completo']}")
                    
                    st.subheader("Change Password")
                    pw_key = f"admin_pw_input_{st.session_state.pw_input_counter}"
                    nova_pw = st.text_input(
                        "New password (leave empty to keep current)", 
                        type="password", 
                        key=pw_key,
                        placeholder="Enter new password..."
                    )
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("Change Password", key="btn_alterar_pw", use_container_width=True):
                            if not sel_user:
                                st.warning("Please select a user.")
                            elif not nova_pw.strip():
                                st.warning("Please enter a new password")
                            elif len(nova_pw.strip()) < 3:
                                st.warning("Password must be at least 3 characters")
                            else:
                                resp_pw = requests.put(
                                    f"{API_URL}/admin/usuarios/{sel_user}/password",
                                    json={"nova_password": nova_pw},
                                    headers=headers_auth()
                                )
                                if resp_pw.status_code == 200:
                                    st.toast(f"✅ Password for '{sel_user}' changed successfully!", icon="✅")
                                    st.session_state.pw_input_counter += 1
                                    st.rerun()
                                else:
                                    try:
                                        erro = resp_pw.json().get("detail", "Unknown error")
                                    except:
                                        erro = resp_pw.text
                                    st.error(f"Error changing password: {erro}")
                    
                    with col_btn2:
                        if st.button("Delete User", key="btn_eliminar_user", use_container_width=True):
                            if not sel_user:
                                st.warning("Please select a user.")
                            elif sel_user == st.session_state.username:
                                st.error("You cannot delete yourself")
                            else:
                                confirm = st.button("Confirm Deletion", key="btn_confirmar_eliminar")
                                if confirm:
                                    resp_del = requests.delete(f"{API_URL}/admin/usuarios/{sel_user}", headers=headers_auth())
                                    if resp_del.status_code == 200:
                                        st.toast(f"User '{sel_user}' deleted successfully!", icon="🗑️")
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_del.json().get("detail", "Unknown error")
                                        except:
                                            erro = resp_del.text
                                        st.error(f"Error deleting: {erro}")
                    
                    with col_btn3:
                        if st.button("Close Details", key="admin_fechar_gerir_user", use_container_width=True):
                            st.session_state.admin_user_dropdown_key += 1
                            st.session_state.doc_selecionado = None
                            st.rerun()

            else:
                st.info("No users found")
        else:
            st.error("Failed to load users")

    else:  # Documents (company) - Admin
        st.header("📋 Company Area (Validation) – Admin")
        
        if "admin_mostrar_form" not in st.session_state:
            st.session_state.admin_mostrar_form = False
        
        if not st.session_state.admin_mostrar_form:
            if st.button("➕ Create new document for partner", use_container_width=True, key="admin_abrir_form"):
                st.session_state.admin_mostrar_form = True
                st.rerun()
        else:
            with st.container():
                st.subheader("Create Document")
                st.info("The administrator creates the document skeleton. The partner will fill in the data later.")
                
                form_key = st.session_state.get("admin_form_key", 0)
                titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"admin_titulo_{form_key}")
                
                parceiros = listar_parceiros_disponiveis()
                
                if not parceiros:
                    st.warning("No partners available. Create a partner first.")
                    if st.button("🔄 Reload partner list", key="admin_reload_parceiros"):
                        st.rerun()
                    if st.button("✖ Close", key="admin_fechar_sem_parceiros"):
                        st.session_state.admin_mostrar_form = False
                        st.rerun()
                else:
                    parceiro_selecionado = st.selectbox(
                        "Select Partner",
                        options=[""] + [p["username"] for p in parceiros],
                        format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                        placeholder="Select a partner from the list",
                        key=f"admin_parceiro_{form_key}"
                    )
                    
                    st.info("Select the processes that will be available in this document for the partner to fill in.")
                    processos_selecionados = render_processos_selecao(key_prefix=f"admin_{form_key}")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                            if st.button("✅ Create Document", key=f"admin_create_doc_btn_{form_key}", use_container_width=True):
                                if not titulo.strip():
                                    st.error("Title is required.")
                                else:
                                    try:
                                        dados = ensure_new_structure({}, processos_selecionados)
                                        novo = criar_documento(titulo, parceiro_selecionado, dados)
                                        if novo:
                                            st.session_state.admin_form_key = form_key + 1
                                            session_key = f"processos_selecionados_admin_{form_key}"
                                            if session_key in st.session_state:
                                                del st.session_state[session_key]
                                            st.session_state.admin_mostrar_form = False
                                            st.session_state.success_message = f"Document created successfully! ID: {novo['id']}"
                                            st.session_state.new_data = None
                                            st.session_state.doc_selecionado = None
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error creating document: {str(e)}")
                        elif processos_selecionados and (not parceiro_selecionado or parceiro_selecionado == ""):
                            st.warning("Please select a partner to continue.")
                        elif parceiro_selecionado and parceiro_selecionado != "" and not processos_selecionados:
                            st.warning("Please select at least one process to continue.")
                    
                    with col_btn2:
                        if st.button("❌ Cancel", key=f"admin_cancel_btn_{form_key}", use_container_width=True):
                            session_key = f"processos_selecionados_admin_{form_key}"
                            if session_key in st.session_state:
                                del st.session_state[session_key]
                            st.session_state.admin_mostrar_form = False
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("✖ Close", key=f"admin_fechar_btn_{form_key}", use_container_width=True):
                            session_key = f"processos_selecionados_admin_{form_key}"
                            if session_key in st.session_state:
                                del st.session_state[session_key]
                            st.session_state.admin_mostrar_form = False
                            st.rerun()
            
            st.divider()

        st.subheader("📋 Available Documents")
        render_filtros()
        
        if st.button("🔄 Refresh list", key="refresh_list_admin"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
        if not documentos:
            st.info("No documents found with the current filters.")
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            if "created_at" in df.columns:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Title", "Partner", "Status", "Version", "Last Update"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]
            id_selecionado = st.selectbox(
                "Select a document:",
                ids,
                format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
                key=f"admin_selectbox_{st.session_state.admin_dropdown_key}",
                placeholder="Choose an option"
            )

            if st.button("📂 Load document", key="admin_carregar_doc"):
                if not id_selecionado:
                    st.warning("Please select a document.")
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    st.session_state.expander_aberto = False
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
                st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

                dados = doc['dados']
                processos = get_processos_from_data(dados)
                
                with st.expander("📊 View document data", expanded=st.session_state.get("expander_aberto", False)):
                    st.subheader("LCA")
                    lca = dados.get("lca", {})
                    for proc in processos:
                        st.write(f"**{proc}**")
                        if lca.get("inputs", {}).get(proc):
                            st.write("Inputs")
                            display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                        if lca.get("processes", {}).get(proc):
                            st.write("Processes")
                            display_dataframe(pd.DataFrame(lca["processes"][proc]))
                        if lca.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                    st.subheader("LCC")
                    lcc = dados.get("lcc", {})
                    for proc in processos:
                        st.write(f"**{proc}**")
                        if lcc.get("materials", {}).get(proc):
                            st.write("Cost Breakdown Material")
                            display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                        if lcc.get("equipment", {}).get(proc):
                            st.write("Equipment")
                            display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                        if lcc.get("labour", {}).get(proc):
                            st.write("Labour")
                            display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                        if lcc.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

                with st.expander("🔍 View raw JSON", expanded=False):
                    st.json(dados)

                st.markdown("---")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                if doc['estado'] in ["Submitted", "Submetido"]:
                    with col_btn1:
                        if st.button("🔍 Start Review", key="admin_iniciar_revisao", use_container_width=True):
                            if iniciar_revisao(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["In Review", "Em Revisão"]:
                    comentario = st.text_area("Comment (required if requesting changes)", key="admin_comentario")
                    col_aprov, col_alt = st.columns(2)
                    with col_aprov:
                        if st.button("✅ Approve", key="admin_aprovar", use_container_width=True):
                            if aprovar(doc['id']):
                                st.rerun()
                    with col_alt:
                        if st.button("🔄 Request Changes", key="admin_pedir_alteracoes", use_container_width=True):
                            if not comentario.strip():
                                st.error("A comment is required to request changes")
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.rerun()
                elif doc['estado'] in ["Approved", "Aprovado"]:
                    with col_btn1:
                        if st.button("🔁 Reopen", key="admin_reabrir", use_container_width=True):
                            if reabrir(doc['id']):
                                st.rerun()
                    with col_btn2:
                        if st.button("📁 Archive", key="admin_arquivar", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Draft", "Rascunho"]:
                    with col_btn1:
                        if st.button("📁 Archive (draft)", key="admin_arquivar_rascunho", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Changes Requested", "Alterações"]:
                    with col_btn1:
                        st.info("⏳ Waiting for partner to edit again.")
                elif doc['estado'] in ["Archived", "Arquivado"]:
                    with col_btn1:
                        st.warning("📁 Document archived (view only).")

                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label="📊 Export History",
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_admin_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )

                with col_btn3:
                    if st.button("✖ Close details", key="admin_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.expander_aberto = False
                        st.rerun()

                st.markdown("---")

                with st.expander("📜 Version history", expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']}) at {data_formatada}")
                            if v['comentario']:
                                st.caption(f"  Comment: {v['comentario']}")
                    else:
                        st.info("No history available.")

# ============================================================
# ENSURE CLOSE_DOC_AFTER_ACTION IS PROCESSED
# ============================================================
if st.session_state.get("close_doc_after_action", False):
    if st.session_state.doc_selecionado is not None:
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False