# frontend/components/load_css.py
import streamlit as st
import os

def load_css():
    """Loads the external CSS file."""
    try:
        # Try to load from frontend directory
        css_path = os.path.join(os.path.dirname(__file__), '..', 'style.css')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css = f.read()
                st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        else:
            # Fallback: try current directory
            with open('style.css', 'r') as f:
                css = f.read()
                st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback CSS if file not found
        st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarNav"] { display: none !important; }
            .main > div { padding: 0 !important; max-width: 100% !important; }
            .block-container { padding: 0 !important; }
            .main-content { margin-top: 80px; padding: 0 2rem 2rem 2rem; max-width: 1440px; margin-left: auto; margin-right: auto; }
            .stat-card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.05); }
            .stat-value { font-size: 2rem; font-weight: 700; color: white; }
            .stat-label { font-size: 0.8rem; color: #80809a; text-transform: uppercase; }
        </style>
        """, unsafe_allow_html=True)
        print("⚠️ style.css not found, using fallback CSS")