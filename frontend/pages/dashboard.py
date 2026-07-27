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
    """Renders the topbar with navigation and user info."""
    username = st.session_state.get("username", "User")
    perfil = st.session_state.get("perfil", "")
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    current_page = st.query_params.get("page", "dashboard")
    is_home = current_page == "home"
    is_dashboard = current_page in ["dashboard", ""] or current_page is None
    is_notifications = current_page == "notificacoes"
    
    home_hidden = 'hidden' if is_home else ''
    dashboard_hidden = 'hidden' if is_dashboard else ''
    notifications_hidden = 'hidden' if is_notifications else ''
    
    notif_display = f'{notif_count}' if notif_count > 0 else ''
    
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
                <a class="dashboard-topbar__link {dashboard_hidden}" href="?page=dashboard">Dashboard</a>
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
    
    page = st.query_params.get("page", "dashboard")
    if page == "home":
        st.switch_page("app.py")
    elif page == "notificacoes":
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
# CLOSE MAIN CONTENT
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)