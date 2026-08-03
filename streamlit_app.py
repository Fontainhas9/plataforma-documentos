# streamlit_app.py
import streamlit as st
import os

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Document Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS PERSONALIZADO
# ============================================================
def load_css():
    css_files = [
        "css/login.css",
        "css/dashboard-topbar.css",
        "css/dashboard-documents.css",
        "css/footer.css"
    ]
    
    css_content = ""
    for css_file in css_files:
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content += f.read() + "\n"
        except FileNotFoundError:
            pass
    
    if css_content:
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

load_css()

# ============================================================
# CARREGAR JAVASCRIPT
# ============================================================
def load_js():
    js_files = [
        "js/auth.js",
        "js/config.js",
        "js/login.js",
        "js/dashboard-documents.js"
    ]
    
    js_content = ""
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content += f.read() + "\n"
        except FileNotFoundError:
            pass
    
    if js_content:
        st.markdown(f'<script>{js_content}</script>', unsafe_allow_html=True)

# ============================================================
# DETETAR A PÁGINA ATUAL
# ============================================================
query_params = st.query_params
page = query_params.get("page", "login")

# ============================================================
# RENDERIZAR PÁGINAS
# ============================================================
def render_page(html_file):
    try:
        with open(f"pages/{html_file}", 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Substituir caminhos relativos para funcionar no Streamlit
        html_content = html_content.replace('href="../css/', 'href="css/')
        html_content = html_content.replace('src="../imagen/', 'src="imagen/')
        html_content = html_content.replace('src="../js/', 'src="js/')
        html_content = html_content.replace('href="../imagen/', 'href="imagen/')
        
        # Remover tags script que vão ser carregadas separadamente
        import re
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Carregar JS depois do HTML
        load_js()
        
    except FileNotFoundError:
        st.error(f"Page {html_file} not found")

# ============================================================
# ROTEAMENTO
# ============================================================
if page == "login" or page == "":
    render_page("login.html")
elif page == "documentos":
    render_page("documentos.html")
elif page == "dashboard":
    render_page("dashboard.html")
elif page == "notificacoes":
    render_page("notificacoes.html")
else:
    render_page("login.html")