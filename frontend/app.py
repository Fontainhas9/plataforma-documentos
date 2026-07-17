# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import copy
from datetime import datetime
import os
import json

# ============================================================
# IMPORTAR TRADUÇÕES
# ============================================================
from translations import (
    get_text, get_language, set_language, get_api_url, 
    get_datasource_options, translate_estado, translate_perfil,
    load_translations
)

API_URL = get_api_url()

# ============================================================
# FUNÇÃO PARA FORMATAR DATA/HORA
# ============================================================
def formatar_data_hora(data_str):
    """Converte uma string de data/hora para formato DD/MM/AAAA HH:MM."""
    if not data_str:
        return ""
    try:
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y %H:%M")
        
        data_str = str(data_str)
        data_str = data_str.replace('Z', '').replace('T', ' ')
        
        formatos = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d"
        ]
        
        for fmt in formatos:
            try:
                dt = datetime.strptime(data_str, fmt)
                return dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        
        return data_str
    except Exception:
        return str(data_str)

# Carregar traduções
if "translations" not in st.session_state:
    st.session_state.translations = load_translations()

PROCESSOS = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = get_datasource_options()

# Configuração da página
st.set_page_config(
    page_title=get_text("app_title"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar componente de notificações
from componentes.notificacoes import render_notificacoes_badge, get_notificacoes_nao_lidas

# ============================================================
# SELETOR DE IDIOMA NO TOPO DA PÁGINA
# ============================================================
def render_language_selector():
    """Renderiza o seletor de idioma."""
    st.markdown("""
    <style>
    .language-selector {
        position: fixed;
        top: 10px;
        right: 120px;
        z-index: 1000;
        display: flex;
        gap: 8px;
        background: white;
        padding: 4px 8px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .lang-btn {
        padding: 4px 10px;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
        background: transparent;
        color: #666;
    }
    .lang-btn:hover {
        background: #f0f0f0;
    }
    .lang-btn.active {
        background: #1a73e8;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🇵🇹 PT", key="lang_pt", use_container_width=True):
            set_language("pt")
    
    with col2:
        if st.button("🇬🇧 EN", key="lang_en", use_container_width=True):
            set_language("en")

# ============================================================
# CSS e JavaScript para scroll automático - SIDEBAR 270px
# ============================================================
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        min-width: 270px !important;
        max-width: 270px !important;
        overflow: auto !important;
        pointer-events: auto !important;
    }
    .main > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    html {
        scroll-behavior: smooth;
    }
    .doc-anchor {
        display: block;
        position: relative;
        top: -80px;
        visibility: hidden;
        height: 0;
    }
</style>

<script>
    function checkScrollParam() {
        var urlParams = new URLSearchParams(window.location.search);
        var docId = urlParams.get('scroll_to');
        if (docId) {
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 400);
            setTimeout(function() {
                var element = document.getElementById('doc-' + docId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 800);
            setTimeout(function() {
                urlParams.delete('scroll_to');
                var newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState({}, '', newUrl);
            }, 1000);
        }
    }
    
    window.addEventListener('load', function() {
        setTimeout(checkScrollParam, 200);
    });
    
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(checkScrollParam, 300);
    });
</script>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if "token" not in st.session_state:
    st.session_state.token = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "username" not in st.session_state:
    st.session_state.username = None
if "doc_selecionado" not in st.session_state:
    st.session_state.doc_selecionado = None
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "menu_parceiro_widget" not in st.session_state:
    st.session_state.menu_parceiro_widget = get_text("my_documents")
if "redirect_to_docs" not in st.session_state:
    st.session_state.redirect_to_docs = False
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None
if "new_data" not in st.session_state:
    st.session_state.new_data = None
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0
if "pw_input_counter" not in st.session_state:
    st.session_state.pw_input_counter = 0
if "parceiro_dropdown_key" not in st.session_state:
    st.session_state.parceiro_dropdown_key = 0
if "empresa_dropdown_key" not in st.session_state:
    st.session_state.empresa_dropdown_key = 0
if "admin_dropdown_key" not in st.session_state:
    st.session_state.admin_dropdown_key = 0
if "admin_user_dropdown_key" not in st.session_state:
    st.session_state.admin_user_dropdown_key = 0
if "ultimo_count" not in st.session_state:
    st.session_state.ultimo_count = 0
if "show_create_user_form" not in st.session_state:
    st.session_state.show_create_user_form = False
if "close_doc_after_action" not in st.session_state:
    st.session_state.close_doc_after_action = False

if "filtros_widget_key" not in st.session_state:
    st.session_state.filtros_widget_key = 0

if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "q": "",
        "estados": [],
        "data_inicio": None,
        "data_fim": None,
        "order_by": "id",
        "order_dir": "desc"
    }

if "filtros_temporarios" not in st.session_state:
    st.session_state.filtros_temporarios = {
        "q": "",
        "estados": [],
        "data_inicio": None,
        "data_fim": None,
        "order_by": "id",
        "order_dir": "desc"
    }

# ---------- Funções auxiliares ----------
def safe_copy(data):
    return copy.deepcopy(data)

def ensure_new_structure(data):
    if not data:
        return {
            "lca": {
                "inputs": {p: [] for p in PROCESSOS},
                "processes": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            },
            "lcc": {
                "materials": {p: [] for p in PROCESSOS},
                "equipment": {p: [] for p in PROCESSOS},
                "labour": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            }
        }

    if "lca" in data and "lcc" in data:
        if all(p in data["lca"].get("inputs", {}) for p in PROCESSOS):
            for secao in ["lca", "lcc"]:
                for categoria in data[secao].keys():
                    for p in PROCESSOS:
                        if p not in data[secao][categoria]:
                            data[secao][categoria][p] = []
            return data

    new_data = {
        "lca": {
            "inputs": {p: [] for p in PROCESSOS},
            "processes": {p: [] for p in PROCESSOS},
            "outputs": {p: [] for p in PROCESSOS}
        },
        "lcc": {
            "materials": {p: [] for p in PROCESSOS},
            "equipment": {p: [] for p in PROCESSOS},
            "labour": {p: [] for p in PROCESSOS},
            "outputs": {p: [] for p in PROCESSOS}
        }
    }

    if "lca" in data:
        old_lca = data["lca"]
        if "inputs" in old_lca and isinstance(old_lca["inputs"], list):
            new_data["lca"]["inputs"]["Demagnetisation"] = old_lca["inputs"]
        if "processes" in old_lca and isinstance(old_lca["processes"], list):
            new_data["lca"]["processes"]["Demagnetisation"] = old_lca["processes"]
        if "outputs" in old_lca and isinstance(old_lca["outputs"], list):
            new_data["lca"]["outputs"]["Demagnetisation"] = old_lca["outputs"]
    if "lcc" in data:
        old_lcc = data["lcc"]
        if "materials" in old_lcc and isinstance(old_lcc["materials"], list):
            new_data["lcc"]["materials"]["Demagnetisation"] = old_lcc["materials"]
        if "equipment" in old_lcc and isinstance(old_lcc["equipment"], list):
            new_data["lcc"]["equipment"]["Demagnetisation"] = old_lcc["equipment"]
        if "labour" in old_lcc and isinstance(old_lcc["labour"], list):
            new_data["lcc"]["labour"]["Demagnetisation"] = old_lcc["labour"]
        if "outputs" in old_lcc and isinstance(old_lcc["outputs"], list):
            new_data["lcc"]["outputs"]["Demagnetisation"] = old_lcc["outputs"]

    return new_data

# ---------- Funções da API ----------
def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def login(username, password):
    resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
    if resp.status_code == 200:
        dados = resp.json()
        st.session_state.token = dados["access_token"]
        headers = {"Authorization": f"Bearer {dados['access_token']}"}
        me = requests.get(f"{API_URL}/me", headers=headers)
        if me.status_code == 200:
            user_info = me.json()
            st.session_state.perfil = user_info["perfil"]
            st.session_state.username = user_info["username"]
        return True
    else:
        st.error(get_text("invalid_credentials"))
        return False

def logout():
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
    st.session_state.ultimo_count = 0

def listar_documentos(estado=None):
    params = {}
    if estado:
        params["estado"] = estado
    resp = requests.get(f"{API_URL}/documentos", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def listar_documentos_com_filtros(filtros):
    params = {}
    
    if filtros.get("q"):
        params["q"] = filtros["q"]
    
    if filtros.get("estados"):
        params["estados"] = ",".join(filtros["estados"])
    
    if filtros.get("data_inicio"):
        params["data_inicio"] = filtros["data_inicio"]
    
    if filtros.get("data_fim"):
        params["data_fim"] = filtros["data_fim"]
    
    if filtros.get("order_by"):
        params["order_by"] = filtros["order_by"]
    
    if filtros.get("order_dir"):
        params["order_dir"] = filtros["order_dir"]
    
    resp = requests.get(f"{API_URL}/documentos/pesquisar", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def criar_documento(titulo, dados):
    resp = requests.post(
        f"{API_URL}/documentos/",
        json={"titulo": titulo, "parceiro_id": st.session_state.username, "dados": dados},
        headers=headers_auth()
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"{get_text('error_creating_document')}: {resp.text}")
        return None

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"{get_text('error_loading_document')}: {resp.text}")
        return None

def editar_documento(doc_id, dados):
    resp = requests.put(
        f"{API_URL}/documentos/{doc_id}/editar",
        json={"dados": dados},
        headers=headers_auth()
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"{get_text('error_editing')}: {resp.text}")
        return None

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error_submitting')}: {resp.text}")
        return None
    st.success(get_text("document_submitted"))
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error')}: {resp.text}")
        return None
    st.success(get_text("review_started"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(
        f"{API_URL}/documentos/{doc_id}/pedir-alteracoes",
        json={"comentario": comentario},
        headers=headers_auth()
    )
    if resp.status_code != 200:
        st.error(f"{get_text('error')}: {resp.text}")
        return None
    st.success(get_text("changes_requested"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error')}: {resp.text}")
        return None
    st.success(get_text("document_reopened_edit"))
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error_approving')}: {resp.text}")
        return None
    st.success(get_text("document_approved"))
    st.session_state.doc_selecionado = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error_reopening')}: {resp.text}")
        return None
    st.success(get_text("document_reopened"))
    st.session_state.doc_selecionado = doc_id
    st.rerun()
    return resp.json()

def arquivar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/arquivar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"{get_text('error_archiving')}: {resp.text}")
        return None
    st.success(get_text("document_archived"))
    st.session_state.doc_selecionado = None
    st.session_state.close_doc_after_action = True
    st.rerun()
    return resp.json()

def listar_versoes(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/versoes", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    return []

def exportar_excel(doc_id, titulo):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/exportar-excel", headers=headers_auth())
    if resp.status_code == 200:
        content = resp.content
        filename = f"{titulo}.xlsx"
        filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
        return content, filename
    else:
        try:
            erro = resp.json().get("detail", "Erro desconhecido")
        except:
            erro = get_text("error_exporting")
        st.error(f"{get_text('error_exporting')}: {erro}")
        return None, None

def verificar_novas_notificacoes():
    if st.session_state.token is None:
        return
    
    try:
        count = get_notificacoes_nao_lidas()
        if count > st.session_state.ultimo_count:
            st.toast(f"🔔 {count - st.session_state.ultimo_count} {get_text('unread_notifications')}!", icon="🔔")
        st.session_state.ultimo_count = count
    except:
        pass

# ---------- Função para resumo ----------
def show_document_summary(documentos):
    if not documentos:
        st.info(get_text("no_documents"))
        return

    estados = ["Rascunho", "Submetido", "Em Revisão", "Alterações", "Aprovado", "Arquivado"]
    contagens = {estado: 0 for estado in estados}
    for doc in documentos:
        estado = doc.get("estado")
        if estado in contagens:
            contagens[estado] += 1

    cols = st.columns(len(estados))
    for i, estado in enumerate(estados):
        with cols[i]:
            st.metric(label=get_text(estado, estado), value=contagens[estado])

# ---------- Função para exibir dataframes ----------
def display_dataframe(df):
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [col.title() for col in df.columns]
        df = df.reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("(sem dados)")

# ---------- Componente de filtros ----------
def render_filtros():
    with st.expander(get_text("filters"), expanded=False):
        col1, col2 = st.columns(2)
        key_suffix = st.session_state.filtros_widget_key
        
        with col1:
            q = st.text_input(
                get_text("search"),
                value=st.session_state.filtros_temporarios.get("q", ""),
                placeholder=get_text("search_placeholder"),
                key=f"filtro_q_{key_suffix}"
            )
            st.session_state.filtros_temporarios["q"] = q
            
            estados_disponiveis = ["Rascunho", "Submetido", "Em Revisão", "Alterações", "Aprovado", "Arquivado"]
            estados_selecionados = st.multiselect(
                get_text("status"),
                options=estados_disponiveis,
                default=st.session_state.filtros_temporarios.get("estados", []),
                format_func=lambda x: get_text(x, x),
                key=f"filtro_estados_{key_suffix}"
            )
            st.session_state.filtros_temporarios["estados"] = estados_selecionados
        
        with col2:
            data_inicio = st.date_input(
                get_text("start_date"),
                value=st.session_state.filtros_temporarios.get("data_inicio"),
                format="DD/MM/YYYY",
                key=f"filtro_data_inicio_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
            
            data_fim = st.date_input(
                get_text("end_date"),
                value=st.session_state.filtros_temporarios.get("data_fim"),
                format="DD/MM/YYYY",
                key=f"filtro_data_fim_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
        
        col3, col4 = st.columns(2)
        with col3:
            ordem_campos = {
                "id": "ID",
                "titulo": get_text("title"),
                "parceiro_id": get_text("partner"),
                "estado": get_text("state"),
                "created_at": get_text("created_at"),
                "updated_at": get_text("updated_at"),
                "versao_atual": get_text("version")
            }
            order_by = st.selectbox(
                get_text("order_by"),
                options=list(ordem_campos.keys()),
                format_func=lambda x: ordem_campos.get(x, x),
                index=list(ordem_campos.keys()).index(st.session_state.filtros_temporarios.get("order_by", "id")),
                key=f"filtro_order_by_{key_suffix}",
                placeholder=get_text("select_document_placeholder")
            )
            st.session_state.filtros_temporarios["order_by"] = order_by
        
        with col4:
            order_dir = st.selectbox(
                get_text("order_direction"),
                options=["desc", "asc"],
                format_func=lambda x: get_text("descending") if x == "desc" else get_text("ascending"),
                index=0 if st.session_state.filtros_temporarios.get("order_dir", "desc") == "desc" else 1,
                key=f"filtro_order_dir_{key_suffix}",
                placeholder=get_text("select_document_placeholder")
            )
            st.session_state.filtros_temporarios["order_dir"] = order_dir
        
        col5, col6 = st.columns(2)
        with col5:
            if st.button(get_text("apply_filters"), use_container_width=True):
                st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                st.rerun()
        with col6:
            if st.button(get_text("clear_filters"), use_container_width=True):
                st.session_state.filtros_temporarios = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                st.session_state.filtros_aplicados = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                st.session_state.filtros_widget_key += 1
                st.rerun()

# ---------- Funções de renderização com auto-add ----------
def render_lca_inputs(data_key, prefix=""):
    st.subheader(get_text("inputs"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["inputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lca"]["inputs"][proc] = items
        
        with st.expander(f"{get_text('inputs')} - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    item["material"] = st.text_input(get_text("material"), item.get("material",""), key=f"{prefix}lca_in_{proc}_mat_{i}")
                with col2:
                    item["qty"] = st.text_input(get_text("qty"), item.get("qty",""), key=f"{prefix}lca_in_{proc}_qty_{i}")
                    item["unit"] = st.text_input(get_text("unit"), item.get("unit",""), key=f"{prefix}lca_in_{proc}_unit_{i}")
                with col3:
                    item["description"] = st.text_area(get_text("description"), item.get("description",""), key=f"{prefix}lca_in_{proc}_desc_{i}")
                    item["cas"] = st.text_input(get_text("cas_comments"), item.get("cas",""), key=f"{prefix}lca_in_{proc}_cas_{i}")
                with col4:
                    item["distance"] = st.text_input(get_text("distance"), item.get("distance",""), key=f"{prefix}lca_in_{proc}_dist_{i}")
                    item["country"] = st.text_input(get_text("country"), item.get("country",""), key=f"{prefix}lca_in_{proc}_country_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lca_in_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_input')} - {proc}", key=f"{prefix}add_lca_in_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lca_in_{proc}"):
                    items.pop()
                    st.rerun()

def render_lca_processes(data_key, prefix=""):
    st.subheader(get_text("processes"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["processes"][proc]
        
        if not items:
            items.append({"tipo": "Energy Consumption (kWh)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            items.append({"tipo": "Rate Power of the Equipment (W)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            items.append({"tipo": "Operating Time (h)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
            st.session_state[data_key]["lca"]["processes"][proc] = items
        
        with st.expander(f"{get_text('processes')} - {proc}", expanded=False):
            num_groups = len(items) // 3
            for g in range(num_groups):
                base = g * 3
                st.markdown(f"**{get_text('processes')} #{g+1}**")
                
                tipos = ["Energy Consumption (kWh)", "Rate Power of the Equipment (W)", "Operating Time (h)"]
                for j, tipo in enumerate(tipos):
                    idx = base + j
                    if idx < len(items):
                        item = items[idx]
                        item["tipo"] = tipo
                        st.markdown(f"*{tipo}*")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            item["qty"] = st.text_input(get_text("qty"), item.get("qty",""), key=f"{prefix}lca_proc_{proc}_qty_{idx}")
                            item["unit"] = st.text_input(get_text("unit"), item.get("unit",""), key=f"{prefix}lca_proc_{proc}_unit_{idx}")
                        with col2:
                            item["description"] = st.text_area(get_text("description"), item.get("description",""), key=f"{prefix}lca_proc_{proc}_desc_{idx}")
                        with col3:
                            item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lca_proc_{proc}_comments_{idx}")
                            current_value = item.get("datasource", "")
                            if current_value in DATASOURCE_OPTIONS:
                                index = DATASOURCE_OPTIONS.index(current_value)
                            else:
                                index = None
                            item["datasource"] = st.selectbox(
                                get_text("data_source"), 
                                DATASOURCE_OPTIONS,
                                index=index,
                                key=f"{prefix}lca_proc_{proc}_ds_{idx}",
                                placeholder=get_text("select_document_placeholder")
                            )
                
                st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_process')} - {proc}", key=f"{prefix}add_lca_proc_{proc}"):
                    items.append({"tipo": "Energy Consumption (kWh)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    items.append({"tipo": "Rate Power of the Equipment (W)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    items.append({"tipo": "Operating Time (h)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": ""})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lca_proc_{proc}"):
                    for _ in range(3):
                        if items:
                            items.pop()
                    st.rerun()

def render_lca_outputs(data_key, prefix=""):
    st.subheader(get_text("outputs"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lca"]["outputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lca"]["outputs"][proc] = items
        
        with st.expander(f"{get_text('outputs')} - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["etapa"] = st.text_input(get_text("etapa"), item.get("etapa",""), key=f"{prefix}lca_out_{proc}_etapa_{i}")
                    
                    tipo_atual = item.get("tipo", "")
                    tipos = ["Subproduct", "Emissions", "Waste"]
                    if tipo_atual in tipos:
                        tipo_index = tipos.index(tipo_atual)
                    else:
                        tipo_index = None
                    
                    item["tipo"] = st.selectbox(
                        get_text("tipo"), 
                        tipos,
                        index=tipo_index,
                        key=f"{prefix}lca_out_{proc}_tipo_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
                    
                    item["sub_tipo"] = st.text_input(get_text("sub_tipo"), item.get("sub_tipo",""), key=f"{prefix}lca_out_{proc}_sub_{i}")
                with col2:
                    item["qty"] = st.text_input(get_text("qty"), item.get("qty",""), key=f"{prefix}lca_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input(get_text("unit"), item.get("unit",""), key=f"{prefix}lca_out_{proc}_unit_{i}")
                    item["description"] = st.text_area(get_text("description"), item.get("description",""), key=f"{prefix}lca_out_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lca_out_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lca_out_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_output')} - {proc}", key=f"{prefix}add_lca_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lca_out_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_materials(data_key, prefix=""):
    st.subheader(get_text("materials"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["materials"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["materials"][proc] = items
        
        with st.expander(f"{get_text('materials')} - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input(get_text("material"), item.get("material",""), key=f"{prefix}lcc_mat_{proc}_mat_{i}")
                    item["price"] = st.text_input(get_text("price"), item.get("price",""), key=f"{prefix}lcc_mat_{proc}_price_{i}")
                with col2:
                    item["qty"] = st.text_input(get_text("qty"), item.get("qty",""), key=f"{prefix}lcc_mat_{proc}_qty_{i}")
                    item["unit"] = st.text_input(get_text("unit"), item.get("unit",""), key=f"{prefix}lcc_mat_{proc}_unit_{i}")
                    item["description"] = st.text_area(get_text("description"), item.get("description",""), key=f"{prefix}lcc_mat_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lcc_mat_{proc}_comments_{i}")
                    item["distance"] = st.text_input(get_text("distance"), item.get("distance",""), key=f"{prefix}lcc_mat_{proc}_dist_{i}")
                    item["country"] = st.text_input(get_text("country"), item.get("country",""), key=f"{prefix}lcc_mat_{proc}_country_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_mat_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_material')} - {proc}", key=f"{prefix}add_lcc_mat_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lcc_mat_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_equipment(data_key, prefix=""):
    st.subheader(get_text("equipment"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["equipment"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["equipment"][proc] = items
        
        with st.expander(f"{get_text('equipment')} - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["equipment"] = st.text_input(get_text("equipment"), item.get("equipment",""), key=f"{prefix}lcc_eq_{proc}_eq_{i}")
                    item["process"] = st.text_input(get_text("process_name"), item.get("process",""), key=f"{prefix}lcc_eq_{proc}_proc_{i}")
                with col2:
                    item["unit_cost"] = st.text_input(get_text("unit_cost"), item.get("unit_cost",""), key=f"{prefix}lcc_eq_{proc}_cost_{i}")
                    item["lifespan"] = st.text_input(get_text("lifespan"), item.get("lifespan",""), key=f"{prefix}lcc_eq_{proc}_life_{i}")
                    item["maintenance"] = st.text_input(get_text("maintenance"), item.get("maintenance",""), key=f"{prefix}lcc_eq_{proc}_maint_{i}")
                with col3:
                    item["industrial_equiv"] = st.text_input(get_text("industrial_equiv"), item.get("industrial_equiv",""), key=f"{prefix}lcc_eq_{proc}_ind_{i}")
                    item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lcc_eq_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_eq_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_equipment')} - {proc}", key=f"{prefix}add_lcc_eq_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lcc_eq_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_labour(data_key, prefix=""):
    st.subheader(get_text("labour"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["labour"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["labour"][proc] = items
        
        with st.expander(f"{get_text('labour')} - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["process"] = st.text_input(get_text("process_name"), item.get("process",""), key=f"{prefix}lcc_lab_{proc}_name_{i}")
                    item["total_number"] = st.text_input(get_text("total_number"), item.get("total_number",""), key=f"{prefix}lcc_lab_{proc}_num_{i}")
                    item["total_cost"] = st.text_input(get_text("total_cost"), item.get("total_cost",""), key=f"{prefix}lcc_lab_{proc}_cost_{i}")
                with col2:
                    item["high_skilled"] = st.text_input(get_text("high_skilled"), item.get("high_skilled",""), key=f"{prefix}lcc_lab_{proc}_high_{i}")
                    item["moderate_skilled"] = st.text_input(get_text("moderate_skilled"), item.get("moderate_skilled",""), key=f"{prefix}lcc_lab_{proc}_mod_{i}")
                    item["unskilled"] = st.text_input(get_text("unskilled"), item.get("unskilled",""), key=f"{prefix}lcc_lab_{proc}_unsk_{i}")
                with col3:
                    item["high_rate"] = st.text_input(get_text("high_rate"), item.get("high_rate",""), key=f"{prefix}lcc_lab_{proc}_highrate_{i}")
                    item["moderate_rate"] = st.text_input(get_text("moderate_rate"), item.get("moderate_rate",""), key=f"{prefix}lcc_lab_{proc}_modrate_{i}")
                    item["unskilled_rate"] = st.text_input(get_text("unskilled_rate"), item.get("unskilled_rate",""), key=f"{prefix}lcc_lab_{proc}_unskrate_{i}")
                    item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lcc_lab_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_lab_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_labour')} - {proc}", key=f"{prefix}add_lcc_lab_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} - {proc}", key=f"{prefix}rem_lcc_lab_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_outputs(data_key, prefix=""):
    st.subheader(get_text("outputs_lcc"))
    for proc in PROCESSOS:
        items = st.session_state[data_key]["lcc"]["outputs"][proc]
        
        if not items:
            items.append({})
            st.session_state[data_key]["lcc"]["outputs"][proc] = items
        
        with st.expander(f"{get_text('outputs')} LCC - {proc}", expanded=False):
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input(get_text("material"), item.get("material",""), key=f"{prefix}lcc_out_{proc}_mat_{i}")
                    item["market_price"] = st.text_input(get_text("market_price"), item.get("market_price",""), key=f"{prefix}lcc_out_{proc}_price_{i}")
                with col2:
                    item["quantity"] = st.text_input(get_text("quantity"), item.get("quantity",""), key=f"{prefix}lcc_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input(get_text("unit"), item.get("unit",""), key=f"{prefix}lcc_out_{proc}_unit_{i}")
                with col3:
                    item["amount_produced"] = st.text_input(get_text("amount_produced"), item.get("amount_produced",""), key=f"{prefix}lcc_out_{proc}_prod_{i}")
                    item["comments"] = st.text_area(get_text("comments"), item.get("comments",""), key=f"{prefix}lcc_out_{proc}_comments_{i}")
                    current_value = item.get("datasource", "")
                    if current_value in DATASOURCE_OPTIONS:
                        index = DATASOURCE_OPTIONS.index(current_value)
                    else:
                        index = None
                    item["datasource"] = st.selectbox(
                        get_text("data_source"), 
                        DATASOURCE_OPTIONS,
                        index=index,
                        key=f"{prefix}lcc_out_{proc}_ds_{i}",
                        placeholder=get_text("select_document_placeholder")
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"{get_text('add_output')} LCC - {proc}", key=f"{prefix}add_lcc_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"{get_text('remove_last')} LCC - {proc}", key=f"{prefix}rem_lcc_out_{proc}"):
                    items.pop()
                    st.rerun()

def render_full_form(data_key, prefix=""):
    if st.session_state[data_key] is None:
        st.session_state[data_key] = {
            "lca": {
                "inputs": {p: [] for p in PROCESSOS},
                "processes": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            },
            "lcc": {
                "materials": {p: [] for p in PROCESSOS},
                "equipment": {p: [] for p in PROCESSOS},
                "labour": {p: [] for p in PROCESSOS},
                "outputs": {p: [] for p in PROCESSOS}
            }
        }
    else:
        st.session_state[data_key] = ensure_new_structure(st.session_state[data_key])

    st.subheader(get_text("lca"))
    render_lca_inputs(data_key, prefix)
    render_lca_processes(data_key, prefix)
    render_lca_outputs(data_key, prefix)

    st.subheader(get_text("lcc"))
    render_lcc_materials(data_key, prefix)
    render_lcc_equipment(data_key, prefix)
    render_lcc_labour(data_key, prefix)
    render_lcc_outputs(data_key, prefix)

# ============================================================
# FUNÇÃO PARA CRIAR ÂNCORA E TRIGGER SCROLL
# ============================================================
def create_document_anchor(doc_id):
    st.markdown(f'<div id="doc-{doc_id}" class="doc-anchor"></div>', unsafe_allow_html=True)

def trigger_scroll(doc_id):
    st.query_params["scroll_to"] = str(doc_id)

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

# Renderizar seletor de idioma
render_language_selector()

# Verificar se o utilizador está autenticado
if st.session_state.token is None:
    st.title(get_text("login"))
    with st.form("login_form"):
        username = st.text_input(get_text("username"))
        password = st.text_input(get_text("password"), type="password")
        submitted = st.form_submit_button(get_text("login_button"))
        if submitted:
            if login(username, password):
                st.session_state.success_message = get_text("login_success")
                st.rerun()
    st.stop()

# ============================================================
# A PARTIR DAQUI, O UTILIZADOR ESTÁ AUTENTICADO
# ============================================================

# Mostrar mensagem de sucesso com toast
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

# Processar abertura de documento vindo das notificações
if "doc_id" in st.query_params and st.query_params["doc_id"]:
    try:
        doc_id = int(st.query_params["doc_id"])
        st.session_state.doc_selecionado = doc_id
        st.query_params.clear()
    except ValueError:
        pass

if st.session_state.redirect_to_docs:
    st.session_state.menu_parceiro_widget = get_text("my_documents")
    st.session_state.redirect_to_docs = False

if st.session_state.get("close_doc_after_action", False):
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False

if st.session_state.token is not None:
    render_notificacoes_badge()
    verificar_novas_notificacoes()

# ============================================================
# SIDEBAR - VISÍVEL APÓS LOGIN - 270px
# ============================================================
with st.sidebar:
    st.write(f"{get_text('logged_as')} **{st.session_state.username}**")
    st.divider()
    
    if st.session_state.token is not None:
        try:
            count = get_notificacoes_nao_lidas()
            if count > 0:
                if count == 1:
                    st.warning(f"🔔 {count} {get_text('unread_notifications')}")
                else:
                    st.warning(f"🔔 {count} {get_text('unread_notifications')}")
            else:
                st.info(f"🔔 {get_text('no_notifications_text')}")
        except:
            pass
    
    st.divider()
    
    if st.button(get_text("dashboard"), use_container_width=True, key="app_dashboard"):
        st.switch_page("pages/dashboard.py")
    
    if st.button(get_text("notifications"), use_container_width=True, key="app_notificacoes"):
        st.switch_page("pages/notificacoes.py")
    
    st.divider()
    
    if st.button(get_text("logout"), use_container_width=True, key="app_logout"):
        logout()
        st.rerun()

st.title(get_text("app_title"))

# ---------- Resumo de documentos ----------
if st.session_state.perfil != "admin":
    documentos = listar_documentos()
    if documentos:
        st.subheader(get_text("document_summary"))
        show_document_summary(documentos)
        st.divider()
    else:
        st.info(get_text("no_documents"))

# ---------- Área do Parceiro ----------
if st.session_state.perfil == "parceiro":
    st.header(get_text("partner_area"))
    menu = st.sidebar.radio(get_text("menu"), [get_text("my_documents"), get_text("create_document")], key="menu_parceiro_widget")

    if menu == get_text("create_document"):
        st.subheader(get_text("create_document"))
        titulo = st.text_input(get_text("document_title"))
        st.info(get_text("fill_form_instructions"))
        if st.session_state.new_data is None:
            st.session_state.new_data = ensure_new_structure({})
        render_full_form("new_data", prefix="new_")
        if st.button(get_text("create_document"), key="create_doc_btn"):
            if not titulo.strip():
                st.error(f"{get_text('document_title')} é obrigatório")
            else:
                dados = st.session_state.new_data
                novo = criar_documento(titulo, dados)
                if novo:
                    st.session_state.success_message = f"{get_text('document_created')} ID: {novo['id']}"
                    st.session_state.new_data = None
                    st.session_state.doc_selecionado = None
                    st.session_state.redirect_to_docs = True
                    st.rerun()

    elif menu == get_text("my_documents"):
        st.subheader(get_text("my_documents"))
        
        if st.button(get_text("refresh_list"), key="refresh_list_parceiro"):
            st.session_state.doc_selecionado = None
            st.session_state.edit_data = None
            st.session_state.parceiro_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos()
        if not documentos:
            st.info(get_text("no_documents"))
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
            df.columns = [get_text("id"), get_text("title"), get_text("state"), get_text("version"), get_text("updated_at")]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                get_text("select_document"),
                ids,
                format_func=lambda x: get_text("select_document_placeholder") if x == "" else f"ID {x}",
                key=f"parceiro_selectbox_{st.session_state.parceiro_dropdown_key}",
                placeholder=get_text("select_document_placeholder")
            )

            if st.button(get_text("load_document"), key="parceiro_carregar_doc"):
                if not id_selecionado:
                    st.warning(get_text("select_document_first"))
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                st.subheader(f"{get_text('document_id')} {doc['id']}: {doc['titulo']}")
                st.write(f"{get_text('status')}: **{get_text(doc['estado'], doc['estado'])}** | {get_text('version')}: {doc['versao_atual']}")
                
                dados = doc['dados']
                
                with st.expander(get_text("view_data_tables"), expanded=False):
                    st.subheader(get_text("lca"))
                    lca = dados.get("lca", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lca.get("inputs", {}).get(proc):
                            st.write(get_text("inputs"))
                            display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                        if lca.get("processes", {}).get(proc):
                            st.write(get_text("processes"))
                            display_dataframe(pd.DataFrame(lca["processes"][proc]))
                        if lca.get("outputs", {}).get(proc):
                            st.write(get_text("outputs"))
                            display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                    st.subheader(get_text("lcc"))
                    lcc = dados.get("lcc", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lcc.get("materials", {}).get(proc):
                            st.write(get_text("materials"))
                            display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                        if lcc.get("equipment", {}).get(proc):
                            st.write(get_text("equipment"))
                            display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                        if lcc.get("labour", {}).get(proc):
                            st.write(get_text("labour"))
                            display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                        if lcc.get("outputs", {}).get(proc):
                            st.write(get_text("outputs"))
                            display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

                with st.expander(get_text("view_raw_json"), expanded=False):
                    st.json(dados)

                st.markdown("---")

                # ---------- BOTÕES DE AÇÃO ----------
                if doc['estado'] == "Rascunho":
                    st.subheader(get_text("edit"))
                    if st.session_state.edit_data is None:
                        st.session_state.edit_data = ensure_new_structure(safe_copy(dados))
                    render_full_form("edit_data", prefix="edit_")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button(get_text("save"), key="parceiro_save_edit", use_container_width=True):
                            novos_dados = st.session_state.edit_data
                            resultado = editar_documento(doc['id'], novos_dados)
                            if resultado:
                                st.session_state.edit_data = None
                                st.session_state.doc_selecionado = None
                                st.session_state.close_doc_after_action = True
                                st.success(get_text("document_edit_saved"))
                                st.rerun()
                    with col_btn2:
                        if st.button(get_text("submit"), key="parceiro_submeter", use_container_width=True):
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                resultado_sub = submeter(doc['id'])
                                if resultado_sub:
                                    st.session_state.edit_data = None
                                    st.session_state.doc_selecionado = None
                                    st.session_state.close_doc_after_action = True
                                    st.success(get_text("document_submitted"))
                                    st.rerun()
                    with col_btn3:
                        if st.button(get_text("close"), key="parceiro_fechar_detalhes", use_container_width=True):
                            st.session_state.doc_selecionado = None
                            st.session_state.edit_data = None
                            st.rerun()

                else:
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    if doc['estado'] == "Alterações":
                        with col_btn1:
                            st.warning(get_text("company_requested_changes"))
                            versoes = listar_versoes(doc['id'])
                            if versoes:
                                ultima = versoes[-1]
                                if ultima['comentario']:
                                    st.info(f"{get_text('reason')}: {ultima['comentario']}")
                            if st.button(get_text("edit_again"), key="parceiro_editar_novamente", use_container_width=True):
                                if editar_novamente(doc['id']):
                                    st.rerun()
                    elif doc['estado'] == "Aprovado":
                        with col_btn1:
                            st.success(get_text("document_approved_status"))
                    elif doc['estado'] in ["Submetido", "Em Revisão"]:
                        with col_btn1:
                            st.info(get_text("under_review"))
                    elif doc['estado'] == "Arquivado":
                        with col_btn1:
                            st.warning(get_text("archived_readonly"))
                    
                    with col_btn2:
                        conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                        if conteudo:
                            st.download_button(
                                label=get_text("export_history"),
                                data=conteudo,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_parceiro_{doc['id']}_{st.session_state.refresh_counter}",
                                use_container_width=True
                            )
                    
                    with col_btn3:
                        if st.button(get_text("close"), key="parceiro_fechar_detalhes", use_container_width=True):
                            st.session_state.doc_selecionado = None
                            st.session_state.edit_data = None
                            st.rerun()

                st.markdown("---")

                with st.expander(get_text("version_history"), expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            st.write(f"v{v['numero_versao']} - {get_text(v['estado'], v['estado'])} por {v['criado_por']} em {data_formatada}")
                            if v['comentario']:
                                st.caption(f"  {get_text('comment')}: {v['comentario']}")
                    else:
                        st.info(get_text("no_history"))

# ---------- Área da Empresa ----------
elif st.session_state.perfil == "empresa":
    st.header(get_text("company_area"))

    st.subheader(get_text("documents"))
    render_filtros()
    
    if st.button(get_text("refresh_list"), key="refresh_list_empresa"):
        st.session_state.doc_selecionado = None
        st.session_state.empresa_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
    if not documentos:
        st.info(get_text("no_documents"))
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = [get_text("id"), get_text("title"), get_text("partner"), get_text("state"), get_text("version"), get_text("updated_at")]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]

        id_selecionado = st.selectbox(
            get_text("select_document"),
            ids,
            format_func=lambda x: get_text("select_document_placeholder") if x == "" else f"ID {x}",
            key=f"empresa_selectbox_{st.session_state.empresa_dropdown_key}",
            placeholder=get_text("select_document_placeholder")
        )

        if st.button(get_text("load_document"), key="empresa_carregar_doc"):
            if not id_selecionado:
                st.warning(get_text("select_document_first"))
            else:
                st.session_state.doc_selecionado = id_selecionado
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            st.subheader(f"{get_text('document_id')} {doc['id']}: {doc['titulo']} ({get_text('partner')}: {doc['parceiro_id']})")
            st.write(f"{get_text('status')}: **{get_text(doc['estado'], doc['estado'])}** | {get_text('version')}: {doc['versao_atual']}")

            dados = doc['dados']
            
            with st.expander(get_text("view_data_tables"), expanded=False):
                st.subheader(get_text("lca"))
                lca = dados.get("lca", {})
                for proc in PROCESSOS:
                    st.write(f"**{proc}**")
                    if lca.get("inputs", {}).get(proc):
                        st.write(get_text("inputs"))
                        display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                    if lca.get("processes", {}).get(proc):
                        st.write(get_text("processes"))
                        display_dataframe(pd.DataFrame(lca["processes"][proc]))
                    if lca.get("outputs", {}).get(proc):
                        st.write(get_text("outputs"))
                        display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                st.subheader(get_text("lcc"))
                lcc = dados.get("lcc", {})
                for proc in PROCESSOS:
                    st.write(f"**{proc}**")
                    if lcc.get("materials", {}).get(proc):
                        st.write(get_text("materials"))
                        display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                    if lcc.get("equipment", {}).get(proc):
                        st.write(get_text("equipment"))
                        display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                    if lcc.get("labour", {}).get(proc):
                        st.write(get_text("labour"))
                        display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                    if lcc.get("outputs", {}).get(proc):
                        st.write(get_text("outputs"))
                        display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

            with st.expander(get_text("view_raw_json"), expanded=False):
                st.json(dados)

            st.markdown("---")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            if doc['estado'] == "Submetido":
                with col_btn1:
                    if st.button(get_text("start_review"), key="empresa_iniciar_revisao", use_container_width=True):
                        if iniciar_revisao(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Em Revisão":
                comentario = st.text_area(get_text("comment_optional"), key="empresa_comentario")
                col_aprov, col_alt = st.columns(2)
                with col_aprov:
                    if st.button(get_text("approve"), key="empresa_aprovar", use_container_width=True):
                        if aprovar(doc['id']):
                            st.rerun()
                with col_alt:
                    if st.button(get_text("request_changes"), key="empresa_pedir_alteracoes", use_container_width=True):
                        if not comentario.strip():
                            st.error(get_text("comment_required"))
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.rerun()
            elif doc['estado'] == "Aprovado":
                with col_btn1:
                    if st.button(get_text("reopen"), key="empresa_reabrir", use_container_width=True):
                        if reabrir(doc['id']):
                            st.rerun()
                with col_btn2:
                    if st.button(get_text("archive"), key="empresa_arquivar", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Rascunho":
                with col_btn1:
                    if st.button(get_text("archive"), key="empresa_arquivar_rascunho", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] == "Alterações":
                with col_btn1:
                    st.info(get_text("waiting_partner"))
            elif doc['estado'] == "Arquivado":
                with col_btn1:
                    st.warning(get_text("archived_readonly"))

            with col_btn2:
                conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                if conteudo:
                    st.download_button(
                        label=get_text("export_history"),
                        data=conteudo,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_empresa_{doc['id']}_{st.session_state.refresh_counter}",
                        use_container_width=True
                    )

            with col_btn3:
                if st.button(get_text("close"), key="empresa_fechar_detalhes", use_container_width=True):
                    st.session_state.doc_selecionado = None
                    st.rerun()

            st.markdown("---")

            with st.expander(get_text("version_history"), expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {get_text(v['estado'], v['estado'])} ({v['criado_por']}) em {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  {get_text('comment')}: {v['comentario']}")
                else:
                    st.info(get_text("no_history"))

# ---------- Área do Admin ----------
elif st.session_state.perfil == "admin":
    st.header(get_text("admin_panel"))
    menu_admin = st.sidebar.radio(get_text("menu"), [get_text("users"), get_text("company_documents")], key="admin_menu")

    if menu_admin == get_text("users"):
        st.subheader(get_text("user_management"))
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(get_text("loading_users"), use_container_width=True, key="admin_carregar_users"):
                st.session_state.doc_selecionado = None
                st.session_state.admin_user_dropdown_key += 1
                st.session_state.refresh_counter += 1
                st.rerun()
        with col2:
            if st.button(get_text("create_user"), use_container_width=True, key="admin_novo_user"):
                st.session_state.show_create_user_form = True
                st.rerun()
        
        st.write("")

        resp = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
        if resp.status_code == 200:
            users = resp.json()
            if users:
                for user in users:
                    if user["perfil"] == "empresa":
                        user["perfil"] = get_text("empresa")
                    elif user["perfil"] == "parceiro":
                        user["perfil"] = get_text("parceiro")
                    elif user["perfil"] == "admin":
                        user["perfil"] = get_text("admin")
                
                df = pd.DataFrame(users)
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_disponiveis = df.columns.tolist()
                colunas_desejadas = ["username", "perfil", "nome_completo", "created_at"]
                colunas_existentes = [col for col in colunas_desejadas if col in cols_disponiveis]
                df = df[colunas_existentes]
                df.columns = [get_text("username"), get_text("profile"), get_text("full_name"), get_text("created_at")]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                
                st.subheader(get_text("manage_user"))
                
                usernames = [""] + [u["username"] for u in users]

                sel_user = st.selectbox(
                    get_text("select_user"),
                    usernames,
                    format_func=lambda x: get_text("select_user_placeholder") if x == "" else x,
                    key=f"admin_user_selectbox_{st.session_state.admin_user_dropdown_key}",
                    placeholder=get_text("select_user_placeholder")
                )

                if sel_user:
                    user_data = next((u for u in users if u["username"] == sel_user), None)
                    if user_data:
                        st.info(f"**{get_text('username')}:** {user_data['username']} | **{get_text('profile')}:** {user_data['perfil']} | **{get_text('full_name')}:** {user_data['nome_completo']}")
                    
                    st.subheader(get_text("change_password"))
                    pw_key = f"admin_pw_input_{st.session_state.pw_input_counter}"
                    nova_pw = st.text_input(
                        get_text("new_password"), 
                        type="password", 
                        key=pw_key,
                        placeholder=get_text("new_password")
                    )
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button(get_text("change_password"), key="btn_alterar_pw", use_container_width=True):
                            if not sel_user:
                                st.warning(get_text("select_user"))
                            elif not nova_pw.strip():
                                st.warning(get_text("password_required"))
                            elif len(nova_pw.strip()) < 3:
                                st.warning(get_text("password_min_length"))
                            else:
                                resp_pw = requests.put(
                                    f"{API_URL}/admin/usuarios/{sel_user}/password",
                                    json={"nova_password": nova_pw},
                                    headers=headers_auth()
                                )
                                if resp_pw.status_code == 200:
                                    st.toast(f"✅ {get_text('password_changed')} '{sel_user}'!", icon="✅")
                                    st.session_state.pw_input_counter += 1
                                    st.rerun()
                                else:
                                    try:
                                        erro = resp_pw.json().get("detail", "Erro desconhecido")
                                    except:
                                        erro = resp_pw.text
                                    st.error(f"{get_text('error_changing_password')}: {erro}")
                    
                    with col_btn2:
                        if st.button(get_text("delete_user"), key="btn_eliminar_user", use_container_width=True):
                            if not sel_user:
                                st.warning(get_text("select_user"))
                            elif sel_user == st.session_state.username:
                                st.error(get_text("cannot_delete_self"))
                            else:
                                confirm = st.button(get_text("confirm_delete"), key="btn_confirmar_eliminar")
                                if confirm:
                                    resp_del = requests.delete(f"{API_URL}/admin/usuarios/{sel_user}", headers=headers_auth())
                                    if resp_del.status_code == 200:
                                        st.toast(f"{get_text('user_deleted')} '{sel_user}'!", icon="🗑️")
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_del.json().get("detail", "Erro desconhecido")
                                        except:
                                            erro = resp_del.text
                                        st.error(f"{get_text('error_deleting_user')}: {erro}")
                    
                    with col_btn3:
                        if st.button(get_text("close_details"), key="admin_fechar_gerir_user", use_container_width=True):
                            st.session_state.admin_user_dropdown_key += 1
                            st.session_state.doc_selecionado = None
                            st.rerun()
                
                if st.session_state.show_create_user_form:
                    st.divider()
                    st.subheader(get_text("create_user_form"))
                    
                    with st.form("create_user_form"):
                        new_username = st.text_input(f"{get_text('username')} *", placeholder="Ex: novo_parceiro")
                        new_password = st.text_input(f"{get_text('password')} *", type="password", placeholder="Mínimo 3 caracteres")
                        new_nome = st.text_input(get_text("full_name"), placeholder="Ex: João Silva")
                        new_perfil = st.selectbox(
                            f"{get_text('profile')} *",
                            options=["parceiro", "empresa", "admin"],
                            format_func=lambda x: {
                                "parceiro": get_text("parceiro"),
                                "empresa": get_text("empresa"),
                                "admin": get_text("admin")
                            }.get(x, x),
                            placeholder=get_text("select_document_placeholder")
                        )
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            submit_create = st.form_submit_button(get_text("create_user"), use_container_width=True)
                        with col2:
                            cancel_create = st.form_submit_button(get_text("cancel"), use_container_width=True)
                        
                        if cancel_create:
                            st.session_state.show_create_user_form = False
                            st.rerun()
                        
                        if submit_create:
                            if not new_username.strip():
                                st.error(get_text("username_required"))
                            elif not new_password.strip() or len(new_password.strip()) < 3:
                                st.error(get_text("password_required"))
                            elif not new_perfil:
                                st.error(get_text("profile_required"))
                            else:
                                if any(u["username"] == new_username for u in users):
                                    st.error(get_text("username_exists"))
                                else:
                                    try:
                                        resp_create = requests.post(
                                            f"{API_URL}/registar",
                                            json={
                                                "username": new_username.strip(),
                                                "password": new_password.strip(),
                                                "perfil": new_perfil,
                                                "nome_completo": new_nome.strip() if new_nome.strip() else new_username.strip()
                                            }
                                        )
                                        if resp_create.status_code == 200:
                                            st.toast(f"{get_text('user_created')} '{new_username}'!", icon="✅")
                                            st.session_state.show_create_user_form = False
                                            st.session_state.pw_input_counter += 1
                                            st.session_state.admin_user_dropdown_key += 1
                                            st.rerun()
                                        else:
                                            try:
                                                erro = resp_create.json().get("detail", "Erro desconhecido")
                                            except:
                                                erro = resp_create.text
                                            st.error(f"{get_text('error_creating_user')}: {erro}")
                                    except Exception as e:
                                        st.error(f"{get_text('error_creating_user')}: {str(e)}")

            else:
                st.info(get_text("no_documents"))
        else:
            st.error(get_text("error_loading_users"))

    else:  # Documentos (empresa) - Admin
        st.header(get_text("company_area"))

        st.subheader(get_text("documents"))
        render_filtros()
        
        if st.button(get_text("refresh_list"), key="refresh_list_admin"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
        if not documentos:
            st.info(get_text("no_documents"))
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            if "created_at" in df.columns:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
            df.columns = [get_text("id"), get_text("title"), get_text("partner"), get_text("state"), get_text("version"), get_text("updated_at")]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                get_text("select_document"),
                ids,
                format_func=lambda x: get_text("select_document_placeholder") if x == "" else f"ID {x}",
                key=f"admin_selectbox_{st.session_state.admin_dropdown_key}",
                placeholder=get_text("select_document_placeholder")
            )

            if st.button(get_text("load_document"), key="admin_carregar_doc"):
                if not id_selecionado:
                    st.warning(get_text("select_document_first"))
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                st.subheader(f"{get_text('document_id')} {doc['id']}: {doc['titulo']} ({get_text('partner')}: {doc['parceiro_id']})")
                st.write(f"{get_text('status')}: **{get_text(doc['estado'], doc['estado'])}** | {get_text('version')}: {doc['versao_atual']}")

                dados = doc['dados']
                
                with st.expander(get_text("view_data_tables"), expanded=False):
                    st.subheader(get_text("lca"))
                    lca = dados.get("lca", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lca.get("inputs", {}).get(proc):
                            st.write(get_text("inputs"))
                            display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                        if lca.get("processes", {}).get(proc):
                            st.write(get_text("processes"))
                            display_dataframe(pd.DataFrame(lca["processes"][proc]))
                        if lca.get("outputs", {}).get(proc):
                            st.write(get_text("outputs"))
                            display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                    st.subheader(get_text("lcc"))
                    lcc = dados.get("lcc", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lcc.get("materials", {}).get(proc):
                            st.write(get_text("materials"))
                            display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                        if lcc.get("equipment", {}).get(proc):
                            st.write(get_text("equipment"))
                            display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                        if lcc.get("labour", {}).get(proc):
                            st.write(get_text("labour"))
                            display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                        if lcc.get("outputs", {}).get(proc):
                            st.write(get_text("outputs"))
                            display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

                with st.expander(get_text("view_raw_json"), expanded=False):
                    st.json(dados)

                st.markdown("---")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                if doc['estado'] == "Submetido":
                    with col_btn1:
                        if st.button(get_text("start_review"), key="admin_iniciar_revisao", use_container_width=True):
                            if iniciar_revisao(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Em Revisão":
                    comentario = st.text_area(get_text("comment_optional"), key="admin_comentario")
                    col_aprov, col_alt = st.columns(2)
                    with col_aprov:
                        if st.button(get_text("approve"), key="admin_aprovar", use_container_width=True):
                            if aprovar(doc['id']):
                                st.rerun()
                    with col_alt:
                        if st.button(get_text("request_changes"), key="admin_pedir_alteracoes", use_container_width=True):
                            if not comentario.strip():
                                st.error(get_text("comment_required"))
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.rerun()
                elif doc['estado'] == "Aprovado":
                    with col_btn1:
                        if st.button(get_text("reopen"), key="admin_reabrir", use_container_width=True):
                            if reabrir(doc['id']):
                                st.rerun()
                    with col_btn2:
                        if st.button(get_text("archive"), key="admin_arquivar", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Rascunho":
                    with col_btn1:
                        if st.button(get_text("archive"), key="admin_arquivar_rascunho", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] == "Alterações":
                    with col_btn1:
                        st.info(get_text("waiting_partner"))
                elif doc['estado'] == "Arquivado":
                    with col_btn1:
                        st.warning(get_text("archived_readonly"))

                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label=get_text("export_history"),
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_admin_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )

                with col_btn3:
                    if st.button(get_text("close"), key="admin_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.rerun()

                st.markdown("---")

                with st.expander(get_text("version_history"), expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            st.write(f"v{v['numero_versao']} - {get_text(v['estado'], v['estado'])} ({v['criado_por']}) em {data_formatada}")
                            if v['comentario']:
                                st.caption(f"  {get_text('comment')}: {v['comentario']}")
                    else:
                        st.info(get_text("no_history"))

# ============================================================
# GARANTIR QUE O CLOSE_DOC_AFTER_ACTION É PROCESSADO
# ============================================================
if st.session_state.get("close_doc_after_action", False):
    if st.session_state.doc_selecionado is not None:
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False