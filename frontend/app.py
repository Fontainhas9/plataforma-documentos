import streamlit as st
import requests
import pandas as pd
import copy
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

PROCESSOS = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = ["Medido", "Calculado", "Estimado", "Literatura"]

# ============================================================
# TRADUÇÕES
# ============================================================
TRADUCOES = {
    "pt": {
        # Interface Geral
        "app_title": "Plataforma de Gestão de Documentos",
        "login": "Login",
        "username": "Utilizador",
        "password": "Palavra-passe",
        "enter": "Entrar",
        "logout": "Sair",
        "back": "← Voltar",
        "logged_as": "Logado como:",
        "no_notifications": "🔔 Sem notificações",
        "unread_notifications_one": "🔔 {count} notificação não lida",
        "unread_notifications_other": "🔔 {count} notificações não lidas",
        "no_documents": "Nenhum documento encontrado.",
        "create_first": "Nenhum documento encontrado. Comece por criar um novo documento.",
        "no_documents_filter": "Nenhum documento encontrado com os filtros atuais.",
        "loading": "Carregando...",
        "save": "Guardar",
        "close": "Fechar",
        "cancel": "Cancelar",
        "confirm": "Confirmar",
        "refresh": "Atualizar lista",
        "select_document": "Selecione um documento...",
        "load_document": "Carregar documento",
        "close_details": "Fechar detalhes",
        "view_json": "Ver JSON bruto",
        "view_history": "Histórico de versões",
        "no_history": "Sem histórico disponível.",
        "version": "v{numero} - {estado} por {criado_por} em {data}",
        "comment": "Comentário: {comentario}",
        "export_history": "Exportar Histórico",
        
        # Login/Registo
        "register": "Registar",
        "register_title": "Criar Conta",
        "full_name": "Nome Completo",
        "profile": "Perfil",
        "profile_parceiro": "Parceiro",
        "profile_empresa": "Empresa",
        "profile_admin": "Admin",
        "language": "Idioma",
        "language_pt": "Português",
        "language_en": "Inglês",
        "choose_language": "Escolha o idioma",
        "already_have_account": "Já tem conta? Faça login",
        "register_success": "Conta criada com sucesso!",
        "register_error": "Erro ao criar conta.",
        "username_exists": "Utilizador já existe.",
        "password_required": "A palavra-passe deve ter pelo menos 3 caracteres.",
        "username_required": "O utilizador é obrigatório.",
        "profile_required": "O perfil é obrigatório.",
        
        # Dashboard
        "dashboard": "Dashboard",
        "notifications": "Notificações",
        "kpi_total": "Total Documentos",
        "kpi_approved": "Aprovados",
        "kpi_approval_rate": "Taxa Aprovação",
        "kpi_avg_review_time": "Tempo Médio Revisão",
        "distribution_by_state": "Distribuição de Documentos por Estado",
        "docs_by_state_bar": "Documentos por Estado (Barras)",
        "recent_documents": "Documentos Recentes",
        "top_partners": "Top Parceiros",
        "partners_with_more_docs": "Parceiros com Mais Documentos",
        "no_recent_docs": "Sem documentos recentes",
        "no_top_partners": "Sem dados de top parceiros",
        
        # Documentos
        "documents": "Documentos",
        "my_documents": "Meus Documentos",
        "create_document": "Criar Documento",
        "new_document_title": "Novo Documento LCA/LCC",
        "document_title": "Título do documento (ex: LCA/LCC NEO-CYCLE)",
        "fill_data_info": "Preencha os dados nas tabelas abaixo. Cada processo tem a sua própria secção.",
        "create_doc_btn": "Criar documento",
        "title_required": "O título é obrigatório.",
        "document_created": "Documento criado com sucesso! ID: {id}",
        "document_submitted": "Documento submetido com sucesso!",
        "document_updated": "Documento atualizado com sucesso!",
        "document_approved": "Documento aprovado com sucesso!",
        "document_archived": "Documento arquivado com sucesso!",
        "document_reopened": "Documento reaberto com sucesso!",
        "document_review_started": "Revisão iniciada com sucesso!",
        "document_changes_requested": "Alterações solicitadas com sucesso!",
        "document_edited_again": "Documento reaberto para edição!",
        
        # Estados
        "status_draft": "Rascunho",
        "status_submitted": "Submetido",
        "status_review": "Em Revisão",
        "status_changes": "Alterações",
        "status_approved": "Aprovado",
        "status_archived": "Arquivado",
        
        # Ações
        "action_submit": "Submeter",
        "action_edit": "Editar",
        "action_edit_again": "Editar novamente",
        "action_approve": "Aprovar",
        "action_request_changes": "Pedir alterações",
        "action_reopen": "Reabrir",
        "action_archive": "Arquivar",
        "action_start_review": "Iniciar revisão",
        "action_archive_draft": "Arquivar (rascunho)",
        "action_comment_required": "É necessário um comentário para pedir alterações",
        
        # Mensagens de estado
        "msg_awaiting_partner": "Aguardando o parceiro editar novamente.",
        "msg_approved_readonly": "Documento aprovado. Não pode ser editado.",
        "msg_under_review": "Documento em análise pela empresa.",
        "msg_archived_readonly": "Documento arquivado (apenas consulta).",
        "msg_changes_requested": "A empresa pediu alterações.",
        "msg_reason": "Motivo: {motivo}",
        
        # Notificações
        "no_notifications_found": "Nenhuma notificação encontrada.",
        "all_notifications_read": "📌 Todas as notificações estão lidas.",
        "unread_notifications": "📌 Você tem {count} notificação(ões) não lida(s).",
        "mark_all_read": "Marcar todas como lidas",
        "mark_read": "✓ Marcar lida",
        "read": "✅ Lida",
        "view_document": "Ver Documento",
        
        # Admin
        "admin_panel": "Painel Administrativo",
        "admin_users": "Utilizadores",
        "admin_documents": "Documentos (empresa)",
        "user_management": "Gestão de Utilizadores",
        "load_users": "Carregar utilizadores",
        "new_user": "Novo Utilizador",
        "manage_user": "Gerir Utilizador",
        "select_user": "Selecionar utilizador para gerir",
        "change_password": "Alterar Password",
        "new_password": "Nova password (deixar vazio para não alterar)",
        "change_password_btn": "Alterar password",
        "delete_user": "Eliminar utilizador",
        "close_details": "Fechar Detalhes",
        "create_new_user": "Criar Novo Utilizador",
        "create_user_btn": "Criar Utilizador",
        "user_created": "Utilizador '{username}' criado com sucesso!",
        "user_deleted": "Utilizador '{username}' eliminado com sucesso!",
        "password_changed": "Password de '{username}' alterada com sucesso!",
        "cannot_delete_self": "Não pode eliminar a si próprio",
        
        # Filtros
        "filters": "Filtros de Pesquisa",
        "search": "Pesquisar",
        "search_placeholder": "Título, parceiro ou ID...",
        "status": "Estado",
        "start_date": "Data Início",
        "end_date": "Data Fim",
        "order_by": "Ordenar por",
        "order_direction": "Direção",
        "order_asc": "Crescente",
        "order_desc": "Decrescente",
        "apply_filters": "Aplicar Filtros",
        "clear_filters": "Limpar Filtros",
        "id": "ID",
        "title": "Título",
        "partner": "Parceiro",
        "created_at": "Data Criação",
        "updated_at": "Data Atualização",
        "version": "Versão"
    },
    "en": {
        # Interface Geral
        "app_title": "Document Management Platform",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "enter": "Login",
        "logout": "Logout",
        "back": "← Back",
        "logged_as": "Logged as:",
        "no_notifications": "🔔 No notifications",
        "unread_notifications_one": "🔔 {count} unread notification",
        "unread_notifications_other": "🔔 {count} unread notifications",
        "no_documents": "No documents found.",
        "create_first": "No documents found. Start by creating a new document.",
        "no_documents_filter": "No documents found with current filters.",
        "loading": "Loading...",
        "save": "Save",
        "close": "Close",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "refresh": "Refresh list",
        "select_document": "Select a document...",
        "load_document": "Load document",
        "close_details": "Close details",
        "view_json": "View raw JSON",
        "view_history": "Version history",
        "no_history": "No history available.",
        "version": "v{numero} - {estado} by {criado_por} on {data}",
        "comment": "Comment: {comentario}",
        "export_history": "Export History",
        
        # Login/Registo
        "register": "Register",
        "register_title": "Create Account",
        "full_name": "Full Name",
        "profile": "Profile",
        "profile_parceiro": "Partner",
        "profile_empresa": "Company",
        "profile_admin": "Admin",
        "language": "Language",
        "language_pt": "Portuguese",
        "language_en": "English",
        "choose_language": "Choose your language",
        "already_have_account": "Already have an account? Login",
        "register_success": "Account created successfully!",
        "register_error": "Error creating account.",
        "username_exists": "Username already exists.",
        "password_required": "Password must be at least 3 characters.",
        "username_required": "Username is required.",
        "profile_required": "Profile is required.",
        
        # Dashboard
        "dashboard": "Dashboard",
        "notifications": "Notifications",
        "kpi_total": "Total Documents",
        "kpi_approved": "Approved",
        "kpi_approval_rate": "Approval Rate",
        "kpi_avg_review_time": "Avg Review Time",
        "distribution_by_state": "Document Distribution by Status",
        "docs_by_state_bar": "Documents by Status (Bar)",
        "recent_documents": "Recent Documents",
        "top_partners": "Top Partners",
        "partners_with_more_docs": "Partners with Most Documents",
        "no_recent_docs": "No recent documents",
        "no_top_partners": "No top partners data",
        
        # Documentos
        "documents": "Documents",
        "my_documents": "My Documents",
        "create_document": "Create Document",
        "new_document_title": "New LCA/LCC Document",
        "document_title": "Document title (ex: LCA/LCC NEO-CYCLE)",
        "fill_data_info": "Fill in the data in the tables below. Each process has its own section.",
        "create_doc_btn": "Create document",
        "title_required": "Title is required.",
        "document_created": "Document created successfully! ID: {id}",
        "document_submitted": "Document submitted successfully!",
        "document_updated": "Document updated successfully!",
        "document_approved": "Document approved successfully!",
        "document_archived": "Document archived successfully!",
        "document_reopened": "Document reopened successfully!",
        "document_review_started": "Review started successfully!",
        "document_changes_requested": "Changes requested successfully!",
        "document_edited_again": "Document reopened for editing!",
        
        # Estados
        "status_draft": "Draft",
        "status_submitted": "Submitted",
        "status_review": "In Review",
        "status_changes": "Changes",
        "status_approved": "Approved",
        "status_archived": "Archived",
        
        # Ações
        "action_submit": "Submit",
        "action_edit": "Edit",
        "action_edit_again": "Edit again",
        "action_approve": "Approve",
        "action_request_changes": "Request changes",
        "action_reopen": "Reopen",
        "action_archive": "Archive",
        "action_start_review": "Start review",
        "action_archive_draft": "Archive (draft)",
        "action_comment_required": "A comment is required to request changes",
        
        # Mensagens de estado
        "msg_awaiting_partner": "Waiting for partner to edit again.",
        "msg_approved_readonly": "Document approved. Cannot be edited.",
        "msg_under_review": "Document under review by the company.",
        "msg_archived_readonly": "Document archived (read only).",
        "msg_changes_requested": "The company requested changes.",
        "msg_reason": "Reason: {motivo}",
        
        # Notificações
        "no_notifications_found": "No notifications found.",
        "all_notifications_read": "📌 All notifications are read.",
        "unread_notifications": "📌 You have {count} unread notification(s).",
        "mark_all_read": "Mark all as read",
        "mark_read": "✓ Mark as read",
        "read": "✅ Read",
        "view_document": "View Document",
        
        # Admin
        "admin_panel": "Admin Panel",
        "admin_users": "Users",
        "admin_documents": "Documents (company)",
        "user_management": "User Management",
        "load_users": "Load users",
        "new_user": "New User",
        "manage_user": "Manage User",
        "select_user": "Select user to manage",
        "change_password": "Change Password",
        "new_password": "New password (leave empty to keep current)",
        "change_password_btn": "Change password",
        "delete_user": "Delete user",
        "close_details": "Close Details",
        "create_new_user": "Create New User",
        "create_user_btn": "Create User",
        "user_created": "User '{username}' created successfully!",
        "user_deleted": "User '{username}' deleted successfully!",
        "password_changed": "Password for '{username}' changed successfully!",
        "cannot_delete_self": "Cannot delete yourself",
        
        # Filtros
        "filters": "Search Filters",
        "search": "Search",
        "search_placeholder": "Title, partner or ID...",
        "status": "Status",
        "start_date": "Start Date",
        "end_date": "End Date",
        "order_by": "Order by",
        "order_direction": "Direction",
        "order_asc": "Ascending",
        "order_desc": "Descending",
        "apply_filters": "Apply Filters",
        "clear_filters": "Clear Filters",
        "id": "ID",
        "title": "Title",
        "partner": "Partner",
        "created_at": "Created At",
        "updated_at": "Updated At",
        "version": "Version"
    }
}

# ============================================================
# FUNÇÃO DE TRADUÇÃO
# ============================================================
def t(key: str, **kwargs) -> str:
    """Retorna a tradução para a chave com formatação."""
    lang = st.session_state.get("idioma", "pt")
    texto = TRADUCOES.get(lang, TRADUCOES["pt"]).get(key, key)
    if kwargs:
        try:
            return texto.format(**kwargs)
        except KeyError:
            return texto
    return texto

# ============================================================
# FUNÇÃO PARA FORMATAR DATA/HORA
# ============================================================
def formatar_data_hora(data_str):
    if not data_str:
        return ""
    try:
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y %H:%M")
        
        data_str = str(data_str)
        data_str = data_str.replace('Z', '').replace('T', ' ')
        
        formatos = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d"
        ]
        
        for fmt in formatos:
            try:
                dt = datetime.strptime(data_str, fmt)
                return dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        
        return data_str
    except Exception:
        return str(data_str)

# Configuração da página
st.set_page_config(
    page_title=t("app_title"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar componente de notificações
from componentes.notificacoes import render_notificacoes_badge, get_notificacoes_nao_lidas

# ============================================================
# CSS e JavaScript para scroll automático - SIDEBAR 270px
# ============================================================
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        min-width: 270px !important;
        max-width: 270px !important;
        overflow: auto !important;
        pointer-events: auto !important;
    }
    .main > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    html {
        scroll-behavior: smooth;
    }
    .doc-anchor {
        display: block;
        position: relative;
        top: -80px;
        visibility: hidden;
        height: 0;
    }
</style>

<script>
    function checkScrollParam() {
        var urlParams = new URLSearchParams(window.location.search);
        var docId = urlParams.get('scroll_to');
        if (docId) {
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 400);
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
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

# Inicializar estado da sessão
if "token" not in st.session_state:
    st.session_state.token = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "username" not in st.session_state:
    st.session_state.username = None
if "idioma" not in st.session_state:
    st.session_state.idioma = "pt"
if "doc_selecionado" not in st.session_state:
    st.session_state.doc_selecionado = None
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "menu_parceiro_widget" not in st.session_state:
    st.session_state.menu_parceiro_widget = "Meus Documentos"
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

# Chave para forçar recriação dos widgets de filtro
if "filtros_widget_key" not in st.session_state:
    st.session_state.filtros_widget_key = 0

# Estado dos filtros - valores atuais aplicados
if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "q": "",
        "estados": [],
        "data_inicio": None,
        "data_fim": None,
        "order_by": "id",
        "order_dir": "desc"
    }

# Estado temporário dos filtros (enquanto o utilizador mexe)
if "filtros_temporarios" not in st.session_state:
    st.session_state.filtros_temporarios = {
        "q": "",
        "estados": [],
        "data_inicio": None,
        "data_fim": None,
        "order_by": "id",
        "order_dir": "desc"
    }

# ---------- Funções auxiliares ----------
def safe_copy(data):
    return copy.deepcopy(data)

def ensure_new_structure(data):
    if not data:
        return {
            "lca": {
                "inputs": {p: [] for p in PROCESSOS},
                "processes": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            },
            "lcc": {
                "materials": {p: [] for p in PROCESSOS},
                "equipment": {p: [] for p in PROCESSOS},
                "labour": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            }
        }

    if "lca" in data and "lcc" in data:
        if all(p in data["lca"].get("inputs", {}) for p in PROCESSOS):
            for secao in ["lca", "lcc"]:
                for categoria in data[secao].keys():
                    for p in PROCESSOS:
                        if p not in data[secao][categoria]:
                            data[secao][categoria][p] = []
            return data

    new_data = {
        "lca": {
            "inputs": {p: [] for p in PROCESSOS},
            "processes": {p: [] for p in PROCESSOS},
            "outputs": {p: [] for p in PROCESSOS}
        },
        "lcc": {
            "materials": {p: [] for p in PROCESSOS},
            "equipment": {p: [] for p in PROCESSOS},
            "labour": {p: [] for p in PROCESSOS},
            "outputs": {p: [] for p in PROCESSOS}
        }
    }

    if "lca" in data:
        old_lca = data["lca"]
        if "inputs" in old_lca and isinstance(old_lca["inputs"], list):
            new_data["lca"]["inputs"]["Demagnetisation"] = old_lca["inputs"]
        if "processes" in old_lca and isinstance(old_lca["processes"], list):
            new_data["lca"]["processes"]["Demagnetisation"] = old_lca["processes"]
        if "outputs" in old_lca and isinstance(old_lca["outputs"], list):
            new_data["lca"]["outputs"]["Demagnetisation"] = old_lca["outputs"]
    if "lcc" in data:
        old_lcc = data["lcc"]
        if "materials" in old_lcc and isinstance(old_lcc["materials"], list):
            new_data["lcc"]["materials"]["Demagnetisation"] = old_lcc["materials"]
        if "equipment" in old_lcc and isinstance(old_lcc["equipment"], list):
            new_data["lcc"]["equipment"]["Demagnetisation"] = old_lcc["equipment"]
        if "labour" in old_lcc and isinstance(old_lcc["labour"], list):
            new_data["lcc"]["labour"]["Demagnetisation"] = old_lcc["labour"]
        if "outputs" in old_lcc and isinstance(old_lcc["outputs"], list):
            new_data["lcc"]["outputs"]["Demagnetisation"] = old_lcc["outputs"]

    return new_data

# ---------- Funções da API ----------
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
            st.session_state.idioma = user_info.get("idioma", "pt")
        return True
    else:
        st.error(t("login_error") if hasattr(st.session_state, 'idioma') else "Credenciais inválidas")
        return False

def logout():
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
    st.session_state.ultimo_count = 0

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def listar_documentos(estado=None):
    params = {}
    if estado:
        params["estado"] = estado
    resp = requests.get(f"{API_URL}/documentos", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def listar_documentos_com_filtros(filtros):
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

def criar_documento(titulo, dados):
    resp = requests.post(
        f"{API_URL}/documentos/",
        json={"titulo": titulo, "parceiro_id": st.session_state.username, "dados": dados},
        headers=headers_auth()
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Erro ao criar documento: {resp.text}")
        return None

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Erro ao obter documento: {resp.text}")
        return None

def editar_documento(doc_id, dados):
    resp = requests.put(
        f"{API_URL}/documentos/{doc_id}/editar",
        json={"dados": dados},
        headers=headers_auth()
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Erro ao editar: {resp.text}")
        return None

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao submeter: {resp.text}")
        return None
    st.success(t("document_submitted"))
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao iniciar revisão: {resp.text}")
        return None
    st.success(t("document_review_started"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(
        f"{API_URL}/documentos/{doc_id}/pedir-alteracoes",
        json={"comentario": comentario},
        headers=headers_auth()
    )
    if resp.status_code != 200:
        st.error(f"Erro ao pedir alterações: {resp.text}")
        return None
    st.success(t("document_changes_requested"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao editar novamente: {resp.text}")
        return None
    st.success(t("document_edited_again"))
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao aprovar: {resp.text}")
        return None
    st.success(t("document_approved"))
    st.session_state.doc_selecionado = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao reabrir: {resp.text}")
        return None
    st.success(t("document_reopened"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def arquivar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/arquivar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao arquivar: {resp.text}")
        return None
    st.success(t("document_archived"))
    st.session_state.doc_selecionado = None
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
            erro = resp.json().get("detail", "Erro desconhecido")
        except:
            erro = "Erro ao exportar"
        st.error(f"Falha na exportação: {erro}")
        return None, None

# ---------- Função para obter notificações ----------
def get_notificacoes_nao_lidas():
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception as e:
        print(f"Erro ao obter notificações: {e}")
    return 0

def verificar_novas_notificacoes():
    if st.session_state.token is None:
        return
    
    try:
        count = get_notificacoes_nao_lidas()
        if count > st.session_state.ultimo_count:
            diff = count - st.session_state.ultimo_count
            if diff == 1:
                st.toast(f"🔔 {t('unread_notifications_one', count=count)}", icon="🔔")
            else:
                st.toast(f"🔔 {t('unread_notifications_other', count=count)}", icon="🔔")
        st.session_state.ultimo_count = count
    except:
        pass

# ---------- Função para resumo ----------
def show_document_summary(documentos):
    if not documentos:
        st.info(t("no_documents"))
        return

    estados = [t("status_draft"), t("status_submitted"), t("status_review"), t("status_changes"), t("status_approved"), t("status_archived")]
    estado_map = {
        "Rascunho": t("status_draft"),
        "Submetido": t("status_submitted"),
        "Em Revisão": t("status_review"),
        "Alterações": t("status_changes"),
        "Aprovado": t("status_approved"),
        "Arquivado": t("status_archived")
    }
    contagens = {estado: 0 for estado in estados}
    for doc in documentos:
        estado_original = doc.get("estado")
        estado_traduzido = estado_map.get(estado_original, estado_original)
        if estado_traduzido in contagens:
            contagens[estado_traduzido] += 1

    cols = st.columns(len(estados))
    for i, estado in enumerate(estados):
        with cols[i]:
            st.metric(label=estado, value=contagens[estado])

# ---------- Função para exibir dataframes ----------
def display_dataframe(df):
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [col.title() for col in df.columns]
        df = df.reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("(sem dados)")

# ---------- Componente de filtros ----------
def render_filtros():
    with st.expander(t("filters"), expanded=False):
        col1, col2 = st.columns(2)
        key_suffix = st.session_state.filtros_widget_key
        
        with col1:
            q = st.text_input(
                t("search"),
                value=st.session_state.filtros_temporarios.get("q", ""),
                placeholder=t("search_placeholder"),
                key=f"filtro_q_{key_suffix}"
            )
            st.session_state.filtros_temporarios["q"] = q
            
            estados_disponiveis = [t("status_draft"), t("status_submitted"), t("status_review"), t("status_changes"), t("status_approved"), t("status_archived")]
            estados_selecionados = st.multiselect(
                t("status"),
                options=estados_disponiveis,
                default=st.session_state.filtros_temporarios.get("estados", []),
                key=f"filtro_estados_{key_suffix}"
            )
            st.session_state.filtros_temporarios["estados"] = estados_selecionados
        
        with col2:
            data_inicio = st.date_input(
                t("start_date"),
                value=st.session_state.filtros_temporarios.get("data_inicio"),
                format="DD/MM/YYYY",
                key=f"filtro_data_inicio_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
            
            data_fim = st.date_input(
                t("end_date"),
                value=st.session_state.filtros_temporarios.get("data_fim"),
                format="DD/MM/YYYY",
                key=f"filtro_data_fim_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
        
        col3, col4 = st.columns(2)
        with col3:
            ordem_campos = {
                "id": t("id"),
                "titulo": t("title"),
                "parceiro_id": t("partner"),
                "estado": t("status"),
                "created_at": t("created_at"),
                "updated_at": t("updated_at"),
                "versao_atual": t("version")
            }
            order_by = st.selectbox(
                t("order_by"),
                options=list(ordem_campos.keys()),
                format_func=lambda x: ordem_campos.get(x, x),
                index=list(ordem_campos.keys()).index(st.session_state.filtros_temporarios.get("order_by", "id")),
                key=f"filtro_order_by_{key_suffix}",
                placeholder=t("choose_language")
            )
            st.session_state.filtros_temporarios["order_by"] = order_by
        
        with col4:
            order_dir = st.selectbox(
                t("order_direction"),
                options=["desc", "asc"],
                format_func=lambda x: t("order_desc") if x == "desc" else t("order_asc"),
                index=0 if st.session_state.filtros_temporarios.get("order_dir", "desc") == "desc" else 1,
                key=f"filtro_order_dir_{key_suffix}",
                placeholder=t("choose_language")
            )
            st.session_state.filtros_temporarios["order_dir"] = order_dir
        
        col5, col6 = st.columns(2)
        with col5:
            if st.button(t("apply_filters"), use_container_width=True):
                st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                st.rerun()
        with col6:
            if st.button(t("clear_filters"), use_container_width=True):
                st.session_state.filtros_temporarios = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                st.session_state.filtros_aplicados = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                st.session_state.filtros_widget_key += 1
                st.rerun()

# ---------- Funções de renderização com auto-add ----------
def render_lca_inputs(data_key, prefix=""):
    st.subheader("Inputs")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["inputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lca"]["inputs"][proc] = items
        
        with st.expander(f"Inputs - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lca_in_{proc}_mat_{i}")
                with col2:
                    item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_in_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_in_{proc}_unit_{i}")
                with col3:
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lca_in_{proc}_desc_{i}")
                    item["cas"] = st.text_input("CAS/Comments", item.get("cas",""), key=f"{prefix}lca_in_{proc}_cas_{i}")
                with col4:
                    item["distance"] = st.text_input("Distance (km)", item.get("distance",""), key=f"{prefix}lca_in_{proc}_dist_{i}")
                    item["country"] = st.text_input("Country", item.get("country",""), key=f"{prefix}lca_in_{proc}_country_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lca_in_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar input - {proc}", key=f"{prefix}add_lca_in_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último input - {proc}", key=f"{prefix}rem_lca_in_{proc}"):
                    items.pop()
                    st.rerun()

def render_lca_processes(data_key, prefix=""):
    st.subheader("Processes")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["processes"][proc]
        
        if not items:
            items.append({"tipo": "Energy Consumption (kWh)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            items.append({"tipo": "Rate Power of the Equipment (W)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            items.append({"tipo": "Operating Time (h)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            st.session_state[data_key]["lca"]["processes"][proc] = items
        
        with st.expander(f"Processes - {proc}", expanded=False):
            num_groups = len(items) // 3
            for g in range(num_groups):
                base = g * 3
                st.markdown(f"**Grupo de processos #{g+1}**")
                
                tipos = ["Energy Consumption (kWh)", "Rate Power of the Equipment (W)", "Operating Time (h)"]
                for j, tipo in enumerate(tipos):
                    idx = base + j
                    if idx < len(items):
                        item = items[idx]
                        item["tipo"] = tipo
                        st.markdown(f"*{tipo}*")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_proc_{proc}_qty_{idx}")
                            item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_proc_{proc}_unit_{idx}")
                        with col2:
                            item["description"] = st.text_area("Description", item.get("description",""), key=f"{prefix}lca_proc_{proc}_desc_{idx}")
                        with col3:
                            item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lca_proc_{proc}_comments_{idx}")
                            current_value = item.get("datasource", "")
                            if current_value in DATASOURCE_OPTIONS:
                                index = DATASOURCE_OPTIONS.index(current_value)
                            else:
                                index = None
                            item["datasource"] = st.selectbox(
                                "Data Source", 
                                DATASOURCE_OPTIONS,
                                index=index,
                                key=f"{prefix}lca_proc_{proc}_ds_{idx}",
                                placeholder=t("choose_language")
                            )
                
                st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar processo (3 linhas) - {proc}", key=f"{prefix}add_lca_proc_{proc}"):
                    items.append({"tipo": "Energy Consumption (kWh)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    items.append({"tipo": "Rate Power of the Equipment (W)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    items.append({"tipo": "Operating Time (h)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último processo (3 linhas) - {proc}", key=f"{prefix}rem_lca_proc_{proc}"):
                    for _ in range(3):
                        if items:
                            items.pop()
                    st.rerun()

def render_lca_outputs(data_key, prefix=""):
    st.subheader("Outputs")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["outputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lca"]["outputs"][proc] = items
        
        with st.expander(f"Outputs - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["etapa"] = st.text_input("Etapa (ex: Demagnetisation)", item.get("etapa",""), key=f"{prefix}lca_out_{proc}_etapa_{i}")
                    
                    tipo_atual = item.get("tipo", "")
                    if tipo_atual in ["Subproduct", "Emissions", "Waste"]:
                        tipo_index = ["Subproduct", "Emissions", "Waste"].index(tipo_atual)
                    else:
                        tipo_index = None
                    
                    item["tipo"] = st.selectbox(
                        "Tipo", 
                        ["Subproduct", "Emissions", "Waste"],
                        index=tipo_index,
                        key=f"{prefix}lca_out_{proc}_tipo_{i}",
                        placeholder=t("choose_language")
                    )
                    
                    item["sub_tipo"] = st.text_input("Sub-tipo (ex: Name 1, Liquid 1, Solid 1, etc.)", item.get("sub_tipo",""), key=f"{prefix}lca_out_{proc}_sub_{i}")
                with col2:
                    item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_out_{proc}_unit_{i}")
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lca_out_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lca_out_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lca_out_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar output - {proc}", key=f"{prefix}add_lca_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último output - {proc}", key=f"{prefix}rem_lca_out_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_materials(data_key, prefix=""):
    st.subheader("Cost Breakdown Material")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["materials"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["materials"][proc] = items
        
        with st.expander(f"Materials - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lcc_mat_{proc}_mat_{i}")
                    item["price"] = st.text_input("Price €", item.get("price",""), key=f"{prefix}lcc_mat_{proc}_price_{i}")
                with col2:
                    item["qty"] = st.text_input("Qty", item.get("qty",""), key=f"{prefix}lcc_mat_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lcc_mat_{proc}_unit_{i}")
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lcc_mat_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_mat_{proc}_comments_{i}")
                    item["distance"] = st.text_input("Distance (km)", item.get("distance",""), key=f"{prefix}lcc_mat_{proc}_dist_{i}")
                    item["country"] = st.text_input("Country", item.get("country",""), key=f"{prefix}lcc_mat_{proc}_country_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_mat_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar material - {proc}", key=f"{prefix}add_lcc_mat_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último material - {proc}", key=f"{prefix}rem_lcc_mat_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_equipment(data_key, prefix=""):
    st.subheader("Equipment")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["equipment"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["equipment"][proc] = items
        
        with st.expander(f"Equipment - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["equipment"] = st.text_input("Equipment", item.get("equipment",""), key=f"{prefix}lcc_eq_{proc}_eq_{i}")
                    item["process"] = st.text_input("Process", item.get("process",""), key=f"{prefix}lcc_eq_{proc}_proc_{i}")
                with col2:
                    item["unit_cost"] = st.text_input("Unit Cost (€)", item.get("unit_cost",""), key=f"{prefix}lcc_eq_{proc}_cost_{i}")
                    item["lifespan"] = st.text_input("Lifespan (Years)", item.get("lifespan",""), key=f"{prefix}lcc_eq_{proc}_life_{i}")
                    item["maintenance"] = st.text_input("Maintenance €/Year", item.get("maintenance",""), key=f"{prefix}lcc_eq_{proc}_maint_{i}")
                with col3:
                    item["industrial_equiv"] = st.text_input("Industrial Equivalent", item.get("industrial_equiv",""), key=f"{prefix}lcc_eq_{proc}_ind_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_eq_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_eq_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar equipamento - {proc}", key=f"{prefix}add_lcc_eq_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último equipamento - {proc}", key=f"{prefix}rem_lcc_eq_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_labour(data_key, prefix=""):
    st.subheader("Labour")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["labour"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["labour"][proc] = items
        
        with st.expander(f"Labour - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["process"] = st.text_input("Name Of The Process", item.get("process",""), key=f"{prefix}lcc_lab_{proc}_name_{i}")
                    item["total_number"] = st.text_input("Total Labour - Number", item.get("total_number",""), key=f"{prefix}lcc_lab_{proc}_num_{i}")
                    item["total_cost"] = st.text_input("Total Labour - Cost €", item.get("total_cost",""), key=f"{prefix}lcc_lab_{proc}_cost_{i}")
                with col2:
                    item["high_skilled"] = st.text_input("Number - High Skilled", item.get("high_skilled",""), key=f"{prefix}lcc_lab_{proc}_high_{i}")
                    item["moderate_skilled"] = st.text_input("Number - Moderated Skilled", item.get("moderate_skilled",""), key=f"{prefix}lcc_lab_{proc}_mod_{i}")
                    item["unskilled"] = st.text_input("Number - Unskilled", item.get("unskilled",""), key=f"{prefix}lcc_lab_{proc}_unsk_{i}")
                with col3:
                    item["high_rate"] = st.text_input("Rate - High Skilled (€/h)", item.get("high_rate",""), key=f"{prefix}lcc_lab_{proc}_highrate_{i}")
                    item["moderate_rate"] = st.text_input("Rate - Moderated Skilled (€/h)", item.get("moderate_rate",""), key=f"{prefix}lcc_lab_{proc}_modrate_{i}")
                    item["unskilled_rate"] = st.text_input("Rate - Unskilled (€/h)", item.get("unskilled_rate",""), key=f"{prefix}lcc_lab_{proc}_unskrate_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_lab_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_lab_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar linha de trabalho - {proc}", key=f"{prefix}add_lcc_lab_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover última linha - {proc}", key=f"{prefix}rem_lcc_lab_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_outputs(data_key, prefix=""):
    st.subheader("Outputs (produto final)")
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["outputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["outputs"][proc] = items
        
        with st.expander(f"Outputs LCC - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lcc_out_{proc}_mat_{i}")
                    item["market_price"] = st.text_input("Market Price €", item.get("market_price",""), key=f"{prefix}lcc_out_{proc}_price_{i}")
                with col2:
                    item["quantity"] = st.text_input("Quantity", item.get("quantity",""), key=f"{prefix}lcc_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lcc_out_{proc}_unit_{i}")
                with col3:
                    item["amount_produced"] = st.text_input("Amount Of Product Produced", item.get("amount_produced",""), key=f"{prefix}lcc_out_{proc}_prod_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_out_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        "Data Source", 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_out_{proc}_ds_{i}",
                        placeholder=t("choose_language")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Adicionar output LCC - {proc}", key=f"{prefix}add_lcc_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"Remover último output LCC - {proc}", key=f"{prefix}rem_lcc_out_{proc}"):
                    items.pop()
                    st.rerun()

def render_full_form(data_key, prefix=""):
    if st.session_state[data_key] is None:
        st.session_state[data_key] = {
            "lca": {
                "inputs": {p: [] for p in PROCESSOS},
                "processes": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            },
            "lcc": {
                "materials": {p: [] for p in PROCESSOS},
                "equipment": {p: [] for p in PROCESSOS},
                "labour": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            }
        }
    else:
        st.session_state[data_key] = ensure_new_structure(st.session_state[data_key])

    st.subheader("LCA - Análise do Ciclo de Vida")
    render_lca_inputs(data_key, prefix)
    render_lca_processes(data_key, prefix)
    render_lca_outputs(data_key, prefix)

    st.subheader("LCC - Custo do Ciclo de Vida")
    render_lcc_materials(data_key, prefix)
    render_lcc_equipment(data_key, prefix)
    render_lcc_labour(data_key, prefix)
    render_lcc_outputs(data_key, prefix)

# ============================================================
# FUNÇÃO PARA CRIAR ÂNCORA E TRIGGER SCROLL
# ============================================================
def create_document_anchor(doc_id):
    st.markdown(f'<div id="doc-{doc_id}" class="doc-anchor"></div>', unsafe_allow_html=True)

def trigger_scroll(doc_id):
    st.query_params["scroll_to"] = str(doc_id)

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

# Verificar se o utilizador está autenticado
if st.session_state.token is None:
    # Tela de Login/Registo com suporte a idioma
    st.title(t("app_title"))
    
    # Seletor de idioma na página de login
    idioma_selecionado = st.selectbox(
        t("language"),
        options=["pt", "en"],
        format_func=lambda x: t("language_pt") if x == "pt" else t("language_en"),
        key="login_idioma"
    )
    
    tab1, tab2 = st.tabs([t("login"), t("register")])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input(t("username"))
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("enter"))
            if submitted:
                # Guardar idioma selecionado para usar na tradução de erros
                st.session_state.idioma = idioma_selecionado
                if login(username, password):
                    st.session_state.success_message = t("login_success") if hasattr(st.session_state, 'idioma') else "Login efetuado com sucesso!"
                    st.rerun()
    
    with tab2:
        with st.form("register_form"):
            reg_username = st.text_input(t("username"))
            reg_password = st.text_input(t("password"), type="password")
            reg_nome = st.text_input(t("full_name"))
            reg_perfil = st.selectbox(
                t("profile"),
                options=["parceiro", "empresa", "admin"],
                format_func=lambda x: {
                    "parceiro": t("profile_parceiro"),
                    "empresa": t("profile_empresa"),
                    "admin": t("profile_admin")
                }.get(x, x),
                placeholder=t("choose_language")
            )
            reg_idioma = st.selectbox(
                t("language"),
                options=["pt", "en"],
                format_func=lambda x: t("language_pt") if x == "pt" else t("language_en"),
                key="register_idioma"
            )
            
            submitted_reg = st.form_submit_button(t("register"))
            if submitted_reg:
                if not reg_username.strip():
                    st.error(t("username_required"))
                elif not reg_password.strip() or len(reg_password.strip()) < 3:
                    st.error(t("password_required"))
                elif not reg_perfil:
                    st.error(t("profile_required"))
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/registar",
                            json={
                                "username": reg_username.strip(),
                                "password": reg_password.strip(),
                                "perfil": reg_perfil,
                                "nome_completo": reg_nome.strip() if reg_nome.strip() else reg_username.strip(),
                                "idioma": reg_idioma
                            }
                        )
                        if resp.status_code == 200:
                            st.session_state.idioma = reg_idioma
                            st.success(t("register_success"))
                            # Fazer login automático
                            if login(reg_username.strip(), reg_password.strip()):
                                st.session_state.success_message = t("register_success")
                                st.rerun()
                        else:
                            try:
                                erro = resp.json().get("detail", "Erro desconhecido")
                            except:
                                erro = resp.text
                            st.error(f"{t('register_error')} {erro}")
                    except Exception as e:
                        st.error(f"{t('register_error')} {str(e)}")
    st.stop()

# ============================================================
# A PARTIR DAQUI, O UTILIZADOR ESTÁ AUTENTICADO
# ============================================================

# Mostrar mensagem de sucesso com toast
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

# Processar abertura de documento vindo das notificações
if "doc_id" in st.query_params and st.query_params["doc_id"]:
    try:
        doc_id = int(st.query_params["doc_id"])
        st.session_state.doc_selecionado = doc_id
        st.query_params.clear()
    except ValueError:
        pass

if st.session_state.redirect_to_docs:
    st.session_state.menu_parceiro_widget = t("my_documents") if hasattr(st.session_state, 'idioma') else "Meus Documentos"
    st.session_state.redirect_to_docs = False

# Se close_doc_after_action estiver ativo, fechar o documento
if st.session_state.get("close_doc_after_action", False):
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False

# Renderizar badge de notificações
if st.session_state.token is not None:
    render_notificacoes_badge()
    verificar_novas_notificacoes()

# ============================================================
# SIDEBAR - VISÍVEL APÓS LOGIN - 270px
# ============================================================
with st.sidebar:
    st.write(f"{t('logged_as')} **{st.session_state.username}**")
    st.divider()
    
    if st.session_state.token is not None:
        try:
            count = get_notificacoes_nao_lidas()
            if count > 0:
                if count == 1:
                    st.warning(t("unread_notifications_one", count=count))
                else:
                    st.warning(t("unread_notifications_other", count=count))
            else:
                st.info(t("no_notifications"))
        except:
            pass
    
    st.divider()
    
    if st.button(t("dashboard"), use_container_width=True, key="app_dashboard"):
        st.switch_page("pages/dashboard.py")
    
    if st.button(t("notifications"), use_container_width=True, key="app_notificacoes"):
        st.switch_page("pages/notificacoes.py")
    
    st.divider()
    
    if st.button(t("logout"), use_container_width=True, key="app_logout"):
        logout()
        st.rerun()

st.title(t("app_title"))

# ---------- Resumo de documentos ----------
if st.session_state.perfil != "admin":
    documentos = listar_documentos()
    if documentos:
        st.subheader(t("documents"))
        show_document_summary(documentos)
        st.divider()
    else:
        st.info(t("create_first"))

# ---------- Área do Parceiro ----------
if st.session_state.perfil == "parceiro":
    st.header(t("profile_parceiro"))
    menu = st.sidebar.radio(t("documents"), [t("my_documents"), t("create_document")], key="menu_parceiro_widget")

    if menu == t("create_document"):
        st.subheader(t("new_document_title"))
        titulo = st.text_input(t("document_title"))
        st.info(t("fill_data_info"))
        if st.session_state.new_data is None:
            st.session_state.new_data = ensure_new_structure({})
        render_full_form("new_data", prefix="new_")
        if st.button(t("create_doc_btn"), key="create_doc_btn"):
            if not titulo.strip():
                st.error(t("title_required"))
            else:
                dados = st.session_state.new_data
                novo = criar_documento(titulo, dados)
                if novo:
                    st.session_state.success_message = t("document_created", id=novo['id'])
                    st.session_state.new_data = None
                    st.session_state.doc_selecionado = None
                    st.session_state.redirect_to_docs = True
                    st.rerun()

    elif menu == t("my_documents"):
        st.subheader(t("my_documents"))
        
        if st.button(t("refresh"), key="refresh_list_parceiro"):
            st.session_state.doc_selecionado = None
            st.session_state.edit_data = None
            st.session_state.parceiro_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos()
        if not documentos:
            st.info(t("no_documents"))
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
            estado_map = {
                "Rascunho": t("status_draft"),
                "Submetido": t("status_submitted"),
                "Em Revisão": t("status_review"),
                "Alterações": t("status_changes"),
                "Aprovado": t("status_approved"),
                "Arquivado": t("status_archived")
            }
            df["estado"] = df["estado"].map(estado_map).fillna(df["estado"])
            df.columns = [t("id"), t("title"), t("status"), t("version"), t("updated_at")]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                t("select_document"),
                ids,
                format_func=lambda x: t("select_document") if x == "" else f"ID {x}",
                key=f"parceiro_selectbox_{st.session_state.parceiro_dropdown_key}",
                placeholder=t("choose_language")
            )

            if st.button(t("load_document"), key="parceiro_carregar_doc"):
                if not id_selecionado:
                    st.warning(t("select_document"))
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                estado_traduzido = estado_map.get(doc['estado'], doc['estado'])
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']}")
                st.write(f"{t('status')}: **{estado_traduzido}** | {t('version')}: {doc['versao_atual']}")
                
                dados = doc['dados']
                
                with st.expander(t("view_json"), expanded=False):
                    st.json(dados)

                st.markdown("---")

                # ---------- BOTÕES DE AÇÃO ----------
                if doc['estado'] == "Rascunho":
                    st.subheader(t("action_edit"))
                    if st.session_state.edit_data is None:
                        st.session_state.edit_data = ensure_new_structure(safe_copy(dados))
                    render_full_form("edit_data", prefix="edit_")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button(t("save"), key="parceiro_save_edit", use_container_width=True):
                            novos_dados = st.session_state.edit_data
                            resultado = editar_documento(doc['id'], novos_dados)
                            if resultado:
                                st.session_state.edit_data = None
                                st.session_state.doc_selecionado = None
                                st.session_state.close_doc_after_action = True
                                st.success(t("document_updated"))
                                st.rerun()
                    with col_btn2:
                        if st.button(t("action_submit"), key="parceiro_submeter", use_container_width=True):
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                resultado_sub = submeter(doc['id'])
                                if resultado_sub:
                                    st.session_state.edit_data = None
                                    st.session_state.doc_selecionado = None
                                    st.session_state.close_doc_after_action = True
                                    st.rerun()
                    with col_btn3:
                        if st.button(t("close"), key="parceiro_fechar_detalhes", use_container_width=True):
                            st.session_state.doc_selecionado = None
                            st.session_state.edit_data = None
                            st.rerun()

                else:
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    if doc['estado'] == "Alterações":
                        with col_btn1:
                            st.warning(t("msg_changes_requested"))
                            versoes = listar_versoes(doc['id'])
                            if versoes:
                                ultima = versoes[-1]
                                if ultima['comentario']:
                                    st.info(t("msg_reason", motivo=ultima['comentario']))
                            if st.button(t("action_edit_again"), key="parceiro_editar_novamente", use_container_width=True):
                                if editar_novamente(doc['id']):
                                    st.rerun()
                    elif doc['estado'] == "Aprovado":
                        with col_btn1:
                            st.success(t("msg_approved_readonly"))
                    elif doc['estado'] in ["Submetido", "Em Revisão"]:
                        with col_btn1:
                            st.info(t("msg_under_review"))
                    elif doc['estado'] == "Arquivado":
                        with col_btn1:
                            st.warning(t("msg_archived_readonly"))
                    
                    with col_btn2:
                        conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                        if conteudo:
                            st.download_button(
                                label=t("export_history"),
                                data=conteudo,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_parceiro_{doc['id']}_{st.session_state.refresh_counter}",
                                use_container_width=True
                            )
                    
                    with col_btn3:
                        if st.button(t("close_details"), key="parceiro_fechar_detalhes", use_container_width=True):
                            st.session_state.doc_selecionado = None
                            st.session_state.edit_data = None
                            st.rerun()

                st.markdown("---")

                with st.expander(t("view_history"), expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            estado_v = estado_map.get(v['estado'], v['estado'])
                            st.write(t("version", numero=v['numero_versao'], estado=estado_v, criado_por=v['criado_por'] or "-", data=data_formatada))
                            if v['comentario']:
                                st.caption(t("comment", comentario=v['comentario']))
                    else:
                        st.info(t("no_history"))

# ---------- Área da Empresa ----------
elif st.session_state.perfil == "empresa":
    st.header(t("profile_empresa"))

    st.subheader(t("documents"))
    render_filtros()
    
    if st.button(t("refresh"), key="refresh_list_empresa"):
        st.session_state.doc_selecionado = None
        st.session_state.empresa_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
    if not documentos:
        st.info(t("no_documents_filter"))
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        estado_map = {
            "Rascunho": t("status_draft"),
            "Submetido": t("status_submitted"),
            "Em Revisão": t("status_review"),
            "Alterações": t("status_changes"),
            "Aprovado": t("status_approved"),
            "Arquivado": t("status_archived")
        }
        df["estado"] = df["estado"].map(estado_map).fillna(df["estado"])
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = [t("id"), t("title"), t("partner"), t("status"), t("version"), t("updated_at")]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]

        id_selecionado = st.selectbox(
            t("select_document"),
            ids,
            format_func=lambda x: t("select_document") if x == "" else f"ID {x}",
            key=f"empresa_selectbox_{st.session_state.empresa_dropdown_key}",
            placeholder=t("choose_language")
        )

        if st.button(t("load_document"), key="empresa_carregar_doc"):
            if not id_selecionado:
                st.warning(t("select_document"))
            else:
                st.session_state.doc_selecionado = id_selecionado
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            estado_traduzido = estado_map.get(doc['estado'], doc['estado'])
            st.subheader(f"Documento ID {doc['id']}: {doc['titulo']} ({t('partner')}: {doc['parceiro_id']})")
            st.write(f"{t('status')}: **{estado_traduzido}** | {t('version')}: {doc['versao_atual']}")

            dados = doc['dados']
            
            with st.expander(t("view_json"), expanded=False):
                st.json(dados)

            st.markdown("---")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            if doc['estado'] == "Submetido":
                with col_btn1:
                    if st.button(t("action_start_review"), key="empresa_iniciar_revisao", use_container_width=True):
                        if iniciar_revisao(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Em Revisão":
                comentario = st.text_area(t("action_comment_required"), key="empresa_comentario")
                col_aprov, col_alt = st.columns(2)
                with col_aprov:
                    if st.button(t("action_approve"), key="empresa_aprovar", use_container_width=True):
                        if aprovar(doc['id']):
                            st.rerun()
                with col_alt:
                    if st.button(t("action_request_changes"), key="empresa_pedir_alteracoes", use_container_width=True):
                        if not comentario.strip():
                            st.error(t("action_comment_required"))
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.rerun()
            elif doc['estado'] == "Aprovado":
                with col_btn1:
                    if st.button(t("action_reopen"), key="empresa_reabrir", use_container_width=True):
                        if reabrir(doc['id']):
                            st.rerun()
                with col_btn2:
                    if st.button(t("action_archive"), key="empresa_arquivar", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Rascunho":
                with col_btn1:
                    if st.button(t("action_archive_draft"), key="empresa_arquivar_rascunho", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Alterações":
                with col_btn1:
                    st.info(t("msg_awaiting_partner"))
            elif doc['estado'] == "Arquivado":
                with col_btn1:
                    st.warning(t("msg_archived_readonly"))

            with col_btn2:
                conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                if conteudo:
                    st.download_button(
                        label=t("export_history"),
                        data=conteudo,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_empresa_{doc['id']}_{st.session_state.refresh_counter}",
                        use_container_width=True
                    )

            with col_btn3:
                if st.button(t("close_details"), key="empresa_fechar_detalhes", use_container_width=True):
                    st.session_state.doc_selecionado = None
                    st.rerun()

            st.markdown("---")

            with st.expander(t("view_history"), expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        estado_v = estado_map.get(v['estado'], v['estado'])
                        st.write(t("version", numero=v['numero_versao'], estado=estado_v, criado_por=v['criado_por'] or "-", data=data_formatada))
                        if v['comentario']:
                            st.caption(t("comment", comentario=v['comentario']))
                else:
                    st.info(t("no_history"))

# ---------- Área do Admin ----------
elif st.session_state.perfil == "admin":
    st.header(t("admin_panel"))
    menu_admin = st.sidebar.radio(t("admin_panel"), [t("admin_users"), t("admin_documents")], key="admin_menu")

    if menu_admin == t("admin_users"):
        st.subheader(t("user_management"))
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(t("load_users"), use_container_width=True, key="admin_carregar_users"):
                st.session_state.doc_selecionado = None
                st.session_state.admin_user_dropdown_key += 1
                st.session_state.refresh_counter += 1
                st.rerun()
        with col2:
            if st.button(t("new_user"), use_container_width=True, key="admin_novo_user"):
                st.session_state.show_create_user_form = True
                st.rerun()
        
        st.write("")

        resp = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
        if resp.status_code == 200:
            users = resp.json()
            if users:
                perfil_map = {
                    "empresa": t("profile_empresa"),
                    "parceiro": t("profile_parceiro"),
                    "admin": t("profile_admin")
                }
                for user in users:
                    user["perfil"] = perfil_map.get(user["perfil"], user["perfil"])
                
                df = pd.DataFrame(users)
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_disponiveis = df.columns.tolist()
                colunas_desejadas = ["username", "perfil", "nome_completo", "idioma", "created_at"]
                colunas_existentes = [col for col in colunas_desejadas if col in cols_disponiveis]
                df = df[colunas_existentes]
                df.columns = [t("username"), t("profile"), t("full_name"), t("language"), t("created_at")]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                
                st.subheader(t("manage_user"))
                
                usernames = [""] + [u["username"] for u in users]

                sel_user = st.selectbox(
                    t("select_user"),
                    usernames,
                    format_func=lambda x: t("select_user") if x == "" else x,
                    key=f"admin_user_selectbox_{st.session_state.admin_user_dropdown_key}",
                    placeholder=t("choose_language")
                )

                if sel_user:
                    user_data = next((u for u in users if u["username"] == sel_user), None)
                    if user_data:
                        st.info(f"**{t('username')}:** {user_data['username']} | **{t('profile')}:** {user_data['perfil']} | **{t('full_name')}:** {user_data['nome_completo']} | **{t('language')}:** {user_data.get('idioma', 'pt')}")
                    
                    st.subheader(t("change_password"))
                    pw_key = f"admin_pw_input_{st.session_state.pw_input_counter}"
                    nova_pw = st.text_input(
                        t("new_password"), 
                        type="password", 
                        key=pw_key,
                        placeholder=t("new_password")
                    )
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button(t("change_password_btn"), key="btn_alterar_pw", use_container_width=True):
                            if not sel_user:
                                st.warning(t("select_user"))
                            elif not nova_pw.strip():
                                st.warning(t("password_required"))
                            elif len(nova_pw.strip()) < 3:
                                st.warning(t("password_required"))
                            else:
                                resp_pw = requests.put(
                                    f"{API_URL}/admin/usuarios/{sel_user}/password",
                                    json={"nova_password": nova_pw},
                                    headers=headers_auth()
                                )
                                if resp_pw.status_code == 200:
                                    st.toast(f"✅ {t('password_changed', username=sel_user)}", icon="✅")
                                    st.session_state.pw_input_counter += 1
                                    st.rerun()
                                else:
                                    try:
                                        erro = resp_pw.json().get("detail", "Erro desconhecido")
                                    except:
                                        erro = resp_pw.text
                                    st.error(f"Erro ao alterar password: {erro}")
                    
                    with col_btn2:
                        if st.button(t("delete_user"), key="btn_eliminar_user", use_container_width=True):
                            if not sel_user:
                                st.warning(t("select_user"))
                            elif sel_user == st.session_state.username:
                                st.error(t("cannot_delete_self"))
                            else:
                                confirm = st.button(t("confirm"), key="btn_confirmar_eliminar")
                                if confirm:
                                    resp_del = requests.delete(f"{API_URL}/admin/usuarios/{sel_user}", headers=headers_auth())
                                    if resp_del.status_code == 200:
                                        st.toast(f"🗑️ {t('user_deleted', username=sel_user)}", icon="🗑️")
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_del.json().get("detail", "Erro desconhecido")
                                        except:
                                            erro = resp_del.text
                                        st.error(f"Erro ao eliminar: {erro}")
                    
                    with col_btn3:
                        if st.button(t("close_details"), key="admin_fechar_gerir_user", use_container_width=True):
                            st.session_state.admin_user_dropdown_key += 1
                            st.session_state.doc_selecionado = None
                            st.rerun()
                
                if st.session_state.show_create_user_form:
                    st.divider()
                    st.subheader(t("create_new_user"))
                    
                    with st.form("create_user_form"):
                        new_username = st.text_input(t("username"), placeholder="Ex: novo_parceiro")
                        new_password = st.text_input(t("password"), type="password", placeholder="Mínimo 3 caracteres")
                        new_nome = st.text_input(t("full_name"), placeholder="Ex: João Silva")
                        new_perfil = st.selectbox(
                            t("profile"),
                            options=["parceiro", "empresa", "admin"],
                            format_func=lambda x: {
                                "parceiro": t("profile_parceiro"),
                                "empresa": t("profile_empresa"),
                                "admin": t("profile_admin")
                            }.get(x, x),
                            placeholder=t("choose_language")
                        )
                        new_idioma = st.selectbox(
                            t("language"),
                            options=["pt", "en"],
                            format_func=lambda x: t("language_pt") if x == "pt" else t("language_en"),
                            key="admin_create_idioma"
                        )
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            submit_create = st.form_submit_button(t("create_user_btn"), use_container_width=True)
                        with col2:
                            cancel_create = st.form_submit_button(t("cancel"), use_container_width=True)
                        
                        if cancel_create:
                            st.session_state.show_create_user_form = False
                            st.rerun()
                        
                        if submit_create:
                            if not new_username.strip():
                                st.error(t("username_required"))
                            elif not new_password.strip() or len(new_password.strip()) < 3:
                                st.error(t("password_required"))
                            elif not new_perfil:
                                st.error(t("profile_required"))
                            else:
                                if any(u["username"] == new_username for u in users):
                                    st.error(f"{t('username_exists')}")
                                else:
                                    try:
                                        resp_create = requests.post(
                                            f"{API_URL}/registar",
                                            json={
                                                "username": new_username.strip(),
                                                "password": new_password.strip(),
                                                "perfil": new_perfil,
                                                "nome_completo": new_nome.strip() if new_nome.strip() else new_username.strip(),
                                                "idioma": new_idioma
                                            }
                                        )
                                        if resp_create.status_code == 200:
                                            st.toast(f"✅ {t('user_created', username=new_username)}", icon="✅")
                                            st.session_state.show_create_user_form = False
                                            st.session_state.pw_input_counter += 1
                                            st.session_state.admin_user_dropdown_key += 1
                                            st.rerun()
                                        else:
                                            try:
                                                erro = resp_create.json().get("detail", "Erro desconhecido")
                                            except:
                                                erro = resp_create.text
                                            st.error(f"{t('register_error')} {erro}")
                                    except Exception as e:
                                        st.error(f"{t('register_error')} {str(e)}")

            else:
                st.info(t("no_documents"))
        else:
            st.error(t("loading"))

    else:  # Documentos (empresa) - Admin
        st.header(f"{t('admin_documents')} – {t('admin_panel')}")

        st.subheader(t("documents"))
        render_filtros()
        
        if st.button(t("refresh"), key="refresh_list_admin"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
        if not documentos:
            st.info(t("no_documents_filter"))
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            if "created_at" in df.columns:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            estado_map = {
                "Rascunho": t("status_draft"),
                "Submetido": t("status_submitted"),
                "Em Revisão": t("status_review"),
                "Alterações": t("status_changes"),
                "Aprovado": t("status_approved"),
                "Arquivado": t("status_archived")
            }
            df["estado"] = df["estado"].map(estado_map).fillna(df["estado"])
            df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
            df.columns = [t("id"), t("title"), t("partner"), t("status"), t("version"), t("updated_at")]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                t("select_document"),
                ids,
                format_func=lambda x: t("select_document") if x == "" else f"ID {x}",
                key=f"admin_selectbox_{st.session_state.admin_dropdown_key}",
                placeholder=t("choose_language")
            )

            if st.button(t("load_document"), key="admin_carregar_doc"):
                if not id_selecionado:
                    st.warning(t("select_document"))
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                estado_traduzido = estado_map.get(doc['estado'], doc['estado'])
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']} ({t('partner')}: {doc['parceiro_id']})")
                st.write(f"{t('status')}: **{estado_traduzido}** | {t('version')}: {doc['versao_atual']}")

                dados = doc['dados']
                
                with st.expander(t("view_json"), expanded=False):
                    st.json(dados)

                st.markdown("---")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                if doc['estado'] == "Submetido":
                    with col_btn1:
                        if st.button(t("action_start_review"), key="admin_iniciar_revisao", use_container_width=True):
                            if iniciar_revisao(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Em Revisão":
                    comentario = st.text_area(t("action_comment_required"), key="admin_comentario")
                    col_aprov, col_alt = st.columns(2)
                    with col_aprov:
                        if st.button(t("action_approve"), key="admin_aprovar", use_container_width=True):
                            if aprovar(doc['id']):
                                st.rerun()
                    with col_alt:
                        if st.button(t("action_request_changes"), key="admin_pedir_alteracoes", use_container_width=True):
                            if not comentario.strip():
                                st.error(t("action_comment_required"))
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.rerun()
                elif doc['estado'] == "Aprovado":
                    with col_btn1:
                        if st.button(t("action_reopen"), key="admin_reabrir", use_container_width=True):
                            if reabrir(doc['id']):
                                st.rerun()
                    with col_btn2:
                        if st.button(t("action_archive"), key="admin_arquivar", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Rascunho":
                    with col_btn1:
                        if st.button(t("action_archive_draft"), key="admin_arquivar_rascunho", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Alterações":
                    with col_btn1:
                        st.info(t("msg_awaiting_partner"))
                elif doc['estado'] == "Arquivado":
                    with col_btn1:
                        st.warning(t("msg_archived_readonly"))

                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label=t("export_history"),
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_admin_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )

                with col_btn3:
                    if st.button(t("close_details"), key="admin_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.rerun()

                st.markdown("---")

                with st.expander(t("view_history"), expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            estado_v = estado_map.get(v['estado'], v['estado'])
                            st.write(t("version", numero=v['numero_versao'], estado=estado_v, criado_por=v['criado_por'] or "-", data=data_formatada))
                            if v['comentario']:
                                st.caption(t("comment", comentario=v['comentario']))
                    else:
                        st.info(t("no_history"))

# ============================================================
# GARANTIR QUE O CLOSE_DOC_AFTER_ACTION É PROCESSADO
# ============================================================
if st.session_state.get("close_doc_after_action", False):
    if st.session_state.doc_selecionado is not None:
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False