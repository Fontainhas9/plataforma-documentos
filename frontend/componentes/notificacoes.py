import streamlit as st
import requests
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

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_notificacoes_nao_lidas():
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception as e:
        print(f"Error getting notifications: {e}")
    return 0

def render_notificacoes_badge():
    if st.session_state.token is None:
        return
    
    count = get_notificacoes_nao_lidas()
    
    if count > 0:
        st.markdown(f"""
        <div style="position:fixed;top:10px;right:100px;z-index:999;cursor:pointer;display:flex;align-items:center;gap:5px;"
             onclick="window.location.href='?page=notificacoes'">
            <span style="font-size:24px;">🔔</span>
            <span style="background:#ff4444;color:white;border-radius:50%;padding:2px 8px;font-size:12px;font-weight:bold;min-width:20px;text-align:center;animation:pulse 1s infinite;">
                {count}
            </span>
        </div>
        <style>
            @keyframes pulse {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.1); }} }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="position:fixed;top:10px;right:100px;z-index:999;cursor:pointer;display:flex;align-items:center;gap:5px;"
             onclick="window.location.href='?page=notificacoes'">
            <span style="font-size:24px;">🔔</span>
            <span style="color:#888;border-radius:50%;padding:2px 8px;font-size:12px;min-width:20px;text-align:center;">0</span>
        </div>
        """, unsafe_allow_html=True)
    
    if "page" in st.query_params and st.query_params["page"] == "notificacoes":
        st.switch_page("pages/notificacoes.py")