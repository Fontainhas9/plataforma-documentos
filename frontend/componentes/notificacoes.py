import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_notificacoes_nao_lidas():
    """Obtém o número de notificações não lidas."""
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception as e:
        print(f"Erro ao obter notificações: {e}")
    return 0

def render_notificacoes_badge():
    """
    Renderiza o badge de notificações no canto superior direito.
    """
    # Verificar se o token existe
    if st.session_state.token is None:
        return
    
    count = get_notificacoes_nao_lidas()
    
    # CSS para posicionar o badge
    st.markdown("""
    <style>
    .notification-badge {
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 999;
        cursor: pointer;
        font-size: 28px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .notification-badge .badge {
        background: #ff4444;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: bold;
        min-width: 20px;
        text-align: center;
        animation: pulse 1s infinite;
    }
    .notification-badge .badge-zero {
        background: transparent;
        color: #888;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 12px;
        min-width: 20px;
        text-align: center;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .notification-badge:hover {
        opacity: 0.8;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Badge HTML com botão de refresh
    if count > 0:
        badge_html = f"""
        <div class="notification-badge">
            <span onclick="window.location.href='?page=notificacoes'" style="cursor:pointer;">
                🔔
                <span class="badge">{count}</span>
            </span>
            <span onclick="window.location.href='?refresh_notifications=true'" 
                  style="cursor:pointer; font-size:14px; color:#666; background:#f0f0f0; padding:2px 8px; border-radius:4px; margin-left:5px;">
                🔄
            </span>
        </div>
        """
    else:
        badge_html = f"""
        <div class="notification-badge">
            <span onclick="window.location.href='?page=notificacoes'" style="cursor:pointer;">
                🔔
                <span class="badge-zero">0</span>
            </span>
            <span onclick="window.location.href='?refresh_notifications=true'" 
                  style="cursor:pointer; font-size:14px; color:#666; background:#f0f0f0; padding:2px 8px; border-radius:4px; margin-left:5px;">
                🔄
            </span>
        </div>
        """
    
    st.markdown(badge_html, unsafe_allow_html=True)
    
    # Verificar se clicou no badge (via query param)
    if "page" in st.query_params and st.query_params["page"] == "notificacoes":
        st.switch_page("pages/notificacoes.py")
    
    # Verificar se clicou no refresh
    if "refresh_notifications" in st.query_params:
        st.query_params.clear()
        st.rerun()