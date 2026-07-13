import streamlit as st
import requests
import pandas as pd
import copy
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
PROCESSOS = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = ["Medido", "Calculado", "Estimado", "Literatura"]

# Configuração da página - sidebar NÃO colapsada para permitir a navegação
st.set_page_config(
    page_title="Plataforma Documentos",
    layout="wide",
    initial_sidebar_state="expanded"  # ALTERADO: expanded em vez de collapsed
)

# Importar componente de notificações
from componentes.notificacoes import render_notificacoes_badge

# ============================================================
# CSS - Apenas para ocultar a barra de navegação automática,
# mas manter a sidebar funcional
# ============================================================
st.markdown("""
<style>
    /* Ocultar apenas a barra de navegação automática do Streamlit */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Manter a sidebar visível e funcional */
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        min-width: auto !important;
        max-width: auto !important;
        overflow: auto !important;
        pointer-events: auto !important;
    }
    
    /* Ajustar o conteúdo principal */
    .main > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
</style>
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
    st.session_state.menu_parceiro_widget = "Meus Documentos"
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

# Chave para forçar recriação dos widgets de filtro
if "filtros_widget_key" not in st.session_state:
    st.session_state.filtros_widget_key = 0

# Estado dos filtros - valores atuais aplicados
if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "q": "",
        "estados": [],
        "data_inicio": None,
        "data_fim": None,
        "order_by": "id",
        "order_dir": "desc"
    }

# Estado temporário dos filtros (enquanto o utilizador mexe)
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
        st.error("Credenciais inválidas")
        return False

def logout():
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
    st.session_state.ultimo_count = 0

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def listar_documentos(estado=None):
    params = {}
    if estado:
        params["estado"] = estado
    resp = requests.get(f"{API_URL}/documentos", headers=headers_auth(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def listar_documentos_com_filtros(filtros):
    """
    Lista documentos aplicando os filtros atuais.
    """
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
        st.error(f"Erro ao criar documento: {resp.text}")
        return None

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Erro ao obter documento: {resp.text}")
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
        st.error(f"Erro ao editar: {resp.text}")
        return None

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao submeter: {resp.text}")
        return None
    st.success("✅ Documento submetido com sucesso!")
    st.rerun()
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao iniciar revisão: {resp.text}")
        return None
    st.success("🔍 Revisão iniciada com sucesso!")
    st.rerun()
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(
        f"{API_URL}/documentos/{doc_id}/pedir-alteracoes",
        json={"comentario": comentario},
        headers=headers_auth()
    )
    if resp.status_code != 200:
        st.error(f"Erro ao pedir alterações: {resp.text}")
        return None
    st.success("🔄 Alterações solicitadas com sucesso!")
    st.rerun()
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao editar novamente: {resp.text}")
        return None
    st.success("📝 Documento reaberto para edição!")
    st.rerun()
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao aprovar: {resp.text}")
        return None
    st.success("✅ Documento aprovado com sucesso!")
    st.rerun()
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao reabrir: {resp.text}")
        return None
    st.success("📂 Documento reaberto com sucesso!")
    st.rerun()
    return resp.json()

def arquivar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/arquivar", headers=headers_auth())
    if resp.status_code != 200:
        st.error(f"Erro ao arquivar: {resp.text}")
        return None
    st.success("📁 Documento arquivado com sucesso!")
    st.rerun()
    return resp.json()

def listar_versoes(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/versoes", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    return []

def exportar_excel(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/exportar-excel", headers=headers_auth())
    if resp.status_code == 200:
        return resp.content
    else:
        try:
            erro = resp.json().get("detail", "Erro desconhecido")
        except:
            erro = "Erro ao exportar"
        st.error(f"Falha na exportação: {erro}")
        return None

# ---------- Função para obter notificações ----------
def get_notificacoes_nao_lidas():
    """Obtém o número de notificações não lidas."""
    try:
        resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json().get("count", 0)
    except Exception as e:
        print(f"Erro ao obter notificações: {e}")
    return 0

def verificar_novas_notificacoes():
    """Verifica se há novas notificações e mostra um toast."""
    if st.session_state.token is None:
        return
    
    try:
        count = get_notificacoes_nao_lidas()
        if count > st.session_state.ultimo_count:
            st.toast(f"🔔 {count - st.session_state.ultimo_count} nova(s) notificação(ões)!", icon="🔔")
        st.session_state.ultimo_count = count
    except:
        pass

# ---------- Função para resumo ----------
def show_document_summary(documentos):
    if not documentos:
        st.info("Nenhum documento encontrado.")
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
            st.metric(label=estado, value=contagens[estado])

# ---------- Função para exibir dataframes sem índice ----------
def display_dataframe(df):
    if df is not None and not df.empty:
        df = df.copy()
        df.columns = [col.title() for col in df.columns]
        df = df.reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("(sem dados)")

# ---------- Componente de filtros (apenas para empresa e admin) ----------
def render_filtros():
    """
    Renderiza os filtros de pesquisa para empresa e admin.
    Os filtros só são aplicados quando o botão "Aplicar Filtros" é clicado.
    """
    with st.expander("🔍 Filtros de Pesquisa", expanded=False):
        col1, col2 = st.columns(2)
        
        # Usar a chave atual para todos os widgets
        key_suffix = st.session_state.filtros_widget_key
        
        with col1:
            # Pesquisa de texto
            q = st.text_input(
                "Pesquisar",
                value=st.session_state.filtros_temporarios.get("q", ""),
                placeholder="Título, parceiro ou ID...",
                key=f"filtro_q_{key_suffix}"
            )
            st.session_state.filtros_temporarios["q"] = q
            
            # Estados
            estados_disponiveis = ["Rascunho", "Submetido", "Em Revisão", "Alterações", "Aprovado", "Arquivado"]
            estados_selecionados = st.multiselect(
                "Estado",
                options=estados_disponiveis,
                default=st.session_state.filtros_temporarios.get("estados", []),
                key=f"filtro_estados_{key_suffix}"
            )
            st.session_state.filtros_temporarios["estados"] = estados_selecionados
        
        with col2:
            # Datas
            data_inicio = st.date_input(
                "Data Início",
                value=st.session_state.filtros_temporarios.get("data_inicio"),
                format="DD/MM/YYYY",
                key=f"filtro_data_inicio_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
            
            data_fim = st.date_input(
                "Data Fim",
                value=st.session_state.filtros_temporarios.get("data_fim"),
                format="DD/MM/YYYY",
                key=f"filtro_data_fim_{key_suffix}"
            )
            st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
        
        # Ordenação
        col3, col4 = st.columns(2)
        with col3:
            ordem_campos = {
                "id": "ID",
                "titulo": "Título",
                "parceiro_id": "Parceiro",
                "estado": "Estado",
                "created_at": "Data Criação",
                "updated_at": "Data Atualização",
                "versao_atual": "Versão"
            }
            order_by = st.selectbox(
                "Ordenar por",
                options=list(ordem_campos.keys()),
                format_func=lambda x: ordem_campos.get(x, x),
                index=list(ordem_campos.keys()).index(st.session_state.filtros_temporarios.get("order_by", "id")),
                key=f"filtro_order_by_{key_suffix}"
            )
            st.session_state.filtros_temporarios["order_by"] = order_by
        
        with col4:
            order_dir = st.selectbox(
                "Direção",
                options=["desc", "asc"],
                format_func=lambda x: "Decrescente" if x == "desc" else "Crescente",
                index=0 if st.session_state.filtros_temporarios.get("order_dir", "desc") == "desc" else 1,
                key=f"filtro_order_dir_{key_suffix}"
            )
            st.session_state.filtros_temporarios["order_dir"] = order_dir
        
        # Botões de ação
        col5, col6 = st.columns(2)
        with col5:
            if st.button("🔍 Aplicar Filtros", use_container_width=True):
                # Copiar filtros temporários para filtros aplicados
                st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                st.rerun()
        with col6:
            if st.button("🧹 Limpar Filtros", use_container_width=True):
                # Reset dos filtros temporários
                st.session_state.filtros_temporarios = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                # Reset dos filtros aplicados também
                st.session_state.filtros_aplicados = {
                    "q": "",
                    "estados": [],
                    "data_inicio": None,
                    "data_fim": None,
                    "order_by": "id",
                    "order_dir": "desc"
                }
                # Incrementar a chave para forçar recriação dos widgets
                st.session_state.filtros_widget_key += 1
                st.rerun()

# ---------- Funções de renderização das tabelas ----------
def render_lca_inputs(data_key, prefix=""):
    st.subheader("Inputs")
    for proc in PROCESSOS:
        with st.expander(f"Inputs - {proc}", expanded=False):
            items = st.session_state[data_key]["lca"]["inputs"][proc]
            for i, item in enumerate(items):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lca_in_{proc}_mat_{i}")
                with col2:
                    item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_in_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_in_{proc}_unit_{i}")
                with col3:
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lca_in_{proc}_desc_{i}")
                    item["cas"] = st.text_input("CAS/Comments", item.get("cas",""), key=f"{prefix}lca_in_{proc}_cas_{i}")
                with col4:
                    item["distance"] = st.text_input("Distance (km)", item.get("distance",""), key=f"{prefix}lca_in_{proc}_dist_{i}")
                    item["country"] = st.text_input("Country", item.get("country",""), key=f"{prefix}lca_in_{proc}_country_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lca_in_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar input - {proc}", key=f"{prefix}add_lca_in_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último input - {proc}", key=f"{prefix}rem_lca_in_{proc}"):
                    items.pop()
                    st.rerun()

def render_lca_processes(data_key, prefix=""):
    st.subheader("Processes")
    for proc in PROCESSOS:
        with st.expander(f"Processes - {proc}", expanded=False):
            items = st.session_state[data_key]["lca"]["processes"][proc]
            num_groups = len(items) // 3
            for g in range(num_groups):
                base = g * 3
                with st.expander(f"Grupo de processos #{g+1}", expanded=False):
                    tipos = ["Energy Consumption (kWh)", "Rate Power of the Equipment (W)", "Operating Time (h)"]
                    for j, tipo in enumerate(tipos):
                        idx = base + j
                        if idx < len(items):
                            item = items[idx]
                            item["tipo"] = tipo
                            with st.expander(f"{tipo}", expanded=False):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_proc_{proc}_qty_{idx}")
                                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_proc_{proc}_unit_{idx}")
                                with col2:
                                    item["description"] = st.text_area("Description", item.get("description",""), key=f"{prefix}lca_proc_{proc}_desc_{idx}")
                                with col3:
                                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lca_proc_{proc}_comments_{idx}")
                                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                                      key=f"{prefix}lca_proc_{proc}_ds_{idx}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar processo (3 linhas) - {proc}", key=f"{prefix}add_lca_proc_{proc}"):
                    items.append({"tipo": "Energy Consumption (kWh)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": "Medido"})
                    items.append({"tipo": "Rate Power of the Equipment (W)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": "Medido"})
                    items.append({"tipo": "Operating Time (h)", "qty": "", "unit": "", "description": "", "comments": "", "datasource": "Medido"})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último processo (3 linhas) - {proc}", key=f"{prefix}rem_lca_proc_{proc}"):
                    for _ in range(3):
                        if items:
                            items.pop()
                    st.rerun()

def render_lca_outputs(data_key, prefix=""):
    st.subheader("Outputs")
    for proc in PROCESSOS:
        with st.expander(f"Outputs - {proc}", expanded=False):
            items = st.session_state[data_key]["lca"]["outputs"][proc]
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["etapa"] = st.text_input("Etapa (ex: Demagnetisation)", item.get("etapa",""), key=f"{prefix}lca_out_{proc}_etapa_{i}")
                    item["tipo"] = st.selectbox("Tipo", ["Subproduct", "Emissions", "Waste"],
                                                index=["Subproduct","Emissions","Waste"].index(item.get("tipo","Subproduct")) if item.get("tipo") in ["Subproduct","Emissions","Waste"] else 0,
                                                key=f"{prefix}lca_out_{proc}_tipo_{i}")
                    item["sub_tipo"] = st.text_input("Sub-tipo (ex: Name 1, Liquid 1, Solid 1, etc.)", item.get("sub_tipo",""), key=f"{prefix}lca_out_{proc}_sub_{i}")
                with col2:
                    item["qty"] = st.text_input("QTY", item.get("qty",""), key=f"{prefix}lca_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lca_out_{proc}_unit_{i}")
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lca_out_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lca_out_{proc}_comments_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lca_out_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar output - {proc}", key=f"{prefix}add_lca_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último output - {proc}", key=f"{prefix}rem_lca_out_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_materials(data_key, prefix=""):
    st.subheader("Cost Breakdown Material")
    for proc in PROCESSOS:
        with st.expander(f"Materials - {proc}", expanded=False):
            items = st.session_state[data_key]["lcc"]["materials"][proc]
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lcc_mat_{proc}_mat_{i}")
                    item["price"] = st.text_input("Price €", item.get("price",""), key=f"{prefix}lcc_mat_{proc}_price_{i}")
                with col2:
                    item["qty"] = st.text_input("Qty", item.get("qty",""), key=f"{prefix}lcc_mat_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lcc_mat_{proc}_unit_{i}")
                    item["description"] = st.text_area("Material Description", item.get("description",""), key=f"{prefix}lcc_mat_{proc}_desc_{i}")
                with col3:
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_mat_{proc}_comments_{i}")
                    item["distance"] = st.text_input("Distance (km)", item.get("distance",""), key=f"{prefix}lcc_mat_{proc}_dist_{i}")
                    item["country"] = st.text_input("Country", item.get("country",""), key=f"{prefix}lcc_mat_{proc}_country_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lcc_mat_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar material - {proc}", key=f"{prefix}add_lcc_mat_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último material - {proc}", key=f"{prefix}rem_lcc_mat_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_equipment(data_key, prefix=""):
    st.subheader("Equipment")
    for proc in PROCESSOS:
        with st.expander(f"Equipment - {proc}", expanded=False):
            items = st.session_state[data_key]["lcc"]["equipment"][proc]
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["equipment"] = st.text_input("Equipment", item.get("equipment",""), key=f"{prefix}lcc_eq_{proc}_eq_{i}")
                    item["process"] = st.text_input("Process", item.get("process",""), key=f"{prefix}lcc_eq_{proc}_proc_{i}")
                with col2:
                    item["unit_cost"] = st.text_input("Unit Cost (€)", item.get("unit_cost",""), key=f"{prefix}lcc_eq_{proc}_cost_{i}")
                    item["lifespan"] = st.text_input("Lifespan (Years)", item.get("lifespan",""), key=f"{prefix}lcc_eq_{proc}_life_{i}")
                    item["maintenance"] = st.text_input("Maintenance €/Year", item.get("maintenance",""), key=f"{prefix}lcc_eq_{proc}_maint_{i}")
                with col3:
                    item["industrial_equiv"] = st.text_input("Industrial Equivalent", item.get("industrial_equiv",""), key=f"{prefix}lcc_eq_{proc}_ind_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_eq_{proc}_comments_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lcc_eq_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar equipamento - {proc}", key=f"{prefix}add_lcc_eq_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último equipamento - {proc}", key=f"{prefix}rem_lcc_eq_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_labour(data_key, prefix=""):
    st.subheader("Labour")
    for proc in PROCESSOS:
        with st.expander(f"Labour - {proc}", expanded=False):
            items = st.session_state[data_key]["lcc"]["labour"][proc]
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["process"] = st.text_input("Name Of The Process", item.get("process",""), key=f"{prefix}lcc_lab_{proc}_name_{i}")
                    item["total_number"] = st.text_input("Total Labour - Number", item.get("total_number",""), key=f"{prefix}lcc_lab_{proc}_num_{i}")
                    item["total_cost"] = st.text_input("Total Labour - Cost €", item.get("total_cost",""), key=f"{prefix}lcc_lab_{proc}_cost_{i}")
                with col2:
                    item["high_skilled"] = st.text_input("Number - High Skilled", item.get("high_skilled",""), key=f"{prefix}lcc_lab_{proc}_high_{i}")
                    item["moderate_skilled"] = st.text_input("Number - Moderated Skilled", item.get("moderate_skilled",""), key=f"{prefix}lcc_lab_{proc}_mod_{i}")
                    item["unskilled"] = st.text_input("Number - Unskilled", item.get("unskilled",""), key=f"{prefix}lcc_lab_{proc}_unsk_{i}")
                with col3:
                    item["high_rate"] = st.text_input("Rate - High Skilled (€/h)", item.get("high_rate",""), key=f"{prefix}lcc_lab_{proc}_highrate_{i}")
                    item["moderate_rate"] = st.text_input("Rate - Moderated Skilled (€/h)", item.get("moderate_rate",""), key=f"{prefix}lcc_lab_{proc}_modrate_{i}")
                    item["unskilled_rate"] = st.text_input("Rate - Unskilled (€/h)", item.get("unskilled_rate",""), key=f"{prefix}lcc_lab_{proc}_unskrate_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_lab_{proc}_comments_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lcc_lab_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar linha de trabalho - {proc}", key=f"{prefix}add_lcc_lab_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover última linha - {proc}", key=f"{prefix}rem_lcc_lab_{proc}"):
                    items.pop()
                    st.rerun()

def render_lcc_outputs(data_key, prefix=""):
    st.subheader("Outputs (produto final)")
    for proc in PROCESSOS:
        with st.expander(f"Outputs LCC - {proc}", expanded=False):
            items = st.session_state[data_key]["lcc"]["outputs"][proc]
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    item["material"] = st.text_input("Material", item.get("material",""), key=f"{prefix}lcc_out_{proc}_mat_{i}")
                    item["market_price"] = st.text_input("Market Price €", item.get("market_price",""), key=f"{prefix}lcc_out_{proc}_price_{i}")
                with col2:
                    item["quantity"] = st.text_input("Quantity", item.get("quantity",""), key=f"{prefix}lcc_out_{proc}_qty_{i}")
                    item["unit"] = st.text_input("Unit", item.get("unit",""), key=f"{prefix}lcc_out_{proc}_unit_{i}")
                with col3:
                    item["amount_produced"] = st.text_input("Amount Of Product Produced", item.get("amount_produced",""), key=f"{prefix}lcc_out_{proc}_prod_{i}")
                    item["comments"] = st.text_area("Comments", item.get("comments",""), key=f"{prefix}lcc_out_{proc}_comments_{i}")
                    item["datasource"] = st.selectbox("Data Source", DATASOURCE_OPTIONS,
                                                      index=DATASOURCE_OPTIONS.index(item.get("datasource", DATASOURCE_OPTIONS[0])) if item.get("datasource") in DATASOURCE_OPTIONS else 0,
                                                      key=f"{prefix}lcc_out_{proc}_ds_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"➕ Adicionar output LCC - {proc}", key=f"{prefix}add_lcc_out_{proc}"):
                    items.append({})
                    st.rerun()
            with col2:
                if items and st.button(f"🗑️ Remover último output LCC - {proc}", key=f"{prefix}rem_lcc_out_{proc}"):
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

    st.subheader("LCA - Análise do Ciclo de Vida")
    render_lca_inputs(data_key, prefix)
    render_lca_processes(data_key, prefix)
    render_lca_outputs(data_key, prefix)

    st.subheader("LCC - Custo do Ciclo de Vida")
    render_lcc_materials(data_key, prefix)
    render_lcc_equipment(data_key, prefix)
    render_lcc_labour(data_key, prefix)
    render_lcc_outputs(data_key, prefix)

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

# Verificar se o utilizador está autenticado
if st.session_state.token is None:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if login(username, password):
                st.session_state.success_message = "Login efetuado com sucesso!"
                st.rerun()
    st.stop()

# ============================================================
# A PARTIR DAQUI, O UTILIZADOR ESTÁ AUTENTICADO
# ============================================================

# Mostrar mensagem de sucesso com toast
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

if st.session_state.redirect_to_docs:
    st.session_state.menu_parceiro_widget = "Meus Documentos"
    st.session_state.redirect_to_docs = False

# Renderizar badge de notificações (apenas após login)
if st.session_state.token is not None:
    render_notificacoes_badge()
    # Verificar novas notificações
    verificar_novas_notificacoes()

# ============================================================
# SIDEBAR - VISÍVEL APÓS LOGIN
# ============================================================
with st.sidebar:
    st.write(f"Logado como: **{st.session_state.username}** ({st.session_state.perfil})")
    st.divider()
    
    # Contador de notificações no sidebar
    if st.session_state.token is not None:
        try:
            count = get_notificacoes_nao_lidas()
            if count > 0:
                st.warning(f"🔔 {count} notificação(ões) não lida(s)")
            else:
                st.info("🔔 Sem notificações")
        except:
            pass
    
    st.divider()
    
    # Botão para Dashboard
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    
    # Botão para Notificações
    if st.button("🔔 Notificações", use_container_width=True):
        st.switch_page("pages/notificacoes.py")
    
    st.divider()
    
    # Botão Logout
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

st.title("📄 Plataforma de Gestão de Documentos")

# ---------- Resumo de documentos (apenas para parceiro e empresa) ----------
if st.session_state.perfil != "admin":
    documentos = listar_documentos()
    if documentos:
        st.subheader("📊 Resumo de documentos")
        show_document_summary(documentos)
        st.divider()
    else:
        st.info("Nenhum documento encontrado. Comece por criar um novo documento.")

# ---------- Área do Parceiro (SEM FILTROS) ----------
if st.session_state.perfil == "parceiro":
    st.header("Área do Parceiro")
    menu = st.sidebar.radio("Menu", ["Meus Documentos", "Criar Documento"], key="menu_parceiro_widget")

    if menu == "Criar Documento":
        st.subheader("Novo Documento LCA/LCC")
        titulo = st.text_input("Título do documento (ex: LCA/LCC NEO-CYCLE)")
        st.info("Preencha os dados nas tabelas abaixo. Cada processo tem a sua própria secção.")
        if st.session_state.new_data is None:
            st.session_state.new_data = ensure_new_structure({})
        render_full_form("new_data", prefix="new_")
        if st.button("📄 Criar documento", key="create_doc_btn"):
            if not titulo.strip():
                st.error("O título é obrigatório.")
            else:
                dados = st.session_state.new_data
                novo = criar_documento(titulo, dados)
                if novo:
                    st.session_state.success_message = f"Documento criado com sucesso! ID: {novo['id']}"
                    st.session_state.new_data = None
                    st.session_state.doc_selecionado = None
                    st.session_state.redirect_to_docs = True
                    st.rerun()

    elif menu == "Meus Documentos":
        st.subheader("Os meus documentos")
        
        # SEM FILTROS - apenas botão atualizar
        if st.button("🔄 Atualizar lista", key="refresh_list"):
            st.session_state.doc_selecionado = None
            st.session_state.edit_data = None
            st.session_state.parceiro_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos()
        if not documentos:
            st.info("Nenhum documento encontrado.")
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Título", "Estado", "Versão", "Última Atualização"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                "Seleciona um documento:",
                ids,
                format_func=lambda x: "Selecione um documento..." if x == "" else f"ID {x}",
                key=f"parceiro_selectbox_{st.session_state.parceiro_dropdown_key}"
            )

            if st.button("Carregar documento"):
                if not id_selecionado:
                    st.warning("Selecione um documento.")
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                st.divider()
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']}")
                st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")

                dados = doc['dados']
                with st.expander("Ver dados em tabelas", expanded=True):
                    st.subheader("LCA")
                    lca = dados.get("lca", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lca.get("inputs", {}).get(proc):
                            st.write("Inputs")
                            display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                        if lca.get("processes", {}).get(proc):
                            st.write("Processes")
                            display_dataframe(pd.DataFrame(lca["processes"][proc]))
                        if lca.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                    st.subheader("LCC")
                    lcc = dados.get("lcc", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lcc.get("materials", {}).get(proc):
                            st.write("Cost Breakdown Material")
                            display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                        if lcc.get("equipment", {}).get(proc):
                            st.write("Equipment")
                            display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                        if lcc.get("labour", {}).get(proc):
                            st.write("Labour")
                            display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                        if lcc.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

                with st.expander("Ver JSON bruto"):
                    st.json(dados)

                if doc['estado'] == "Rascunho":
                    st.subheader("✏️ Editar documento")
                    if st.session_state.edit_data is None:
                        st.session_state.edit_data = ensure_new_structure(safe_copy(dados))
                    render_full_form("edit_data", prefix="edit_")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar alterações", key="save_edit_btn"):
                            novos_dados = st.session_state.edit_data
                            resultado = editar_documento(doc['id'], novos_dados)
                            if resultado:
                                st.session_state.edit_data = None
                                st.session_state.doc_selecionado = None
                                st.success("Documento atualizado com sucesso!")
                                st.rerun()
                    with col2:
                        if st.button("📤 Submeter para validação", key="submit_doc_btn"):
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                resultado_sub = submeter(doc['id'])
                                if resultado_sub:
                                    st.session_state.edit_data = None
                                    st.session_state.doc_selecionado = None
                                    st.success("Documento submetido!")
                                    st.rerun()
                elif doc['estado'] == "Alterações":
                    st.warning("A empresa pediu alterações. Vê os comentários abaixo.")
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        ultima = versoes[-1]
                        if ultima['comentario']:
                            st.info(f"Motivo: {ultima['comentario']}")
                    if st.button("✏️ Editar novamente", key="edit_again_btn"):
                        if editar_novamente(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Documento reaberto para edição.")
                            st.rerun()
                elif doc['estado'] == "Aprovado":
                    st.success("Documento aprovado. Não pode ser editado.")
                elif doc['estado'] in ["Submetido", "Em Revisão"]:
                    st.info("Documento em análise pela empresa.")
                elif doc['estado'] == "Arquivado":
                    st.warning("Documento arquivado (apenas consulta).")

                with st.expander("Histórico de versões"):
                    versoes = listar_versoes(doc['id'])
                    for v in versoes:
                        st.write(f"v{v['numero_versao']} - {v['estado']} por {v['criado_por']} em {v['created_at']}")
                        if v['comentario']:
                            st.caption(f"  Comentário: {v['comentario']}")

                if st.button("Fechar detalhes"):
                    st.session_state.doc_selecionado = None
                    st.session_state.edit_data = None
                    st.rerun()

# ---------- Área da Empresa (COM FILTROS) ----------
elif st.session_state.perfil == "empresa":
    st.header("Área da Empresa (Validação)")

    st.subheader("Documentos disponíveis")
    
    # FILTROS disponíveis para a empresa
    render_filtros()
    
    if st.button("🔄 Atualizar lista", key="refresh_list_empresa"):
        st.session_state.doc_selecionado = None
        st.session_state.empresa_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    # Usar a função com filtros aplicados
    documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
    if not documentos:
        st.info("Nenhum documento encontrado com os filtros atuais.")
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Título", "Parceiro", "Estado", "Versão", "Última Atualização"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]

        id_selecionado = st.selectbox(
            "Seleciona um documento:",
            ids,
            format_func=lambda x: "Selecione um documento..." if x == "" else f"ID {x}",
            key=f"empresa_selectbox_{st.session_state.empresa_dropdown_key}"
        )

        if st.button("Carregar documento"):
            if not id_selecionado:
                st.warning("Selecione um documento.")
            else:
                st.session_state.doc_selecionado = id_selecionado
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            st.divider()
            st.subheader(f"Documento ID {doc['id']}: {doc['titulo']} (Parceiro: {doc['parceiro_id']})")
            st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")

            dados = doc['dados']
            with st.expander("Ver dados do documento", expanded=True):
                st.subheader("LCA")
                lca = dados.get("lca", {})
                for proc in PROCESSOS:
                    st.write(f"**{proc}**")
                    if lca.get("inputs", {}).get(proc):
                        st.write("Inputs")
                        display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                    if lca.get("processes", {}).get(proc):
                        st.write("Processes")
                        display_dataframe(pd.DataFrame(lca["processes"][proc]))
                    if lca.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                st.subheader("LCC")
                lcc = dados.get("lcc", {})
                for proc in PROCESSOS:
                    st.write(f"**{proc}**")
                    if lcc.get("materials", {}).get(proc):
                        st.write("Cost Breakdown Material")
                        display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                    if lcc.get("equipment", {}).get(proc):
                        st.write("Equipment")
                        display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                    if lcc.get("labour", {}).get(proc):
                        st.write("Labour")
                        display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                    if lcc.get("outputs", {}).get(proc):
                        st.write("Outputs")
                        display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

            with st.expander("Ver JSON bruto"):
                st.json(dados)

            if doc['estado'] == "Submetido":
                if st.button("Iniciar revisão"):
                    if iniciar_revisao(doc['id']):
                        st.session_state.doc_selecionado = None
                        st.success("Revisão iniciada.")
                        st.rerun()
            elif doc['estado'] == "Em Revisão":
                comentario = st.text_area("Comentário (obrigatório se pedir alterações)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Aprovar"):
                        if aprovar(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Documento aprovado.")
                            st.rerun()
                with col2:
                    if st.button("🔄 Pedir alterações"):
                        if not comentario.strip():
                            st.error("É necessário um comentário para pedir alterações")
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.session_state.doc_selecionado = None
                                st.success("Pedido de alterações registado.")
                                st.rerun()
            elif doc['estado'] == "Aprovado":
                st.success("Documento aprovado.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Reabrir para nova edição"):
                        if reabrir(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Documento reaberto.")
                            st.rerun()
                with col2:
                    if st.button("📁 Arquivar documento"):
                        if arquivar(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Documento arquivado.")
                            st.rerun()
            elif doc['estado'] == "Rascunho":
                st.info("O parceiro ainda está a editar.")
                if st.button("📁 Arquivar documento (rascunho)"):
                    if arquivar(doc['id']):
                        st.session_state.doc_selecionado = None
                        st.success("Documento arquivado.")
                        st.rerun()
            elif doc['estado'] == "Alterações":
                st.warning("Aguardando o parceiro iniciar a edição.")
            elif doc['estado'] == "Arquivado":
                st.warning("Documento arquivado (apenas consulta).")

            with st.expander("📥 Exportar histórico"):
                if st.button("Exportar versões para Excel (completo)"):
                    conteudo = exportar_excel(doc['id'])
                    if conteudo:
                        st.download_button(
                            label="Clique para descarregar o ficheiro",
                            data=conteudo,
                            file_name=f"documento_{doc['id']}_completo.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            with st.expander("Histórico de versões"):
                versoes = listar_versoes(doc['id'])
                for v in versoes:
                    st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']})")
                    if v['comentario']:
                        st.caption(f"  Comentário: {v['comentario']}")

            if st.button("Fechar detalhes"):
                st.session_state.doc_selecionado = None
                st.rerun()

# ---------- Área do Admin (COM FILTROS) ----------
elif st.session_state.perfil == "admin":
    st.header("Painel Administrativo")
    menu_admin = st.sidebar.radio("Admin", ["Utilizadores", "Documentos (empresa)"])

    if menu_admin == "Utilizadores":
        st.subheader("Gestão de Utilizadores")
        if st.button("🔄 Carregar utilizadores"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_user_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        resp = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
        if resp.status_code == 200:
            users = resp.json()
            if users:
                df = pd.DataFrame(users)
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_disponiveis = df.columns.tolist()
                colunas_desejadas = ["username", "perfil", "nome_completo", "created_at"]
                colunas_existentes = [col for col in colunas_desejadas if col in cols_disponiveis]
                df = df[colunas_existentes]
                df.columns = ["Username", "Perfil", "Nome", "Criado em"]
                st.dataframe(df, hide_index=True)
            else:
                st.info("Nenhum utilizador encontrado")
        else:
            st.error("Falha ao carregar utilizadores")

    else:  # Documentos (empresa) - COM FILTROS
        st.header("Área da Empresa (Validação) – Admin")

        st.subheader("Documentos disponíveis")
        
        # FILTROS disponíveis para o admin
        render_filtros()
        
        if st.button("🔄 Atualizar lista", key="refresh_list_admin"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        # Usar a função com filtros aplicados
        documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
        if not documentos:
            st.info("Nenhum documento encontrado com os filtros atuais.")
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            if "created_at" in df.columns:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Título", "Parceiro", "Estado", "Versão", "Última Atualização"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                "Seleciona um documento:",
                ids,
                format_func=lambda x: "Selecione um documento..." if x == "" else f"ID {x}",
                key=f"admin_selectbox_{st.session_state.admin_dropdown_key}"
            )

            if st.button("Carregar documento", key="load_doc_admin"):
                if not id_selecionado:
                    st.warning("Selecione um documento.")
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                st.divider()
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']} (Parceiro: {doc['parceiro_id']})")
                st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")

                dados = doc['dados']
                with st.expander("Ver dados do documento", expanded=True):
                    st.subheader("LCA")
                    lca = dados.get("lca", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lca.get("inputs", {}).get(proc):
                            st.write("Inputs")
                            display_dataframe(pd.DataFrame(lca["inputs"][proc]))
                        if lca.get("processes", {}).get(proc):
                            st.write("Processes")
                            display_dataframe(pd.DataFrame(lca["processes"][proc]))
                        if lca.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lca["outputs"][proc]))
                    st.subheader("LCC")
                    lcc = dados.get("lcc", {})
                    for proc in PROCESSOS:
                        st.write(f"**{proc}**")
                        if lcc.get("materials", {}).get(proc):
                            st.write("Cost Breakdown Material")
                            display_dataframe(pd.DataFrame(lcc["materials"][proc]))
                        if lcc.get("equipment", {}).get(proc):
                            st.write("Equipment")
                            display_dataframe(pd.DataFrame(lcc["equipment"][proc]))
                        if lcc.get("labour", {}).get(proc):
                            st.write("Labour")
                            display_dataframe(pd.DataFrame(lcc["labour"][proc]))
                        if lcc.get("outputs", {}).get(proc):
                            st.write("Outputs")
                            display_dataframe(pd.DataFrame(lcc["outputs"][proc]))

                with st.expander("Ver JSON bruto"):
                    st.json(dados)

                if doc['estado'] == "Submetido":
                    if st.button("Iniciar revisão", key="admin_iniciar_revisao"):
                        if iniciar_revisao(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Revisão iniciada.")
                            st.rerun()
                elif doc['estado'] == "Em Revisão":
                    comentario = st.text_area("Comentário (obrigatório se pedir alterações)", key="admin_comentario")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Aprovar", key="admin_aprovar"):
                            if aprovar(doc['id']):
                                st.session_state.doc_selecionado = None
                                st.success("Documento aprovado.")
                                st.rerun()
                    with col2:
                        if st.button("🔄 Pedir alterações", key="admin_pedir_alt"):
                            if not comentario.strip():
                                st.error("É necessário um comentário para pedir alterações")
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.session_state.doc_selecionado = None
                                    st.success("Pedido de alterações registado.")
                                    st.rerun()
                elif doc['estado'] == "Aprovado":
                    st.success("Documento aprovado.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Reabrir para nova edição", key="admin_reabrir"):
                            if reabrir(doc['id']):
                                st.session_state.doc_selecionado = None
                                st.success("Documento reaberto.")
                                st.rerun()
                    with col2:
                        if st.button("📁 Arquivar documento", key="admin_arquivar"):
                            if arquivar(doc['id']):
                                st.session_state.doc_selecionado = None
                                st.success("Documento arquivado.")
                                st.rerun()
                elif doc['estado'] == "Rascunho":
                    st.info("O parceiro ainda está a editar.")
                    if st.button("📁 Arquivar documento (rascunho)", key="admin_arquivar_rasc"):
                        if arquivar(doc['id']):
                            st.session_state.doc_selecionado = None
                            st.success("Documento arquivado.")
                            st.rerun()
                elif doc['estado'] == "Alterações":
                    st.warning("Aguardando o parceiro iniciar a edição.")
                elif doc['estado'] == "Arquivado":
                    st.warning("Documento arquivado (apenas consulta).")

                with st.expander("📥 Exportar histórico"):
                    if st.button("Exportar versões para Excel (completo)", key="admin_exportar"):
                        conteudo = exportar_excel(doc['id'])
                        if conteudo:
                            st.download_button(
                                label="Clique para descarregar o ficheiro",
                                data=conteudo,
                                file_name=f"documento_{doc['id']}_completo.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                with st.expander("Histórico de versões"):
                    versoes = listar_versoes(doc['id'])
                    for v in versoes:
                        st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']})")
                        if v['comentario']:
                            st.caption(f"  Comentário: {v['comentario']}")

                if st.button("Fechar detalhes", key="admin_fechar"):
                    st.session_state.doc_selecionado = None
                    st.rerun()