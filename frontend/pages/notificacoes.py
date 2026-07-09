import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Notificações",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar a barra de navegação automática do Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticação
if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Por favor, faça login primeiro.")
    st.stop()

def headers_auth():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_notificacoes(limit=100):
    try:
        resp = requests.get(f"{API_URL}/notificacoes?limit={limit}", headers=headers_auth())
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Erro ao carregar notificações: {resp.status_code}")
            return []
    except Exception as e:
        st.error(f"Erro ao carregar notificações: {e}")
        return []

def marcar_todas_lidas():
    try:
        resp = requests.put(f"{API_URL}/notificacoes/ler-todas", headers=headers_auth())
        if resp.status_code == 200:
            count = resp.json().get("count", 0)
            st.success(f"✅ {count} notificações marcadas como lidas!")
            return True
        else:
            st.error(f"Erro ao marcar todas como lidas: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Erro ao marcar todas como lidas: {e}")
        return False

def marcar_como_lida(notificacao_id):
    try:
        resp = requests.put(f"{API_URL}/notificacoes/{notificacao_id}/ler", headers=headers_auth())
        if resp.status_code == 200:
            st.success("✅ Notificação marcada como lida!")
            return True
        else:
            st.error(f"Erro ao marcar como lida: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        st.error(f"Erro ao marcar como lida: {e}")
        return False

# Sidebar personalizada
st.sidebar.write(f"Logado como: **{st.session_state.username}** ({st.session_state.perfil})")

if st.sidebar.button("← Voltar", use_container_width=True):
    st.switch_page("app.py")

if st.sidebar.button("Logout"):
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
st.title("🔔 Notificações")

# Contador de não lidas
try:
    resp = requests.get(f"{API_URL}/notificacoes/nao-lidas", headers=headers_auth())
    if resp.status_code == 200:
        count = resp.json().get("count", 0)
        if count > 0:
            st.info(f"📌 Você tem {count} notificação(ões) não lida(s).")
        else:
            st.info("📌 Todas as notificações estão lidas.")
except:
    pass

# Botões de ação
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("← Voltar", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("📌 Marcar todas como lidas", use_container_width=True):
        if marcar_todas_lidas():
            st.rerun()

st.divider()

# Listar notificações
notificacoes = get_notificacoes(100)

if not notificacoes:
    st.info("📭 Nenhuma notificação encontrada.")
else:
    for notif in notificacoes:
        with st.container():
            col1, col2, col3 = st.columns([0.5, 8, 1.5])
            with col1:
                st.write(notif.get("icone", "📄"))
            with col2:
                if not notif.get("lida", False):
                    st.markdown(f"**🔵 {notif['titulo']}**")
                else:
                    st.markdown(f"**{notif['titulo']}**")
                st.write(notif['mensagem'])
                st.caption(f"📅 {notif['created_at']}")
            with col3:
                if not notif.get("lida", False):
                    if st.button("✓ Marcar lida", key=f"ler_{notif['id']}"):
                        if marcar_como_lida(notif['id']):
                            # Atualizar o contador de não lidas
                            st.rerun()
                else:
                    st.write("✅ Lida")
            
            # Link para o documento
            if notif.get("link"):
                # Extrair o ID do documento do link
                link = notif['link'].replace("/documentos?doc_id=", "")
                if link and st.button(f"🔗 Ver documento ID {link}", key=f"link_{notif['id']}"):
                    try:
                        st.session_state.doc_selecionado = int(link)
                        st.switch_page("app.py")
                    except:
                        pass
            
            st.divider()