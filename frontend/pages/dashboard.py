import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_text, get_language, get_api_url, headers_auth

API_URL = get_api_url()

# Configuração da página
st.set_page_config(
    page_title=get_text("dashboard"),
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
    st.warning(get_text("please_login_first"))
    st.stop()

# Sidebar personalizada
with st.sidebar:
    st.write(f"{get_text('logged_as')} **{st.session_state.username}**")
    st.divider()
    
    if st.button(get_text("back"), use_container_width=True, key="dashboard_sidebar_voltar"):
        st.switch_page("app.py")
    
    if st.button(get_text("logout"), key="dashboard_sidebar_logout"):
        st.session_state.token = None
        st.session_state.perfil = None
        st.session_state.username = None
        st.session_state.doc_selecionado = None
        st.session_state.success_message = None
        st.session_state.menu_parceiro_widget = get_text("my_documents")
        st.session_state.redirect_to_docs = False
        st.session_state.edit_data = None
        st.session_state.new_data = None
        st.session_state.refresh_counter = 0
        st.rerun()

# Título
st.title(get_text("dashboard"))

# ---------- KPIs ----------
st.subheader(get_text("key_indicators"))

try:
    response = requests.get(f"{API_URL}/dashboard/kpis", headers=headers_auth())
    if response.status_code == 200:
        kpis = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label=get_text("total_documents"),
                value=kpis.get("total_documentos", 0)
            )
        with col2:
            st.metric(
                label=get_text("approved"),
                value=kpis.get("aprovados", 0)
            )
        with col3:
            st.metric(
                label=get_text("approval_rate"),
                value=f"{kpis.get('taxa_aprovacao', 0)}%"
            )
        with col4:
            st.metric(
                label=get_text("avg_review_time"),
                value=f"{kpis.get('tempo_medio_revisao', 0)} {get_text('days')}"
            )
        
        # Distribuição por estado (gráfico de pizza)
        estados = kpis.get("documentos_por_estado", {})
        if estados and sum(estados.values()) > 0:
            # Traduzir os estados para o idioma atual
            estados_traduzidos = {}
            for estado, valor in estados.items():
                estados_traduzidos[get_text(estado, estado)] = valor
            
            df_estados = pd.DataFrame({
                get_text("state"): list(estados_traduzidos.keys()),
                "Quantidade": list(estados_traduzidos.values())
            })
            
            fig_pizza = px.pie(
                df_estados,
                values="Quantidade",
                names=get_text("state"),
                title=get_text("documents_by_status"),
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
                    x=get_text("state"),
                    y="Quantidade",
                    title=get_text("documents_by_status"),
                    color=get_text("state"),
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_barras.update_layout(showlegend=False)
                st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.error(get_text("error"))

except Exception as e:
    st.error(f"{get_text('error')}: {e}")

# ---------- Documentos Recentes ----------
st.divider()
st.subheader(get_text("recent_documents"))

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
            
            # Traduzir estados
            df_recentes["estado"] = df_recentes["estado"].apply(lambda x: get_text(x, x))
            
            st.dataframe(
                df_recentes[["id", "titulo", "estado", "parceiro_id", "created_at"]],
                column_config={
                    "id": get_text("id"),
                    "titulo": get_text("title"),
                    "estado": get_text("state"),
                    "parceiro_id": get_text("partner"),
                    "created_at": get_text("created_at_table")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(get_text("no_recent_documents"))
    else:
        st.error(get_text("error"))
except Exception as e:
    st.error(f"{get_text('error')}: {e}")

# ---------- Top Parceiros ----------
if st.session_state.perfil != "parceiro":
    st.divider()
    st.subheader(get_text("top_partners"))
    
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
                    title=get_text("partner_documents"),
                    labels={"total": get_text("total_documents"), "parceiro": get_text("partner")},
                    color="total",
                    color_continuous_scale="Blues"
                )
                fig_top.update_layout(
                    xaxis_title=get_text("total_documents"),
                    yaxis_title=get_text("partner"),
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info(get_text("no_top_partners"))
        else:
            st.error(get_text("error"))
    except Exception as e:
        st.error(f"{get_text('error')}: {e}")