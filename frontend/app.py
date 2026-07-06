import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Plataforma Documentos", layout="wide")

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

def criar_documento(titulo, dados):
    resp = requests.post(
        f"{API_URL}/documentos/",
        json={"titulo": titulo, "parceiro_id": st.session_state.username, "dados": dados},
        headers=headers_auth()
    )
    return resp.json()

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    return None

def editar_documento(doc_id, dados):
    resp = requests.put(
        f"{API_URL}/documentos/{doc_id}/editar",
        json={"dados": dados},
        headers=headers_auth()
    )
    return resp.json()

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter", headers=headers_auth())
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao", headers=headers_auth())
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(
        f"{API_URL}/documentos/{doc_id}/pedir-alteracoes",
        json={"comentario": comentario},
        headers=headers_auth()
    )
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente", headers=headers_auth())
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar", headers=headers_auth())
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir", headers=headers_auth())
    return resp.json()

def arquivar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/arquivar", headers=headers_auth())
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

# ---------- Função para renderizar o formulário LCA/LCC (sem st.form) ----------
def render_lca_lcc_form(data_key, key_prefix=""):
    """
    Renderiza o formulário completo para edição dos dados LCA/LCC.
    Os dados são lidos e escritos em st.session_state[data_key].
    Retorna o dicionário atualizado (apenas para conveniência).
    """
    # Garantir que os dados existem
    if st.session_state[data_key] is None:
        st.session_state[data_key] = {
            "inputs": [],
            "processes": [],
            "outputs": [],
            "lcc_materials": [],
            "lcc_equipment": [],
            "lcc_labour": [],
            "lcc_outputs": []
        }
    dados = st.session_state[data_key]

    # ---------- INPUTS ----------
    st.subheader("📥 Inputs (Materiais)")
    inputs = dados["inputs"]
    for i, item in enumerate(inputs):
        with st.expander(f"Input #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["material"] = st.text_input("Material", item.get("material", ""), key=f"{key_prefix}in_mat_{i}")
                item["qty"] = st.text_input("Quantidade", item.get("qty", ""), key=f"{key_prefix}in_qty_{i}")
                item["unit"] = st.text_input("Unidade", item.get("unit", ""), key=f"{key_prefix}in_unit_{i}")
                item["description"] = st.text_area("Descrição", item.get("description", ""), key=f"{key_prefix}in_desc_{i}")
            with col2:
                item["cas"] = st.text_input("CAS / Comentários", item.get("cas", ""), key=f"{key_prefix}in_cas_{i}")
                item["distance"] = st.text_input("Distância (km)", item.get("distance", ""), key=f"{key_prefix}in_dist_{i}")
                item["country"] = st.text_input("País", item.get("country", ""), key=f"{key_prefix}in_country_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}in_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar input", key=f"{key_prefix}add_input"):
            inputs.append({})
            st.rerun()
    with col2:
        if inputs and st.button("🗑️ Remover último input", key=f"{key_prefix}rem_input"):
            inputs.pop()
            st.rerun()

    # ---------- PROCESSES ----------
    st.subheader("⚙️ Processos")
    processes = dados["processes"]
    for i, item in enumerate(processes):
        with st.expander(f"Processo #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["process"] = st.text_input("Nome do processo", item.get("process", ""), key=f"{key_prefix}proc_name_{i}")
                item["qty"] = st.text_input("Quantidade", item.get("qty", ""), key=f"{key_prefix}proc_qty_{i}")
                item["unit"] = st.text_input("Unidade", item.get("unit", ""), key=f"{key_prefix}proc_unit_{i}")
            with col2:
                item["description"] = st.text_area("Descrição (máquina/energia)", item.get("description", ""), key=f"{key_prefix}proc_desc_{i}")
                item["comments"] = st.text_area("Comentários", item.get("comments", ""), key=f"{key_prefix}proc_comments_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}proc_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar processo", key=f"{key_prefix}add_process"):
            processes.append({})
            st.rerun()
    with col2:
        if processes and st.button("🗑️ Remover último processo", key=f"{key_prefix}rem_process"):
            processes.pop()
            st.rerun()

    # ---------- OUTPUTS ----------
    st.subheader("📤 Outputs (subprodutos, emissões, resíduos)")
    outputs = dados["outputs"]
    for i, item in enumerate(outputs):
        with st.expander(f"Output #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["etapa"] = st.text_input("Etapa (ex: Demagnetização)", item.get("etapa", ""), key=f"{key_prefix}out_etapa_{i}")
                item["tipo"] = st.selectbox("Tipo", ["Subproduto", "Emissão", "Resíduo"],
                                            index=["Subproduto", "Emissão", "Resíduo"].index(item.get("tipo", "Subproduto")),
                                            key=f"{key_prefix}out_tipo_{i}")
                item["nome"] = st.text_input("Nome", item.get("nome", ""), key=f"{key_prefix}out_nome_{i}")
                item["qty"] = st.text_input("Quantidade", item.get("qty", ""), key=f"{key_prefix}out_qty_{i}")
            with col2:
                item["unit"] = st.text_input("Unidade", item.get("unit", ""), key=f"{key_prefix}out_unit_{i}")
                item["description"] = st.text_area("Descrição", item.get("description", ""), key=f"{key_prefix}out_desc_{i}")
                item["comments"] = st.text_area("Comentários", item.get("comments", ""), key=f"{key_prefix}out_comments_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}out_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar output", key=f"{key_prefix}add_output"):
            outputs.append({})
            st.rerun()
    with col2:
        if outputs and st.button("🗑️ Remover último output", key=f"{key_prefix}rem_output"):
            outputs.pop()
            st.rerun()

    # ---------- LCC MATERIAIS ----------
    st.subheader("💰 LCC - Materiais")
    lcc_materials = dados["lcc_materials"]
    for i, item in enumerate(lcc_materials):
        with st.expander(f"Material LCC #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["material"] = st.text_input("Material", item.get("material", ""), key=f"{key_prefix}lccmat_mat_{i}")
                item["price"] = st.text_input("Preço (€)", item.get("price", ""), key=f"{key_prefix}lccmat_price_{i}")
                item["qty"] = st.text_input("Quantidade", item.get("qty", ""), key=f"{key_prefix}lccmat_qty_{i}")
                item["unit"] = st.text_input("Unidade", item.get("unit", ""), key=f"{key_prefix}lccmat_unit_{i}")
            with col2:
                item["brand"] = st.text_input("Marca/identificador", item.get("brand", ""), key=f"{key_prefix}lccmat_brand_{i}")
                item["amount_used"] = st.text_input("Quantidade usada por FU", item.get("amount_used", ""), key=f"{key_prefix}lccmat_used_{i}")
                item["distance"] = st.text_input("Distância (km)", item.get("distance", ""), key=f"{key_prefix}lccmat_dist_{i}")
                item["country"] = st.text_input("País", item.get("country", ""), key=f"{key_prefix}lccmat_country_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}lccmat_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar material LCC", key=f"{key_prefix}add_lccmat"):
            lcc_materials.append({})
            st.rerun()
    with col2:
        if lcc_materials and st.button("🗑️ Remover último material LCC", key=f"{key_prefix}rem_lccmat"):
            lcc_materials.pop()
            st.rerun()

    # ---------- LCC EQUIPAMENTOS ----------
    st.subheader("🛠️ LCC - Equipamentos")
    lcc_equipment = dados["lcc_equipment"]
    for i, item in enumerate(lcc_equipment):
        with st.expander(f"Equipamento LCC #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["equipment"] = st.text_input("Equipamento", item.get("equipment", ""), key=f"{key_prefix}lcc_eq_name_{i}")
                item["process"] = st.text_input("Processo associado", item.get("process", ""), key=f"{key_prefix}lcc_eq_proc_{i}")
                item["unit_cost"] = st.text_input("Custo unitário (€)", item.get("unit_cost", ""), key=f"{key_prefix}lcc_eq_cost_{i}")
                item["lifespan"] = st.text_input("Vida útil (anos)", item.get("lifespan", ""), key=f"{key_prefix}lcc_eq_life_{i}")
            with col2:
                item["maintenance"] = st.text_input("Manutenção (€/ano)", item.get("maintenance", ""), key=f"{key_prefix}lcc_eq_maint_{i}")
                item["industrial_equiv"] = st.text_input("Equivalente industrial", item.get("industrial_equiv", ""), key=f"{key_prefix}lcc_eq_ind_{i}")
                item["comments"] = st.text_area("Comentários", item.get("comments", ""), key=f"{key_prefix}lcc_eq_comments_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}lcc_eq_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar equipamento LCC", key=f"{key_prefix}add_lcceq"):
            lcc_equipment.append({})
            st.rerun()
    with col2:
        if lcc_equipment and st.button("🗑️ Remover último equipamento LCC", key=f"{key_prefix}rem_lcceq"):
            lcc_equipment.pop()
            st.rerun()

    # ---------- LCC MÃO-DE-OBRA ----------
    st.subheader("👷 LCC - Mão-de-obra")
    lcc_labour = dados["lcc_labour"]
    for i, item in enumerate(lcc_labour):
        with st.expander(f"Mão-de-obra LCC #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["process"] = st.text_input("Processo", item.get("process", ""), key=f"{key_prefix}lcc_lab_proc_{i}")
                item["total_labour"] = st.text_input("Nº total de trabalhadores", item.get("total_labour", ""), key=f"{key_prefix}lcc_lab_total_{i}")
                item["cost"] = st.text_input("Custo total (€)", item.get("cost", ""), key=f"{key_prefix}lcc_lab_cost_{i}")
                item["high_skilled"] = st.text_input("Nº alta qualificação", item.get("high_skilled", ""), key=f"{key_prefix}lcc_lab_high_{i}")
                item["moderate"] = st.text_input("Nº qualificação média", item.get("moderate", ""), key=f"{key_prefix}lcc_lab_mod_{i}")
                item["unskilled"] = st.text_input("Nº não qualificados", item.get("unskilled", ""), key=f"{key_prefix}lcc_lab_unsk_{i}")
            with col2:
                item["high_rate"] = st.text_input("Taxa alta (€/h)", item.get("high_rate", ""), key=f"{key_prefix}lcc_lab_highrate_{i}")
                item["moderate_rate"] = st.text_input("Taxa média (€/h)", item.get("moderate_rate", ""), key=f"{key_prefix}lcc_lab_modrate_{i}")
                item["unskilled_rate"] = st.text_input("Taxa não qualificada (€/h)", item.get("unskilled_rate", ""), key=f"{key_prefix}lcc_lab_unskrate_{i}")
                item["comments"] = st.text_area("Comentários", item.get("comments", ""), key=f"{key_prefix}lcc_lab_comments_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}lcc_lab_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar mão-de-obra LCC", key=f"{key_prefix}add_lcclab"):
            lcc_labour.append({})
            st.rerun()
    with col2:
        if lcc_labour and st.button("🗑️ Remover último mão-de-obra LCC", key=f"{key_prefix}rem_lcclab"):
            lcc_labour.pop()
            st.rerun()

    # ---------- LCC OUTPUTS (produto final) ----------
    st.subheader("📦 LCC - Outputs (produto final)")
    lcc_outputs = dados["lcc_outputs"]
    for i, item in enumerate(lcc_outputs):
        with st.expander(f"Output LCC #{i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                item["material"] = st.text_input("Material", item.get("material", ""), key=f"{key_prefix}lccout_mat_{i}")
                item["market_price"] = st.text_input("Preço de mercado (€)", item.get("market_price", ""), key=f"{key_prefix}lccout_price_{i}")
                item["quantity"] = st.text_input("Quantidade", item.get("quantity", ""), key=f"{key_prefix}lccout_qty_{i}")
            with col2:
                item["unit"] = st.text_input("Unidade", item.get("unit", ""), key=f"{key_prefix}lccout_unit_{i}")
                item["amount_produced"] = st.text_input("Quantidade produzida (por FU)", item.get("amount_produced", ""), key=f"{key_prefix}lccout_prod_{i}")
                item["comments"] = st.text_area("Comentários", item.get("comments", ""), key=f"{key_prefix}lccout_comments_{i}")
                item["datasource"] = st.selectbox("Fonte", ["Medido", "Calculado", "Estimado", "Literatura"],
                                                  index=["Medido", "Calculado", "Estimado", "Literatura"].index(item.get("datasource", "Medido")),
                                                  key=f"{key_prefix}lccout_ds_{i}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Adicionar output LCC", key=f"{key_prefix}add_lccout"):
            lcc_outputs.append({})
            st.rerun()
    with col2:
        if lcc_outputs and st.button("🗑️ Remover último output LCC", key=f"{key_prefix}rem_lccout"):
            lcc_outputs.pop()
            st.rerun()

    return dados

# ---------- Interface principal ----------
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
            else:
                st.error("Credenciais inválidas")
    st.stop()

# Usuário logado – mostrar mensagem de sucesso se existir
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = None

# Se houve redireccionamento pendente, atualiza o menu ANTES de criar a widget
if st.session_state.redirect_to_docs:
    st.session_state.menu_parceiro_widget = "Meus Documentos"
    st.session_state.redirect_to_docs = False

st.sidebar.write(f"Logado como: **{st.session_state.username}** ({st.session_state.perfil})")
if st.sidebar.button("Logout"):
    logout()
    st.rerun()

st.title("📄 Plataforma de Gestão de Documentos")

# ---------- Área do Parceiro ----------
if st.session_state.perfil == "parceiro":
    st.header("Área do Parceiro")
    menu = st.sidebar.radio(
        "Menu",
        ["Meus Documentos", "Criar Documento"],
        key="menu_parceiro_widget"
    )

    if menu == "Criar Documento":
        st.subheader("Novo Documento LCA/LCC")
        titulo = st.text_input("Título do documento (ex: LCA/LCC NEO-CYCLE)")
        st.info("Preencha os dados do documento. Pode adicionar quantas linhas quiser em cada secção.")

        if st.session_state.new_data is None:
            st.session_state.new_data = {
                "inputs": [],
                "processes": [],
                "outputs": [],
                "lcc_materials": [],
                "lcc_equipment": [],
                "lcc_labour": [],
                "lcc_outputs": []
            }

        render_lca_lcc_form("new_data", key_prefix="new_")

        if st.button("📄 Criar documento", key="create_doc_btn"):
            if not titulo.strip():
                st.error("O título é obrigatório.")
            else:
                dados = st.session_state.new_data
                novo = criar_documento(titulo, dados)
                st.session_state.success_message = f"Documento criado com sucesso! ID: {novo['id']}"
                st.session_state.new_data = None
                st.session_state.redirect_to_docs = True
                st.rerun()

    elif menu == "Meus Documentos":
        st.subheader("Os meus documentos")
        documentos = listar_documentos()
        if not documentos:
            st.info("Nenhum documento encontrado.")
        else:
            df = pd.DataFrame(documentos)
            df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Título", "Estado", "Versão", "Última atualização"]
            st.dataframe(df, width='stretch', hide_index=True)

            ids = [doc["id"] for doc in documentos]
            id_selecionado = st.selectbox("Seleciona um documento para ver detalhes:", ids, format_func=lambda x: f"ID {x}")
            if st.button("Carregar documento"):
                st.session_state.doc_selecionado = id_selecionado
                st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                st.divider()
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']}")
                st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")

                dados = doc['dados']
                st.subheader("📋 Dados do documento")
                with st.expander("Ver dados em tabelas", expanded=True):
                    if dados.get("inputs"):
                        st.write("**Inputs**")
                        st.dataframe(pd.DataFrame(dados["inputs"]), use_container_width=True)
                    if dados.get("processes"):
                        st.write("**Processos**")
                        st.dataframe(pd.DataFrame(dados["processes"]), use_container_width=True)
                    if dados.get("outputs"):
                        st.write("**Outputs**")
                        st.dataframe(pd.DataFrame(dados["outputs"]), use_container_width=True)
                    if dados.get("lcc_materials"):
                        st.write("**LCC - Materiais**")
                        st.dataframe(pd.DataFrame(dados["lcc_materials"]), use_container_width=True)
                    if dados.get("lcc_equipment"):
                        st.write("**LCC - Equipamentos**")
                        st.dataframe(pd.DataFrame(dados["lcc_equipment"]), use_container_width=True)
                    if dados.get("lcc_labour"):
                        st.write("**LCC - Mão-de-obra**")
                        st.dataframe(pd.DataFrame(dados["lcc_labour"]), use_container_width=True)
                    if dados.get("lcc_outputs"):
                        st.write("**LCC - Outputs**")
                        st.dataframe(pd.DataFrame(dados["lcc_outputs"]), use_container_width=True)
                with st.expander("Ver JSON bruto"):
                    st.json(dados)

                if doc['estado'] == 'rascunho':
                    st.subheader("✏️ Editar documento")
                    if st.session_state.edit_data is None:
                        st.session_state.edit_data = dados.copy()
                    render_lca_lcc_form("edit_data", key_prefix="edit_")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar alterações", key="save_edit_btn"):
                            novos_dados = st.session_state.edit_data
                            editar_documento(doc['id'], novos_dados)
                            st.session_state.edit_data = None
                            st.success("Documento atualizado")
                            st.rerun()
                    with col2:
                        if st.button("📤 Submeter para validação", key="submit_doc_btn"):
                            novos_dados = st.session_state.edit_data
                            editar_documento(doc['id'], novos_dados)
                            st.session_state.edit_data = None
                            submeter(doc['id'])
                            st.success("Documento submetido!")
                            st.rerun()

                elif doc['estado'] == 'alteracoes':
                    st.warning("A empresa pediu alterações. Vê os comentários abaixo.")
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        ultima = versoes[-1]
                        if ultima['comentario']:
                            st.info(f"Motivo: {ultima['comentario']}")
                    if st.button("✏️ Editar novamente", key="edit_again_btn"):
                        editar_novamente(doc['id'])
                        st.rerun()
                elif doc['estado'] == 'aprovado':
                    st.success("Documento aprovado. Não pode ser editado.")
                elif doc['estado'] in ['submetido', 'em_revisao']:
                    st.info("Documento em análise pela empresa.")
                elif doc['estado'] == 'arquivado':
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

# ---------- Área da Empresa / Admin ----------
elif st.session_state.perfil in ["empresa", "admin"]:
    st.header("Área da Empresa (Validação)")
    st.subheader("Documentos disponíveis")
    documentos = listar_documentos()
    if not documentos:
        st.info("Nenhum documento encontrado.")
    else:
        df = pd.DataFrame(documentos)
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Título", "Parceiro", "Estado", "Versão", "Última atualização"]
        st.dataframe(df, width='stretch', hide_index=True)

        ids = [doc["id"] for doc in documentos]
        id_selecionado = st.selectbox("Seleciona um documento para agir:", ids, format_func=lambda x: f"ID {x}")
        if st.button("Carregar documento"):
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
                if dados.get("inputs"):
                    st.write("**Inputs**")
                    st.dataframe(pd.DataFrame(dados["inputs"]), use_container_width=True)
                if dados.get("processes"):
                    st.write("**Processos**")
                    st.dataframe(pd.DataFrame(dados["processes"]), use_container_width=True)
                if dados.get("outputs"):
                    st.write("**Outputs**")
                    st.dataframe(pd.DataFrame(dados["outputs"]), use_container_width=True)
                if dados.get("lcc_materials"):
                    st.write("**LCC - Materiais**")
                    st.dataframe(pd.DataFrame(dados["lcc_materials"]), use_container_width=True)
                if dados.get("lcc_equipment"):
                    st.write("**LCC - Equipamentos**")
                    st.dataframe(pd.DataFrame(dados["lcc_equipment"]), use_container_width=True)
                if dados.get("lcc_labour"):
                    st.write("**LCC - Mão-de-obra**")
                    st.dataframe(pd.DataFrame(dados["lcc_labour"]), use_container_width=True)
                if dados.get("lcc_outputs"):
                    st.write("**LCC - Outputs**")
                    st.dataframe(pd.DataFrame(dados["lcc_outputs"]), use_container_width=True)
            with st.expander("Ver JSON bruto"):
                st.json(dados)

            if doc['estado'] == 'submetido':
                if st.button("Iniciar revisão"):
                    iniciar_revisao(doc['id'])
                    st.rerun()
            elif doc['estado'] == 'em_revisao':
                comentario = st.text_area("Comentário (obrigatório se pedir alterações)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Aprovar"):
                        aprovar(doc['id'])
                        st.rerun()
                with col2:
                    if st.button("🔄 Pedir alterações"):
                        if not comentario.strip():
                            st.error("É necessário um comentário para pedir alterações")
                        else:
                            pedir_alteracoes(doc['id'], comentario)
                            st.rerun()
            elif doc['estado'] == 'aprovado':
                st.success("Documento aprovado.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Reabrir para nova edição"):
                        reabrir(doc['id'])
                        st.rerun()
                with col2:
                    if st.button("📁 Arquivar documento"):
                        arquivar(doc['id'])
                        st.success("Documento arquivado.")
                        st.rerun()
            elif doc['estado'] == 'rascunho':
                st.info("O parceiro ainda está a editar.")
                if st.button("📁 Arquivar documento (rascunho)"):
                    arquivar(doc['id'])
                    st.success("Documento arquivado.")
                    st.rerun()
            elif doc['estado'] == 'alteracoes':
                st.warning("Aguardando o parceiro iniciar a edição.")
            elif doc['estado'] == 'arquivado':
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