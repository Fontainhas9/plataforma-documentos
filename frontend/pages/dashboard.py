import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="Dashboard",
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
                [data-testid="stSidebarNav"] { display: none !important; }
                .main > div { padding: 0 !important; max-width: 100% !important; }
                .block-container { padding: 0 !important; }
                body { background: #032949; color: #e8edf3; }
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

if st.session_state.perfil != "admin":
    st.error("Access denied. Only administrators can access the Dashboard.")
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

# ============================================================
# RENDER TOPBAR
# ============================================================
def render_topbar():
    username = st.session_state.get("username", "User")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    topbar_html = f'''
    <header class="dashboard-topbar">
        <div class="dashboard-topbar__inner">
            <h1 class="dashboard-topbar__title" onclick="window.location.href='?page=home'" style="cursor:pointer;">📄 DocPlatform</h1>
            <nav class="dashboard-topbar__nav">
                <a class="dashboard-topbar__link" onclick="window.location.href='?page=home'">Home</a>
                <a class="dashboard-topbar__link active" onclick="window.location.href='?page=dashboard'">Dashboard</a>
                <a class="dashboard-topbar__link" onclick="window.location.href='?page=notificacoes'">Notifications</a>
                <span style="color: rgba(255,255,255,0.1); padding: 0 4px;">|</span>
                <span class="user-name">{username}</span>
                <div class="notification-bell-wrapper" onclick="window.location.href='?page=notificacoes'">
                    <span class="bell-icon">🔔</span>
                    {f'<span class="badge">{notif_count}</span>' if notif_count > 0 else ''}
                </div>
                <div class="user-avatar">{username[0].upper() if username else 'U'}</div>
                <button class="logout-btn" onclick="window.location.href='?logout=true'">Logout</button>
            </nav>
        </div>
    </header>
    <div class="dashboard-shell">
    '''
    st.markdown(topbar_html, unsafe_allow_html=True)
    
    if st.query_params.get("page") == "home":
        st.switch_page("app.py")
    elif st.query_params.get("page") == "notificacoes":
        st.switch_page("pages/notificacoes.py")
    
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        from app import logout
        logout()
        st.rerun()

render_topbar()

# ============================================================
# DASHBOARD CONTENT
# ============================================================
st.title("Dashboard")
st.caption("Overview of all documents and partners.")

# ---------- KPIs ----------
st.subheader("Key Indicators")

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Documents", value=kpis.get("total_documentos", 0))
        with col2:
            st.metric(label="Approved", value=kpis.get("aprovados", 0))
        with col3:
            st.metric(label="Approval Rate", value=f"{kpis.get('taxa_aprovacao', 0)}%")
        
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            df_estados = pd.DataFrame({"Estado": list(estados.keys()), "Quantidade": list(estados.values())})
            
            fig_pizza = px.pie(df_estados, values="Quantidade", names="Estado", title="Document Distribution by Status", color_discrete_sequence=px.colors.qualitative.Set3, hole=0.3)
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_pizza, use_container_width=True)
            with col2:
                fig_barras = px.bar(df_estados, x="Estado", y="Quantidade", title="Documents by Status (Bar)", color="Estado", color_discrete_sequence=px.colors.qualitative.Set3)
                fig_barras.update_layout(showlegend=False)
                st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.error("Error loading KPIs")
except Exception as e:
    st.error(f"Error loading data: {e}")

# ---------- All Documents ----------
st.divider()
st.subheader("All Documents")

try:
    response = requests.get(f"{API_URL}/dashboard/documentos-recentes?limit=9999", headers=headers_auth())
    if response.status_code == 200:
        dados = response.json()
        if dados:
            df_recentes = pd.DataFrame(dados)
            estado_cores = {"Rascunho": "#FFB74D", "Submetido": "#64B5F6", "Em Revisão": "#FFD54F", "Alterações": "#FF8A65", "Aprovado": "#81C784", "Arquivado": "#BDBDBD"}
            df_recentes["Cor"] = df_recentes["estado"].map(estado_cores)
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={"id": "ID", "titulo": "Title", "estado": "Status", "parceiro_id": "Partner", "created_at": "Created At"},
                hide_index=True,
                use_container_width=True
            )
            st.caption(f"Total documents: {len(df_recentes)}")
        else:
            st.info("No documents in the platform")
    else:
        st.error("Error loading documents")
except Exception as e:
    st.error(f"Error loading documents: {e}")

# ---------- Top Partners ----------
st.divider()
st.subheader("Top Partners")

try:
    response = requests.get(f"{API_URL}/dashboard/top-parceiros?limit=10", headers=headers_auth())
    if response.status_code == 200:
        dados = response.json()
        if dados:
            df_top = pd.DataFrame(dados)
            df_top = df_top.sort_values("total", ascending=True)
            
            fig_top = px.bar(df_top, x="total", y="parceiro", orientation='h', title="Partners with Most Documents", labels={"total": "Documents", "parceiro": "Partner"}, color="total", color_continuous_scale="Blues")
            fig_top.update_layout(xaxis_title="Documents", yaxis_title="Partner", showlegend=False)
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No top partners data")
    else:
        st.error("Error loading top partners")
except Exception as e:
    st.error(f"Error loading top partners: {e}")

# ============================================================
# CLOSE DASHBOARD-SHELL DIV
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)