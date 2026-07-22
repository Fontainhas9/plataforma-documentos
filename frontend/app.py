import streamlit as st
import requests
import pandas as pd
import copy
from datetime import datetime
import os

# ============================================================
# LOAD CSS
# ============================================================
# Add the frontend directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))

from components.load_css import load_css
load_css()

# ============================================================
# API URL CONFIGURATION - WORKS IN LOCAL AND PRODUCTION
# ============================================================
def get_api_url():
    """Returns the API URL based on the environment (local or production)."""
    try:
        if hasattr(st, 'secrets') and st.secrets and 'API_URL' in st.secrets:
            return st.secrets['API_URL']
    except Exception:
        pass
    
    api_url = os.getenv('API_URL')
    if api_url:
        return api_url
    
    return "http://127.0.0.1:8000"

API_URL = get_api_url()

# Default processes (used as fallback)
PROCESSOS_PADRAO = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]
DATASOURCE_OPTIONS = ["Measured", "Calculated", "Estimated", "Literature"]

# ============================================================
# FUNCTION TO FORMAT DATE/TIME
# ============================================================
def formatar_data_hora(data_str):
    """
    Converts a date/time string to DD/MM/YYYY HH:MM format.
    Supports ISO 8601 formats with T and Z.
    Example: "2026-07-16T14:30:45.856282Z" -> "16/07/2026 14:30"
    """
    if not data_str:
        return ""
    try:
        if isinstance(data_str, datetime):
            return data_str.strftime("%d/%m/%Y %H:%M")
        
        data_str = str(data_str)
        data_str = data_str.replace('Z', '').replace('T', ' ')
        
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(data_str, fmt)
                return dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        
        return data_str
    except Exception:
        return str(data_str)

# Page configuration
st.set_page_config(
    page_title="Document Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import notification component
from componentes.notificacoes import render_notificacoes_badge, get_notificacoes_nao_lidas

# ============================================================
# HEADER COMPONENT
# ============================================================
def render_header():
    """
    Renders the fixed header with logo, navigation and user profile.
    """
    username = st.session_state.get("username", "User")
    
    # Get unread notifications count
    notif_count = get_notificacoes_nao_lidas() if st.session_state.get("token") else 0
    
    # Determine active page
    current_page = st.query_params.get("page", "home")
    is_home = current_page == "home" or current_page == ""
    is_dashboard = current_page == "dashboard"
    is_notifications = current_page == "notificacoes"
    
    # Build badge HTML
    badge_html = f'<span class="badge">{notif_count}</span>' if notif_count > 0 else ''
    
    # HTML do header
    header_html = f'''
    <header class="main-header">
        <div class="header-logo" onclick="window.location.href='?page=home'">
            <div class="logo-icon">📄</div>
            <span>DocPlatform</span>
        </div>
        
        <nav class="header-nav">
            <a class="{'active' if is_home else ''}" onclick="window.location.href='?page=home'">Home</a>
            <a class="{'active' if is_dashboard else ''}" onclick="window.location.href='?page=dashboard'">Dashboard</a>
            <span class="nav-divider"></span>
            <a class="{'active' if is_notifications else ''}" onclick="window.location.href='?page=notificacoes'">Notifications</a>
        </nav>
        
        <div class="header-user">
            <span class="user-name">{username}</span>
            <button class="notification-bell" onclick="window.location.href='?page=notificacoes'">
                🔔
                {badge_html}
            </button>
            <div class="user-avatar">{username[0].upper() if username else 'U'}</div>
            <button class="logout-btn" onclick="window.location.href='?logout=true'">Logout</button>
        </div>
    </header>
    <div class="main-content">
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Process logout
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        logout()
        st.rerun()
    
    # Process navigation
    if st.query_params.get("page") == "dashboard":
        st.switch_page("pages/dashboard.py")
    elif st.query_params.get("page") == "notificacoes":
        st.switch_page("pages/notificacoes.py")
    
    return username

# ============================================================
# JAVASCRIPT FOR AUTO SCROLL
# ============================================================
st.markdown("""
<script>
    function checkScrollParam() {
        var urlParams = new URLSearchParams(window.location.search);
        var targetId = urlParams.get('scroll_to');
        if (targetId) {
            setTimeout(function() {
                var element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
            setTimeout(function() {
                var element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 400);
            setTimeout(function() {
                var element = document.getElementById(targetId);
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

# Initialize session state
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
if "expander_aberto" not in st.session_state:
    st.session_state.expander_aberto = False
if "processos_do_documento" not in st.session_state:
    st.session_state.processos_do_documento = []
if "empresa_form_key" not in st.session_state:
    st.session_state.empresa_form_key = 0
if "admin_form_key" not in st.session_state:
    st.session_state.admin_form_key = 0
if "empresa_mostrar_form" not in st.session_state:
    st.session_state.empresa_mostrar_form = False
if "admin_mostrar_form" not in st.session_state:
    st.session_state.admin_mostrar_form = False

# ... (resto do código igual, todas as funções permanecem)

# ============================================================
# MAIN INTERFACE
# ============================================================

# Check if user is authenticated
if st.session_state.token is None:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login(username, password):
                st.session_state.success_message = "Login successful!"
                st.rerun()
    st.stop()

# ============================================================
# FROM HERE, USER IS AUTHENTICATED - RENDER HEADER
# ============================================================

# Render the fixed header
username = render_header()

# Show success message with toast
if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None

# Process document opening from notifications
if "doc_id" in st.query_params and st.query_params["doc_id"]:
    try:
        doc_id = int(st.query_params["doc_id"])
        st.session_state.doc_selecionado = doc_id
        st.query_params.clear()
    except ValueError:
        pass

if st.session_state.redirect_to_docs:
    st.session_state.redirect_to_docs = False

# If close_doc_after_action is active, close the document
if st.session_state.get("close_doc_after_action", False):
    st.session_state.doc_selecionado = None
    st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False

# ============================================================
# MAIN CONTENT
# ============================================================

st.title("📄 Document Management Platform")

# ---------- Document summary ----------
if st.session_state.perfil != "admin":
    documentos = listar_documentos()
    if documentos:
        st.subheader("📊 Document Summary")
        show_document_summary(documentos)
        st.divider()
    else:
        st.info("No documents found. Start by creating a new document.")

# ---------- Partner Area ----------
if st.session_state.perfil == "parceiro":
    st.header("👤 Partner Area")
    st.caption("Documents are created by the company. You only fill in the data and submit.")
    
    st.subheader("📋 My Documents")
    
    if st.button("🔄 Refresh list", key="refresh_list_parceiro"):
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

        if st.button("📂 Load document", key="parceiro_carregar_doc"):
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
            st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']}")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")
            st.caption(f"Created by: {doc.get('empresa_id', 'N/A')}")
            
            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            # Use expander_aberto controlled by state
            with st.expander("📊 View data in tables", expanded=st.session_state.get("expander_aberto", False)):
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

            with st.expander("🔍 View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            # ---------- ACTION BUTTONS ----------
            # Check if document is in Draft status (either "Draft" or "Rascunho")
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
                            # First save the current data
                            novos_dados = st.session_state.edit_data
                            resultado_edicao = editar_documento(doc['id'], novos_dados)
                            if resultado_edicao:
                                # Then submit
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
                # Document is not in Draft status - show view-only with Export History
                st.subheader("📄 View Document")
                st.info(f"This document is in status: **{estado_doc}**")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                # Show specific messages based on status
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

            with st.expander("📜 Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} by {v['criado_por']} at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ---------- Company Area ----------
elif st.session_state.perfil == "empresa":
    st.header("🏢 Company Area (Validation)")
    
    # ---------- CREATE DOCUMENT (COMPANY) ----------
    # Control form state
    if "empresa_mostrar_form" not in st.session_state:
        st.session_state.empresa_mostrar_form = False
    
    # Button to open form
    if not st.session_state.empresa_mostrar_form:
        if st.button("➕ Create new document for partner", use_container_width=True, key="empresa_abrir_form"):
            st.session_state.empresa_mostrar_form = True
            st.rerun()
    else:
        # Show the form
        with st.container():
            st.subheader("Create Document")
            st.info("The company creates the document skeleton. The partner will fill in the data later.")
            
            # Generate a unique key to force widget recreation
            form_key = st.session_state.get("empresa_form_key", 0)
            
            titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"empresa_titulo_{form_key}")
            
            # Select partner
            parceiros = listar_parceiros_disponiveis()
            
            if not parceiros:
                st.warning("No partners available. Create a partner first in the Admin area.")
                if st.button("🔄 Reload partner list"):
                    st.rerun()
                # Button to close the form
                if st.button("✖ Close", key="empresa_fechar_sem_parceiros"):
                    st.session_state.empresa_mostrar_form = False
                    st.rerun()
            else:
                # Placeholder for selectbox
                parceiro_selecionado = st.selectbox(
                    "Select Partner",
                    options=[""] + [p["username"] for p in parceiros],
                    format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                    placeholder="Select a partner from the list",
                    key=f"empresa_parceiro_{form_key}"
                )
                
                # Select processes using the new function
                st.info("Select the processes that will be available in this document for the partner to fill in.")
                processos_selecionados = render_processos_selecao(key_prefix=f"empresa_{form_key}")
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn1:
                    # Show create button only if processes selected and partner selected
                    if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                        if st.button("✅ Create Document", key=f"empresa_create_doc_btn_{form_key}", use_container_width=True):
                            if not titulo.strip():
                                st.error("Title is required.")
                            else:
                                try:
                                    # Create empty structure with selected processes
                                    dados = ensure_new_structure({}, processos_selecionados)
                                    
                                    novo = criar_documento(titulo, parceiro_selecionado, dados)
                                    if novo:
                                        # Increment form key to clear all fields
                                        st.session_state.empresa_form_key = form_key + 1
                                        # Clear selected processes list
                                        session_key = f"processos_selecionados_empresa_{form_key}"
                                        if session_key in st.session_state:
                                            del st.session_state[session_key]
                                        # Close the form
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
                        # Clear form data
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
    
    # ---------- AVAILABLE DOCUMENTS ----------
    st.subheader("📋 Available Documents")
    render_filtros()
    
    if st.button("🔄 Refresh list", key="refresh_list_empresa"):
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

        if st.button("📂 Load document", key="empresa_carregar_doc"):
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
            st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
            st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

            dados = doc['dados']
            processos = get_processos_from_data(dados)
            
            # Use expander_aberto controlled by state
            with st.expander("📊 View document data", expanded=st.session_state.get("expander_aberto", False)):
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

            with st.expander("🔍 View raw JSON", expanded=False):
                st.json(dados)

            st.markdown("---")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            if doc['estado'] in ["Submitted", "Submetido"]:
                with col_btn1:
                    if st.button("🔍 Start Review", key="empresa_iniciar_revisao", use_container_width=True):
                        if iniciar_revisao(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["In Review", "Em Revisão"]:
                comentario = st.text_area("Comment (required if requesting changes)", key="empresa_comentario")
                col_aprov, col_alt = st.columns(2)
                with col_aprov:
                    if st.button("✅ Approve", key="empresa_aprovar", use_container_width=True):
                        if aprovar(doc['id']):
                            st.rerun()
                with col_alt:
                    if st.button("🔄 Request Changes", key="empresa_pedir_alteracoes", use_container_width=True):
                        if not comentario.strip():
                            st.error("A comment is required to request changes")
                        else:
                            if pedir_alteracoes(doc['id'], comentario):
                                st.rerun()
            elif doc['estado'] in ["Approved", "Aprovado"]:
                with col_btn1:
                    if st.button("🔁 Reopen", key="empresa_reabrir", use_container_width=True):
                        if reabrir(doc['id']):
                            st.rerun()
                with col_btn2:
                    if st.button("📁 Archive", key="empresa_arquivar", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Draft", "Rascunho"]:
                with col_btn1:
                    if st.button("📁 Archive (draft)", key="empresa_arquivar_rascunho", use_container_width=True):
                        if arquivar(doc['id']):
                            st.rerun()
            elif doc['estado'] in ["Changes Requested", "Alterações"]:
                with col_btn1:
                    st.info("⏳ Waiting for partner to edit again.")
            elif doc['estado'] in ["Archived", "Arquivado"]:
                with col_btn1:
                    st.warning("📁 Document archived (view only).")

            with col_btn2:
                conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                if conteudo:
                    st.download_button(
                        label="📊 Export History",
                        data=conteudo,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_empresa_{doc['id']}_{st.session_state.refresh_counter}",
                        use_container_width=True
                    )

            with col_btn3:
                if st.button("✖ Close details", key="empresa_fechar_detalhes", use_container_width=True):
                    st.session_state.doc_selecionado = None
                    st.session_state.expander_aberto = False
                    st.rerun()

            st.markdown("---")

            with st.expander("📜 Version history", expanded=False):
                versoes = listar_versoes(doc['id'])
                if versoes:
                    for v in versoes:
                        data_formatada = formatar_data_hora(v['created_at'])
                        st.write(f"v{v['numero_versao']} - {v['estado']} ({v['criado_por']}) at {data_formatada}")
                        if v['comentario']:
                            st.caption(f"  Comment: {v['comentario']}")
                else:
                    st.info("No history available.")

# ---------- Admin Area ----------
elif st.session_state.perfil == "admin":
    st.header("⚙️ Administrative Panel")
    
    # Admin menu as tabs instead of sidebar
    menu_admin = st.radio("Admin", ["Users", "Documents (company)"], key="admin_menu", horizontal=True)

    if menu_admin == "Users":
        st.subheader("👥 User Management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔄 Load users", use_container_width=True, key="admin_carregar_users"):
                st.session_state.doc_selecionado = None
                st.session_state.admin_user_dropdown_key += 1
                st.session_state.refresh_counter += 1
                st.rerun()
        with col2:
            if st.button("➕ New User", use_container_width=True, key="admin_novo_user"):
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
                    format_func=lambda x: {
                        "parceiro": "Partner",
                        "empresa": "Company",
                        "admin": "Admin"
                    }.get(x, x),
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
                    nova_pw = st.text_input(
                        "New password (leave empty to keep current)", 
                        type="password", 
                        key=pw_key,
                        placeholder="Enter new password..."
                    )
                    
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
        st.header("📋 Company Area (Validation) – Admin")
        
        # ---------- CREATE DOCUMENT (ADMIN) ----------
        # Control form state
        if "admin_mostrar_form" not in st.session_state:
            st.session_state.admin_mostrar_form = False
        
        # Button to open form
        if not st.session_state.admin_mostrar_form:
            if st.button("➕ Create new document for partner", use_container_width=True, key="admin_abrir_form"):
                st.session_state.admin_mostrar_form = True
                st.rerun()
        else:
            # Show the form
            with st.container():
                st.subheader("Create Document")
                st.info("The administrator creates the document skeleton. The partner will fill in the data later.")
                
                # Generate a unique key to force widget recreation
                form_key = st.session_state.get("admin_form_key", 0)
                
                titulo = st.text_input("Document title (ex: LCA/LCC NEO-CYCLE)", key=f"admin_titulo_{form_key}")
                
                # Select partner
                parceiros = listar_parceiros_disponiveis()
                
                if not parceiros:
                    st.warning("No partners available. Create a partner first.")
                    if st.button("🔄 Reload partner list", key="admin_reload_parceiros"):
                        st.rerun()
                    # Button to close the form
                    if st.button("✖ Close", key="admin_fechar_sem_parceiros"):
                        st.session_state.admin_mostrar_form = False
                        st.rerun()
                else:
                    # Placeholder for selectbox
                    parceiro_selecionado = st.selectbox(
                        "Select Partner",
                        options=[""] + [p["username"] for p in parceiros],
                        format_func=lambda x: "Select a partner from the list" if x == "" else f"{x} - {next((p['nome_completo'] for p in parceiros if p['username'] == x), '')}",
                        placeholder="Select a partner from the list",
                        key=f"admin_parceiro_{form_key}"
                    )
                    
                    # Select processes using the new function
                    st.info("Select the processes that will be available in this document for the partner to fill in.")
                    processos_selecionados = render_processos_selecao(key_prefix=f"admin_{form_key}")
                    
                    # Action buttons
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        # Show create button only if processes selected and partner selected
                        if processos_selecionados and parceiro_selecionado and parceiro_selecionado != "":
                            if st.button("✅ Create Document", key=f"admin_create_doc_btn_{form_key}", use_container_width=True):
                                if not titulo.strip():
                                    st.error("Title is required.")
                                else:
                                    try:
                                        # Create empty structure with selected processes
                                        dados = ensure_new_structure({}, processos_selecionados)
                                        
                                        novo = criar_documento(titulo, parceiro_selecionado, dados)
                                        if novo:
                                            # Increment form key to clear all fields
                                            st.session_state.admin_form_key = form_key + 1
                                            # Clear selected processes list
                                            session_key = f"processos_selecionados_admin_{form_key}"
                                            if session_key in st.session_state:
                                                del st.session_state[session_key]
                                            # Close the form
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
                            # Clear form data
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

        st.subheader("📋 Available Documents")
        render_filtros()
        
        if st.button("🔄 Refresh list", key="refresh_list_admin"):
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

            if st.button("📂 Load document", key="admin_carregar_doc"):
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
                st.subheader(f"📄 Document ID {doc['id']}: {doc['titulo']} (Partner: {doc['parceiro_id']})")
                st.write(f"Status: **{doc['estado']}** | Version: {doc['versao_atual']}")

                dados = doc['dados']
                processos = get_processos_from_data(dados)
                
                with st.expander("📊 View document data", expanded=st.session_state.get("expander_aberto", False)):
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

                with st.expander("🔍 View raw JSON", expanded=False):
                    st.json(dados)

                st.markdown("---")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                if doc['estado'] in ["Submitted", "Submetido"]:
                    with col_btn1:
                        if st.button("🔍 Start Review", key="admin_iniciar_revisao", use_container_width=True):
                            if iniciar_revisao(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["In Review", "Em Revisão"]:
                    comentario = st.text_area("Comment (required if requesting changes)", key="admin_comentario")
                    col_aprov, col_alt = st.columns(2)
                    with col_aprov:
                        if st.button("✅ Approve", key="admin_aprovar", use_container_width=True):
                            if aprovar(doc['id']):
                                st.rerun()
                    with col_alt:
                        if st.button("🔄 Request Changes", key="admin_pedir_alteracoes", use_container_width=True):
                            if not comentario.strip():
                                st.error("A comment is required to request changes")
                            else:
                                if pedir_alteracoes(doc['id'], comentario):
                                    st.rerun()
                elif doc['estado'] in ["Approved", "Aprovado"]:
                    with col_btn1:
                        if st.button("🔁 Reopen", key="admin_reabrir", use_container_width=True):
                            if reabrir(doc['id']):
                                st.rerun()
                    with col_btn2:
                        if st.button("📁 Archive", key="admin_arquivar", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Draft", "Rascunho"]:
                    with col_btn1:
                        if st.button("📁 Archive (draft)", key="admin_arquivar_rascunho", use_container_width=True):
                            if arquivar(doc['id']):
                                st.rerun()
                elif doc['estado'] in ["Changes Requested", "Alterações"]:
                    with col_btn1:
                        st.info("⏳ Waiting for partner to edit again.")
                elif doc['estado'] in ["Archived", "Arquivado"]:
                    with col_btn1:
                        st.warning("📁 Document archived (view only).")

                with col_btn2:
                    conteudo, filename = exportar_excel(doc['id'], doc['titulo'])
                    if conteudo:
                        st.download_button(
                            label="📊 Export History",
                            data=conteudo,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_admin_{doc['id']}_{st.session_state.refresh_counter}",
                            use_container_width=True
                        )

                with col_btn3:
                    if st.button("✖ Close details", key="admin_fechar_detalhes", use_container_width=True):
                        st.session_state.doc_selecionado = None
                        st.session_state.expander_aberto = False
                        st.rerun()

                st.markdown("---")

                with st.expander("📜 Version history", expanded=False):
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
# ENSURE CLOSE_DOC_AFTER_ACTION IS PROCESSED
# ============================================================
if st.session_state.get("close_doc_after_action", False):
    if st.session_state.doc_selecionado is not None:
        st.session_state.doc_selecionado = None
        st.session_state.edit_data = None
    st.session_state.close_doc_after_action = False