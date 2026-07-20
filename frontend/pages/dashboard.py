# frontend/pages/dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Configuração da página
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS - sidebar 270px
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        min-width: 270px !important;
        width: 270px !important;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticação
if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Por favor, faça login primeiro.")
    st.stop()

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# Sidebar personalizada
with st.sidebar:
    st.write(f"Logado como: **{st.session_state.username}**")
    st.divider()
    
    if st.button("← Voltar", use_container_width=True, key="dashboard_sidebar_voltar"):
        st.switch_page("app.py")
    
    if st.button("Logout", key="dashboard_sidebar_logout"):
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
        st.rerun()

# Título
st.title("Dashboard")

# ---------- KPIs ----------
st.subheader("Indicadores Chave")

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Total Documentos",
                value=kpis.get("total_documentos", 0)
            )
        with col2:
            st.metric(
                label="Aprovados",
                value=kpis.get("aprovados", 0)
            )
        with col3:
            st.metric(
                label="Taxa Aprovação",
                value=f"{kpis.get('taxa_aprovacao', 0)}%"
            )
        with col4:
            st.metric(
                label="Tempo Médio Revisão",
                value=f"{kpis.get('tempo_medio_revisao', 0)} dias"
            )
        
        # Distribuição por estado (gráfico de pizza)
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            df_estados = pd.DataFrame({
                "Estado": list(estados.keys()),
                "Quantidade": list(estados.values())
            })
            
            fig_pizza = px.pie(
                df_estados,
                values="Quantidade",
                names="Estado",
                title="Distribuição de Documentos por Estado",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3
            )
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                fig_barras = px.bar(
                    df_estados,
                    x="Estado",
                    y="Quantidade",
                    title="Documentos por Estado (Barras)",
                    color="Estado",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_barras.update_layout(showlegend=False)
                st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.error("Erro ao carregar KPIs")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

# ---------- Documentos Recentes ----------
st.divider()
st.subheader("Documentos Recentes")

try:
    response = requests.get(f"{API_URL}/dashboard/documentos-recentes?limit=10", headers=headers_auth())
    if response.status_code == 200:
        dados = response.json()
        if dados:
            df_recentes = pd.DataFrame(dados)
            
            estado_cores = {
                "Rascunho": "#FFB74D",
                "Submetido": "#64B5F6",
                "Em Revisão": "#FFD54F",
                "Alterações": "#FF8A65",
                "Aprovado": "#81C784",
                "Arquivado": "#BDBDBD"
            }
            df_recentes["Cor"] = df_recentes["estado"].map(estado_cores)
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={
                    "id": "ID",
                    "titulo": "Título",
                    "estado": "Estado",
                    "parceiro_id": "Parceiro",
                    "created_at": "Criado em"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Sem documentos recentes")
    else:
        st.error("Erro ao carregar documentos recentes")
except Exception as e:
    st.error(f"Erro ao carregar documentos recentes: {e}")

# ---------- Top Parceiros ----------
if st.session_state.perfil != "parceiro":
    st.divider()
    st.subheader("Top Parceiros")
    
    try:
        response = requests.get(f"{API_URL}/dashboard/top-parceiros?limit=10", headers=headers_auth())
        if response.status_code == 200:
            dados = response.json()
            if dados:
                df_top = pd.DataFrame(dados)
                df_top = df_top.sort_values("total", ascending=True)
                
                fig_top = px.bar(
                    df_top,
                    x="total",
                    y="parceiro",
                    orientation='h',
                    title="Parceiros com Mais Documentos",
                    labels={"total": "Documentos", "parceiro": "Parceiro"},
                    color="total",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(
                    xaxis_title="Documentos",
                    yaxis_title="Parceiro",
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("Sem dados de top parceiros")
        else:
            st.error("Erro ao carregar top parceiros")
    except Exception as e:
        st.error(f"Erro ao carregar top parceiros: {e}")