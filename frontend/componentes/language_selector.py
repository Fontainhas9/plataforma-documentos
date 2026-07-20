# frontend/componentes/language_selector.py
import streamlit as st
import os
import sys

# Adicionar o caminho do backend para importar o módulo de tradução
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from translations import get_language, set_language, t

def render_language_selector():
    """Renderiza o seletor de idioma no rodapé da página."""
    current_lang = get_language()
    
    # CSS para o rodapé
    st.markdown("""
    <style>
    .footer-selector {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
        font-size: 12px;
        color: #666;
        background: rgba(255,255,255,0.95);
        padding: 4px 14px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .footer-selector select {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        color: #333;
        font-family: inherit;
        min-width: 100px;
    }
    .footer-selector select:focus {
        outline: none;
        border-color: #888;
    }
    .footer-selector select:hover {
        border-color: #888;
    }
    .footer-selector span {
        font-size: 12px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar se o idioma foi alterado via query param
    if "lang" in st.query_params:
        new_lang = st.query_params["lang"]
        if new_lang in ["en", "pt"] and new_lang != current_lang:
            set_language(new_lang)
            # Limpar os query params e recarregar
            st.query_params.clear()
            st.rerun()
    
    # Opções de idioma com bandeiras
    lang_options = {
        "en": "🇬🇧 English",
        "pt": "🇵🇹 Português"
    }
    
    # Renderizar o seletor com JavaScript para trocar idioma
    html = f"""
    <div class="footer-selector">
        <span>🌐 {t('language')}:</span>
        <select id="lang-selector" onchange="changeLanguage(this.value)">
            <option value="en" {'selected' if current_lang == 'en' else ''}>🇬🇧 English</option>
            <option value="pt" {'selected' if current_lang == 'pt' else ''}>🇵🇹 Português</option>
        </select>
    </div>
    
    <script>
    function changeLanguage(lang) {{
        // Usar window.location para recarregar com o novo idioma
        var url = new URL(window.location.href);
        url.searchParams.set('lang', lang);
        window.location.href = url.toString();
    }}
    </script>
    """
    
    st.markdown(html, unsafe_allow_html=True)