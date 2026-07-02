import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Plataforma Documentos", layout="wide")
st.title("📄 Plataforma de Gestão de Documentos")

perfil = st.sidebar.radio("Seleciona o perfil", ("Parceiro", "Empresa"))

def criar_documento(titulo, parceiro_id, dados):
    resp = requests.post(f"{API_URL}/documentos/", json={
        "titulo": titulo,
        "parceiro_id": parceiro_id,
        "dados": dados
    })
    return resp.json()

def obter_documento(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}")
    if resp.status_code == 200:
        return resp.json()
    return None

def editar_documento(doc_id, dados):
    resp = requests.put(f"{API_URL}/documentos/{doc_id}/editar", json={"dados": dados})
    return resp.json()

def submeter(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/submeter")
    return resp.json()

def iniciar_revisao(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/iniciar-revisao")
    return resp.json()

def pedir_alteracoes(doc_id, comentario):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/pedir-alteracoes", json={"comentario": comentario})
    return resp.json()

def editar_novamente(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/editar-novamente")
    return resp.json()

def aprovar(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/aprovar")
    return resp.json()

def reabrir(doc_id):
    resp = requests.post(f"{API_URL}/documentos/{doc_id}/reabrir")
    return resp.json()

def listar_versoes(doc_id):
    resp = requests.get(f"{API_URL}/documentos/{doc_id}/versoes")
    if resp.status_code == 200:
        return resp.json()
    return []

if perfil == "Parceiro":
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
                novo = criar_documento(titulo, parceiro_id="parceiro1", dados=dados)
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
                                atualizado = editar_documento(doc_id_input, novos_dados)
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
                st.error("Documento não encontrado")

elif perfil == "Empresa":
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
            st.error("Documento não encontrado")