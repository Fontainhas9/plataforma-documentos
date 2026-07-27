import streamlit as st
import requests
import os

def get_api_url():
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

def show_login():
    # CSS específico para o login
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #0a2f57 0%, #15528d 100%) !important;
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
        }
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="stSidebarUserContent"] { display: none !important; }
        .stApp > header { display: none !important; }
        .stAppHeader, .stDecoration { display: none !important; }
        
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.94);
            border-radius: 28px;
            padding: 40px 36px 32px;
            max-width: 440px;
            width: 100%;
            box-shadow: 0 24px 48px rgba(5, 20, 40, 0.22);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .login-title {
            color: #123b72;
            font-size: 28px;
            font-weight: 800;
            margin: 0;
        }
        .login-subtitle {
            color: #5f6f86;
            font-size: 14px;
            margin: 0 0 28px 0;
        }
        .login-card .stTextInput > div > div > input {
            height: 50px;
            border-radius: 12px;
            border: 1px solid #d2d9e3;
            font-size: 15px;
            padding: 0 14px;
            background: #ffffff;
            color: #21344d;
        }
        .login-card .stTextInput > div > div > input:focus {
            border-color: #003662;
            box-shadow: 0 0 0 4px rgba(55, 113, 176, 0.14);
        }
        .login-card .stTextInput label {
            font-size: 14px;
            font-weight: 600;
            color: #123b72;
            margin-bottom: 6px;
        }
        .login-card .stButton > button {
            width: 100%;
            height: 50px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #003662 0%, #295d96 100%);
            color: #ffffff;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 12px 24px rgba(41, 93, 150, 0.26);
            margin-top: 6px;
        }
        .login-card .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 28px rgba(41, 93, 150, 0.32);
        }
        .login-card .stAlert {
            margin-top: 12px;
            border-radius: 10px;
            padding: 10px 14px;
        }
        .st-emotion-cache-1r6slb0 { padding: 0 !important; margin: 0 !important; }
        .stTextInput { display: block !important; }
        .stButton { display: block !important; }
        .stForm { display: block !important; }
    </style>
    
    <div class="login-container">
        <div class="login-card">
            <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
                <div style="font-size:42px;">📄</div>
                <div>
                    <h1 class="login-title">Document Platform</h1>
                    <p class="login-subtitle" style="margin:0;">Sign in to continue</p>
                </div>
            </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        submitted = st.form_submit_button("Log in", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/login",
                        data={"username": username, "password": password}
                    )
                    
                    if response.status_code == 200:
                        dados = response.json()
                        st.session_state.token = dados["access_token"]
                        
                        headers = {"Authorization": f"Bearer {dados['access_token']}"}
                        me = requests.get(f"{API_URL}/me", headers=headers)
                        
                        if me.status_code == 200:
                            user_info = me.json()
                            st.session_state.perfil = user_info["perfil"]
                            st.session_state.username = user_info["username"]
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("Error fetching user information.")
                    else:
                        try:
                            erro = response.json().get("detail", "Invalid credentials")
                        except:
                            erro = "Invalid credentials"
                        st.error(f"❌ {erro}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the server. Make sure the backend is running on http://127.0.0.1:8000")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Se executado diretamente
if __name__ == "__main__":
    show_login()