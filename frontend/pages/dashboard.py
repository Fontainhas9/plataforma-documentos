import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from traducoes import t

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

# Obter idioma
idioma = st.session_state.get('idioma', 'pt')

# Sidebar personalizada
with st.sidebar:
    st.write(f"{t('logged_as', idioma)} **{st.session_state.username}**")
    st.divider()
    
    if st.button(t("back", idioma), use_container_width=True, key="dashboard_sidebar_voltar"):
        st.switch_page("app.py")
    
    if st.button(t("logout", idioma), key="dashboard_sidebar_logout"):
        st.session_state.token = None
        st.session_state.perfil = None
        st.session_state.username = None
        st.session_state.doc_selecionado = None
        st.session_state.success_message = None
        st.session_state.menu_parceiro_widget = t("menu_documents", idioma)
        st.session_state.redirect_to_docs = False
        st.session_state.edit_data = None
        st.session_state.new_data = None
        st.session_state.refresh_counter = 0
        st.rerun()

# Título
st.title(t("dashboard_title", idioma))

# ---------- KPIs ----------
st.subheader(t("kpi", idioma))

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label=t("kpi_total", idioma),
                value=kpis.get("total_documentos", 0)
            )
        with col2:
            st.metric(
                label=t("kpi_approved", idioma),
                value=kpis.get("aprovados", 0)
            )
        with col3:
            st.metric(
                label=t("kpi_approval_rate", idioma),
                value=f"{kpis.get('taxa_aprovacao', 0)}%"
            )
        with col4:
            st.metric(
                label=t("kpi_avg_review", idioma),
                value=f"{kpis.get('tempo_medio_revisao', 0)} {t('kpi_days', idioma)}"
            )
        
        # Distribuição por estado (gráfico de pizza)
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            # Traduzir nomes dos estados
            estado_map = {
                "Rascunho": t("estado_rascunho", idioma),
                "Submetido": t("estado_submetido", idioma),
                "Em Revisão": t("estado_em_revisao", idioma),
                "Alterações": t("estado_alteracoes", idioma),
                "Aprovado": t("estado_aprovado", idioma),
                "Arquivado": t("estado_arquivado", idioma)
            }
            estados_traduzidos = {estado_map.get(k, k): v for k, v in estados.items()}
            
            df_estados = pd.DataFrame({
                t("document_state", idioma): list(estados_traduzidos.keys()),
                "Quantidade": list(estados_traduzidos.values())
            })
            
            fig_pizza = px.pie(
                df_estados,
                values="Quantidade",
                names=t("document_state", idioma),
                title=t("chart_distribution", idioma),
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
                    x=t("document_state", idioma),
                    y="Quantidade",
                    title=t("chart_bar", idioma),
                    color=t("document_state", idioma),
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
st.subheader(t("recent_docs", idioma))

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
            # Traduzir estados
            estado_map = {
                "Rascunho": t("estado_rascunho", idioma),
                "Submetido": t("estado_submetido", idioma),
                "Em Revisão": t("estado_em_revisao", idioma),
                "Alterações": t("estado_alteracoes", idioma),
                "Aprovado": t("estado_aprovado", idioma),
                "Arquivado": t("estado_arquivado", idioma)
            }
            df_recentes["estado"] = df_recentes["estado"].map(estado_map).fillna(df_recentes["estado"])
            df_recentes["Cor"] = df_recentes["estado"].map(estado_cores)
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={
                    "id": t("document_id", idioma),
                    "titulo": t("document_title", idioma),
                    "estado": t("document_state", idioma),
                    "parceiro_id": t("document_partner", idioma),
                    "created_at": t("document_created", idioma)
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(t("no_documents", idioma))
    else:
        st.error("Erro ao carregar documentos recentes")
except Exception as e:
    st.error(f"Erro ao carregar documentos recentes: {e}")

# ---------- Top Parceiros ----------
if st.session_state.perfil != "parceiro":
    st.divider()
    st.subheader(t("top_partners", idioma))
    
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
                    title=t("top_partners_title", idioma),
                    labels={"total": t("documents_title", idioma), "parceiro": t("document_partner", idioma)},
                    color="total",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(
                    xaxis_title=t("documents_title", idioma),
                    yaxis_title=t("document_partner", idioma),
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info(t("no_data", idioma))
        else:
            st.error("Erro ao carregar top parceiros")
    except Exception as e:
        st.error(f"Erro ao carregar top parceiros: {e}")