# frontend/pages/dashboard.py (modificado)
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Importar módulo de tradução
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.translations import t, get_language, set_language

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
    page_title=t("dashboard_title"),
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
    st.warning(t("login_required"))
    st.stop()

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# Sidebar personalizada
with st.sidebar:
    st.write(f"{t('logged_as')}: **{st.session_state.username}**")
    st.divider()
    
    if st.button(t("back"), use_container_width=True, key="dashboard_sidebar_voltar"):
        st.switch_page("app.py")
    
    if st.button(t("logout"), key="dashboard_sidebar_logout"):
        st.session_state.token = None
        st.session_state.perfil = None
        st.session_state.username = None
        st.session_state.doc_selecionado = None
        st.session_state.success_message = None
        st.session_state.menu_parceiro_widget = "Meus Documentos"
        st.session_state.redirect_to_docs = False        st.session_state.edit_data = None
        st.session_state.new_data = None
        st.session_state.refresh_counter = 0
        st.rerun()

# Título
st.title(t("dashboard_title"))

# ---------- KPIs ----------
st.subheader(t("kpi_title"))

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label=t("kpi_total"),
                value=kpis.get("total_documentos", 0)
            )
        with col2:
            st.metric(
                label=t("kpi_approved"),
                value=kpis.get("aprovados", 0)
            )
        with col3:
            st.metric(
                label=t("kpi_approval_rate"),
                value=f"{kpis.get('taxa_aprovacao', 0)}%"
            )
        with col4:
            # Ajustar para dias se disponível
            avg_time = kpis.get("tempo_medio_revisao", 0)
            st.metric(
                label=t("kpi_avg_review"),
                value=f"{avg_time} {t('days') if avg_time != 1 else t('day')}"
            )
        
        # Distribuição por estado (gráfico de pizza)
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            estado_labels = {
                "Rascunho": t("doc_state_draft"),
                "Submetido": t("doc_state_submitted"),
                "Em Revisão": t("doc_state_review"),
                "Alterações": t("doc_state_changes"),
                "Aprovado": t("doc_state_approved"),
                "Arquivado": t("doc_state_archived")
            }
            df_estados = pd.DataFrame({
                "Estado": [estado_labels.get(k, k) for k in estados.keys()],
                "Quantidade": list(estados.values())
            })
            
            fig_pizza = px.pie(
                df_estados,
                values="Quantidade",
                names="Estado",
                title=t("documents_by_status"),
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
                    title=t("documents_by_status"),
                    color="Estado",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_barras.update_layout(showlegend=False)
                st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.error(t("kpi_error"))

except Exception as e:
    st.error(f"{t('kpi_error')}: {e}")

# ---------- Documentos Recentes ----------
st.divider()
st.subheader(t("recent_documents"))

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
            
            estado_labels = {
                "Rascunho": t("doc_state_draft"),
                "Submetido": t("doc_state_submitted"),
                "Em Revisão": t("doc_state_review"),
                "Alterações": t("doc_state_changes"),
                "Aprovado": t("doc_state_approved"),
                "Arquivado": t("doc_state_archived")
            }
            df_recentes["estado"] = df_recentes["estado"].map(lambda x: estado_labels.get(x, x))
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={
                    "id": t("doc_id"),
                    "titulo": t("doc_title"),
                    "estado": t("doc_status"),
                    "parceiro_id": t("doc_partner"),
                    "created_at": t("doc_created_at")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(t("no_data"))
    else:
        st.error(t("recent_docs_error"))
except Exception as e:
    st.error(f"{t('recent_docs_error')}: {e}")

# ---------- Top Parceiros ----------
if st.session_state.perfil != "parceiro":
    st.divider()
    st.subheader(t("top_partners"))
    
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
                    title=t("top_partners"),
                    labels={"total": t("documents"), "parceiro": t("doc_partner")},
                    color="total",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(
                    xaxis_title=t("documents"),
                    yaxis_title=t("doc_partner"),
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info(t("no_data"))
        else:
            st.error(t("top_partners_error"))
    except Exception as e:
        st.error(f"{t('top_partners_error')}: {e}")