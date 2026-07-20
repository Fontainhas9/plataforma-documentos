# backend/translations.py
"""
Módulo de tradução para a plataforma.
Suporta Inglês (en) e Português (pt).
"""

TRANSLATIONS = {
    "en": {
        # Geral
        "app_title": "Document Management Platform",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "enter": "Enter",
        "logout": "Logout",
        "back": "Back",
        "dashboard": "Dashboard",
        "notifications": "Notifications",
        "document": "Document",
        "documents": "Documents",
        "status": "Status",
        "version": "Version",
        "created": "Created",
        "updated": "Updated",
        "actions": "Actions",
        "close": "Close",
        "save": "Save",
        "submit": "Submit",
        "edit": "Edit",
        "delete": "Delete",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "search": "Search",
        "filter": "Filter",
        "clear": "Clear",
        "apply": "Apply",
        "refresh": "Refresh",
        "loading": "Loading...",
        "no_data": "No data found",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Information",
        "select_option": "Select an option",
        "required": "Required",
        "optional": "Optional",
        "language": "Language",
        "portuguese": "Português",
        "english": "English",

        # Perfis
        "profile_parceiro": "Partner",
        "profile_empresa": "Company",
        "profile_admin": "Admin",

        # Documentos
        "doc_id": "ID",
        "doc_title": "Title",
        "doc_partner": "Partner",
        "doc_status": "Status",
        "doc_version": "Version",
        "doc_last_update": "Last Update",
        "doc_created_at": "Created At",
        "doc_updated_at": "Updated At",
        "doc_state_draft": "Draft",
        "doc_state_submitted": "Submitted",
        "doc_state_review": "Under Review",
        "doc_state_changes": "Changes Requested",
        "doc_state_approved": "Approved",
        "doc_state_archived": "Archived",

        # Estados do fluxo
        "new_document": "New Document",
        "my_documents": "My Documents",
        "create_document": "Create Document",
        "edit_document": "Edit Document",
        "document_details": "Document Details",
        "document_history": "History",
        "view_data": "View Data",
        "view_json": "View JSON",
        "export_excel": "Export to Excel",
        "export_history": "Export History",
        "submit_for_review": "Submit for Review",
        "start_review": "Start Review",
        "request_changes": "Request Changes",
        "approve": "Approve",
        "reopen": "Reopen",
        "archive": "Archive",
        "edit_again": "Edit Again",
        "waiting_company": "Awaiting company action",
        "waiting_partner": "Awaiting partner action",
        "changes_requested": "Changes requested",
        "in_review": "In review",
        "approved": "Approved",
        "archived": "Archived (view only)",

        # Notificações
        "no_notifications": "No notifications",
        "unread_notifications": "unread notifications",
        "unread_notification": "unread notification",
        "mark_as_read": "Mark as read",
        "mark_all_read": "Mark all as read",
        "view_document": "View Document",

        # KPIs
        "kpi_total": "Total Documents",
        "kpi_approved": "Approved",
        "kpi_approval_rate": "Approval Rate",
        "kpi_avg_review": "Avg Review Time",

        # Filtros
        "filters": "Filters",
        "filter_search": "Search",
        "filter_status": "Status",
        "filter_date_start": "Start Date",
        "filter_date_end": "End Date",
        "filter_order_by": "Order By",
        "filter_order_dir": "Direction",
        "filter_order_asc": "Ascending",
        "filter_order_desc": "Descending",

        # Dashboard
        "dashboard_title": "Dashboard",
        "recent_documents": "Recent Documents",
        "top_partners": "Top Partners",
        "documents_by_status": "Documents by Status",

        # Admin
        "admin_panel": "Admin Panel",
        "user_management": "User Management",
        "manage_users": "Manage Users",
        "new_user": "New User",
        "create_user": "Create User",
        "edit_user": "Edit User",
        "change_password": "Change Password",
        "new_password": "New Password",
        "full_name": "Full Name",
        "profile": "Profile",
        "user_exists": "User already exists",
        "cannot_delete_self": "Cannot delete yourself",

        # Comentários
        "comment": "Comment",
        "comment_required": "Comment is required when requesting changes",

        # Placeholders
        "placeholder_search": "Title, partner or ID...",
        "placeholder_title": "Document title",
        "placeholder_username": "Enter username",
        "placeholder_password": "Enter password",
        "placeholder_full_name": "Full name",
    },

    "pt": {
        # Geral
        "app_title": "Plataforma de Gestão de Documentos",
        "login": "Entrar",
        "username": "Utilizador",
        "password": "Palavra-passe",
        "enter": "Entrar",
        "logout": "Sair",
        "back": "Voltar",
        "dashboard": "Painel",
        "notifications": "Notificações",
        "document": "Documento",
        "documents": "Documentos",
        "status": "Estado",
        "version": "Versão",
        "created": "Criado",
        "updated": "Atualizado",
        "actions": "Ações",
        "close": "Fechar",
        "save": "Guardar",
        "submit": "Submeter",
        "edit": "Editar",
        "delete": "Eliminar",
        "cancel": "Cancelar",
        "confirm": "Confirmar",
        "search": "Pesquisar",
        "filter": "Filtrar",
        "clear": "Limpar",
        "apply": "Aplicar",
        "refresh": "Atualizar",
        "loading": "A carregar...",
        "no_data": "Sem dados",
        "error": "Erro",
        "success": "Sucesso",
        "warning": "Aviso",
        "info": "Informação",
        "select_option": "Selecione uma opção",
        "required": "Obrigatório",
        "optional": "Opcional",
        "language": "Idioma",
        "portuguese": "Português",
        "english": "English",

        # Perfis
        "profile_parceiro": "Parceiro",
        "profile_empresa": "Empresa",
        "profile_admin": "Admin",

        # Documentos
        "doc_id": "ID",
        "doc_title": "Título",
        "doc_partner": "Parceiro",
        "doc_status": "Estado",
        "doc_version": "Versão",
        "doc_last_update": "Última Atualização",
        "doc_created_at": "Criado em",
        "doc_updated_at": "Atualizado em",
        "doc_state_draft": "Rascunho",
        "doc_state_submitted": "Submetido",
        "doc_state_review": "Em Revisão",
        "doc_state_changes": "Alterações",
        "doc_state_approved": "Aprovado",
        "doc_state_archived": "Arquivado",

        # Estados do fluxo
        "new_document": "Novo Documento",
        "my_documents": "Meus Documentos",
        "create_document": "Criar Documento",
        "edit_document": "Editar Documento",
        "document_details": "Detalhes do Documento",
        "document_history": "Histórico",
        "view_data": "Ver Dados",
        "view_json": "Ver JSON",
        "export_excel": "Exportar para Excel",
        "export_history": "Exportar Histórico",
        "submit_for_review": "Submeter para Revisão",
        "start_review": "Iniciar Revisão",
        "request_changes": "Pedir Alterações",
        "approve": "Aprovar",
        "reopen": "Reabrir",
        "archive": "Arquivar",
        "edit_again": "Editar Novamente",
        "waiting_company": "A aguardar ação da empresa",
        "waiting_partner": "A aguardar ação do parceiro",
        "changes_requested": "Alterações solicitadas",
        "in_review": "Em revisão",
        "approved": "Aprovado",
        "archived": "Arquivado (apenas consulta)",

        # Notificações
        "no_notifications": "Sem notificações",
        "unread_notifications": "notificações não lidas",
        "unread_notification": "notificação não lida",
        "mark_as_read": "Marcar como lida",
        "mark_all_read": "Marcar todas como lidas",
        "view_document": "Ver Documento",

        # KPIs
        "kpi_total": "Total Documentos",
        "kpi_approved": "Aprovados",
        "kpi_approval_rate": "Taxa Aprovação",
        "kpi_avg_review": "Tempo Médio Revisão",

        # Filtros
        "filters": "Filtros",
        "filter_search": "Pesquisar",
        "filter_status": "Estado",
        "filter_date_start": "Data Início",
        "filter_date_end": "Data Fim",
        "filter_order_by": "Ordenar por",
        "filter_order_dir": "Direção",
        "filter_order_asc": "Crescente",
        "filter_order_desc": "Decrescente",

        # Dashboard
        "dashboard_title": "Painel de Controlo",
        "recent_documents": "Documentos Recentes",
        "top_partners": "Top Parceiros",
        "documents_by_status": "Documentos por Estado",

        # Admin
        "admin_panel": "Painel Administrativo",
        "user_management": "Utilizadores",
        "manage_users": "Gerir Utilizadores",
        "new_user": "Novo Utilizador",
        "create_user": "Criar Utilizador",
        "edit_user": "Editar Utilizador",
        "change_password": "Alterar Palavra-passe",
        "new_password": "Nova Palavra-passe",
        "full_name": "Nome Completo",
        "profile": "Perfil",
        "user_exists": "Utilizador já existe",
        "cannot_delete_self": "Não pode eliminar a si próprio",

        # Comentários
        "comment": "Comentário",
        "comment_required": "É necessário um comentário para pedir alterações",

        # Placeholders
        "placeholder_search": "Título, parceiro ou ID...",
        "placeholder_title": "Título do documento",
        "placeholder_username": "Insira o utilizador",
        "placeholder_password": "Insira a palavra-passe",
        "placeholder_full_name": "Nome completo",
    }
}

def get_translation(key: str, lang: str = "en") -> str:
    """Obtém a tradução para uma chave específica."""
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang].get(key, key)

def get_language() -> str:
    """Obtém o idioma atual da sessão."""
    import streamlit as st
    if "language" not in st.session_state:
        st.session_state.language = "en"
    return st.session_state.language

def set_language(lang: str):
    """Define o idioma da sessão."""
    import streamlit as st
    if lang in TRANSLATIONS:
        st.session_state.language = lang

def t(key: str) -> str:
    """Função de atalho para obter tradução com o idioma atual."""
    return get_translation(key, get_language())

def get_language_options():
    """Retorna as opções de idioma disponíveis."""
    return ["en", "pt"]