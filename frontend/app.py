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

def listar_versoes(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/versoes", headers=headers_auth())
    if resp.status_code == 200:
        return resp.json()
    return []

# ---------- Interface ----------
if st.session_state.token is None:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if login(username, password):
                st.success("Login efetuado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    st.stop()

# Usuário logado
st.sidebar.write(f"Logado como: **{st.session_state.username}** ({st.session_state.perfil})")
if st.sidebar.button("Logout"):
    logout()
    st.rerun()

st.title("📄 Plataforma de Gestão de Documentos")

# ---------- Área do Parceiro ----------
if st.session_state.perfil == "parceiro":
    st.header("Área do Parceiro")
    menu = st.sidebar.radio("Menu", ["Meus Documentos", "Criar Documento"])

    if menu == "Criar Documento":
        with st.form("novo_doc"):
            titulo = st.text_input("Título do documento")
            campo1 = st.text_input("Campo 1")
            campo2 = st.text_area("Campo 2")
            submitted = st.form_submit_button("Criar")
            if submitted:
                dados = {"campo1": campo1, "campo2": campo2}
                novo = criar_documento(titulo, dados)
                st.success(f"Documento criado! ID: {novo['id']}")
                st.rerun()

    elif menu == "Meus Documentos":
        st.subheader("Os meus documentos")
        documentos = listar_documentos()
        if not documentos:
            st.info("Nenhum documento encontrado.")
        else:
            # Tabela com os documentos
            df = pd.DataFrame(documentos)
            df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Título", "Estado", "Versão", "Última atualização"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Selecionar documento para ver detalhes
            ids = [doc["id"] for doc in documentos]
            id_selecionado = st.selectbox("Seleciona um documento para ver detalhes:", ids, format_func=lambda x: f"ID {x}")
            if st.button("Carregar documento"):
                st.session_state.doc_selecionado = id_selecionado
                st.rerun()

        # Se um documento estiver selecionado, mostrar detalhes e ações
        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                st.divider()
                st.subheader(f"Documento ID {doc['id']}: {doc['titulo']}")
                st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")
                st.json(doc['dados'])

                if doc['estado'] == 'rascunho':
                    with st.form("editar_form"):
                        st.write("Editar dados")
                        campo1 = st.text_input("Campo 1", value=doc['dados'].get('campo1', ''))
                        campo2 = st.text_area("Campo 2", value=doc['dados'].get('campo2', ''))
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Guardar alterações"):
                                novos_dados = {"campo1": campo1, "campo2": campo2}
                                editar_documento(doc['id'], novos_dados)
                                st.success("Documento atualizado")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Submeter para validação"):
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
                    if st.button("✏️ Editar novamente"):
                        editar_novamente(doc['id'])
                        st.rerun()
                elif doc['estado'] == 'aprovado':
                    st.success("Documento aprovado. Não pode ser editado.")
                elif doc['estado'] in ['submetido', 'em_revisao']:
                    st.info("Documento em análise pela empresa.")

                with st.expander("Histórico de versões"):
                    versoes = listar_versoes(doc['id'])
                    for v in versoes:
                        st.write(f"v{v['numero_versao']} - {v['estado']} por {v['criado_por']} em {v['created_at']}")
                        if v['comentario']:
                            st.caption(f"  Comentário: {v['comentario']}")

                if st.button("Fechar detalhes"):
                    st.session_state.doc_selecionado = None
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
        st.dataframe(df, use_container_width=True, hide_index=True)

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
            st.json(doc['dados'])

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
                if st.button("Reabrir para nova edição"):
                    reabrir(doc['id'])
                    st.rerun()
            elif doc['estado'] == 'alteracoes':
                st.warning("Aguardando o parceiro iniciar a edição.")
            elif doc['estado'] == 'rascunho':
                st.info("O parceiro ainda está a editar.")

            with st.expander("Histórico de versões"):
                versoes = listar_versoes(doc['id'])
                for v in versoes:
                    st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']})")
                    if v['comentario']:
                        st.caption(f"  Comentário: {v['comentario']}")

            if st.button("Fechar detalhes"):
                st.session_state.doc_selecionado = None
                st.rerun()