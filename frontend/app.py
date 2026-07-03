import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Plataforma Documentos", layout="wide")

# Inicializar estado da sessão
if "token" not in st.session_state:
    st.session_state.token = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "username" not in st.session_state:
    st.session_state.username = None

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

# Funções auxiliares para chamadas autenticadas
def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

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

if st.session_state.perfil == "parceiro":
    st.header("Área do Parceiro")
    menu = st.sidebar.radio("Ação", ["Criar Documento", "Meus Documentos"])
    if menu == "Criar Documento":
        with st.form("novo_doc"):
            titulo = st.text_input("Título do documento")
            campo1 = st.text_input("Campo 1")
            campo2 = st.text_area("Campo 2")
            submitted = st.form_submit_button("Criar")
            if submitted:
                dados = {"campo1": campo1, "campo2": campo2}
                novo = criar_documento(titulo, dados)
                st.success(f"Documento criado! ID: {novo['id'][:8]}...")
    else:
        doc_id_input = st.text_input("ID do documento")
        if doc_id_input:
            doc = obter_documento(doc_id_input)
            if doc:
                st.subheader(f"Documento: {doc['titulo']}")
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
                                editar_documento(doc_id_input, novos_dados)
                                st.success("Documento atualizado")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Submeter para validação"):
                                submeter(doc_id_input)
                                st.success("Documento submetido!")
                                st.rerun()
                elif doc['estado'] == 'alteracoes':
                    st.warning("A empresa pediu alterações. Vê os comentários abaixo.")
                    versoes = listar_versoes(doc_id_input)
                    if versoes:
                        ultima = versoes[-1]
                        if ultima['comentario']:
                            st.info(f"Motivo: {ultima['comentario']}")
                    if st.button("✏️ Editar novamente"):
                        editar_novamente(doc_id_input)
                        st.rerun()
                elif doc['estado'] == 'aprovado':
                    st.success("Documento aprovado. Não pode ser editado.")
                elif doc['estado'] in ['submetido', 'em_revisao']:
                    st.info("Documento em análise pela empresa.")

                with st.expander("Histórico de versões"):
                    versoes = listar_versoes(doc_id_input)
                    for v in versoes:
                        st.write(f"v{v['numero_versao']} - {v['estado']} por {v['criado_por']} em {v['created_at']}")
                        if v['comentario']:
                            st.caption(f"  Comentário: {v['comentario']}")
            else:
                st.error("Documento não encontrado ou acesso negado")

elif st.session_state.perfil in ["empresa", "admin"]:
    st.header("Área da Empresa (Validação)")
    doc_id_input = st.text_input("ID do documento a validar")
    if doc_id_input:
        doc = obter_documento(doc_id_input)
        if doc:
            st.subheader(f"Documento: {doc['titulo']} (Parceiro: {doc['parceiro_id']})")
            st.write(f"Estado: **{doc['estado']}** | Versão: {doc['versao_atual']}")
            st.json(doc['dados'])

            if doc['estado'] == 'submetido':
                if st.button("Iniciar revisão"):
                    iniciar_revisao(doc_id_input)
                    st.rerun()
            elif doc['estado'] == 'em_revisao':
                comentario = st.text_area("Comentário (obrigatório se pedir alterações)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Aprovar"):
                        aprovar(doc_id_input)
                        st.rerun()
                with col2:
                    if st.button("🔄 Pedir alterações"):
                        if not comentario.strip():
                            st.error("É necessário um comentário para pedir alterações")
                        else:
                            pedir_alteracoes(doc_id_input, comentario)
                            st.rerun()
            elif doc['estado'] == 'aprovado':
                st.success("Documento aprovado.")
                if st.button("Reabrir para nova edição"):
                    reabrir(doc_id_input)
                    st.rerun()
            elif doc['estado'] == 'alteracoes':
                st.warning("Aguardando o parceiro iniciar a edição.")
            elif doc['estado'] == 'rascunho':
                st.info("O parceiro ainda está a editar.")

            with st.expander("Histórico"):
                versoes = listar_versoes(doc_id_input)
                for v in versoes:
                    st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']})")
        else:
            st.error("Documento não encontrado ou acesso negado")