# frontend/components/header.py
import streamlit as st

def render_header():
    """
    Renderiza o header fixo no topo com logo, navegação e perfil do utilizador.
    """
    # Buscar informações do utilizador
    username = st.session_state.get("username", "User")
    perfil = st.session_state.get("perfil", "")
    
    # Contar notificações não lidas
    from componentes.notificacoes import get_notificacoes_nao_lidas
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    # Determinar link ativo
    current_page = st.query_params.get("page", "home")
    
    # CSS do header
    st.markdown("""
    <style>
    .main-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(10, 10, 26, 0.92);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 0 2rem;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        text-decoration: none;
        cursor: pointer;
    }
    .header-logo .logo-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: white;
    }
    .header-nav {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .header-nav a {
        color: #a0a0b8;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        background: transparent;
        border: none;
        font-family: inherit;
    }
    .header-nav a:hover {
        color: #ffffff;
        background: rgba(255,255,255,0.06);
    }
    .header-nav a.active {
        color: #ffffff;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.15) 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
    }
    .header-nav .nav-divider {
        width: 1px;
        height: 24px;
        background: rgba(255,255,255,0.06);
        margin: 0 8px;
    }
    .header-user {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .header-user .user-name {
        color: #e8e8e8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .header-user .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ffffff;
    }
    .header-user .notification-bell {
        position: relative;
        cursor: pointer;
        font-size: 1.2rem;
        color: #a0a0b8;
        transition: color 0.3s ease;
        background: none;
        border: none;
    }
    .header-user .notification-bell:hover {
        color: #ffffff;
    }
    .header-user .notification-bell .badge {
        position: absolute;
        top: -6px;
        right: -8px;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 9px;
        font-weight: 700;
        min-width: 18px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(238, 90, 36, 0.4);
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    .header-user .logout-btn {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        color: #a0a0b8 !important;
        padding: 6px 14px !important;
        font-size: 0.85rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        font-family: inherit !important;
    }
    .header-user .logout-btn:hover {
        color: #ffffff !important;
        background: rgba(255,255,255,0.10) !important;
    }
    .main-content {
        margin-top: 80px;
        padding: 0 2rem 2rem 2rem;
        max-width: 1440px;
        margin-left: auto;
        margin-right: auto;
    }
    /* Remove default sidebar */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .main > div { padding: 0 !important; max-width: 100% !important; }
    .block-container { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Montar o HTML do header
    perfil_display = "👤" if not perfil else perfil.capitalize()
    
    # Determinar links ativos
    is_home = "home" in str(st.query_params.get("page", "home")) or not st.query_params.get("page")
    is_dashboard = st.query_params.get("page") == "dashboard"
    is_notifications = st.query_params.get("page") == "notificacoes"
    
    # HTML do header
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
                🔔
                {'<span class="badge">{}</span>'.format(notif_count) if notif_count > 0 else ''}
            </button>
            <div class="user-avatar">{username[0].upper() if username else 'U'}</div>
            <button class="logout-btn" onclick="window.location.href='?logout=true'">Logout</button>
        </div>
    </header>
    <div class="main-content">
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Processar logout
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        from app import logout
        logout()
        st.rerun()
    
    # Processar navegação
    if st.query_params.get("page") == "dashboard":
        st.switch_page("pages/dashboard.py")
    elif st.query_params.get("page") == "notificacoes":
        st.switch_page("pages/notificacoes.py")
    
    # Retornar o username para uso no resto da página
    return username