import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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

# ============================================================
# TRADUÇÕES (copiadas do app.py para o dashboard)
# ============================================================
TRADUCOES = {
    "pt": {
        "app_title": "Dashboard",
        "logout": "Sair",
        "back": "← Voltar",
        "logged_as": "Logado como:",
        "kpi_total": "Total Documentos",
        "kpi_approved": "Aprovados",
        "kpi_approval_rate": "Taxa Aprovação",
        "kpi_avg_review_time": "Tempo Médio Revisão",
        "distribution_by_state": "Distribuição de Documentos por Estado",
        "docs_by_state_bar": "Documentos por Estado (Barras)",
        "recent_documents": "Documentos Recentes",
        "top_partners": "Top Parceiros",
        "partners_with_more_docs": "Parceiros com Mais Documentos",
        "no_recent_docs": "Sem documentos recentes",
        "no_top_partners": "Sem dados de top parceiros",
        "no_documents": "Nenhum documento encontrado.",
        "status_draft": "Rascunho",
        "status_submitted": "Submetido",
        "status_review": "Em Revisão",
        "status_changes": "Alterações",
        "status_approved": "Aprovado",
        "status_archived": "Arquivado",
        "id": "ID",
        "title": "Título",
        "status": "Estado",
        "partner": "Parceiro",
        "created_at": "Criado em",
        "no_data": "Sem dados disponíveis"
    },
    "en": {
        "app_title": "Dashboard",
        "logout": "Logout",
        "back": "← Back",
        "logged_as": "Logged as:",
        "kpi_total": "Total Documents",
        "kpi_approved": "Approved",
        "kpi_approval_rate": "Approval Rate",
        "kpi_avg_review_time": "Avg Review Time",
        "distribution_by_state": "Document Distribution by Status",
        "docs_by_state_bar": "Documents by Status (Bar)",
        "recent_documents": "Recent Documents",
        "top_partners": "Top Partners",
        "partners_with_more_docs": "Partners with Most Documents",
        "no_recent_docs": "No recent documents",
        "no_top_partners": "No top partners data",
        "no_documents": "No documents found.",
        "status_draft": "Draft",
        "status_submitted": "Submitted",
        "status_review": "In Review",
        "status_changes": "Changes",
        "status_approved": "Approved",
        "status_archived": "Archived",
        "id": "ID",
        "title": "Title",
        "status": "Status",
        "partner": "Partner",
        "created_at": "Created At",
        "no_data": "No data available"
    }
}

def t(key: str, **kwargs) -> str:
    """Retorna a tradução para a chave com formatação."""
    lang = st.session_state.get("idioma", "pt")
    texto = TRADUCOES.get(lang, TRADUCOES["pt"]).get(key, key)
    if kwargs:
        try:
            return texto.format(**kwargs)
        except KeyError:
            return texto
    return texto

# Configuração da página
st.set_page_config(
    page_title=t("app_title"),
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
    st.write(f"{t('logged_as')} **{st.session_state.username}**")
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
        st.session_state.redirect_to_docs = False
        st.session_state.edit_data = None
        st.session_state.new_data = None
        st.session_state.refresh_counter = 0
        st.rerun()

# Título
st.title(t("app_title"))

# ---------- KPIs ----------
st.subheader(t("kpi_total") + " / " + t("kpi_approved"))

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        # Mapeamento de estados para tradução
        estado_map = {
            "Rascunho": t("status_draft"),
            "Submetido": t("status_submitted"),
            "Em Revisão": t("status_review"),
            "Alterações": t("status_changes"),
            "Aprovado": t("status_approved"),
            "Arquivado": t("status_archived")
        }
        
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
            st.metric(
                label=t("kpi_avg_review_time"),
                value=f"{kpis.get('tempo_medio_revisao', 0)} dias"
            )
        
        # Distribuição por estado (gráfico de pizza)
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            # Traduzir os estados para o gráfico
            estados_traduzidos = {}
            for k, v in estados.items():
                estados_traduzidos[estado_map.get(k, k)] = v
            
            df_estados = pd.DataFrame({
                t("status"): list(estados_traduzidos.keys()),
                "Quantidade": list(estados_traduzidos.values())
            })
            
            fig_pizza = px.pie(
                df_estados,
                values="Quantidade",
                names=t("status"),
                title=t("distribution_by_state"),
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
                    x=t("status"),
                    y="Quantidade",
                    title=t("docs_by_state_bar"),
                    color=t("status"),
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
st.subheader(t("recent_documents"))

try:
    response = requests.get(f"{API_URL}/dashboard/documentos-recentes?limit=10", headers=headers_auth())
    if response.status_code == 200:
        dados = response.json()
        if dados:
            df_recentes = pd.DataFrame(dados)
            
            # Traduzir estados
            estado_map = {
                "Rascunho": t("status_draft"),
                "Submetido": t("status_submitted"),
                "Em Revisão": t("status_review"),
                "Alterações": t("status_changes"),
                "Aprovado": t("status_approved"),
                "Arquivado": t("status_archived")
            }
            df_recentes["estado"] = df_recentes["estado"].map(estado_map).fillna(df_recentes["estado"])
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={
                    "id": t("id"),
                    "titulo": t("title"),
                    "estado": t("status"),
                    "parceiro_id": t("partner"),
                    "created_at": t("created_at")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(t("no_recent_docs"))
    else:
        st.error("Erro ao carregar documentos recentes")
except Exception as e:
    st.error(f"Erro ao carregar documentos recentes: {e}")

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
                    title=t("partners_with_more_docs"),
                    labels={"total": t("kpi_total"), "parceiro": t("partner")},
                    color="total",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(
                    xaxis_title=t("kpi_total"),
                    yaxis_title=t("partner"),
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info(t("no_top_partners"))
        else:
            st.error("Erro ao carregar top parceiros")
    except Exception as e:
        st.error(f"Erro ao carregar top parceiros: {e}")