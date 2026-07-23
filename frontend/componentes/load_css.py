# frontend/componentes/load_css.py
import streamlit as st
import os

def load_css():
    """Loads the external CSS file."""
    try:
        # Try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'style.css'),  # from components folder
            os.path.join(os.getcwd(), 'style.css'),  # current working directory
            'style.css',  # relative path
            os.path.join(os.path.dirname(__file__), 'style.css'),  # same as components
        ]
        
        css_content = None
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        css_content = f.read()
                    print(f"✅ CSS loaded from: {path}")
                    break
            except:
                continue
        
        if css_content:
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        else:
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
                .main-header { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: rgba(10,10,26,0.92); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255,255,255,0.06); padding: 0 2rem; height: 64px; display: flex; align-items: center; justify-content: space-between; }
                .header-logo { display: flex; align-items: center; gap: 12px; font-size: 1.2rem; font-weight: 700; color: #ffffff; cursor: pointer; }
                .header-logo .logo-icon { width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: white; }
                .header-nav { display: flex; align-items: center; gap: 4px; flex: 1; justify-content: center; }
                .header-nav a { color: #a0a0b8; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-size: 0.9rem; font-weight: 500; transition: all 0.3s ease; cursor: pointer; }
                .header-nav a:hover { color: #ffffff; background: rgba(255,255,255,0.06); }
                .header-nav a.active { color: #ffffff; background: rgba(102,126,234,0.2); }
                .header-user { display: flex; align-items: center; gap: 16px; flex-shrink: 0; }
                .header-user .user-name { color: #e8e8e8; font-size: 0.9rem; font-weight: 500; }
                .header-user .user-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 600; color: #ffffff; }
                .header-user .logout-btn { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; color: #a0a0b8; padding: 6px 14px; font-size: 0.85rem; cursor: pointer; transition: all 0.3s ease; }
                .header-user .logout-btn:hover { color: #ffffff; background: rgba(255,255,255,0.10); }
                .header-user .notification-bell { position: relative; cursor: pointer; font-size: 1.2rem; color: #a0a0b8; background: none; border: none; padding: 4px; }
                .header-user .notification-bell .badge { position: absolute; top: -6px; right: -8px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; border-radius: 50%; padding: 2px 6px; font-size: 9px; font-weight: 700; min-width: 18px; text-align: center; animation: pulse 1s infinite; }
                @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
            </style>
            """, unsafe_allow_html=True)
            print("⚠️ style.css not found, using fallback CSS")
            
    except Exception as e:
        print(f"❌ Error loading CSS: {e}")
        # Minimal fallback
        st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            .main > div { padding: 0 !important; }
            .block-container { padding: 0 !important; }
            .main-content { margin-top: 80px; padding: 0 2rem 2rem 2rem; }
        </style>
        """, unsafe_allow_html=True)