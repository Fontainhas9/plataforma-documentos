# frontend/translations.py
import streamlit as st
import requests
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
# CONFIGURAÇÃO DE IDIOMA
# ============================================================
def get_available_languages():
    return {
        "pt": {"flag": "🇵🇹", "name": "Português"},
        "en": {"flag": "🇬🇧", "name": "English"}
    }

def get_language():
    """Obtém o idioma atual da sessão."""
    if "language" not in st.session_state:
        try:
            browser_lang = st.query_params.get("lang", "pt")
            if browser_lang in ["pt", "en"]:
                st.session_state.language = browser_lang
            else:
                st.session_state.language = "pt"
        except:
            st.session_state.language = "pt"
    return st.session_state.language

def set_language(lang):
    """Define o idioma e recarrega a página."""
    if lang in ["pt", "en"]:
        st.session_state.language = lang
        st.query_params["lang"] = lang
        st.rerun()

def load_translations():
    """Carrega as traduções da API."""
    lang = get_language()
    try:
        response = requests.get(f"{API_URL}/translations?lang={lang}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao carregar traduções: {e}")
    
    # Fallback básico
    if lang == "en":
        return {
            "app_title": "Document Management Platform",
            "login": "Login",
            "username": "Username",
            "password": "Password",
            "login_button": "Login",
            "logout": "Logout",
            "dashboard": "Dashboard",
            "notifications": "Notifications",
            "back": "← Back",
            "parceiro": "Partner",
            "empresa": "Company",
            "admin": "Administrator",
            "my_documents": "My Documents",
            "create_document": "Create Document",
            "document_title": "Document Title",
            "save": "Save",
            "submit": "Submit",
            "approve": "Approve",
            "reopen": "Reopen",
            "archive": "Archive",
            "request_changes": "Request Changes",
            "edit_again": "Edit Again",
            "start_review": "Start Review",
            "export_history": "Export History",
            "close": "Close",
            "edit": "Edit",
            "delete": "Delete",
            "confirm": "Confirm",
            "cancel": "Cancel",
            "status": "Status",
            "version": "Version",
            "partner": "Partner",
            "state": "State",
            "title": "Title",
            "id": "ID",
            "version_number": "Version",
            "partner_id": "Partner",
            "full_name": "Full Name",
            "profile": "Profile",
            "created_at": "Created At",
            "updated_at": "Updated At",
            "no_documents": "No documents found.",
            "select_document": "Select a document",
            "select_document_placeholder": "Select a document...",
            "load_document": "Load document",
            "close_details": "Close details",
            "refresh_list": "Refresh list",
            "invalid_credentials": "Invalid credentials",
            "login_success": "Login successful!",
            "document_created": "Document created successfully!",
            "document_updated": "Document updated successfully!",
            "document_submitted": "Document submitted successfully!",
            "document_approved": "Document approved successfully!",
            "document_archived": "Document archived successfully!",
            "review_started": "Review started successfully!",
            "changes_requested": "Changes requested successfully!",
            "document_reopened": "Document reopened for editing!",
            "user_created": "User created successfully!",
            "password_changed": "Password changed successfully!",
            "user_deleted": "User deleted successfully!",
            "document_edit_saved": "Document updated successfully!",
            "document_reopened_edit": "Document reopened for editing!",
            "comment_required": "A comment is required to request changes",
            "document_state_error": "Document is not submitted",
            "document_review_error": "Can only approve during review",
            "document_archive_error": "Can only archive draft or approved documents",
            "document_reopen_error": "Can only reopen an approved document",
            "document_not_found": "Document not found",
            "access_denied": "Access denied",
            "error_creating_document": "Error creating document",
            "error_loading_document": "Error loading document",
            "error_editing": "Error editing",
            "error_submitting": "Error submitting",
            "error_approving": "Error approving",
            "error_archiving": "Error archiving",
            "error_reopening": "Error reopening",
            "error_exporting": "Export failed",
            "error_loading_notifications": "Error loading notifications",
            "error_marking_read": "Error marking as read",
            "error_marking_all_read": "Error marking all as read",
            "error_loading_users": "Failed to load users",
            "error_creating_user": "Error creating user",
            "error_deleting_user": "Error deleting",
            "error_changing_password": "Error changing password",
            "logged_as": "Logged as:",
            "no_notifications_text": "No notifications",
            "unread_notifications": "unread notification(s)",
            "home": "Home",
            "document_id": "Document ID",
            "last_update": "Last Update",
            "comment": "Comment",
            "comment_optional": "Comment (required if requesting changes)",
            "waiting_partner": "Waiting for partner to edit again.",
            "document_approved_status": "Document approved. Cannot be edited.",
            "under_review": "Document under review by the company.",
            "archived_readonly": "Document archived (view only).",
            "company_requested_changes": "The company requested changes.",
            "reason": "Reason",
            "export_historical": "Export History",
            "filters": "Search Filters",
            "search": "Search",
            "search_placeholder": "Title, partner or ID...",
            "start_date": "Start Date",
            "end_date": "End Date",
            "order_by": "Order By",
            "order_direction": "Direction",
            "ascending": "Ascending",
            "descending": "Descending",
            "apply_filters": "Apply Filters",
            "clear_filters": "Clear Filters",
            "key_indicators": "Key Indicators",
            "total_documents": "Total Documents",
            "approved": "Approved",
            "approval_rate": "Approval Rate",
            "avg_review_time": "Avg Review Time",
            "documents_by_status": "Document Distribution by Status",
            "recent_documents": "Recent Documents",
            "top_partners": "Top Partners",
            "partner_documents": "Partners with Most Documents",
            "days": "days",
            "no_recent_documents": "No recent documents",
            "no_top_partners": "No top partners data",
            "admin_panel": "Administrative Panel",
            "users": "Users",
            "company_documents": "Company Documents",
            "user_management": "User Management",
            "create_user": "New User",
            "change_password": "Change Password",
            "delete_user": "Delete User",
            "confirm_delete": "Confirm Deletion",
            "close_details": "Close Details",
            "new_password": "New password (leave empty to keep current)",
            "create_user_form": "Create New User",
            "username_required": "Username is required",
            "password_required": "Password is required and must be at least 3 characters",
            "profile_required": "Profile is required",
            "username_exists": "Username already exists!",
            "select_user": "Select user to manage",
            "select_user_placeholder": "Select a user...",
            "loading_users": "Load users",
            "manage_user": "Manage User",
            "password_min_length": "Password must be at least 3 characters",
            "cannot_delete_self": "Cannot delete yourself",
            "user_not_found": "User not found",
            "only_admin": "Admin only",
            "please_login_first": "Please login first.",
            "no_notifications": "No notifications found.",
            "mark_all_read": "Mark all as read",
            "mark_read": "Mark as read",
            "unread": "Unread",
            "read": "Read",
            "all_notifications_read": "All notifications are read.",
            "view_document": "View Document",
            "no_notifications_text_sidebar": "No notifications",
            "unread_notifications_sidebar": "unread notification(s)",
            "menu": "Menu",
            "error": "Error",
            "warning": "Warning",
            "info": "Information",
            "success": "Success",
            "fill_form_instructions": "Fill in the data in the tables below. Each process has its own section.",
            "document_summary": "Document Summary",
            "view_data_tables": "View data in tables",
            "view_raw_json": "View raw JSON",
            "version_history": "Version History",
            "no_history": "No history available.",
            "select_document_first": "Select a document.",
            "partner_area": "Partner Area",
            "company_area": "Company Area (Validation)",
            "admin_area": "Administrative Panel",
            "Rascunho": "Draft",
            "Submetido": "Submitted",
            "Em Revisão": "Under Review",
            "Alterações": "Changes Requested",
            "Aprovado": "Approved",
            "Arquivado": "Archived",
        }
    else:
        return {
            "app_title": "Plataforma de Gestão de Documentos",
            "login": "Login",
            "username": "Utilizador",
            "password": "Palavra-passe",
            "login_button": "Entrar",
            "logout": "Sair",
            "dashboard": "Painel de Controlo",
            "notifications": "Notificações",
            "back": "← Voltar",
            "parceiro": "Parceiro",
            "empresa": "Empresa",
            "admin": "Administrador",
            "my_documents": "Meus Documentos",
            "create_document": "Criar Documento",
            "document_title": "Título do Documento",
            "save": "Guardar",
            "submit": "Submeter",
            "approve": "Aprovar",
            "reopen": "Reabrir",
            "archive": "Arquivar",
            "request_changes": "Pedir alterações",
            "edit_again": "Editar novamente",
            "start_review": "Iniciar revisão",
            "export_history": "Exportar Histórico",
            "close": "Fechar",
            "edit": "Editar",
            "delete": "Eliminar",
            "confirm": "Confirmar",
            "cancel": "Cancelar",
            "status": "Estado",
            "version": "Versão",
            "partner": "Parceiro",
            "state": "Estado",
            "title": "Título",
            "id": "ID",
            "version_number": "Versão",
            "partner_id": "Parceiro",
            "full_name": "Nome",
            "profile": "Perfil",
            "created_at": "Data Criação",
            "updated_at": "Data Atualização",
            "no_documents": "Nenhum documento encontrado.",
            "select_document": "Seleciona um documento",
            "select_document_placeholder": "Selecione um documento...",
            "load_document": "Carregar documento",
            "close_details": "Fechar detalhes",
            "refresh_list": "Atualizar lista",
            "invalid_credentials": "Credenciais inválidas",
            "login_success": "Login efetuado com sucesso!",
            "document_created": "Documento criado com sucesso!",
            "document_updated": "Documento atualizado com sucesso!",
            "document_submitted": "Documento submetido com sucesso!",
            "document_approved": "Documento aprovado com sucesso!",
            "document_archived": "Documento arquivado com sucesso!",
            "review_started": "Revisão iniciada com sucesso!",
            "changes_requested": "Alterações solicitadas com sucesso!",
            "document_reopened": "Documento reaberto para edição!",
            "user_created": "Utilizador criado com sucesso!",
            "password_changed": "Password alterada com sucesso!",
            "user_deleted": "Utilizador eliminado com sucesso!",
            "document_edit_saved": "Documento atualizado com sucesso!",
            "document_reopened_edit": "Documento reaberto para edição!",
            "comment_required": "É necessário um comentário para pedir alterações",
            "document_state_error": "Documento não está submetido",
            "document_review_error": "Só pode aprovar durante a revisão",
            "document_archive_error": "Só é possível arquivar documentos em rascunho ou aprovados",
            "document_reopen_error": "Só pode reabrir um documento aprovado",
            "document_not_found": "Documento não encontrado",
            "access_denied": "Acesso negado",
            "error_creating_document": "Erro ao criar documento",
            "error_loading_document": "Erro ao obter documento",
            "error_editing": "Erro ao editar",
            "error_submitting": "Erro ao submeter",
            "error_approving": "Erro ao aprovar",
            "error_archiving": "Erro ao arquivar",
            "error_reopening": "Erro ao reabrir",
            "error_exporting": "Falha na exportação",
            "error_loading_notifications": "Erro ao carregar notificações",
            "error_marking_read": "Erro ao marcar como lida",
            "error_marking_all_read": "Erro ao marcar todas como lidas",
            "error_loading_users": "Falha ao carregar utilizadores",
            "error_creating_user": "Erro ao criar utilizador",
            "error_deleting_user": "Erro ao eliminar",
            "error_changing_password": "Erro ao alterar password",
            "logged_as": "Logado como:",
            "no_notifications_text": "Sem notificações",
            "unread_notifications": "notificação(ões) não lida(s)",
            "home": "Início",
            "document_id": "Documento ID",
            "last_update": "Última Atualização",
            "comment": "Comentário",
            "comment_optional": "Comentário (obrigatório se pedir alterações)",
            "waiting_partner": "Aguardando o parceiro editar novamente.",
            "document_approved_status": "Documento aprovado. Não pode ser editado.",
            "under_review": "Documento em análise pela empresa.",
            "archived_readonly": "Documento arquivado (apenas consulta).",
            "company_requested_changes": "A empresa pediu alterações.",
            "reason": "Motivo",
            "export_historical": "Exportar Histórico",
            "filters": "Filtros de Pesquisa",
            "search": "Pesquisar",
            "search_placeholder": "Título, parceiro ou ID...",
            "start_date": "Data Início",
            "end_date": "Data Fim",
            "order_by": "Ordenar por",
            "order_direction": "Direção",
            "ascending": "Crescente",
            "descending": "Decrescente",
            "apply_filters": "Aplicar Filtros",
            "clear_filters": "Limpar Filtros",
            "key_indicators": "Indicadores Chave",
            "total_documents": "Total Documentos",
            "approved": "Aprovados",
            "approval_rate": "Taxa Aprovação",
            "avg_review_time": "Tempo Médio Revisão",
            "documents_by_status": "Distribuição de Documentos por Estado",
            "recent_documents": "Documentos Recentes",
            "top_partners": "Top Parceiros",
            "partner_documents": "Parceiros com Mais Documentos",
            "days": "dias",
            "no_recent_documents": "Sem documentos recentes",
            "no_top_partners": "Sem dados de top parceiros",
            "admin_panel": "Painel Administrativo",
            "users": "Utilizadores",
            "company_documents": "Documentos (empresa)",
            "user_management": "Gestão de Utilizadores",
            "create_user": "Novo Utilizador",
            "change_password": "Alterar Password",
            "delete_user": "Eliminar utilizador",
            "confirm_delete": "Confirmar eliminação",
            "close_details": "Fechar Detalhes",
            "new_password": "Nova password (deixar vazio para não alterar)",
            "create_user_form": "Criar Novo Utilizador",
            "username_required": "Username é obrigatório",
            "password_required": "Password é obrigatória e deve ter pelo menos 3 caracteres",
            "profile_required": "Perfil é obrigatório",
            "username_exists": "Username já existe!",
            "select_user": "Selecionar utilizador para gerir",
            "select_user_placeholder": "Selecione um utilizador...",
            "loading_users": "Carregar utilizadores",
            "manage_user": "Gerir Utilizador",
            "password_min_length": "A password deve ter pelo menos 3 caracteres",
            "cannot_delete_self": "Não pode eliminar a si próprio",
            "user_not_found": "Utilizador não encontrado",
            "only_admin": "Apenas admin",
            "please_login_first": "Por favor, faça login primeiro.",
            "no_notifications": "Nenhuma notificação encontrada.",
            "mark_all_read": "Marcar todas como lidas",
            "mark_read": "Marcar como lida",
            "unread": "Não lida",
            "read": "Lida",
            "all_notifications_read": "Todas as notificações estão lidas.",
            "view_document": "Ver Documento",
            "no_notifications_text_sidebar": "Sem notificações",
            "unread_notifications_sidebar": "notificação(ões) não lida(s)",
            "menu": "Menu",
            "error": "Erro",
            "warning": "Aviso",
            "info": "Informação",
            "success": "Sucesso",
            "fill_form_instructions": "Preencha os dados nas tabelas abaixo. Cada processo tem a sua própria secção.",
            "document_summary": "Resumo de documentos",
            "view_data_tables": "Ver dados em tabelas",
            "view_raw_json": "Ver JSON bruto",
            "version_history": "Histórico de versões",
            "no_history": "Sem histórico disponível.",
            "select_document_first": "Selecione um documento.",
            "partner_area": "Área do Parceiro",
            "company_area": "Área da Empresa (Validação)",
            "admin_area": "Painel Administrativo",
            "Rascunho": "Rascunho",
            "Submetido": "Submetido",
            "Em Revisão": "Em Revisão",
            "Alterações": "Alterações",
            "Aprovado": "Aprovado",
            "Arquivado": "Arquivado",
        }

def get_text(key, default=None):
    """Obtém um texto traduzido."""
    if "translations" not in st.session_state:
        st.session_state.translations = load_translations()
    
    if key in st.session_state.translations:
        return st.session_state.translations[key]
    
    return default or key

def get_datasource_options():
    """Obtém as opções de fonte de dados no idioma atual."""
    lang = get_language()
    try:
        response = requests.get(f"{API_URL}/datasource-options?lang={lang}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    if lang == "en":
        return ["Measured", "Calculated", "Estimated", "Literature"]
    return ["Medido", "Calculado", "Estimado", "Literatura"]

def translate_estado(estado):
    """Traduz um estado de documento."""
    return get_text(estado, estado)

def translate_perfil(perfil):
    """Traduz um perfil de utilizador."""
    return get_text(perfil, perfil)

# Carregar traduções inicialmente
if "translations" not in st.session_state:
    st.session_state.translations = load_translations()