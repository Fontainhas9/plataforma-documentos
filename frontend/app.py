import streamlit as st
import requests
import pandas as pd
import copy
from datetime import datetime
import os
import base64

# ============================================================
# API URL CONFIGURATION
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
    
    # Usar a URL do Render em produção
    return "https://plataforma-documentos-backend.onrender.com"

API_URL = get_api_url()

# Default processes
PROCESSOS_PADRAO = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = ["Measured", "Calculated", "Estimated", "Literature"]

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Document Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS GLOBAL - GARANTIR VISIBILIDADE
# ============================================================
st.markdown("""
<style>
    /* REMOVER BORDAS BRANCAS */
    .stApp {
        background: transparent !important;
    }
    .stAppViewContainer {
        background: transparent !important;
    }
    .main > div {
        padding: 0 !important;
        max-width: 100% !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarUserContent"] { display: none !important; }
    .stApp > header { display: none !important; }
    .stAppHeader, .stDecoration { display: none !important; }
    .st-emotion-cache-1r6slb0 { padding: 0 !important; margin: 0 !important; }
    
    /* FORÇAR TODOS OS WIDGETS A APARECEREM */
    .stTextInput { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stTextInput > div { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stTextInput > div > div { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stTextInput > div > div > input { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stButton { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stButton > button { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stForm { display: block !important; visibility: visible !important; opacity: 1 !important; }
    .stAlert { display: block !important; visibility: visible !important; opacity: 1 !important; }
    
    /* GARANTIR QUE O LOGIN APARECE */
    .login-wrapper {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
        width: 100% !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: linear-gradient(180deg, #0a2f57 0%, #15528d 100%) !important;
        z-index: 999999 !important;
        margin: 0 !important;
        padding: 20px !important;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.94) !important;
        border-radius: 28px !important;
        padding: 30px 30px 26px !important;
        max-width: 440px !important;
        width: 100% !important;
        box-shadow: 0 24px 48px rgba(5, 20, 40, 0.22) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    .login-brand {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        margin-bottom: 24px !important;
    }
    .login-brand-logo {
        width: 58px !important;
        height: 58px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: white !important;
        flex-shrink: 0 !important;
    }
    .login-brand-logo img {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        display: block !important;
    }
    .login-brand-text h2 {
        margin: 0 0 4px !important;
        font-size: 30px !important;
        line-height: 1.1 !important;
        font-weight: 800 !important;
        color: #123b72 !important;
    }
    .login-brand-text p {
        margin: 0 !important;
        font-size: 14px !important;
        color: #5f6f86 !important;
        line-height: 1.4 !important;
    }
    
    /* INPUTS */
    .login-card .stTextInput > div > div > input {
        height: 50px !important;
        border-radius: 12px !important;
        border: 1px solid #d2d9e3 !important;
        font-size: 15px !important;
        padding: 0 14px !important;
        background: #ffffff !important;
        color: #21344d !important;
        width: 100% !important;
    }
    .login-card .stTextInput > div > div > input:focus {
        border-color: #003662 !important;
        box-shadow: 0 0 0 4px rgba(55, 113, 176, 0.14) !important;
        outline: none !important;
    }
    .login-card .stTextInput label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #123b72 !important;
        margin-bottom: 6px !important;
    }
    
    /* BOTÃO */
    .login-card .stButton > button {
        width: 100% !important;
        height: 50px !important;
        border: none !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #003662 0%, #295d96 100%) !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        box-shadow: 0 12px 24px rgba(41, 93, 150, 0.26) !important;
        margin-top: 6px !important;
    }
    .login-card .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 16px 28px rgba(41, 93, 150, 0.32) !important;
    }
    
    /* ALERTAS */
    .login-card .stAlert {
        margin-top: 12px !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    
    @media (max-width: 768px) {
        .login-card { padding: 24px 18px 22px !important; border-radius: 22px !important; }
        .login-brand-logo { width: 50px !important; height: 50px !important; }
        .login-brand-text h2 { font-size: 24px !important; }
        .login-card .stTextInput > div > div > input { height: 48px !important; }
        .login-card .stButton > button { height: 48px !important; }
    }
    @media (max-width: 480px) {
        .login-brand { align-items: flex-start !important; }
        .login-brand-text h2 { font-size: 22px !important; }
        .login-brand-text p { font-size: 13px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INICIALIZAÇÃO DAS VARIÁVEIS DE SESSÃO
# ============================================================
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
# ... (resto das variáveis de sessão)

# ============================================================
# LOGIN SCREEN - COM BACKEND NO RENDER
# ============================================================
if st.session_state.token is None:
    import streamlit.components.v1 as components
    import base64
    import os
    
    # Verificar se o login foi bem-sucedido via query param
    if st.query_params.get("login_success") == "true":
        st.query_params.clear()
        st.rerun()
    
    # Ler a imagem do ficheiro e converter para Base64
    img_path = os.path.join(os.path.dirname(__file__), 'img', 'HOLOSSORIGINAL.png')
    
    logo_base64 = ""
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    
    # URL DO BACKEND NO RENDER (NÃO LOCALHOST!)
    backend_url = "https://plataforma-documentos-backend.onrender.com"
    
    # HTML do login
    login_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{ width: 100%; height: 100%; margin: 0 !important; padding: 0 !important; font-family: "Inter", sans-serif; overflow: hidden !important; background: transparent !important; }}
        :root {{
            --login-bg-top: #0a2f57; --login-bg-bottom: #15528d; --login-card-bg: rgba(255,255,255,0.94);
            --login-card-border: rgba(255,255,255,0.18); --login-title: #123b72; --login-text: #5f6f86;
            --login-input-border: #d2d9e3; --login-input-bg: #ffffff; --login-button: rgb(0,54,98);
            --login-button-hover: rgb(41,93,150); --login-shadow: 0 24px 48px rgba(5,20,40,0.22);
            --login-radius-xl: 28px; --login-radius-md: 12px;
        }}
        .login-page {{ width: 100vw; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 32px 20px; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, #0a2f57 0%, #15528d 100%); overflow: hidden !important; margin: 0 !important; z-index: 9999999; }}
        .login-container {{ width: 100%; max-width: 520px; position: relative; z-index: 1; }}
        .login-box {{ background: var(--login-card-bg); border: 1px solid var(--login-card-border); border-radius: var(--login-radius-xl); padding: 30px 30px 26px; box-shadow: var(--login-shadow); backdrop-filter: blur(8px); }}
        .login-box__brand {{ display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }}
        .login-box__logo {{ width: 58px; height: 58px; object-fit: contain; flex-shrink: 0; border-radius: 12px; overflow: hidden; background: white; }}
        .login-box__logo img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
        .login-box__brand-text h2 {{ margin: 0 0 4px; font-size: 30px; line-height: 1.1; font-weight: 800; color: var(--login-title); }}
        .login-box__brand-text p {{ margin: 0; font-size: 14px; color: var(--login-text); line-height: 1.4; }}
        .login-form {{ display: flex; flex-direction: column; gap: 16px; }}
        .input-group {{ display: flex; flex-direction: column; gap: 7px; }}
        .input-group label {{ font-size: 14px; font-weight: 600; color: var(--login-title); }}
        .input-group input {{ width: 100%; height: 50px; padding: 0 14px; border-radius: var(--login-radius-md); border: 1px solid var(--login-input-border); background: var(--login-input-bg); color: #21344d; font-size: 15px; box-sizing: border-box; font-family: "Inter", sans-serif; }}
        .input-group input:focus {{ outline: none; border-color: var(--login-button); box-shadow: 0 0 0 4px rgba(55,113,176,0.14); }}
        .login-btn {{ margin-top: 6px; height: 50px; border: none; border-radius: var(--login-radius-md); background: linear-gradient(135deg, var(--login-button) 0%, var(--login-button-hover) 100%); color: #ffffff; font-size: 16px; font-weight: 700; cursor: pointer; box-shadow: 0 12px 24px rgba(41,93,150,0.26); font-family: "Inter", sans-serif; width: 100%; }}
        .login-btn:hover {{ transform: translateY(-1px); box-shadow: 0 16px 28px rgba(41,93,150,0.32); }}
        .login-btn:disabled {{ opacity: 0.7; cursor: not-allowed; }}
        .login-error {{ min-height: 22px; margin: 16px 0 0; font-size: 14px; font-weight: 500; color: #c0392b; display: none; font-family: "Inter", sans-serif; }}
        .login-error.show {{ display: block; }}
        @media (max-width: 768px) {{ .login-box {{ padding: 24px 18px 22px; border-radius: 22px; }} .login-box__brand {{ gap: 12px; margin-bottom: 20px; }} .login-box__logo {{ width: 50px; height: 50px; }} .login-box__brand-text h2 {{ font-size: 24px; }} .input-group input, .login-btn {{ height: 48px; }} }}
    </style>
    </head>
    <body>
        <div class="login-page">
            <div class="login-container">
                <div class="login-box">
                    <div class="login-box__brand">
                        <div class="login-box__logo">
                            <img src="data:image/png;base64,{logo_base64}" alt="Holoss" />
                        </div>
                        <div class="login-box__brand-text">
                            <h2>Document Platform</h2>
                            <p>Sign in to continue</p>
                        </div>
                    </div>
                    <form id="loginForm" class="login-form" novalidate>
                        <div class="input-group">
                            <label for="username">Username</label>
                            <input type="text" id="username" placeholder="Enter your username" required />
                        </div>
                        <div class="input-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" placeholder="Enter your password" required />
                        </div>
                        <button type="submit" id="loginButton" class="login-btn">Log in</button>
                    </form>
                    <p id="errorMsg" class="login-error"></p>
                </div>
            </div>
        </div>
        <script>
        (function() {{
            const API_URL = '{backend_url}';
            
            document.getElementById('loginForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                var username = document.getElementById('username').value.trim();
                var password = document.getElementById('password').value.trim();
                var errorMsg = document.getElementById('errorMsg');
                var loginBtn = document.getElementById('loginButton');
                
                errorMsg.classList.remove('show');
                errorMsg.textContent = '';
                
                if (!username || !password) {{
                    errorMsg.textContent = 'Please enter both username and password.';
                    errorMsg.classList.add('show');
                    return;
                }}
                
                loginBtn.disabled = true;
                loginBtn.textContent = 'Signing in...';
                
                fetch(API_URL + '/login', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                    body: 'username=' + encodeURIComponent(username) + '&password=' + encodeURIComponent(password)
                }})
                .then(function(response) {{
                    if (!response.ok) {{
                        return response.text().then(function(text) {{ throw new Error(text || 'Invalid credentials'); }});
                    }}
                    return response.json();
                }})
                .then(function(data) {{
                    if (data.access_token) {{
                        window.location.href = '?login_success=true&token=' + encodeURIComponent(data.access_token) + '&username=' + encodeURIComponent(username);
                    }} else {{
                        errorMsg.textContent = 'Invalid credentials. Please try again.';
                        errorMsg.classList.add('show');
                        loginBtn.disabled = false;
                        loginBtn.textContent = 'Log in';
                    }}
                }})
                .catch(function(error) {{
                    errorMsg.textContent = error.message || 'Connection error. Please check if the server is running.';
                    errorMsg.classList.add('show');
                    loginBtn.disabled = false;
                    loginBtn.textContent = 'Log in';
                }});
            }});
        }})();
        </script>
    </body>
    </html>
    '''
    
    # Renderizar o HTML
    components.html(login_html, height=800, scrolling=False)
    
    # Processar o login a partir dos query params
    if st.query_params.get("login_success") == "true":
        token = st.query_params.get("token")
        username = st.query_params.get("username")
        
        if token and username:
            st.session_state.token = token
            st.session_state.username = username
            
            # Buscar o perfil do usuário
            try:
                headers = {"Authorization": f"Bearer {token}"}
                me = requests.get(f"{backend_url}/me", headers=headers)
                if me.status_code == 200:
                    user_info = me.json()
                    st.session_state.perfil = user_info["perfil"]
                    st.query_params.clear()
                    st.rerun()
            except Exception as e:
                print(f"Erro ao buscar perfil: {e}")
    
    st.stop()
    
# ============================================================
# A PARTIR DAQUI O UTILIZADOR ESTÁ AUTENTICADO
# ============================================================

# Mostrar mensagem de sucesso
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

# Processar abertura de documento a partir de notificações
if "doc_id" in st.query_params and st.query_params["doc_id"]:
    try:
        doc_id = int(st.query_params["doc_id"])
        st.session_state.doc_selecionado = doc_id
        st.query_params.clear()
    except ValueError:
        pass

if st.session_state.redirect_to_docs:
    st.session_state.menu_parceiro_widget = "My Documents"
    st.session_state.redirect_to_docs = False

if st.session_state.get("close_doc_after_action", False):
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False

# Verificar novas notificações
if st.session_state.token is not None:
    verificar_novas_notificacoes()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.username}**")
    st.divider()
    
    if st.session_state.token is not None:
        try:
            count = get_notificacoes_nao_lidas()
            if count > 0:
                st.warning(f"🔔 {count} unread notification{'s' if count > 1 else ''}")
            else:
                st.info("🔔 No notifications")
        except:
            pass
    
    st.divider()
    
    if st.session_state.perfil == "admin":
        if st.button("Dashboard", use_container_width=True, key="app_dashboard"):
            st.switch_page("pages/dashboard.py")
    
    if st.button("Notifications", use_container_width=True, key="app_notificacoes"):
        st.switch_page("pages/notificacoes.py")
    
    st.divider()
    
    if st.button("Logout", use_container_width=True, key="app_logout"):
        logout()
        st.rerun()

st.title("Document Management Platform")


# ============================================================
# PARTNER AREA
# ============================================================
if st.session_state.perfil == "parceiro":
    st.header("Partner Area")
    st.caption("Documents are created by the company. You only fill in the data and submit.")
    
    st.subheader("My Documents")
    
    if st.button("Refresh list", key="refresh_list_parceiro"):
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
        st.session_state.parceiro_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos()
    if not documentos:
        st.info("No documents found. Wait for the company to create a document for you.")
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Title", "Status", "Version", "Last Update"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]

        id_selecionado = st.selectbox(
            "Select a document:",
            ids,
            format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
            key=f"parceiro_selectbox_{st.session_state.parceiro_dropdown_key}",
            placeholder="Choose an option"
        )

        if st.button("Load document", key="parceiro_carregar_doc"):
            if not id_selecionado:
                st.warning("Please select a document.")
            else:
                st.session_state.doc_selecionado = id_selecionado
                st.session_state.expander_aberto = False
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            st.subheader(f"Document ID {doc['id']}: {doc['titulo']}")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")
            st.caption(f"Created by: {doc.get('empresa_id', 'N/A')}")
            
            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            with st.expander("View data in tables", expanded=st.session_state.get("expander_aberto", False)):
                st.subheader("LCA")
                lca = dados.get("lca", {})
                for proc in processos:
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
                for proc in processos:
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

            with st.expander("View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            estado_doc = doc.get('estado', '')
            is_draft = estado_doc in ["Draft", "Rascunho"]
            
            if is_draft:
                st.subheader("✏️ Edit Document")
                st.info("Fill in the data below and submit for validation.")
                
                if st.session_state.edit_data is None:
                    st.session_state.edit_data = ensure_new_structure(safe_copy(dados), processos)
                render_full_form("edit_data", prefix="edit_", processos=processos)
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("💾 Save Draft", key="parceiro_save_edit", use_container_width=True):
                        try:
                            novos_dados = st.session_state.edit_data
                            resultado = editar_documento(doc['id'], novos_dados)
                            if resultado:
                                st.session_state.edit_data = None
                                st.session_state.doc_selecionado = None
                                st.session_state.expander_aberto = False
                                st.session_state.close_doc_after_action = True
                                st.success("✅ Document updated successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {str(e)}")
                with col_btn2:
                    if st.button("📤 Submit for Review", key="parceiro_submeter", use_container_width=True):
                        try:
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                resultado_sub = submeter(doc['id'])
                                if resultado_sub:
                                    st.session_state.edit_data = None
                                    st.session_state.doc_selecionado = None
                                    st.session_state.expander_aberto = False
                                    st.session_state.close_doc_after_action = True
                                    st.success("✅ Document submitted successfully!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting: {str(e)}")
                with col_btn3:
                    if st.button("✖ Close", key="parceiro_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.edit_data = None
                        st.session_state.expander_aberto = False
                        st.rerun()

            else:
                st.subheader("📄 View Document")
                st.info(f"This document is in status: **{estado_doc}**")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                if estado_doc in ["Changes Requested", "Alterações"]:
                    with col_btn1:
                        st.warning("⚠️ The company has requested changes.")
                        versoes = listar_versoes(doc['id'])
                        if versoes:
                            ultima = versoes[-1]
                            if ultima['comentario']:
                                st.info(f"Reason: {ultima['comentario']}")
                        if st.button("✏️ Edit again", key="parceiro_editar_novamente", use_container_width=True):
                            if editar_novamente(doc['id']):
                                st.rerun()
                elif estado_doc in ["Approved", "Aprovado"]:
                    with col_btn1:
                        st.success("✅ Document approved. Cannot be edited.")
                elif estado_doc in ["Submitted", "Submetido", "In Review", "Em Revisão"]:
                    with col_btn1:
                        st.info("📋 Document under review by the company.")
                elif estado_doc in ["Archived", "Arquivado"]:
                    with col_btn1:
                        st.warning("📁 Document archived (view only).")
                else:
                    with col_btn1:
                        st.info(f"Document is in status: {estado_doc}")
                
                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label="📊 Export History",
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_parceiro_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )
                
                with col_btn3:
                    if st.button("✖ Close", key="parceiro_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.edit_data = None
                        st.session_state.expander_aberto = False
                        st.rerun()

            st.markdown("---")

            with st.expander("Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} by {v['criado_por']} at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ============================================================
# COMPANY AREA
# ============================================================
elif st.session_state.perfil == "empresa":
    st.header("Company Area (Validation)")
    
    if "empresa_mostrar_form" not in st.session_state:
        st.session_state.empresa_mostrar_form = False
    
    if not st.session_state.empresa_mostrar_form:
        if st.button("➕ Create new document for partner", use_container_width=True, key="empresa_abrir_form"):
            st.session_state.empresa_mostrar_form = True
            st.rerun()
    else:
        with st.container():
            st.subheader("Create Document")
            st.info("The company creates the document skeleton. The partner will fill in the data later.")
            
            form_key = st.session_state.get("empresa_form_key", 0)
            
            titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"empresa_titulo_{form_key}")
            
            parceiros = listar_parceiros_disponiveis()
            
            if not parceiros:
                st.warning("No partners available. Create a partner first in the Admin area.")
                if st.button("🔄 Reload partner list"):
                    st.rerun()
                if st.button("✖ Close", key="empresa_fechar_sem_parceiros"):
                    st.session_state.empresa_mostrar_form = False
                    st.rerun()
            else:
                parceiro_selecionado = st.selectbox(
                    "Select Partner",
                    options=[""] + [p["username"] for p in parceiros],
                    format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                    placeholder="Select a partner from the list",
                    key=f"empresa_parceiro_{form_key}"
                )
                
                st.info("Select the processes that will be available in this document for the partner to fill in.")
                processos_selecionados = render_processos_selecao(key_prefix=f"empresa_{form_key}")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn1:
                    if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                        if st.button("✅ Create Document", key=f"empresa_create_doc_btn_{form_key}", use_container_width=True):
                            if not titulo.strip():
                                st.error("Title is required.")
                            else:
                                try:
                                    dados = ensure_new_structure({}, processos_selecionados)
                                    novo = criar_documento(titulo, parceiro_selecionado, dados)
                                    if novo:
                                        st.session_state.empresa_form_key = form_key + 1
                                        session_key = f"processos_selecionados_empresa_{form_key}"
                                        if session_key in st.session_state:
                                            del st.session_state[session_key]
                                        st.session_state.empresa_mostrar_form = False
                                        st.session_state.success_message = f"Document created successfully! ID: {novo['id']}"
                                        st.session_state.new_data = None
                                        st.session_state.doc_selecionado = None
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating document: {str(e)}")
                    elif processos_selecionados and (not parceiro_selecionado or parceiro_selecionado == ""):
                        st.warning("Please select a partner to continue.")
                    elif parceiro_selecionado and parceiro_selecionado != "" and not processos_selecionados:
                        st.warning("Please select at least one process to continue.")
                
                with col_btn2:
                    if st.button("❌ Cancel", key=f"empresa_cancel_btn_{form_key}", use_container_width=True):
                        session_key = f"processos_selecionados_empresa_{form_key}"
                        if session_key in st.session_state:
                            del st.session_state[session_key]
                        st.session_state.empresa_mostrar_form = False
                        st.rerun()
                
                with col_btn3:
                    if st.button("✖ Close", key=f"empresa_fechar_btn_{form_key}", use_container_width=True):
                        session_key = f"processos_selecionados_empresa_{form_key}"
                        if session_key in st.session_state:
                            del st.session_state[session_key]
                        st.session_state.empresa_mostrar_form = False
                        st.rerun()
        
        st.divider()
    
    st.divider()
    
    st.subheader("Available Documents")
    
    with st.expander("Search Filters", expanded=False):
        col1, col2 = st.columns(2)
        key_suffix = st.session_state.filtros_widget_key
        
        with col1:
            q = st.text_input("Search", value=st.session_state.filtros_temporarios.get("q", ""), placeholder="Title, partner or ID...", key=f"filtro_q_{key_suffix}")
            st.session_state.filtros_temporarios["q"] = q
            estados_disponiveis = ["Draft", "Submitted", "In Review", "Changes Requested", "Approved", "Archived"]
            estados_selecionados = st.multiselect("Status", options=estados_disponiveis, default=st.session_state.filtros_temporarios.get("estados", []), key=f"filtro_estados_{key_suffix}")
            st.session_state.filtros_temporarios["estados"] = estados_selecionados
        
        with col2:
            data_inicio = st.date_input("Start Date", value=st.session_state.filtros_temporarios.get("data_inicio"), format="DD/MM/YYYY", key=f"filtro_data_inicio_{key_suffix}")
            st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
            data_fim = st.date_input("End Date", value=st.session_state.filtros_temporarios.get("data_fim"), format="DD/MM/YYYY", key=f"filtro_data_fim_{key_suffix}")
            st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
        
        col5, col6 = st.columns(2)
        with col5:
            if st.button("Apply Filters", use_container_width=True):
                st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                st.rerun()
        with col6:
            if st.button("Clear Filters", use_container_width=True):
                st.session_state.filtros_temporarios = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                st.session_state.filtros_aplicados = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                st.session_state.filtros_widget_key += 1
                st.rerun()
    
    if st.button("Refresh list", key="refresh_list_empresa"):
        st.session_state.doc_selecionado = None
        st.session_state.empresa_dropdown_key += 1
        st.session_state.refresh_counter += 1
        st.rerun()
    st.write("")

    documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
    if not documentos:
        st.info("No documents found with the current filters.")
    else:
        df = pd.DataFrame(documentos)
        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
        df.columns = ["ID", "Title", "Partner", "Status", "Version", "Last Update"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        ids = [""] + [doc["id"] for doc in documentos]

        id_selecionado = st.selectbox(
            "Select a document:",
            ids,
            format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
            key=f"empresa_selectbox_{st.session_state.empresa_dropdown_key}",
            placeholder="Choose an option"
        )

        if st.button("Load document", key="empresa_carregar_doc"):
            if not id_selecionado:
                st.warning("Please select a document.")
            else:
                st.session_state.doc_selecionado = id_selecionado
                st.session_state.expander_aberto = False
                trigger_scroll(id_selecionado)
                st.rerun()

    if st.session_state.doc_selecionado:
        doc = obter_documento(st.session_state.doc_selecionado)
        if doc:
            create_document_anchor(doc['id'])
            
            st.divider()
            st.subheader(f"Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            with st.expander("View document data", expanded=st.session_state.get("expander_aberto", False)):
                st.subheader("LCA")
                lca = dados.get("lca", {})
                for proc in processos:
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
                for proc in processos:
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

            with st.expander("View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            if doc['estado'] in ["Submitted", "Submetido"]:
                with col_btn1:
                    if st.button("Start Review", key="empresa_iniciar_revisao", use_container_width=True):
                        if iniciar_revisao(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["In Review", "Em Revisão"]:
                comentario = st.text_area("Comment (required if requesting changes)", key="empresa_comentario")
                col_aprov, col_alt = st.columns(2)
                with col_aprov:
                    if st.button("Approve", key="empresa_aprovar", use_container_width=True):
                        if aprovar(doc['id']):
                            st.rerun()
                with col_alt:
                    if st.button("Request Changes", key="empresa_pedir_alteracoes", use_container_width=True):
                        if not comentario.strip():
                            st.error("A comment is required to request changes")
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.rerun()
            elif doc['estado'] in ["Approved", "Aprovado"]:
                with col_btn1:
                    if st.button("Reopen", key="empresa_reabrir", use_container_width=True):
                        if reabrir(doc['id']):
                            st.rerun()
                with col_btn2:
                    if st.button("Archive", key="empresa_arquivar", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Draft", "Rascunho"]:
                with col_btn1:
                    if st.button("Archive (draft)", key="empresa_arquivar_rascunho", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Changes Requested", "Alterações"]:
                with col_btn1:
                    st.info("Waiting for partner to edit again.")
            elif doc['estado'] in ["Archived", "Arquivado"]:
                with col_btn1:
                    st.warning("Document archived (view only).")

            with col_btn2:
                conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                if conteudo:
                    st.download_button(
                        label="Export History",
                        data=conteudo,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_empresa_{doc['id']}_{st.session_state.refresh_counter}",
                        use_container_width=True
                    )

            with col_btn3:
                if st.button("Close details", key="empresa_fechar_detalhes", use_container_width=True):
                    st.session_state.doc_selecionado = None
                    st.session_state.expander_aberto = False
                    st.rerun()

            st.markdown("---")

            with st.expander("Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']}) at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ============================================================
# ADMIN AREA
# ============================================================
elif st.session_state.perfil == "admin":
    st.header("Administrative Panel")
    menu_admin = st.sidebar.radio("Admin", ["Users", "Documents (company)"], key="admin_menu")

    if menu_admin == "Users":
        st.subheader("User Management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Load users", use_container_width=True, key="admin_carregar_users"):
                st.session_state.doc_selecionado = None
                st.session_state.admin_user_dropdown_key += 1
                st.session_state.refresh_counter += 1
                st.rerun()
        with col2:
            if st.button("New User", use_container_width=True, key="admin_novo_user"):
                st.session_state.show_create_user_form = not st.session_state.show_create_user_form
                st.rerun()
        
        st.write("")
        
        if st.session_state.show_create_user_form:
            st.divider()
            st.subheader("Create New User")
            
            with st.form("create_user_form"):
                new_username = st.text_input("Username *", placeholder="Ex: new_partner")
                new_password = st.text_input("Password *", type="password", placeholder="Minimum 3 characters")
                new_nome = st.text_input("Full Name", placeholder="Ex: John Doe")
                new_perfil = st.selectbox(
                    "Profile *",
                    options=["parceiro", "empresa", "admin"],
                    format_func=lambda x: {"parceiro": "Partner", "empresa": "Company", "admin": "Admin"}.get(x, x),
                    placeholder="Choose an option"
                )
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    submit_create = st.form_submit_button("Create User", use_container_width=True)
                with col2:
                    cancel_create = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancel_create:
                    st.session_state.show_create_user_form = False
                    st.rerun()
                
                if submit_create:
                    if not new_username.strip():
                        st.error("Username is required")
                    elif not new_password.strip() or len(new_password.strip()) < 3:
                        st.error("Password is required and must be at least 3 characters")
                    elif not new_perfil:
                        st.error("Profile is required")
                    else:
                        resp_check = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
                        if resp_check.status_code == 200:
                            users_existentes = resp_check.json()
                            if any(u["username"] == new_username for u in users_existentes):
                                st.error(f"Username '{new_username}' already exists!")
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
                                        st.toast(f"User '{new_username}' created successfully!", icon="✅")
                                        st.session_state.show_create_user_form = False
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_create.json().get("detail", "Unknown error")
                                        except:
                                            erro = resp_create.text
                                        st.error(f"Error creating user: {erro}")
                                except Exception as e:
                                    st.error(f"Error creating user: {str(e)}")
                        else:
                            st.error("Error checking existing users")
            
            st.divider()
        
        resp = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth())
        if resp.status_code == 200:
            users = resp.json()
            if users:
                for user in users:
                    if user["perfil"] == "empresa":
                        user["perfil"] = "Company"
                    elif user["perfil"] == "parceiro":
                        user["perfil"] = "Partner"
                    elif user["perfil"] == "admin":
                        user["perfil"] = "Admin"
                
                df = pd.DataFrame(users)
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_disponiveis = df.columns.tolist()
                colunas_desejadas = ["username", "perfil", "nome_completo", "created_at"]
                colunas_existentes = [col for col in colunas_desejadas if col in cols_disponiveis]
                df = df[colunas_existentes]
                df.columns = ["Username", "Profile", "Name", "Created At"]
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                
                st.subheader("Manage User")
                
                usernames = [""] + [u["username"] for u in users]

                sel_user = st.selectbox(
                    "Select user to manage",
                    usernames,
                    format_func=lambda x: "Select a user..." if x == "" else x,
                    key=f"admin_user_selectbox_{st.session_state.admin_user_dropdown_key}",
                    placeholder="Choose an option"
                )

                if sel_user:
                    user_data = next((u for u in users if u["username"] == sel_user), None)
                    if user_data:
                        st.info(f"**Username:** {user_data['username']} | **Profile:** {user_data['perfil']} | **Name:** {user_data['nome_completo']}")
                    
                    st.subheader("Change Password")
                    pw_key = f"admin_pw_input_{st.session_state.pw_input_counter}"
                    nova_pw = st.text_input("New password (leave empty to keep current)", type="password", key=pw_key, placeholder="Enter new password...")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("Change Password", key="btn_alterar_pw", use_container_width=True):
                            if not sel_user:
                                st.warning("Please select a user.")
                            elif not nova_pw.strip():
                                st.warning("Please enter a new password")
                            elif len(nova_pw.strip()) < 3:
                                st.warning("Password must be at least 3 characters")
                            else:
                                resp_pw = requests.put(
                                    f"{API_URL}/admin/usuarios/{sel_user}/password",
                                    json={"nova_password": nova_pw},
                                    headers=headers_auth()
                                )
                                if resp_pw.status_code == 200:
                                    st.toast(f"✅ Password for '{sel_user}' changed successfully!", icon="✅")
                                    st.session_state.pw_input_counter += 1
                                    st.rerun()
                                else:
                                    try:
                                        erro = resp_pw.json().get("detail", "Unknown error")
                                    except:
                                        erro = resp_pw.text
                                    st.error(f"Error changing password: {erro}")
                    
                    with col_btn2:
                        if st.button("Delete User", key="btn_eliminar_user", use_container_width=True):
                            if not sel_user:
                                st.warning("Please select a user.")
                            elif sel_user == st.session_state.username:
                                st.error("You cannot delete yourself")
                            else:
                                confirm = st.button("Confirm Deletion", key="btn_confirmar_eliminar")
                                if confirm:
                                    resp_del = requests.delete(f"{API_URL}/admin/usuarios/{sel_user}", headers=headers_auth())
                                    if resp_del.status_code == 200:
                                        st.toast(f"User '{sel_user}' deleted successfully!", icon="🗑️")
                                        st.session_state.pw_input_counter += 1
                                        st.session_state.admin_user_dropdown_key += 1
                                        st.rerun()
                                    else:
                                        try:
                                            erro = resp_del.json().get("detail", "Unknown error")
                                        except:
                                            erro = resp_del.text
                                        st.error(f"Error deleting: {erro}")
                    
                    with col_btn3:
                        if st.button("Close Details", key="admin_fechar_gerir_user", use_container_width=True):
                            st.session_state.admin_user_dropdown_key += 1
                            st.session_state.doc_selecionado = None
                            st.rerun()

            else:
                st.info("No users found")
        else:
            st.error("Failed to load users")

    else:  # Documents (company) - Admin
        st.header("Company Area (Validation) – Admin")
        
        if "admin_mostrar_form" not in st.session_state:
            st.session_state.admin_mostrar_form = False
        
        if not st.session_state.admin_mostrar_form:
            if st.button("➕ Create new document for partner", use_container_width=True, key="admin_abrir_form"):
                st.session_state.admin_mostrar_form = True
                st.rerun()
        else:
            with st.container():
                st.subheader("Create Document")
                st.info("The administrator creates the document skeleton. The partner will fill in the data later.")
                
                form_key = st.session_state.get("admin_form_key", 0)
                
                titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"admin_titulo_{form_key}")
                
                parceiros = listar_parceiros_disponiveis()
                
                if not parceiros:
                    st.warning("No partners available. Create a partner first.")
                    if st.button("🔄 Reload partner list", key="admin_reload_parceiros"):
                        st.rerun()
                    if st.button("✖ Close", key="admin_fechar_sem_parceiros"):
                        st.session_state.admin_mostrar_form = False
                        st.rerun()
                else:
                    parceiro_selecionado = st.selectbox(
                        "Select Partner",
                        options=[""] + [p["username"] for p in parceiros],
                        format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                        placeholder="Select a partner from the list",
                        key=f"admin_parceiro_{form_key}"
                    )
                    
                    st.info("Select the processes that will be available in this document for the partner to fill in.")
                    processos_selecionados = render_processos_selecao(key_prefix=f"admin_{form_key}")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                            if st.button("✅ Create Document", key=f"admin_create_doc_btn_{form_key}", use_container_width=True):
                                if not titulo.strip():
                                    st.error("Title is required.")
                                else:
                                    try:
                                        dados = ensure_new_structure({}, processos_selecionados)
                                        novo = criar_documento(titulo, parceiro_selecionado, dados)
                                        if novo:
                                            st.session_state.admin_form_key = form_key + 1
                                            session_key = f"processos_selecionados_admin_{form_key}"
                                            if session_key in st.session_state:
                                                del st.session_state[session_key]
                                            st.session_state.admin_mostrar_form = False
                                            st.session_state.success_message = f"Document created successfully! ID: {novo['id']}"
                                            st.session_state.new_data = None
                                            st.session_state.doc_selecionado = None
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error creating document: {str(e)}")
                        elif processos_selecionados and (not parceiro_selecionado or parceiro_selecionado == ""):
                            st.warning("Please select a partner to continue.")
                        elif parceiro_selecionado and parceiro_selecionado != "" and not processos_selecionados:
                            st.warning("Please select at least one process to continue.")
                    
                    with col_btn2:
                        if st.button("❌ Cancel", key=f"admin_cancel_btn_{form_key}", use_container_width=True):
                            session_key = f"processos_selecionados_admin_{form_key}"
                            if session_key in st.session_state:
                                del st.session_state[session_key]
                            st.session_state.admin_mostrar_form = False
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("✖ Close", key=f"admin_fechar_btn_{form_key}", use_container_width=True):
                            session_key = f"processos_selecionados_admin_{form_key}"
                            if session_key in st.session_state:
                                del st.session_state[session_key]
                            st.session_state.admin_mostrar_form = False
                            st.rerun()
            
            st.divider()

        st.subheader("Available Documents")
        
        with st.expander("Search Filters", expanded=False):
            col1, col2 = st.columns(2)
            key_suffix = st.session_state.filtros_widget_key
            
            with col1:
                q = st.text_input("Search", value=st.session_state.filtros_temporarios.get("q", ""), placeholder="Title, partner or ID...", key=f"filtro_q_{key_suffix}")
                st.session_state.filtros_temporarios["q"] = q
                estados_disponiveis = ["Draft", "Submitted", "In Review", "Changes Requested", "Approved", "Archived"]
                estados_selecionados = st.multiselect("Status", options=estados_disponiveis, default=st.session_state.filtros_temporarios.get("estados", []), key=f"filtro_estados_{key_suffix}")
                st.session_state.filtros_temporarios["estados"] = estados_selecionados
            
            with col2:
                data_inicio = st.date_input("Start Date", value=st.session_state.filtros_temporarios.get("data_inicio"), format="DD/MM/YYYY", key=f"filtro_data_inicio_{key_suffix}")
                st.session_state.filtros_temporarios["data_inicio"] = data_inicio.strftime("%Y-%m-%d") if data_inicio else None
                data_fim = st.date_input("End Date", value=st.session_state.filtros_temporarios.get("data_fim"), format="DD/MM/YYYY", key=f"filtro_data_fim_{key_suffix}")
                st.session_state.filtros_temporarios["data_fim"] = data_fim.strftime("%Y-%m-%d") if data_fim else None
            
            col5, col6 = st.columns(2)
            with col5:
                if st.button("Apply Filters", use_container_width=True):
                    st.session_state.filtros_aplicados = st.session_state.filtros_temporarios.copy()
                    st.rerun()
            with col6:
                if st.button("Clear Filters", use_container_width=True):
                    st.session_state.filtros_temporarios = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                    st.session_state.filtros_aplicados = {"q": "", "estados": [], "data_inicio": None, "data_fim": None, "order_by": "id", "order_dir": "desc"}
                    st.session_state.filtros_widget_key += 1
                    st.rerun()
        
        if st.button("Refresh list", key="refresh_list_admin"):
            st.session_state.doc_selecionado = None
            st.session_state.admin_dropdown_key += 1
            st.session_state.refresh_counter += 1
            st.rerun()
        st.write("")

        documentos = listar_documentos_com_filtros(st.session_state.filtros_aplicados)
        if not documentos:
            st.info("No documents found with the current filters.")
        else:
            df = pd.DataFrame(documentos)
            if "updated_at" in df.columns:
                df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%d/%m/%Y %H:%M")
            if "created_at" in df.columns:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df = df[["id", "titulo", "parceiro_id", "estado", "versao_atual", "updated_at"]]
            df.columns = ["ID", "Title", "Partner", "Status", "Version", "Last Update"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [""] + [doc["id"] for doc in documentos]

            id_selecionado = st.selectbox(
                "Select a document:",
                ids,
                format_func=lambda x: "Select a document..." if x == "" else f"ID {x}",
                key=f"admin_selectbox_{st.session_state.admin_dropdown_key}",
                placeholder="Choose an option"
            )

            if st.button("Load document", key="admin_carregar_doc"):
                if not id_selecionado:
                    st.warning("Please select a document.")
                else:
                    st.session_state.doc_selecionado = id_selecionado
                    st.session_state.expander_aberto = False
                    trigger_scroll(id_selecionado)
                    st.rerun()

        if st.session_state.doc_selecionado:
            doc = obter_documento(st.session_state.doc_selecionado)
            if doc:
                create_document_anchor(doc['id'])
                
                st.divider()
                st.subheader(f"Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
                st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

                dados = doc['dados']
                processos = get_processos_from_data(dados)
                
                with st.expander("View document data", expanded=st.session_state.get("expander_aberto", False)):
                    st.subheader("LCA")
                    lca = dados.get("lca", {})
                    for proc in processos:
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
                    for proc in processos:
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

                with st.expander("View raw JSON", expanded=False):
                    st.json(dados)

                st.markdown("---")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                if doc['estado'] in ["Submitted", "Submetido"]:
                    with col_btn1:
                        if st.button("Start Review", key="admin_iniciar_revisao", use_container_width=True):
                            if iniciar_revisao(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["In Review", "Em Revisão"]:
                    comentario = st.text_area("Comment (required if requesting changes)", key="admin_comentario")
                    col_aprov, col_alt = st.columns(2)
                    with col_aprov:
                        if st.button("Approve", key="admin_aprovar", use_container_width=True):
                            if aprovar(doc['id']):
                                st.rerun()
                    with col_alt:
                        if st.button("Request Changes", key="admin_pedir_alteracoes", use_container_width=True):
                            if not comentario.strip():
                                st.error("A comment is required to request changes")
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.rerun()
                elif doc['estado'] in ["Approved", "Aprovado"]:
                    with col_btn1:
                        if st.button("Reopen", key="admin_reabrir", use_container_width=True):
                            if reabrir(doc['id']):
                                st.rerun()
                    with col_btn2:
                        if st.button("Archive", key="admin_arquivar", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Draft", "Rascunho"]:
                    with col_btn1:
                        if st.button("Archive (draft)", key="admin_arquivar_rascunho", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Changes Requested", "Alterações"]:
                    with col_btn1:
                        st.info("Waiting for partner to edit again.")
                elif doc['estado'] in ["Archived", "Arquivado"]:
                    with col_btn1:
                        st.warning("Document archived (view only).")

                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label="Export History",
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_admin_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )

                with col_btn3:
                    if st.button("Close details", key="admin_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.expander_aberto = False
                        st.rerun()

                st.markdown("---")

                with st.expander("Version history", expanded=False):
                    versoes = listar_versoes(doc['id'])
                    if versoes:
                        for v in versoes:
                            data_formatada = formatar_data_hora(v['created_at'])
                            st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']}) at {data_formatada}")
                            if v['comentario']:
                                st.caption(f"  Comment: {v['comentario']}")
                    else:
                        st.info("No history available.")

# ============================================================
# CLOSE MAIN CONTENT
# ============================================================
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PROCESS CLOSE_DOC_AFTER_ACTION
# ============================================================
if st.session_state.get("close_doc_after_action", False):
    if st.session_state.doc_selecionado is not None:
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False