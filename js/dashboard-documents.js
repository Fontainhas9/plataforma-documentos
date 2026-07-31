// =====================================================
// DASHBOARD DOCUMENTS - Holoss Style
// =====================================================

// =====================================================
// CONFIGURAÇÃO
// =====================================================

const API_URL = 'http://localhost:8000';
console.log('🔗 API URL:', API_URL);

const PERFIS = {
    parceiro: 'Partner',
    empresa: 'Company',
    admin: 'Admin'
};

const ESTADOS_MAP = {
    'Rascunho': 'Draft',
    'Submetido': 'Submitted',
    'Em Revisão': 'In Review',
    'Alterações': 'Changes Requested',
    'Aprovado': 'Approved',
    'Arquivado': 'Archived'
};

const ESTADOS_CORES = {
    'Rascunho': 'status-draft',
    'Submetido': 'status-submitted',
    'Em Revisão': 'status-review',
    'Alterações': 'status-changes',
    'Aprovado': 'status-approved',
    'Arquivado': 'status-archived'
};

const PROCESSOS_PADRAO = [
    'Demagnetisation',
    'Crushing / Grinding',
    'Aqua regia microwave digestion',
    'ICP-OES/-MS'
];

const DATASOURCE_OPTIONS = ['Measured', 'Calculated', 'Estimated', 'Literature'];

// =====================================================
// ESTADO GLOBAL - USAR sessionStorage
// =====================================================

let state = {
    token: sessionStorage.getItem('doc_token'),
    username: sessionStorage.getItem('doc_username'),
    perfil: sessionStorage.getItem('doc_perfil'),
    nome: sessionStorage.getItem('doc_nome'),
    currentPage: 'documentos',
    documentos: [],
    docSelecionado: null,
    editData: null,
    filtros: {
        q: '',
        estados: [],
        dataInicio: null,
        dataFim: null
    },
    notificacoesNaoLidas: 0,
    toastTimer: null
};

// =====================================================
// TOAST - MENSAGENS NO CENTRO DA PÁGINA
// =====================================================

function showToast(message, type = 'success') {
    // Remover toast anterior
    const oldToast = document.getElementById('customToast');
    if (oldToast) {
        oldToast.remove();
    }
    if (state.toastTimer) {
        clearTimeout(state.toastTimer);
        state.toastTimer = null;
    }

    const colors = {
        success: '#2e7d32',
        error: '#c62828',
        warning: '#ed6c02',
        info: '#0288d1'
    };

    const toast = document.createElement('div');
    toast.id = 'customToast';
    toast.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: ${colors[type] || colors.success};
        color: white;
        padding: 20px 40px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        z-index: 999999;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        text-align: center;
        min-width: 300px;
        max-width: 500px;
        animation: fadeIn 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    `;
    toast.textContent = message;

    // Adicionar animação
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
        @keyframes fadeOut {
            from { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            to { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(toast);

    // ✅ REMOVER APÓS 4 SEGUNDOS (em vez de 5)
    state.toastTimer = setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            toast.remove();
            state.toastTimer = null;
        }, 300);
    }, 4000);
}

// =====================================================
// ADMIN - MENU
// =====================================================

let adminMenuAtivo = 'documents'; // 'documents' ou 'users'

// =====================================================
// LOGOUT - LIMPAR sessionStorage (APENAS ESTE SEPARADOR)
// =====================================================

function logout() {
    sessionStorage.removeItem('doc_token');
    sessionStorage.removeItem('doc_username');
    sessionStorage.removeItem('doc_perfil');
    sessionStorage.removeItem('doc_nome');
    
    console.log('🔓 Logout efetuado neste separador');
    window.location.href = 'login.html';
}

// =====================================================
// ADMIN - GESTÃO DE UTILIZADORES
// =====================================================

function mudarAdminView(view) {
    adminMenuAtivo = view;
    carregarDocumentos();
}

async function carregarUtilizadores() {
    try {
        const response = await fetch(`${API_URL}/admin/usuarios`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Error loading users');
        }

        const users = await response.json();
        renderListaUtilizadores(users);
    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading users: ' + error.message, 'error');
    }
}

function renderListaUtilizadores(users) {
    const container = document.getElementById('adminUsersContainer');
    if (!container) return;

    const perfilMap = {
        'parceiro': 'Partner',
        'empresa': 'Company',
        'admin': 'Admin'
    };

    let html = `
        <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;margin-top:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
                <h4 style="color:#fff;margin:0;">👥 Users (${users.length})</h4>
                <button class="btn btn-primary btn-sm" onclick="abrirFormCriarUser()">➕ New User</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Profile</th>
                            <th>Full Name</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    users.forEach(user => {
        const isCurrentUser = user.username === state.username;
        html += `
            <tr>
                <td><strong>${user.username}</strong> ${isCurrentUser ? '👤' : ''}</td>
                <td><span class="status-tag ${user.perfil === 'admin' ? 'status-approved' : user.perfil === 'empresa' ? 'status-submitted' : 'status-draft'}">${perfilMap[user.perfil] || user.perfil}</span></td>
                <td>${user.nome_completo || '-'}</td>
                <td>${formatDate(user.created_at)}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="abrirFormAlterarPassword('${user.username}')">🔑</button>
                    ${!isCurrentUser ? `<button class="btn btn-danger btn-sm" onclick="eliminarUtilizador('${user.username}')">🗑️</button>` : ''}
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================
// ADMIN - CRIAR USER (COM AJUSTE LATERAL)
// =====================================================

function abrirFormCriarUser() {
    const container = document.getElementById('adminUsersContainer');
    if (!container) return;

    container.innerHTML = `
        <div style="background:rgba(255,255,255,0.08);border-radius:12px;padding:24px;margin-top:12px;border:1px solid rgba(254,200,0,0.2);">
            <h4 style="color:#fec800;margin:0 0 20px;">➕ Create New User</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                <div class="form-group" style="margin:0;display:flex;flex-direction:column;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;margin-bottom:4px;">Username *</label>
                    <input type="text" id="newUserUsername" placeholder="Ex: new_partner" style="width:100%;padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.1);color:#fff;font-size:14px;box-sizing:border-box;">
                </div>
                <div class="form-group" style="margin:0;display:flex;flex-direction:column;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;margin-bottom:4px;">Password *</label>
                    <input type="password" id="newUserPassword" placeholder="Min 3 characters" style="width:100%;padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.1);color:#fff;font-size:14px;box-sizing:border-box;">
                </div>
                <div class="form-group" style="margin:0;display:flex;flex-direction:column;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;margin-bottom:4px;">Full Name</label>
                    <input type="text" id="newUserNome" placeholder="Ex: John Doe" style="width:100%;padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.1);color:#fff;font-size:14px;box-sizing:border-box;">
                </div>
                <div class="form-group" style="margin:0;display:flex;flex-direction:column;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;margin-bottom:4px;">Profile *</label>
                    <select id="newUserPerfil" style="width:100%;padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.12);color:#fff;font-size:14px;box-sizing:border-box;">
                        <option value="parceiro" style="background:#1a2a4a;color:#fff;">Partner</option>
                        <option value="empresa" style="background:#1a2a4a;color:#fff;">Company</option>
                        <option value="admin" style="background:#1a2a4a;color:#fff;">Admin</option>
                    </select>
                </div>
            </div>
            <div style="display:flex;gap:10px;margin-top:20px;">
                <button class="btn btn-primary btn-sm" onclick="criarUtilizador()">✅ Create</button>
                <button class="btn btn-secondary btn-sm" onclick="carregarUtilizadores()">❌ Cancel</button>
            </div>
        </div>
    `;
}

async function criarUtilizador() {
    const username = document.getElementById('newUserUsername')?.value.trim();
    const password = document.getElementById('newUserPassword')?.value.trim();
    const nome = document.getElementById('newUserNome')?.value.trim();
    const perfil = document.getElementById('newUserPerfil')?.value;

    if (!username) {
        showToast('Username is required.', 'error');
        return;
    }

    if (!password || password.length < 3) {
        showToast('Password must be at least 3 characters.', 'error');
        return;
    }

    if (!perfil) {
        showToast('Profile is required.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/registar`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                username: username,
                password: password,
                perfil: perfil,
                nome_completo: nome || username
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error creating user');
        }

        showToast(`✅ User '${username}' created successfully!`, 'success');
        carregarUtilizadores();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error creating user: ' + error.message, 'error');
    }
}

// =====================================================
// ADMIN - ALTERAR PASSWORD (COM AJUSTE LATERAL)
// =====================================================

function abrirFormAlterarPassword(username) {
    const container = document.getElementById('adminUsersContainer');
    if (!container) return;

    container.innerHTML = `
        <div style="background:rgba(255,255,255,0.08);border-radius:12px;padding:20px 24px;margin-top:12px;border:1px solid rgba(254,200,0,0.2);max-width:450px;">
            <h4 style="color:#fec800;margin:0 0 16px;">🔑 Change Password - ${username}</h4>
            <div class="form-group" style="margin:0;display:flex;flex-direction:column;">
                <label style="color:rgba(255,255,255,0.7);font-size:12px;text-transform:uppercase;margin-bottom:4px;">New Password *</label>
                <input type="password" id="newPasswordInput" placeholder="Min 3 characters" style="width:100%;padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.1);color:#fff;font-size:14px;box-sizing:border-box;">
            </div>
            <div style="display:flex;gap:10px;margin-top:16px;">
                <button class="btn btn-primary btn-sm" onclick="alterarPassword('${username}')">✅ Save</button>
                <button class="btn btn-secondary btn-sm" onclick="carregarUtilizadores()">❌ Cancel</button>
            </div>
        </div>
    `;
}

async function alterarPassword(username) {
    const novaPassword = document.getElementById('newPasswordInput')?.value.trim();

    if (!novaPassword || novaPassword.length < 3) {
        showToast('Password must be at least 3 characters.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/usuarios/${username}/password`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                nova_password: novaPassword
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error changing password');
        }

        showToast(`✅ Password for '${username}' changed successfully!`, 'success');
        carregarUtilizadores();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error changing password: ' + error.message, 'error');
    }
}

async function eliminarUtilizador(username) {
    if (!confirm(`Are you sure you want to delete user '${username}'? This action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/usuarios/${username}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error deleting user');
        }

        showToast(`✅ User '${username}' deleted successfully!`, 'success');
        carregarUtilizadores();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error deleting user: ' + error.message, 'error');
    }
}

// =====================================================
// HEADERS DE AUTENTICAÇÃO
// =====================================================

function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${state.token}`,
        'Content-Type': 'application/json'
    };
}

// =====================================================
// HELPERS
// =====================================================

function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
}

function getDisplayName() {
    if (state.nome) {
        return state.nome.split(' ')[0];
    }
    if (state.username) {
        return state.username.split('.')[0];
    }
    return 'User';
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateStr;
    }
}

function getEstadoDisplay(estado) {
    return ESTADOS_MAP[estado] || estado;
}

function getEstadoClass(estado) {
    return ESTADOS_CORES[estado] || 'status-draft';
}

function safeCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// =====================================================
// TOPBAR
// =====================================================

function renderTopbar() {
    const nav = document.getElementById('topbarNav');
    if (!nav) return;

    const notifBadge = state.notificacoesNaoLidas > 0
        ? `<span class="badge-count">${state.notificacoesNaoLidas}</span>`
        : '';

    const isAdmin = state.perfil === 'admin';
    const currentPage = getCurrentPage();

    let html = '';
    let linkCount = 0;

    if (isAdmin) {
        if (currentPage !== 'documentos') {
            html += `
                <a href="documentos.html" class="dashboard-topbar__link">
                    📄 Documents
                </a>
            `;
            linkCount++;
        }
        
        if (currentPage !== 'dashboard') {
            html += `
                <a href="dashboard.html" class="dashboard-topbar__link">
                    📊 Dashboard
                </a>
            `;
            linkCount++;
        }
    } else {
        if (currentPage !== 'documentos') {
            html += `
                <a href="documentos.html" class="dashboard-topbar__link">
                    📄 Documents
                </a>
            `;
            linkCount++;
        }
    }

    if (currentPage !== 'notificacoes') {
        html += `
            <a href="notificacoes.html" class="dashboard-topbar__link">
                <span class="notification-badge">
                    🔔 Notifications ${notifBadge}
                </span>
            </a>
        `;
        linkCount++;
    }

    html += `
        <a href="#" class="dashboard-topbar__link" id="logoutLink">
            Logout
        </a>
    `;
    linkCount++;

    nav.innerHTML = html;

    document.getElementById('logoutLink')?.addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });

    const titleMap = {
        'documentos': '📄 Documents',
        'dashboard': '📊 Dashboard',
        'notificacoes': '🔔 Notifications'
    };
    const titleEl = document.getElementById('pageTitle');
    if (titleEl) {
        const currentPage = getCurrentPage();
        titleEl.textContent = titleMap[currentPage] || '📄 Documents';
    }

    const greetingEl = document.getElementById('dashboardGreeting');
    if (greetingEl) {
        greetingEl.textContent = `${getGreeting()}, ${state.username} 👋`;
    }

    const subtitleEl = document.getElementById('dashboardSubtitle');
    if (subtitleEl) {
        const perfilMap = {
            'admin': 'Administrator',
            'empresa': 'Company',
            'parceiro': 'Partner'
        };
        const perfilDisplay = perfilMap[state.perfil] || state.perfil;
        subtitleEl.textContent = `${perfilDisplay} Dashboard`;
    }
}

function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('dashboard.html')) return 'dashboard';
    if (path.includes('notificacoes.html')) return 'notificacoes';
    return 'documentos';
}

// =====================================================
// NOTIFICAÇÕES
// =====================================================

async function carregarNotificacoesNaoLidas() {
    try {
        const response = await fetch(`${API_URL}/notificacoes/nao-lidas`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            state.notificacoesNaoLidas = data.count || 0;
            renderTopbar();
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// =====================================================
// FILTROS
// =====================================================

function toggleFiltros() {
    const container = document.getElementById('filtrosContainer');
    const button = document.querySelector('.btn-filter-toggle');
    if (!container) return;

    const isVisible = container.style.maxHeight !== '0px' && container.style.maxHeight !== '0';
    
    if (isVisible) {
        container.style.maxHeight = '0';
        container.style.padding = '0';
        container.style.marginBottom = '0';
        container.style.borderColor = 'transparent';
        if (button) {
            button.classList.remove('active');
            button.innerHTML = '▶️ Filters';
        }
        sessionStorage.setItem('filtrosExpandidos', 'false');
    } else {
        container.style.maxHeight = '500px';
        container.style.padding = '16px';
        container.style.marginBottom = '20px';
        container.style.borderColor = 'rgba(254, 200, 0, 0.2)';
        if (button) {
            button.classList.add('active');
            button.innerHTML = '🔽 Filters';
        }
        sessionStorage.setItem('filtrosExpandidos', 'true');
    }
}

// =====================================================
// DOCUMENTOS - LISTAGEM
// =====================================================

async function carregarDocumentos() {
    try {
        const params = new URLSearchParams();
        if (state.filtros.q) params.append('q', state.filtros.q);
        if (state.filtros.estados.length) params.append('estados', state.filtros.estados.join(','));
        if (state.filtros.dataInicio) params.append('data_inicio', state.filtros.dataInicio);
        if (state.filtros.dataFim) params.append('data_fim', state.filtros.dataFim);

        const url = `${API_URL}/documentos/pesquisar?${params.toString()}`;
        const response = await fetch(url, { headers: getAuthHeaders() });

        if (response.ok) {
            state.documentos = await response.json();
            renderDocumentosList();
        } else {
            console.error('Error loading documents:', response.status);
            renderDocumentosList();
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        renderDocumentosList();
    }
}

function renderDocumentosList() {
    const container = document.getElementById('appContent');
    if (!container) return;

    const isParceiro = state.perfil === 'parceiro';
    const isEmpresa = state.perfil === 'empresa';
    const isAdmin = state.perfil === 'admin';

    let html = '';

    // ============================================================
    // ADMIN MENU (apenas para admin)
    // ============================================================
    if (isAdmin) {
        html += `
            <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;">
                <button class="btn ${adminMenuAtivo === 'documents' ? 'btn-primary' : 'btn-secondary'}" 
                        onclick="mudarAdminView('documents')">
                    📄 Documents
                </button>
                <button class="btn ${adminMenuAtivo === 'users' ? 'btn-primary' : 'btn-secondary'}" 
                        onclick="mudarAdminView('users'); carregarUtilizadores();">
                    👥 Users
                </button>
            </div>
        `;
    }

    // ============================================================
    // ADMIN - USERS VIEW
    // ============================================================
    if (isAdmin && adminMenuAtivo === 'users') {
        html += `<div id="adminUsersContainer"></div>`;
        container.innerHTML = html;
        carregarUtilizadores();
        return;
    }

    // ============================================================
    // DOCUMENTS VIEW (para todos os perfis)
    // ============================================================

    const filtrosExpandidos = false;

    html += `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
                ${isEmpresa ? `<button class="btn btn-primary" onclick="abrirFormCriar()">➕ New Document</button>` : ''}
                <button class="btn btn-secondary" onclick="carregarDocumentos()">
                    🔄 Refresh
                </button>
                <button class="btn-filter-toggle" onclick="toggleFiltros()">
                    ▶️ Filters
                </button>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
                <span style="color:rgba(255,255,255,0.7);font-size:14px;">${state.documentos.length} documents</span>
            </div>
        </div>
    `;

    // FILTROS
    html += `
        <div id="filtrosContainer" style="max-height:0;padding:0;margin-bottom:0;overflow:hidden;transition:max-height 0.3s ease, padding 0.3s ease, margin 0.3s ease;background:rgba(255,255,255,0.08);border-radius:10px;border:1px solid transparent;">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;align-items:end;padding:0;">
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;margin-bottom:4px;display:block;text-transform:uppercase;letter-spacing:0.5px;">Search</label>
                    <input type="text" id="filtroBusca" placeholder="Title, partner or ID..." 
                           value="${state.filtros.q}" style="width:100%;">
                </div>
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;margin-bottom:4px;display:block;text-transform:uppercase;letter-spacing:0.5px;">Status</label>
                    <select id="filtroEstados" style="width:100%;">
                        <option value="">All Statuses</option>
                        <option value="Rascunho" ${state.filtros.estados.includes('Rascunho') ? 'selected' : ''}>Draft</option>
                        <option value="Submetido" ${state.filtros.estados.includes('Submetido') ? 'selected' : ''}>Submitted</option>
                        <option value="Em Revisão" ${state.filtros.estados.includes('Em Revisão') ? 'selected' : ''}>In Review</option>
                        <option value="Alterações" ${state.filtros.estados.includes('Alterações') ? 'selected' : ''}>Changes Requested</option>
                        <option value="Aprovado" ${state.filtros.estados.includes('Aprovado') ? 'selected' : ''}>Approved</option>
                        <option value="Arquivado" ${state.filtros.estados.includes('Arquivado') ? 'selected' : ''}>Archived</option>
                    </select>
                </div>
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;margin-bottom:4px;display:block;text-transform:uppercase;letter-spacing:0.5px;">From</label>
                    <input type="date" id="filtroDataInicio" value="${state.filtros.dataInicio || ''}" style="width:100%;">
                </div>
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;margin-bottom:4px;display:block;text-transform:uppercase;letter-spacing:0.5px;">To</label>
                    <input type="date" id="filtroDataFim" value="${state.filtros.dataFim || ''}" style="width:100%;">
                </div>
            </div>
            <div style="display:flex;gap:10px;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">
                <button class="btn btn-primary btn-sm" onclick="aplicarFiltros()">Apply Filters</button>
                <button class="btn btn-secondary btn-sm" onclick="limparFiltros()">Clear</button>
            </div>
        </div>
    `;

    // Lista de documentos
    if (!state.documentos || state.documentos.length === 0) {
        html += `
            <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:40px;text-align:center;color:rgba(255,255,255,0.6);">
                <p style="font-size:18px;">📭 No documents found</p>
                <p style="font-size:14px;">Create a new document to get started</p>
            </div>
        `;
    } else {
        html += `
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Partner</th>
                            <th>Status</th>
                            <th>Version</th>
                            <th>Last Update</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                `;

        state.documentos.forEach(doc => {
            const estadoDisplay = getEstadoDisplay(doc.estado);
            const estadoClass = getEstadoClass(doc.estado);

            html += `
                <tr>
                    <td><strong>${doc.id}</strong></td>
                    <td>${doc.titulo}</td>
                    <td>${doc.parceiro_id}</td>
                    <td><span class="status-tag ${estadoClass}">${estadoDisplay}</span></td>
                    <td>v${doc.versao_atual}</td>
                    <td>${formatDate(doc.updated_at)}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="abrirDocumento(${doc.id})">Open</button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
    }

    if (state.docSelecionado) {
        html += `<div id="documentoDetalhe" style="margin-top:30px;"></div>`;
    }

    container.innerHTML = html;

    if (state.docSelecionado) {
        carregarDocumentoDetalhe(state.docSelecionado);
    }

    document.getElementById('filtroBusca')?.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') aplicarFiltros();
    });
}

// =====================================================
// DOCUMENTOS - ABRIR / DETALHE
// =====================================================

async function abrirDocumento(docId) {
    console.log('📄 Abrindo documento:', docId);
    state.docSelecionado = docId;
    state.editData = null;
    
    await carregarDocumentos();
    
    setTimeout(() => {
        const detalhe = document.getElementById('documentoDetalhe');
        if (detalhe) {
            detalhe.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 300);
}

async function carregarDocumentoDetalhe(docId) {
    try {
        const response = await fetch(`${API_URL}/documentos/${docId}`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Error loading document');
        }

        const doc = await response.json();
        renderDocumentoDetalhe(doc);
    } catch (error) {
        console.error('Error:', error);
        const container = document.getElementById('documentoDetalhe');
        if (container) {
            container.innerHTML = `
                <div style="background:rgba(255,0,0,0.1);border-radius:12px;padding:20px;color:#ff6b6b;">
                    ❌ Error loading document: ${error.message}
                </div>
            `;
        }
    }
}

function renderDocumentoDetalhe(doc) {
    const container = document.getElementById('documentoDetalhe');
    if (!container) return;

    const isParceiro = state.perfil === 'parceiro';
    const isEmpresa = state.perfil === 'empresa';
    const isAdmin = state.perfil === 'admin';

    const estadoDisplay = getEstadoDisplay(doc.estado);
    const estadoClass = getEstadoClass(doc.estado);

    // ✅ PARCEIRO PODE EDITAR EM RASCUNHO OU CHANGES REQUESTED
    const podeEditar = isParceiro && (doc.estado === 'Rascunho' || doc.estado === 'Alterações');
    const podeSubmeter = isParceiro && doc.estado === 'Rascunho';
    const podeRevisar = (isEmpresa || isAdmin) && doc.estado === 'Submetido';
    const podeAprovar = (isEmpresa || isAdmin) && doc.estado === 'Em Revisão';
    const podePedirAlteracoes = (isEmpresa || isAdmin) && doc.estado === 'Em Revisão';
    const podeReabrir = (isEmpresa || isAdmin) && doc.estado === 'Aprovado';
    const podeArquivar = (isEmpresa || isAdmin) && ['Rascunho', 'Aprovado'].includes(doc.estado);

    const processos = getProcessosFromData(doc.dados);

    let html = `
        <div style="background:rgba(255,255,255,0.05);border-radius:16px;padding:24px;border-left:4px solid #fec800;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
                <div>
                    <h3 style="color:#fff;margin:0;">📄 ${doc.titulo}</h3>
                    <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">ID: ${doc.id} | Partner: ${doc.parceiro_id} | Version: v${doc.versao_atual}</p>
                </div>
                <span class="status-tag ${estadoClass}" style="font-size:16px;padding:6px 16px;">${estadoDisplay}</span>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:12px;">
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;">Created</span>
                    <p style="color:rgba(255,255,255,0.8);margin:0;">${formatDate(doc.created_at)}</p>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:12px;">
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;">Last Update</span>
                    <p style="color:rgba(255,255,255,0.8);margin:0;">${formatDate(doc.updated_at)}</p>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:12px;">
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;">Processes</span>
                    <p style="color:rgba(255,255,255,0.8);margin:0;">${processos.join(', ')}</p>
                </div>
            </div>
    `;

    // Conteúdo
    html += `
        <div style="margin-bottom:20px;">
            <button class="btn btn-secondary btn-sm" onclick="toggleConteudoDocumento(${doc.id})">
                📊 Show/Hide Document Content
            </button>
            <div id="conteudoDocumento" style="display:none;margin-top:12px;">
                ${renderConteudoDocumento(doc.dados, processos, true)}
            </div>
        </div>
    `;

    // Ações
    html += `
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">
    `;

    if (podeEditar) {
        html += `<button class="btn btn-primary" onclick="abrirEdicaoDocumento(${doc.id})">✏️ Edit</button>`;
    }

    if (podeSubmeter) {
        html += `<button class="btn btn-success" onclick="submeterDocumento(${doc.id})">📤 Submit for Review</button>`;
    }

    if (podeRevisar) {
        html += `<button class="btn btn-warning" onclick="iniciarRevisao(${doc.id})">🔍 Start Review</button>`;
    }

    if (podeAprovar) {
        html += `<button class="btn btn-success" onclick="aprovarDocumento(${doc.id})">✅ Approve</button>`;
    }

    if (podePedirAlteracoes) {
        html += `
            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                <input type="text" id="comentarioAlteracoes" placeholder="Reason for changes..." style="flex:1;min-width:200px;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;" />
                <button class="btn btn-danger" onclick="pedirAlteracoes(${doc.id})">🔄 Request Changes</button>
            </div>
        `;
    }

    if (podeReabrir) {
        html += `<button class="btn btn-warning" onclick="reabrirDocumento(${doc.id})">🔁 Reopen</button>`;
    }

    if (podeArquivar) {
        html += `<button class="btn btn-secondary" onclick="arquivarDocumento(${doc.id})">📁 Archive</button>`;
    }

    html += `
        <button class="btn btn-secondary" onclick="exportarExcel(${doc.id}, '${doc.titulo}')">📊 Export Excel</button>
        <button class="btn btn-secondary" onclick="fecharDocumento()">✖ Close</button>
    `;

    html += `
        </div>
    `;

    // Editor
    if (state.editData !== null) {
        html += renderEditorDocumento(doc.id, processos);
    }

    // Histórico
    html += `
        <div style="margin-top:16px;">
            <button class="btn btn-secondary btn-sm" onclick="carregarHistorico(${doc.id})">📜 Version History</button>
            <div id="historicoVersoes" style="margin-top:12px;"></div>
        </div>
    `;

    html += `
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================
// CONTEÚDO DO DOCUMENTO (LCA/LCC) - COM TODOS OS DROPDOWNS ABERTOS
// =====================================================

function renderConteudoDocumento(dados, processos, allOpen = false) {
    let html = '';

    // LCA
    html += `<h4 style="color:#fff;margin:16px 0 8px;">🌱 LCA - Life Cycle Assessment</h4>`;

    ['inputs', 'processes', 'outputs'].forEach(section => {
        const sectionDisplay = section.charAt(0).toUpperCase() + section.slice(1);
        html += `<h5 style="color:rgba(255,255,255,0.6);margin:12px 0 4px;">${sectionDisplay}</h5>`;
        processos.forEach(proc => {
            const items = dados?.lca?.[section]?.[proc] || [];
            if (items.length) {
                html += `
                    <details style="margin:4px 0 8px;" ${allOpen ? 'open' : ''}>
                        <summary style="color:rgba(255,255,255,0.7);cursor:pointer;">${proc} (${items.length} items)</summary>
                        <div style="padding:8px;background:rgba(255,255,255,0.03);border-radius:6px;margin-top:4px;overflow-x:auto;">
                            <table style="width:100%;font-size:12px;border-collapse:collapse;">
                                <thead>
                                    <tr style="color:rgba(255,255,255,0.4);border-bottom:1px solid rgba(255,255,255,0.1);">
                                        ${Object.keys(items[0] || {}).map(k => `<th style="padding:4px 8px;text-align:left;">${k}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${items.map(item => `
                                        <tr style="color:rgba(255,255,255,0.6);border-bottom:1px solid rgba(255,255,255,0.05);">
                                            ${Object.values(item).map(v => `<td style="padding:4px 8px;">${v || '-'}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </details>
                `;
            } else {
                html += `<div style="color:rgba(255,255,255,0.3);font-size:12px;margin:4px 0 8px 16px;">${proc}: no data</div>`;
            }
        });
    });

    // LCC
    html += `<h4 style="color:#fff;margin:16px 0 8px;">💰 LCC - Life Cycle Cost</h4>`;

    ['materials', 'equipment', 'labour', 'outputs'].forEach(section => {
        const sectionNames = {
            materials: 'Cost Breakdown Material',
            equipment: 'Equipment',
            labour: 'Labour',
            outputs: 'Outputs'
        };
        html += `<h5 style="color:rgba(255,255,255,0.6);margin:12px 0 4px;">${sectionNames[section]}</h5>`;
        processos.forEach(proc => {
            const items = dados?.lcc?.[section]?.[proc] || [];
            if (items.length) {
                html += `
                    <details style="margin:4px 0 8px;" ${allOpen ? 'open' : ''}>
                        <summary style="color:rgba(255,255,255,0.7);cursor:pointer;">${proc} (${items.length} items)</summary>
                        <div style="padding:8px;background:rgba(255,255,255,0.03);border-radius:6px;margin-top:4px;overflow-x:auto;">
                            <table style="width:100%;font-size:12px;border-collapse:collapse;">
                                <thead>
                                    <tr style="color:rgba(255,255,255,0.4);border-bottom:1px solid rgba(255,255,255,0.1);">
                                        ${Object.keys(items[0] || {}).map(k => `<th style="padding:4px 8px;text-align:left;">${k}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${items.map(item => `
                                        <tr style="color:rgba(255,255,255,0.6);border-bottom:1px solid rgba(255,255,255,0.05);">
                                            ${Object.values(item).map(v => `<td style="padding:4px 8px;">${v || '-'}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </details>
                `;
            } else {
                html += `<div style="color:rgba(255,255,255,0.3);font-size:12px;margin:4px 0 8px 16px;">${proc}: no data</div>`;
            }
        });
    });

    return html;
}

function toggleConteudoDocumento(docId) {
    const container = document.getElementById('conteudoDocumento');
    if (container) {
        const isVisible = container.style.display === 'none' || container.style.display === '';
        
        if (isVisible) {
            // ✅ ABRIR: carregar com allOpen=true
            container.style.display = 'block';
            
            // Buscar o documento e re-renderizar com todos os dropdowns abertos
            fetch(`${API_URL}/documentos/${docId}`, {
                headers: getAuthHeaders()
            })
            .then(response => response.json())
            .then(doc => {
                const processos = getProcessosFromData(doc.dados);
                container.innerHTML = renderConteudoDocumento(doc.dados, processos, true);
                
                // ✅ ABRIR TODOS OS DETAILS MANUALMENTE
                const details = container.querySelectorAll('details');
                details.forEach(d => d.setAttribute('open', ''));
            })
            .catch(error => {
                console.error('Error loading document content:', error);
                showToast('Error loading document content', 'error');
            });
        } else {
            // FECHAR
            container.style.display = 'none';
        }
    }
}

function getProcessosFromData(dados) {
    if (dados && dados.lca && dados.lca.inputs) {
        const processos = Object.keys(dados.lca.inputs);
        if (processos.length) return processos;
    }
    return PROCESSOS_PADRAO;
}

// =====================================================
// EDITOR DO DOCUMENTO (LCA/LCC)
// =====================================================

function abrirEdicaoDocumento(docId) {
    fetch(`${API_URL}/documentos/${docId}`, {
        headers: getAuthHeaders()
    })
    .then(response => response.json())
    .then(doc => {
        const processos = getProcessosFromData(doc.dados);
        state.editData = ensureEstruturaCompleta(doc.dados, processos);
        carregarDocumentoDetalhe(docId);
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error preparing editor: ' + error.message, 'error');
    });
}

function ensureEstruturaCompleta(dados, processos) {
    if (!dados) {
        return criarEstruturaVazia(processos);
    }

    if (!dados.lca) dados.lca = { inputs: {}, processes: {}, outputs: {} };
    if (!dados.lcc) dados.lcc = { materials: {}, equipment: {}, labour: {}, outputs: {} };

    ['lca', 'lcc'].forEach(secao => {
        const campos = secao === 'lca' 
            ? ['inputs', 'processes', 'outputs']
            : ['materials', 'equipment', 'labour', 'outputs'];
        campos.forEach(campo => {
            if (!dados[secao][campo]) dados[secao][campo] = {};
            processos.forEach(p => {
                if (!dados[secao][campo][p]) dados[secao][campo][p] = [];
            });
        });
    });

    return dados;
}

function criarEstruturaVazia(processos) {
    const dados = {
        lca: { inputs: {}, processes: {}, outputs: {} },
        lcc: { materials: {}, equipment: {}, labour: {}, outputs: {} }
    };

    processos.forEach(p => {
        dados.lca.inputs[p] = [];
        dados.lca.processes[p] = [];
        dados.lca.outputs[p] = [];
        dados.lcc.materials[p] = [];
        dados.lcc.equipment[p] = [];
        dados.lcc.labour[p] = [];
        dados.lcc.outputs[p] = [];
    });

    return dados;
}

// =====================================================
// RENDER EDITOR SECAO - CORRIGIDO
// =====================================================

function renderEditorSecao(secao, campo, docId, processos) {
    const dados = state.editData;
    if (!dados) return '';

    const nomesCampos = {
        inputs: 'Inputs',
        processes: 'Processes',
        outputs: 'Outputs (LCA)',
        materials: 'Cost Breakdown Material',
        equipment: 'Equipment',
        labour: 'Labour',
        outputs_lcc: 'Outputs (LCC)'
    };

    const nomeCampo = campo === 'outputs' && secao === 'lcc' ? 'outputs_lcc' : campo;
    const displayName = nomesCampos[nomeCampo] || campo;

    const fieldLabels = {
        material: 'Material',
        qty: 'Qty',
        unit: 'Unit',
        description: 'Description',
        cas: 'CAS',
        distance: 'Distance',
        country: 'Country',
        datasource: 'Data Source',
        tipo: 'Type',
        comments: 'Comments',
        etapa: 'Step',
        sub_tipo: 'Sub Type',
        price: 'Price',
        equipment: 'Equipment',
        process: 'Process',
        unit_cost: 'Unit Cost',
        lifespan: 'Lifespan',
        maintenance: 'Maintenance',
        industrial_equiv: 'Industrial Equiv',
        total_number: 'Total Number',
        total_cost: 'Total Cost',
        high_skilled: 'High Skilled',
        moderate_skilled: 'Moderate Skilled',
        unskilled: 'Unskilled',
        high_rate: 'High Rate',
        moderate_rate: 'Moderate Rate',
        unskilled_rate: 'Unskilled Rate',
        market_price: 'Market Price',
        quantity: 'Quantity',
        amount_produced: 'Amount Produced'
    };

    const camposReadOnly = ['tipo', 'unit'];

    let html = `
        <details style="margin:12px 0;" open>
            <summary style="color:rgba(255,255,255,0.8);cursor:pointer;font-weight:600;font-size:15px;padding:4px 0;">${displayName}</summary>
            <div style="padding:16px 20px;background:rgba(255,255,255,0.02);border-radius:10px;margin-top:10px;">
    `;

    processos.forEach(proc => {
        const items = dados[secao]?.[campo]?.[proc] || [];
        const itemKey = `${secao}_${campo}_${proc}`;

        html += `
            <div style="margin:12px 0 16px;border-left:3px solid rgba(254,200,0,0.25);padding-left:16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:8px;">
                    <strong style="color:rgba(255,255,255,0.85);font-size:15px;">${proc}</strong>
                    <span style="color:rgba(255,255,255,0.35);font-size:13px;">${items.length} items</span>
                </div>
                <div id="${itemKey}_container">
        `;

        if (items.length === 0) {
            html += `
                <div style="color:rgba(255,255,255,0.35);font-size:14px;padding:12px 0;">No items</div>
            `;
        } else {
            items.forEach((item, idx) => {
                const itemId = `${itemKey}_${idx}`;
                const keys = Object.keys(item);
                
                const grupos = [];
                for (let i = 0; i < keys.length; i += 3) {
                    grupos.push(keys.slice(i, i + 3));
                }

                html += `
                    <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:12px 14px;margin:6px 0 8px;border:1px solid rgba(255,255,255,0.05);">
                `;

                grupos.forEach(grupo => {
                    html += `
                        <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px 16px;margin-bottom:4px;">
                    `;
                    grupo.forEach(key => {
                        const value = item[key] || '';
                        const label = fieldLabels[key] || key.charAt(0).toUpperCase() + key.slice(1);
                        const isReadOnly = camposReadOnly.includes(key);

                        if (key === 'datasource') {
                            html += `
                                <div style="display:flex;flex-direction:column;gap:2px;">
                                    <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                                    <select data-section="${secao}" data-campo="${campo}" data-proc="${proc}" data-idx="${idx}" data-key="${key}" 
                                            style="width:100%;max-width:180px;background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.15);border-radius:5px;padding:6px 10px;font-size:13px;font-family:'Inter',sans-serif;transition:border-color 0.2s;">
                                        ${DATASOURCE_OPTIONS.map(opt => `<option value="${opt}" ${opt === value ? 'selected' : ''} style="background:#1a2a4a;color:#fff;">${opt}</option>`).join('')}
                                    </select>
                                </div>
                            `;
                        } else if (typeof value === 'string' || typeof value === 'number') {
                            if (isReadOnly) {
                                html += `
                                    <div style="display:flex;flex-direction:column;gap:2px;">
                                        <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                                        <input type="text" value="${value}" 
                                               disabled
                                               style="width:100%;max-width:180px;background:rgba(255,255,255,0.07);color:#fff;border:1px solid rgba(255,255,255,0.12);border-radius:5px;padding:6px 10px;font-size:13px;font-family:'Inter',sans-serif;opacity:0.8;cursor:not-allowed;" />
                                    </div>
                                `;
                            } else {
                                html += `
                                    <div style="display:flex;flex-direction:column;gap:2px;">
                                        <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                                        <input type="text" value="${value}" 
                                               data-section="${secao}" data-campo="${campo}" data-proc="${proc}" data-idx="${idx}" data-key="${key}"
                                               placeholder="${label}"
                                               style="width:100%;max-width:180px;background:rgba(255,255,255,0.07);color:#fff;border:1px solid rgba(255,255,255,0.12);border-radius:5px;padding:6px 10px;font-size:13px;font-family:'Inter',sans-serif;transition:border-color 0.2s, background 0.2s;" />
                                    </div>
                                `;
                            }
                        }
                    });
                    html += `
                        </div>
                    `;
                });

                html += `
                        <div style="display:flex;justify-content:flex-end;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.05);">
                            <button class="btn btn-danger btn-sm" onclick="removerItemEditor('${secao}','${campo}','${proc}',${idx})" style="padding:3px 10px;font-size:11px;border-radius:4px;">✕ Remove</button>
                        </div>
                    </div>
                `;
            });
        }

        html += `
                </div>
                <button class="btn btn-secondary btn-sm" style="margin-top:6px;padding:5px 14px;font-size:12px;border-radius:5px;" onclick="adicionarItemEditor('${secao}','${campo}','${proc}')">+ Add item</button>
            </div>
        `;
    });

    html += `
            </div>
        </details>
    `;

    return html;
}

// =====================================================
// EDITOR DOCUMENTO - COMPLETO
// =====================================================

function renderEditorDocumento(docId, processos) {
    let html = `
        <div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:20px;margin-top:16px;border:1px solid rgba(254,200,0,0.2);">
            <h4 style="color:#fec800;margin:0 0 16px;">✏️ Editing Document</h4>
    `;

    html += `<h5 style="color:#fff;">🌱 LCA</h5>`;
    html += renderEditorSecao('lca', 'inputs', docId, processos);
    html += renderEditorSecao('lca', 'processes', docId, processos);
    html += renderEditorSecao('lca', 'outputs', docId, processos);

    html += `<h5 style="color:#fff;margin-top:20px;">💰 LCC</h5>`;
    html += renderEditorSecao('lcc', 'materials', docId, processos);
    html += renderEditorSecao('lcc', 'equipment', docId, processos);
    html += renderEditorSecao('lcc', 'labour', docId, processos);
    html += renderEditorSecao('lcc', 'outputs', docId, processos);

    html += `
        <div style="display:flex;gap:12px;margin-top:20px;flex-wrap:wrap;">
            <button class="btn btn-primary" onclick="salvarEdicao(${docId})">💾 Save Draft</button>
            <button class="btn btn-success" onclick="submeterEdicao(${docId})">📤 Submit for Review</button>
            <button class="btn btn-secondary" onclick="cancelarEdicao()">✖ Cancel</button>
        </div>
    `;

    html += `</div>`;
    return html;
}

// =====================================================
// ADICIONAR ITEM - MANTÉM MENUS ABERTOS
// =====================================================

function adicionarItemEditor(secao, campo, proc) {
    if (!state.editData) return;
    if (!state.editData[secao]) state.editData[secao] = {};
    if (!state.editData[secao][campo]) state.editData[secao][campo] = {};
    if (!state.editData[secao][campo][proc]) state.editData[secao][campo][proc] = [];

    // ✅ CRIAR NOVO ITEM COM A MESMA ESTRUTURA DO PRIMEIRO ITEM
    const currentItems = state.editData[secao][campo][proc];
    let newItem = {};
    
    if (currentItems.length > 0) {
        // Copiar a estrutura do primeiro item (com os campos vazios)
        const firstItem = currentItems[0];
        Object.keys(firstItem).forEach(key => {
            newItem[key] = '';
        });
    } else {
        // Se não houver itens, criar um item vazio com os campos padrão
        const camposPadrao = {
            'lca': {
                'inputs': ['material', 'qty', 'unit', 'description', 'cas', 'distance', 'country', 'datasource'],
                'processes': ['tipo', 'qty', 'unit', 'description', 'comments', 'datasource'],
                'outputs': ['etapa', 'tipo', 'sub_tipo', 'qty', 'unit', 'description', 'comments', 'datasource']
            },
            'lcc': {
                'materials': ['material', 'price', 'qty', 'unit', 'description', 'comments', 'distance', 'country', 'datasource'],
                'equipment': ['equipment', 'process', 'unit_cost', 'lifespan', 'maintenance', 'industrial_equiv', 'comments', 'datasource'],
                'labour': ['process', 'total_number', 'total_cost', 'high_skilled', 'moderate_skilled', 'unskilled', 'high_rate', 'moderate_rate', 'unskilled_rate', 'comments', 'datasource'],
                'outputs': ['material', 'market_price', 'quantity', 'unit', 'amount_produced', 'comments', 'datasource']
            }
        };
        
        const campos = camposPadrao[secao]?.[campo] || [];
        campos.forEach(key => {
            newItem[key] = '';
        });
    }

    currentItems.push(newItem);
    
    // ✅ RECARREGAR O DOCUMENTO MANTENDO OS MENUS ABERTOS
    carregarDocumentoDetalhe(state.docSelecionado);
}

function removerItemEditor(secao, campo, proc, idx) {
    if (!state.editData) return;
    if (!state.editData[secao]?.[campo]?.[proc]) return;

    state.editData[secao][campo][proc].splice(idx, 1);
    
    // ✅ RECARREGAR O DOCUMENTO MANTENDO OS MENUS ABERTOS
    carregarDocumentoDetalhe(state.docSelecionado);
}

// =====================================================
// SALVAR E SUBMETER EDIÇÃO
// =====================================================

function salvarEdicao(docId) {
    const dados = state.editData;
    if (!dados) return;

    fetch(`${API_URL}/documentos/${docId}/editar`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ dados: dados })
    })
    .then(response => {
        if (!response.ok) throw new Error('Error saving');
        return response.json();
    })
    .then(() => {
        showToast('✅ Document saved successfully!', 'success');
        state.editData = null;
        carregarDocumentoDetalhe(docId);
        carregarDocumentos();
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error saving: ' + error.message, 'error');
    });
}

function submeterEdicao(docId) {
    const dados = state.editData;
    if (!dados) return;

    fetch(`${API_URL}/documentos/${docId}/editar`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ dados: dados })
    })
    .then(response => {
        if (!response.ok) throw new Error('Error saving');
        return response.json();
    })
    .then(() => {
        return fetch(`${API_URL}/documentos/${docId}/submeter`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
    })
    .then(response => {
        if (!response.ok) throw new Error('Error submitting');
        return response.json();
    })
    .then(() => {
        showToast('✅ Document submitted successfully!', 'success');
        state.editData = null;
        state.docSelecionado = null;
        carregarDocumentos();
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    });
}

function cancelarEdicao() {
    state.editData = null;
    carregarDocumentoDetalhe(state.docSelecionado);
}

// =====================================================
// AÇÕES DOS DOCUMENTOS
// =====================================================

async function submeterDocumento(docId) {
    if (!confirm('Submit this document for review?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/submeter`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error submitting');

        showToast('✅ Document submitted successfully!', 'success');
        state.docSelecionado = null;
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function iniciarRevisao(docId) {
    if (!confirm('Start review for this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/iniciar-revisao`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error starting review');

        showToast('✅ Review started!', 'success');
        carregarDocumentoDetalhe(docId);
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function aprovarDocumento(docId) {
    if (!confirm('Approve this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/aprovar`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error approving');

        showToast('✅ Document approved!', 'success');
        state.docSelecionado = null;
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function pedirAlteracoes(docId) {
    const comentario = document.getElementById('comentarioAlteracoes')?.value?.trim();
    if (!comentario) {
        showToast('Please enter a reason for the changes.', 'warning');
        return;
    }

    if (!confirm('Request changes for this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/pedir-alteracoes`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ comentario: comentario })
        });

        if (!response.ok) throw new Error('Error requesting changes');

        showToast('✅ Changes requested!', 'success');
        carregarDocumentoDetalhe(docId);
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function reabrirDocumento(docId) {
    if (!confirm('Reopen this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/reabrir`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error reopening');

        showToast('✅ Document reopened!', 'success');
        carregarDocumentoDetalhe(docId);
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function arquivarDocumento(docId) {
    if (!confirm('Archive this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/arquivar`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error archiving');

        showToast('✅ Document archived!', 'success');
        state.docSelecionado = null;
        carregarDocumentos();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

function fecharDocumento() {
    state.docSelecionado = null;
    state.editData = null;
    carregarDocumentos();
}

// =====================================================
// HISTÓRICO
// =====================================================

async function carregarHistorico(docId) {
    const container = document.getElementById('historicoVersoes');
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/versoes`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error loading history');

        const versoes = await response.json();

        if (!versoes || versoes.length === 0) {
            container.innerHTML = `<div style="color:rgba(255,255,255,0.4);padding:8px;">No history available.</div>`;
            return;
        }

        let html = `
            <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;">
                <table style="width:100%;font-size:13px;border-collapse:collapse;">
                    <thead>
                        <tr style="color:rgba(255,255,255,0.4);border-bottom:1px solid rgba(255,255,255,0.1);">
                            <th style="padding:6px 8px;text-align:left;">Version</th>
                            <th style="padding:6px 8px;text-align:left;">Status</th>
                            <th style="padding:6px 8px;text-align:left;">User</th>
                            <th style="padding:6px 8px;text-align:left;">Date</th>
                            <th style="padding:6px 8px;text-align:left;">Comment</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        versoes.forEach(v => {
            html += `
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:6px 8px;color:rgba(255,255,255,0.7);">v${v.numero_versao}</td>
                    <td style="padding:6px 8px;"><span class="status-tag ${getEstadoClass(v.estado)}">${getEstadoDisplay(v.estado)}</span></td>
                    <td style="padding:6px 8px;color:rgba(255,255,255,0.6);">${v.criado_por || '-'}</td>
                    <td style="padding:6px 8px;color:rgba(255,255,255,0.4);">${formatDate(v.created_at)}</td>
                    <td style="padding:6px 8px;color:rgba(255,255,255,0.5);">${v.comentario || '-'}</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div style="color:#ff6b6b;">Error loading history.</div>`;
    }
}

// =====================================================
// EXPORTAR EXCEL
// =====================================================

async function exportarExcel(docId, titulo) {
    try {
        const response = await fetch(`${API_URL}/documentos/${docId}/exportar-excel`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error exporting');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${titulo || 'document'}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error:', error);
        showToast('Error exporting: ' + error.message, 'error');
    }
}

// =====================================================
// DASHBOARD
// =====================================================

async function carregarDashboard() {
    const container = document.getElementById('appContent');
    if (!container) return;

    try {
        const kpiResponse = await fetch(`${API_URL}/dashboard/kpis`, {
            headers: getAuthHeaders()
        });

        if (!kpiResponse.ok) throw new Error('Error loading KPIs');

        const kpis = await kpiResponse.json();

        const docsResponse = await fetch(`${API_URL}/dashboard/documentos-recentes?limit=100`, {
            headers: getAuthHeaders()
        });

        let documentos = [];
        if (docsResponse.ok) {
            documentos = await docsResponse.json();
        }

        const topResponse = await fetch(`${API_URL}/dashboard/top-parceiros?limit=10`, {
            headers: getAuthHeaders()
        });

        let topParceiros = [];
        if (topResponse.ok) {
            topParceiros = await topResponse.json();
        }

        renderDashboard(kpis, documentos, topParceiros);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div style="background:rgba(255,0,0,0.1);border-radius:12px;padding:20px;color:#ff6b6b;">
                ❌ Error loading dashboard: ${error.message}
            </div>
        `;
    }
}

function renderDashboard(kpis, documentos, topParceiros) {
    const container = document.getElementById('appContent');
    if (!container) return;

    const estados = kpis.documentos_por_estado || {};
    const totalDocs = kpis.total_documentos || 0;
    const aprovados = kpis.aprovados || 0;
    const taxaAprovacao = kpis.taxa_aprovacao || 0;

    let html = `
        <!-- STATS -->
        <div class="dashboard-stats" style="margin-bottom:24px;">
            <div class="dashboard-stat-card">
                <div class="stat-icon stat-icon-draft">
                    <div class="stat-icon-img" style="background-image:url('../imagen/Annual_leave_left.png');"></div>
                </div>
                <div class="stat-copy">
                    <strong class="stat-value">${totalDocs}</strong>
                    <span class="stat-label">Total Documents</span>
                    <span class="stat-meta">in the platform</span>
                </div>
            </div>
            <div class="dashboard-stat-card">
                <div class="stat-icon stat-icon-approved">
                    <div class="stat-icon-img" style="background-image:url('../imagen/Pending_approvals.png');"></div>
                </div>
                <div class="stat-copy">
                    <strong class="stat-value">${aprovados}</strong>
                    <span class="stat-label">Approved</span>
                    <span class="stat-meta">documents approved</span>
                </div>
            </div>
            <div class="dashboard-stat-card">
                <div class="stat-icon stat-icon-submitted">
                    <div class="stat-icon-img" style="background-image:url('../imagen/WFH_Days_left.png');"></div>
                </div>
                <div class="stat-copy">
                    <strong class="stat-value">${taxaAprovacao}%</strong>
                    <span class="stat-label">Approval Rate</span>
                    <span class="stat-meta">of submitted documents</span>
                </div>
            </div>
        </div>

        <!-- GRÁFICOS -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:24px;">
            <div style="background:#f7f7f8;border-radius:16px;padding:16px;">
                <h4 style="color:#17345a;margin:0 0 12px;">Documents by Status</h4>
                <div id="chartPizza" style="height:300px;"></div>
            </div>
            <div style="background:#f7f7f8;border-radius:16px;padding:16px;">
                <h4 style="color:#17345a;margin:0 0 12px;">Status Distribution</h4>
                <div id="chartBarras" style="height:300px;"></div>
            </div>
        </div>
    `;

    // ✅ TOP PARTNERS (mantido)
    if (topParceiros && topParceiros.length > 0) {
        html += `
            <div style="background:#f7f7f8;border-radius:16px;padding:16px;margin-bottom:24px;">
                <h4 style="color:#17345a;margin:0 0 12px;">🏆 Top Partners</h4>
                <div id="chartTop" style="height:250px;"></div>
            </div>
        `;
    }

    // ❌ TABELA DE DOCUMENTOS RECENTES REMOVIDA

    container.innerHTML = html;

    // Renderizar gráficos
    renderGraficos(estados, topParceiros);
}

function renderGraficos(estados, topParceiros) {
    // ✅ CONFIGURAÇÃO PARA REMOVER TODOS OS BOTÕES
    const config = {
        displaylogo: false,
        responsive: true,
        staticPlot: false, // Mantém false para exibir, mas remove botões
        modeBarButtonsToRemove: [
            'zoom2d',
            'pan2d',
            'select2d',
            'lasso2d',
            'zoomIn2d',
            'zoomOut2d',
            'autoScale2d',
            'resetScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toImage',
            'sendDataToCloud',
            'toggleSpikelines',
            'resetViews',
            'toggleHover'
        ]
    };

    const pizzaEl = document.getElementById('chartPizza');
    if (pizzaEl && Object.keys(estados).length > 0) {
        const labels = Object.keys(estados);
        const values = Object.values(estados);

        const cores = {
            'Rascunho': '#f3e5be',
            'Submetido': '#d7e9f4',
            'Em Revisão': '#f2dcc8',
            'Alterações': '#ffcdd2',
            'Aprovado': '#c8e6c9',
            'Arquivado': '#e0e0e0'
        };

        const colors = labels.map(l => cores[l] || '#d2d9e3');

        Plotly.newPlot(pizzaEl, [{
            values: values,
            labels: labels.map(l => getEstadoDisplay(l)),
            type: 'pie',
            hole: 0.3,
            marker: { colors: colors },
            textinfo: 'label+percent',
            textposition: 'inside'
        }], {
            margin: { t: 0, b: 0, l: 0, r: 0 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { family: 'Inter, sans-serif' },
            showlegend: false,
            staticPlot: true,
            hovermode: false,
            dragmode: false
        }, config);
    }

    const barrasEl = document.getElementById('chartBarras');
    if (barrasEl && Object.keys(estados).length > 0) {
        const labels = Object.keys(estados);
        const values = Object.values(estados);

        Plotly.newPlot(barrasEl, [{
            x: labels.map(l => getEstadoDisplay(l)),
            y: values,
            type: 'bar',
            marker: {
                color: ['#f3e5be', '#d7e9f4', '#f2dcc8', '#ffcdd2', '#c8e6c9', '#e0e0e0']
            }
        }], {
            margin: { t: 0, b: 40, l: 40, r: 0 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { family: 'Inter, sans-serif' },
            xaxis: { gridcolor: 'rgba(0,0,0,0.05)', fixedrange: true },
            yaxis: { gridcolor: 'rgba(0,0,0,0.05)', fixedrange: true },
            showlegend: false,
            staticPlot: true,
            hovermode: false,
            dragmode: false
        }, config);
    }

    const topEl = document.getElementById('chartTop');
    if (topEl && topParceiros && topParceiros.length > 0) {
        const sorted = [...topParceiros].sort((a, b) => a.total - b.total);
        const labels = sorted.map(p => p.parceiro);
        const values = sorted.map(p => p.total);

        Plotly.newPlot(topEl, [{
            x: values,
            y: labels,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: values.map(v => {
                    const max = Math.max(...values);
                    const ratio = v / max;
                    return `rgb(${Math.round(0 + ratio * 54)}, ${Math.round(54 + ratio * 98)}, ${Math.round(98 + ratio * 98)})`;
                })
            }
        }], {
            margin: { t: 0, b: 20, l: 80, r: 20 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { family: 'Inter, sans-serif' },
            xaxis: { gridcolor: 'rgba(0,0,0,0.05)', title: 'Documents', fixedrange: true },
            yaxis: { gridcolor: 'rgba(0,0,0,0.05)', fixedrange: true },
            showlegend: false,
            staticPlot: true,
            hovermode: false,
            dragmode: false
        }, config);
    }
}

// =====================================================
// NOTIFICAÇÕES
// =====================================================

async function carregarNotificacoes() {
    const container = document.getElementById('appContent');
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/notificacoes?limit=100`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error loading notifications');

        const notificacoes = await response.json();

        const naoLidas = notificacoes.filter(n => !n.lida).length;
        state.notificacoesNaoLidas = naoLidas;
        renderTopbar();

        renderNotificacoes(notificacoes);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div style="background:rgba(255,0,0,0.1);border-radius:12px;padding:20px;color:#ff6b6b;">
                ❌ Error loading notifications: ${error.message}
            </div>
        `;
    }
}

function renderNotificacoes(notificacoes) {
    const container = document.getElementById('appContent');
    if (!container) return;

    const naoLidas = notificacoes.filter(n => !n.lida).length;

    let html = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
            <div>
                <span style="color:rgba(255,255,255,0.6);">${notificacoes.length} notifications</span>
                ${naoLidas > 0 ? `<span class="status-tag status-draft" style="margin-left:8px;">${naoLidas} unread</span>` : ''}
            </div>
            <div style="display:flex;gap:10px;">
                ${naoLidas > 0 ? `<button class="btn btn-primary btn-sm" onclick="marcarTodasLidas()">Mark all as read</button>` : ''}
                <button class="btn btn-secondary btn-sm" onclick="carregarNotificacoes()">🔄 Refresh</button>
            </div>
        </div>
    `;

    if (!notificacoes || notificacoes.length === 0) {
        html += `
            <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:40px;text-align:center;color:rgba(255,255,255,0.4);">
                <p style="font-size:18px;">🔔 No notifications</p>
                <p style="font-size:14px;">You're all caught up!</p>
            </div>
        `;
    } else {
        notificacoes.forEach(notif => {
            const isLida = notif.lida;
            html += `
                <div style="background:${isLida ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.06)'};border-radius:12px;padding:16px;margin-bottom:10px;border-left:3px solid ${isLida ? 'rgba(255,255,255,0.1)' : '#fec800'};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:24px;">${notif.icone || '📄'}</span>
                            <div>
                                <h4 style="color:#fff;margin:0;font-size:15px;">${notif.titulo}</h4>
                                <p style="color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:14px;">${notif.mensagem}</p>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                            <span style="color:rgba(255,255,255,0.3);font-size:12px;">${formatDate(notif.created_at)}</span>
                            ${!isLida ? `<button class="btn btn-primary btn-sm" onclick="marcarLida(${notif.id})">✓ Read</button>` : '<span style="color:rgba(255,255,255,0.3);font-size:12px;">✅ Read</span>'}
                            ${notif.link ? `<button class="btn btn-secondary btn-sm" onclick="irParaDocumento('${notif.link}')">📄 View</button>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
    }

    container.innerHTML = html;
}

async function marcarLida(notificacaoId) {
    try {
        const response = await fetch(`${API_URL}/notificacoes/${notificacaoId}/ler`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error marking as read');

        carregarNotificacoes();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error marking notification as read.', 'error');
    }
}

async function marcarTodasLidas() {
    try {
        const response = await fetch(`${API_URL}/notificacoes/ler-todas`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Error marking all as read');

        carregarNotificacoes();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error marking all as read.', 'error');
    }
}

function irParaDocumento(link) {
    const match = link.match(/doc_id=(\d+)/);
    if (match) {
        const docId = parseInt(match[1]);
        window.location.href = `documentos.html?docId=${docId}`;
    } else {
        window.location.href = 'documentos.html';
    }
}

// =====================================================
// DOCUMENTOS - CRIAR
// =====================================================

function abrirFormCriar() {
    if (state.perfil === 'parceiro') {
        showToast('Only companies can create documents.', 'warning');
        return;
    }

    if (state.perfil === 'admin') {
        showToast('Administrators cannot create documents. Only companies can create documents.', 'warning');
        return;
    }

    fetch(`${API_URL}/parceiros/disponiveis`, {
        headers: getAuthHeaders()
    })
    .then(response => {
        if (!response.ok) throw new Error('Error loading partners');
        return response.json();
    })
    .then(parceiros => {
        renderFormCriar(parceiros);
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error loading partners. Please try again.', 'error');
    });
}

function renderFormCriar(parceiros) {
    const container = document.getElementById('appContent');
    if (!container) return;

    let html = `
        <div style="background:rgba(255,255,255,0.05);border-radius:16px;padding:24px;margin:20px 0;">
            <h3 style="color:#fff;margin:0 0 16px;">📝 Create New Document</h3>
            <p style="color:rgba(255,255,255,0.6);margin-bottom:20px;">
                Company creating a document for a partner to fill in.
            </p>

            <div class="form-group">
                <label style="color:rgba(255,255,255,0.8);">Document Title *</label>
                <input type="text" id="novoTitulo" placeholder="Ex: LCA/LCC NEO-CYCLE" style="width:100%;padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;font-size:15px;" />
            </div>

            <div class="form-group">
                <label style="color:rgba(255,255,255,0.8);">Partner *</label>
                <select id="novoParceiro" style="width:100%;padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.15);color:#fff;font-size:15px;">
                    <option value="" style="background:#1a2a4a;color:rgba(255,255,255,0.6);">Select a partner...</option>
                    ${parceiros.map(p => `<option value="${p.username}" style="background:#1a2a4a;color:#fff;padding:8px;">${p.username} - ${p.nome_completo}</option>`).join('')}
                </select>
            </div>

            <div class="form-group">
                <label style="color:rgba(255,255,255,0.8);">Processes</label>
                <p style="color:rgba(255,255,255,0.4);font-size:13px;margin-bottom:8px;">Select the processes that will be available in this document</p>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px;">
                    ${PROCESSOS_PADRAO.map(proc => `
                        <label style="color:rgba(255,255,255,0.7);font-size:14px;display:flex;align-items:center;gap:8px;cursor:pointer;">
                            <input type="checkbox" value="${proc}" class="processo-check" style="width:16px;height:16px;cursor:pointer;" />
                            ${proc}
                        </label>
                    `).join('')}
                </div>
                <div style="margin-top:10px;display:flex;gap:10px;">
                    <input type="text" id="novoProcessoInput" placeholder="Add custom process..." style="flex:1;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;" />
                    <button class="btn btn-secondary btn-sm" onclick="adicionarProcessoCustom()">Add</button>
                </div>
                <div id="processosCustom" style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;"></div>
            </div>

            <div style="display:flex;gap:12px;margin-top:20px;flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="criarDocumento()">✅ Create Document</button>
                <button class="btn btn-secondary" onclick="fecharFormCriar()">❌ Cancel</button>
            </div>
        </div>
        <div id="documentosLista"></div>
    `;

    container.innerHTML = html;
}

function adicionarProcessoCustom() {
    const input = document.getElementById('novoProcessoInput');
    if (!input || !input.value.trim()) return;

    const nome = input.value.trim();
    const container = document.getElementById('processosCustom');
    if (!container) return;

    const existing = container.querySelector(`[data-processo="${nome}"]`);
    if (existing) {
        showToast('This process already exists.', 'warning');
        return;
    }

    const chip = document.createElement('span');
    chip.className = 'status-tag status-draft';
    chip.setAttribute('data-processo', nome);
    chip.innerHTML = `${nome} <span style="cursor:pointer;margin-left:4px;" onclick="removerProcessoCustom(this)">✕</span>`;
    container.appendChild(chip);
    input.value = '';
}

function removerProcessoCustom(el) {
    const container = document.getElementById('processosCustom');
    if (container) {
        container.removeChild(el.closest('[data-processo]') || el.parentElement);
    }
}

function getProcessosSelecionados() {
    const checks = document.querySelectorAll('.processo-check:checked');
    const processos = Array.from(checks).map(c => c.value);

    const custom = document.querySelectorAll('#processosCustom [data-processo]');
    custom.forEach(el => {
        processos.push(el.getAttribute('data-processo'));
    });

    return processos;
}

async function criarDocumento() {
    const titulo = document.getElementById('novoTitulo')?.value.trim();
    const parceiro = document.getElementById('novoParceiro')?.value;

    if (!titulo) {
        showToast('Please enter a document title.', 'warning');
        return;
    }

    if (!parceiro) {
        showToast('Please select a partner.', 'warning');
        return;
    }

    const processos = getProcessosSelecionados();
    
    if (processos.length === 0) {
        showToast('Please select at least one process.', 'warning');
        return;
    }

    const dados = criarEstruturaDocumento(processos);

    const payload = {
        titulo: titulo,
        parceiro_id: parceiro,
        empresa_id: state.username,
        dados: dados
    };

    console.log('📤 Enviando documento:', JSON.stringify(payload, null, 2));

    try {
        const response = await fetch(`${API_URL}/documentos/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        const responseText = await response.text();
        console.log('📥 Status:', response.status);
        console.log('📥 Resposta:', responseText);

        let responseData;
        try {
            responseData = JSON.parse(responseText);
        } catch (e) {
            console.error('❌ Erro ao fazer parse do JSON:', e);
            throw new Error(`Resposta do servidor: ${responseText.substring(0, 200)}`);
        }

        if (!response.ok) {
            let errorMessage = 'Erro desconhecido';
            if (responseData.detail) {
                if (typeof responseData.detail === 'string') {
                    errorMessage = responseData.detail;
                } else if (Array.isArray(responseData.detail)) {
                    errorMessage = responseData.detail.map(e => e.msg || e).join(', ');
                } else {
                    errorMessage = JSON.stringify(responseData.detail);
                }
            } else if (responseData.message) {
                errorMessage = responseData.message;
            } else if (responseData.error) {
                errorMessage = responseData.error;
            } else {
                errorMessage = JSON.stringify(responseData);
            }
            
            console.error('❌ Erro do backend:', errorMessage);
            throw new Error(errorMessage);
        }

        console.log('✅ Documento criado:', responseData);
        showToast(`✅ Document created successfully! ID: ${responseData.id}`, 'success');
        state.docSelecionado = null;
        state.editData = null;
        carregarDocumentos();
    } catch (error) {
        console.error('❌ Error creating document:', error);
        showToast('Error creating document: ' + error.message, 'error');
    }
}

function criarEstruturaDocumento(processos) {
    const estrutura = {
        lca: {
            inputs: {},
            processes: {},
            outputs: {}
        },
        lcc: {
            materials: {},
            equipment: {},
            labour: {},
            outputs: {}
        }
    };

    processos.forEach(p => {
        estrutura.lca.inputs[p] = [
            { material: "", qty: "", unit: "", description: "", cas: "", distance: "", country: "", datasource: "" }
        ];

        estrutura.lca.processes[p] = [
            { tipo: "Energy Consumption (kWh)", qty: "", unit: "kWh", description: "", comments: "", datasource: "" },
            { tipo: "Rate Power of the Equipment (W)", qty: "", unit: "W", description: "", comments: "", datasource: "" },
            { tipo: "Operating Time (h)", qty: "", unit: "h", description: "", comments: "", datasource: "" }
        ];

        estrutura.lca.outputs[p] = [
            { etapa: "", tipo: "", sub_tipo: "", qty: "", unit: "", description: "", comments: "", datasource: "" }
        ];

        estrutura.lcc.materials[p] = [
            { material: "", price: "", qty: "", unit: "€", description: "", comments: "", distance: "", country: "", datasource: "" }
        ];

        estrutura.lcc.equipment[p] = [
            { equipment: "", process: "", unit_cost: "", lifespan: "", maintenance: "", industrial_equiv: "", comments: "", datasource: "" }
        ];

        estrutura.lcc.labour[p] = [
            { process: "", total_number: "", total_cost: "", high_skilled: "", moderate_skilled: "", unskilled: "", high_rate: "", moderate_rate: "", unskilled_rate: "", comments: "", datasource: "" }
        ];

        estrutura.lcc.outputs[p] = [
            { material: "", market_price: "", quantity: "", unit: "€", amount_produced: "", comments: "", datasource: "" }
        ];
    });

    return estrutura;
}

function fecharFormCriar() {
    carregarDocumentos();
}

// =====================================================
// DOCUMENTOS - FILTROS
// =====================================================

function aplicarFiltros() {
    const busca = document.getElementById('filtroBusca')?.value || '';
    const estadoSelect = document.getElementById('filtroEstados');
    const estadoSelecionado = estadoSelect ? estadoSelect.value : '';
    const dataInicio = document.getElementById('filtroDataInicio')?.value || '';
    const dataFim = document.getElementById('filtroDataFim')?.value || '';

    const estados = estadoSelecionado ? [estadoSelecionado] : [];

    state.filtros = {
        q: busca,
        estados: estados,
        dataInicio: dataInicio || null,
        dataFim: dataFim || null
    };

    carregarDocumentos();
}

function limparFiltros() {
    state.filtros = {
        q: '',
        estados: [],
        dataInicio: null,
        dataFim: null
    };
    
    const buscaInput = document.getElementById('filtroBusca');
    const estadoSelect = document.getElementById('filtroEstados');
    const dataInicioInput = document.getElementById('filtroDataInicio');
    const dataFimInput = document.getElementById('filtroDataFim');
    
    if (buscaInput) buscaInput.value = '';
    if (estadoSelect) estadoSelect.value = '';
    if (dataInicioInput) dataInicioInput.value = '';
    if (dataFimInput) dataFimInput.value = '';
    
    carregarDocumentos();
}

// =====================================================
// INICIALIZAÇÃO - USAR AUTH DO WINDOW
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!window.AUTH || !window.AUTH.isAuthenticated) {
        console.log('🔒 Sem autenticação neste separador, redirecionar...');
        window.location.href = 'login.html';
        return;
    }

    state.token = window.AUTH.token;
    state.username = window.AUTH.username;
    state.perfil = window.AUTH.perfil;
    state.nome = window.AUTH.nome;

    console.log('✅ Inicializando com utilizador:', state.username, '(apenas neste separador)');

    adminMenuAtivo = 'documents';

    const params = new URLSearchParams(window.location.search);
    const docId = params.get('docId');
    if (docId) {
        state.docSelecionado = parseInt(docId);
    }

    carregarNotificacoesNaoLidas();
    renderTopbar();

    const currentPage = getCurrentPage();

    switch (currentPage) {
        case 'dashboard':
            carregarDashboard();
            break;
        case 'notificacoes':
            carregarNotificacoes();
            break;
        default:
            carregarDocumentos();
            break;
    }

    setInterval(carregarNotificacoesNaoLidas, 30000);
});
