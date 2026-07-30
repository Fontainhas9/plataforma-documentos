// =====================================================
// LOGIN - Holoss Style
// =====================================================

const API_URL = 'http://localhost:8000';

console.log('🔗 API URL:', API_URL);
console.log('🌐 Hostname:', window.location.hostname);

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMsg = document.getElementById('errorMsg');
    const loginButton = document.getElementById('loginButton');

    // ✅ Verificar sessionStorage (NÃO localStorage)
    const token = sessionStorage.getItem('doc_token');
    if (token) {
        console.log('✅ Já autenticado neste separador, redirecionar para documentos');
        window.location.href = 'documentos.html';
        return;
    }

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        errorMsg.textContent = '';
        errorMsg.style.color = '#c0392b';

        if (!username || !password) {
            errorMsg.textContent = 'Please enter your username and password.';
            return;
        }

        loginButton.disabled = true;
        loginButton.textContent = 'Signing in...';

        try {
            console.log('📤 A enviar login para:', `${API_URL}/login`);
            
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });

            console.log('📥 Resposta recebida:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erro:', errorText);
                throw new Error(`Erro ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            console.log('📦 Dados recebidos:', data);

            if (data.access_token) {
                // ✅ GUARDAR EM sessionStorage (NÃO localStorage)
                sessionStorage.setItem('doc_token', data.access_token);
                sessionStorage.setItem('doc_username', username);
                console.log('✅ Token guardado em sessionStorage (apenas este separador)!');

                // Buscar informações do utilizador
                try {
                    const meResponse = await fetch(`${API_URL}/me`, {
                        headers: {
                            'Authorization': `Bearer ${data.access_token}`
                        }
                    });

                    if (meResponse.ok) {
                        const userInfo = await meResponse.json();
                        sessionStorage.setItem('doc_perfil', userInfo.perfil);
                        sessionStorage.setItem('doc_nome', userInfo.nome_completo || username);
                        console.log('👤 Utilizador:', userInfo);
                    }
                } catch (meError) {
                    console.warn('Erro ao buscar perfil:', meError);
                }

                console.log('🚀 Redirecionar para documentos.html');
                window.location.href = 'documentos.html';
            } else {
                errorMsg.textContent = data.detail || 'Invalid credentials.';
            }
        } catch (error) {
            console.error('❌ Login error:', error);
            errorMsg.textContent = `Unable to connect to the server. Make sure the backend is running at ${API_URL}`;
        } finally {
            loginButton.disabled = false;
            loginButton.textContent = 'Log in';
        }
    });

    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
});