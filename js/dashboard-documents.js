// =====================================================
// DASHBOARD DOCUMENTS - Holoss Style
// =====================================================

// =====================================================
// HELPERS - ESCAPE HTML
// =====================================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
// ESTADO GLOBAL
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
    imagemUrl: null,
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
// PARCEIROS SELECIONADOS (CHIPS)
// =====================================================

window.parceirosSelecionados = [];

function adicionarParceiroSelecionado() {
    const select = document.getElementById('novoParceiroSelect');
    if (!select) return;
    
    const selectedValue = select.value;
    if (!selectedValue) {
        showToast('Please select a partner first.', 'warning');
        return;
    }
    
    if (window.parceirosSelecionados.includes(selectedValue)) {
        showToast('This partner is already added.', 'warning');
        return;
    }
    
    window.parceirosSelecionados.push(selectedValue);
    select.value = '';
    atualizarParceirosSelecionados();
}

function removerParceiroSelecionado(username) {
    window.parceirosSelecionados = window.parceirosSelecionados.filter(p => p !== username);
    atualizarParceirosSelecionados();
}

function atualizarParceirosSelecionados() {
    const container = document.getElementById('parceirosSelecionadosContainer');
    if (!container) return;
    
    container.innerHTML = window.parceirosSelecionados.map(p => `
        <span class="status-tag status-submitted" style="padding:4px 12px;font-size:13px;display:inline-flex;align-items:center;gap:6px;">
            ${p}
            <span style="cursor:pointer;color:#ff6b6b;font-weight:bold;" onclick="removerParceiroSelecionado('${p}')">✕</span>
        </span>
    `).join('');
}

// =====================================================
// TOAST - MENSAGENS NO CENTRO DA PÁGINA
// =====================================================

function showToast(message, type = 'success') {
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

    state.toastTimer = setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            toast.remove();
            state.toastTimer = null;
        }, 300);
    }, 4000);
}

// =====================================================
// CONFIRMAÇÃO - MODAL COM ESTILO TOAST
// =====================================================

function showConfirm(message, onConfirm, onCancel = null) {
    const oldConfirm = document.getElementById('customConfirm');
    if (oldConfirm) {
        oldConfirm.remove();
    }

    const overlay = document.createElement('div');
    overlay.id = 'customConfirm';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.6);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(4px);
        animation: fadeIn 0.3s ease;
    `;

    const modal = document.createElement('div');
    modal.style.cssText = `
        background: #1a2a4a;
        color: white;
        padding: 32px 40px;
        border-radius: 16px;
        max-width: 500px;
        width: 90%;
        text-align: center;
        box-shadow: 0 24px 60px rgba(0,0,0,0.5);
        border: 1px solid rgba(254,200,0,0.2);
        animation: fadeIn 0.3s ease;
    `;

    modal.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
        <p style="font-size: 18px; font-weight: 500; margin: 0 0 24px 0; color: rgba(255,255,255,0.9); line-height: 1.5;">
            ${message}
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <button id="confirmYes" class="btn btn-success" style="min-width: 120px; padding: 12px 24px; font-size: 15px;">
                ✅ Yes
            </button>
            <button id="confirmNo" class="btn btn-secondary" style="min-width: 120px; padding: 12px 24px; font-size: 15px;">
                ❌ No
            </button>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to { opacity: 0; transform: scale(0.95); }
        }
    `;
    document.head.appendChild(style);

    document.getElementById('confirmYes').addEventListener('click', function() {
        closeConfirm();
        if (onConfirm) onConfirm();
    });

    document.getElementById('confirmNo').addEventListener('click', function() {
        closeConfirm();
        if (onCancel) onCancel();
    });

    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            closeConfirm();
            if (onCancel) onCancel();
        }
    });

    function closeConfirm() {
        const el = document.getElementById('customConfirm');
        if (el) {
            el.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                el.remove();
            }, 300);
        }
    }
}

// =====================================================
// ADMIN - MENU
// =====================================================

let adminMenuAtivo = 'documents';

// =====================================================
// LOGOUT
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
    showConfirm(`Are you sure you want to delete user '${username}'? This action cannot be undone.`, async function() {
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
    });
}

// =====================================================
// ADMIN - ELIMINAR DOCUMENTO
// =====================================================

async function eliminarDocumento(docId) {
    let titulo = 'document';
    try {
        const response = await fetch(`${API_URL}/documentos/${docId}`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const doc = await response.json();
            titulo = doc.titulo;
        }
    } catch (e) {
        // Ignorar erro
    }

    showConfirm(
        `Are you sure you want to permanently delete document "${titulo}" (ID: ${docId})? This action cannot be undone. All versions and notifications will also be deleted.`,
        async function() {
            try {
                const response = await fetch(`${API_URL}/admin/documentos/${docId}`, {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Error deleting document');
                }

                const result = await response.json();
                showToast(`✅ ${result.message || 'Document deleted successfully!'}`, 'success');
                
                state.docSelecionado = null;
                state.editData = null;
                carregarDocumentos();
            } catch (error) {
                console.error('Error:', error);
                showToast('Error deleting document: ' + error.message, 'error');
            }
        }
    );
}

// =====================================================
// HEADERS DE AUTENTICAÇÃO
// =====================================================

function getAuthHeaders() {
    // ✅ Verificar se o token existe
    if (!state.token) {
        console.warn('⚠️ Token não encontrado!');
        // Tentar recuperar do sessionStorage
        state.token = sessionStorage.getItem('doc_token');
        if (!state.token) {
            console.error('❌ Token não encontrado no sessionStorage');
            // Redirecionar para login
            window.location.href = 'login.html';
            return {};
        }
    }
    
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

// ✅ ADICIONAR AQUI A FUNÇÃO escapeHtml
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getEstadoDisplay(estado) {
    const estadoMap = {
        'Rascunho': 'Draft',
        'Submetido': 'Submitted',
        'Em Revisão': 'In Review',
        'Alterações': 'Changes Requested',
        'Aprovado': 'Approved',
        'Arquivado': 'Archived',
        'Draft': 'Rascunho',
        'Submitted': 'Submetido',
        'In Review': 'Em Revisão',
        'Changes Requested': 'Alterações',
        'Approved': 'Aprovado',
        'Archived': 'Arquivado'
    };
    
    if (estado && estado in estadoMap) {
        return estadoMap[estado];
    }
    return estado || 'Unknown';
}

function getEstadoClass(estado) {
    const estadoClassMap = {
        'Rascunho': 'status-draft',
        'Draft': 'status-draft',
        'Submetido': 'status-submitted',
        'Submitted': 'status-submitted',
        'Em Revisão': 'status-review',
        'In Review': 'status-review',
        'Alterações': 'status-changes',
        'Changes Requested': 'status-changes',
        'Aprovado': 'status-approved',
        'Approved': 'status-approved',
        'Arquivado': 'status-archived',
        'Archived': 'status-archived'
    };
    
    return estadoClassMap[estado] || 'status-draft';
}

function safeCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// =====================================================
// SINCRONIZAR INPUTS DO EDITOR
// =====================================================

function syncEditorInputs() {
    document.querySelectorAll('.editor-input:not([disabled])').forEach(input => {
        input.removeEventListener('input', handleInputChange);
        input.addEventListener('input', handleInputChange);
    });

    document.querySelectorAll('.editor-select').forEach(select => {
        select.removeEventListener('change', handleSelectChange);
        select.addEventListener('change', handleSelectChange);
    });
}

function handleInputChange(e) {
    const input = e.target;
    const section = input.getAttribute('data-section');
    const campo = input.getAttribute('data-campo');
    const proc = input.getAttribute('data-proc');
    const idx = parseInt(input.getAttribute('data-idx'));
    const key = input.getAttribute('data-key');
    const value = input.value;

    if (!state.editData) return;
    if (!state.editData[section]) return;
    if (!state.editData[section][campo]) return;
    if (!state.editData[section][campo][proc]) return;
    if (!state.editData[section][campo][proc][idx]) return;

    state.editData[section][campo][proc][idx][key] = value;
    
    console.log(`📝 Atualizado: ${section}.${campo}.${proc}[${idx}].${key} = "${value}"`);
}

function handleSelectChange(e) {
    const select = e.target;
    const section = select.getAttribute('data-section');
    const campo = select.getAttribute('data-campo');
    const proc = select.getAttribute('data-proc');
    const idx = parseInt(select.getAttribute('data-idx'));
    const key = select.getAttribute('data-key');
    const value = select.value;

    if (!state.editData) return;
    if (!state.editData[section]) return;
    if (!state.editData[section][campo]) return;
    if (!state.editData[section][campo][proc]) return;
    if (!state.editData[section][campo][proc][idx]) return;

    state.editData[section][campo][proc][idx][key] = value;
    
    console.log(`📝 Atualizado (select): ${section}.${campo}.${proc}[${idx}].${key} = "${value}"`);
}

function setupCheckboxListener() {
    const checkbox = document.getElementById('confirmSubmissionCheckbox');
    if (checkbox) {
        checkbox.addEventListener('click', function() {
            this.style.outline = 'none';
        });
    }
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

function aplicarFiltros() {
    const busca = document.getElementById('filtroBusca')?.value || '';
    const estadoSelect = document.getElementById('filtroEstados');
    const estadoSelecionado = estadoSelect ? estadoSelect.value : '';
    const dataInicio = document.getElementById('filtroDataInicio')?.value || '';
    const dataFim = document.getElementById('filtroDataFim')?.value || '';

    let estados = [];
    if (estadoSelecionado) {
        estados = [estadoSelecionado];
    }

    state.filtros = {
        q: busca,
        estados: estados,
        dataInicio: dataInicio || null,
        dataFim: dataFim || null
    };

    console.log('🔍 Filtros aplicados:', state.filtros);
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
    
    console.log('🧹 Filtros limpos');
    carregarDocumentos();
}

// =====================================================
// DOCUMENTOS - LISTAGEM
// =====================================================

async function carregarDocumentos() {
    try {
        const params = new URLSearchParams();
        if (state.filtros.q) params.append('q', state.filtros.q);
        if (state.filtros.estados && state.filtros.estados.length > 0) {
            params.append('estados', state.filtros.estados.join(','));
        }
        if (state.filtros.dataInicio) params.append('data_inicio', state.filtros.dataInicio);
        if (state.filtros.dataFim) params.append('data_fim', state.filtros.dataFim);

        params.append('order_by', 'id');
        params.append('order_dir', 'desc');

        const url = `${API_URL}/documentos/pesquisar?${params.toString()}`;
        console.log('📤 URL da requisição:', url);
        
        const response = await fetch(url, { headers: getAuthHeaders() });

        if (response.ok) {
            state.documentos = await response.json();
            console.log('📥 Documentos recebidos:', state.documentos.length);
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
    if (!container) {
        console.error('❌ container #appContent não encontrado!');
        return;
    }

    const isParceiro = state.perfil === 'parceiro';
    const isEmpresa = state.perfil === 'empresa';
    const isAdmin = state.perfil === 'admin';

    let html = '';

    // MENU ADMIN
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

    if (isAdmin && adminMenuAtivo === 'users') {
        html += `<div id="adminUsersContainer"></div>`;
        container.innerHTML = html;
        carregarUtilizadores();
        return;
    }

    // BARRA DE AÇÕES
    html += `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
                ${isEmpresa ? `<button class="btn btn-primary" onclick="abrirFormCriar()">➕ New Document</button>` : ''}
                <button class="btn btn-secondary" onclick="carregarDocumentos()">🔄 Refresh</button>
                <button class="btn-filter-toggle" onclick="toggleFiltros()">▶️ Filters</button>
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
                           value="${state.filtros.q || ''}" style="width:100%;">
                </div>
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;margin-bottom:4px;display:block;text-transform:uppercase;letter-spacing:0.5px;">Status</label>
                    <select id="filtroEstados" style="width:100%;">
                        <option value="">All Statuses</option>
                        <option value="Rascunho" ${state.filtros.estados && state.filtros.estados.includes('Rascunho') ? 'selected' : ''}>Draft</option>
                        <option value="Submetido" ${state.filtros.estados && state.filtros.estados.includes('Submetido') ? 'selected' : ''}>Submitted</option>
                        <option value="Em Revisão" ${state.filtros.estados && state.filtros.estados.includes('Em Revisão') ? 'selected' : ''}>In Review</option>
                        <option value="Alterações" ${state.filtros.estados && state.filtros.estados.includes('Alterações') ? 'selected' : ''}>Changes Requested</option>
                        <option value="Aprovado" ${state.filtros.estados && state.filtros.estados.includes('Aprovado') ? 'selected' : ''}>Approved</option>
                        <option value="Arquivado" ${state.filtros.estados && state.filtros.estados.includes('Arquivado') ? 'selected' : ''}>Archived</option>
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

    // LISTA DE DOCUMENTOS
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
            const parceirosDisplay = doc.parceiros_ids ? doc.parceiros_ids.join(', ') : (doc.parceiro_id || 'No partners');

            html += `
                <tr>
                    <td><strong>${doc.id}</strong></td>
                    <td>${doc.titulo}</td>
                    <td>${parceirosDisplay}</td>
                    <td><span class="status-tag ${estadoClass}">${estadoDisplay}</span></td>
                    <td>v${doc.versao_atual}</td>
                    <td>${formatDate(doc.updated_at)}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="abrirDocumento(${doc.id})">Open</button>
                        ${isAdmin ? `<button class="btn btn-danger btn-sm" onclick="eliminarDocumento(${doc.id})" style="margin-left:4px;">🗑️</button>` : ''}
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
        if (e.key === 'Enter') {
            e.preventDefault();
            aplicarFiltros();
        }
    });

    const filtrosExpandidos = sessionStorage.getItem('filtrosExpandidos') === 'true';
    if (filtrosExpandidos) {
        const containerFiltros = document.getElementById('filtrosContainer');
        const button = document.querySelector('.btn-filter-toggle');
        if (containerFiltros) {
            containerFiltros.style.maxHeight = '500px';
            containerFiltros.style.padding = '16px';
            containerFiltros.style.marginBottom = '20px';
            containerFiltros.style.borderColor = 'rgba(254, 200, 0, 0.2)';
        }
        if (button) {
            button.classList.add('active');
            button.innerHTML = '🔽 Filters';
        }
    }

    console.log('📋 Documentos renderizados:', state.documentos.length);
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

// =====================================================
// RENDER DOCUMENTO DETALHE
// =====================================================

function renderDocumentoDetalhe(doc) {
    const container = document.getElementById('documentoDetalhe');
    if (!container) return;

    const isParceiro = state.perfil === 'parceiro';
    const isEmpresa = state.perfil === 'empresa';
    const isAdmin = state.perfil === 'admin';

    const estadoDisplay = getEstadoDisplay(doc.estado);
    const estadoClass = getEstadoClass(doc.estado);

    const isPartnerAssigned = doc.parceiros_ids && doc.parceiros_ids.includes(state.username);

    const podeEditar = isParceiro && isPartnerAssigned && (doc.estado === 'Rascunho' || doc.estado === 'Alterações');
    const podeSubmeter = isParceiro && isPartnerAssigned && doc.estado === 'Rascunho';
    const podeRevisar = (isEmpresa || isAdmin) && doc.estado === 'Submetido';
    const podeAprovar = (isEmpresa || isAdmin) && doc.estado === 'Em Revisão';
    const podePedirAlteracoes = (isEmpresa || isAdmin) && doc.estado === 'Em Revisão';
    const podeReabrir = (isEmpresa || isAdmin) && doc.estado === 'Aprovado';
    const podeArquivar = (isEmpresa || isAdmin) && ['Rascunho', 'Aprovado'].includes(doc.estado);

    const processos = getProcessosFromData(doc.dados);

    const functionalUnit = doc.dados?.functional_unit || 'Not defined';
    const systemBoundary = doc.dados?.system_boundary || 'Not defined';
    const parceirosList = doc.parceiros_ids ? doc.parceiros_ids.join(', ') : (doc.parceiro_id || 'No partners');
    const imagemUrl = doc.imagem_url || null;

    // ✅ Verificar se está em modo de edição
    const isEditing = state.editData !== null;
    const shouldBeOpen = doc.estado === 'Em Revisão' || doc.estado === 'Submetido';

    // FUNÇÃO PARA GERAR BOTÕES DE AÇÃO
    function gerarBotoesAcao(docId, posicao) {
        if (isEditing) {
            return '';
        }

        const isTopo = posicao === 'topo';
        const isBaixo = posicao === 'baixo';
        const displayStyle = (isTopo) ? 'flex' : (shouldBeOpen ? 'flex' : 'none');

        let html = `
            <div class="actions-container" id="actionsContainer_${posicao}" style="display:${displayStyle};flex-wrap:wrap;gap:10px;margin:${isTopo ? '0 0 20px 0' : '20px 0 0 0'};padding:${isTopo ? '0 0 16px 0' : '16px 0 0 0'};border-bottom:${isTopo ? '1px solid rgba(255,255,255,0.06)' : 'none'};border-top:${isBaixo ? '1px solid rgba(255,255,255,0.06)' : 'none'};">
        `;

        if (podeEditar) {
            html += `<button class="btn btn-primary" onclick="abrirEdicaoDocumento(${docId})">✏️ Edit</button>`;
        }

        if (podeSubmeter) {
            html += `<button class="btn btn-success" onclick="submeterDocumento(${docId})">📤 Submit for Review</button>`;
        }

        if (podeRevisar) {
            html += `<button class="btn btn-warning" onclick="iniciarRevisao(${docId})">🔍 Start Review</button>`;
        }

        if (podeAprovar) {
            html += `<button class="btn btn-success" onclick="aprovarDocumento(${docId})">✅ Approve</button>`;
        }

        if (podePedirAlteracoes) {
            html += `
                <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                    <input type="text" id="comentarioAlteracoes_${posicao}" placeholder="Reason for changes..." style="flex:1;min-width:200px;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;" />
                    <button class="btn btn-danger" onclick="pedirAlteracoes(${docId})">🔄 Request Changes</button>
                </div>
            `;
        }

        if (podeReabrir) {
            html += `<button class="btn btn-warning" onclick="reabrirDocumento(${docId})">🔁 Reopen</button>`;
        }

        if (podeArquivar) {
            html += `<button class="btn btn-secondary" onclick="arquivarDocumento(${docId})">📁 Archive</button>`;
        }

        html += `
            <button class="btn btn-secondary" onclick="exportarExcel(${docId}, '${doc.titulo}')">📊 Export Excel</button>
            <button class="btn btn-secondary" onclick="fecharDocumento()">✖ Close</button>
        `;

        html += `
            </div>
        `;

        return html;
    }

    // ============================================================
    // HTML PRINCIPAL
    // ============================================================
    let html = `
        <div style="background:rgba(255,255,255,0.05);border-radius:16px;padding:24px;border-left:4px solid #fec800;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
                <div>
                    <h3 style="color:#fff;margin:0;">📄 ${doc.titulo}</h3>
                    <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">ID: ${doc.id} | Partners: ${parceirosList} | Version: v${doc.versao_atual}</p>
                </div>
                <span class="status-tag ${estadoClass}" style="font-size:16px;padding:6px 16px;">${estadoDisplay}</span>
            </div>

            <!-- SEMPRE VISÍVEL: Functional Unit, System Boundary, Created, Last Update -->
            <div class="document-info-grid">
                <div class="document-info-card">
                    <span class="info-label">Functional Unit</span>
                    <span class="info-value">${functionalUnit}</span>
                </div>
                <div class="document-info-card">
                    <span class="info-label">System Boundary</span>
                    <span class="info-value">${systemBoundary}</span>
                </div>
                <div class="document-info-card">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
                        <div>
                            <span class="info-label">Created</span>
                            <span class="info-value">${formatDate(doc.created_at)}</span>
                        </div>
                        <div>
                            <span class="info-label">Last Update</span>
                            <span class="info-value">${formatDate(doc.updated_at)}</span>
                        </div>
                    </div>
                </div>
            </div>
    `;

    // SEMPRE VISÍVEL: IMAGEM DO DOCUMENTO + COMENTÁRIOS DA IMAGEM
    if (imagemUrl && imagemUrl.startsWith('data:image')) {
        html += `
            <div class="document-image-container" style="margin-bottom:20px;padding:12px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">🖼️ Document Image</span>
                    <button class="btn-zoom" onclick="abrirModalImagem('${imagemUrl}')" style="padding:4px 12px;font-size:12px;border-radius:4px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);cursor:pointer;transition:all 0.2s ease;font-family:'Inter',sans-serif;">
                        🔍 Zoom
                    </button>
                </div>
                <img src="${imagemUrl}" alt="Document image" style="max-width:100%;max-height:200px;border-radius:6px;cursor:pointer;object-fit:contain;background:rgba(0,0,0,0.2);transition:transform 0.2s ease;" onclick="abrirModalImagem('${imagemUrl}')" />
            </div>
            <div style="margin-top: -12px; margin-bottom: 20px;">
                ${gerarCaixaComentariosTipo(doc.id, 'imagem', 'Image', '🖼️', 'imagem')}
            </div>
        `;
    }

    // ============================================================
    // BOTÕES DE AÇÃO - TOPO
    // ============================================================
    html += gerarBotoesAcao(doc.id, 'topo');

    // ============================================================
    // CONTEÚDO: OU VISUALIZAÇÃO OU EDITOR (NUNCA OS DOIS)
    // ============================================================
    if (isEditing) {
        // ✅ MODO EDIÇÃO: Apenas o editor (com comentários LCA/LCC dentro)
        html += `
            <div style="margin-top: 16px; clear: both;">
                ${renderEditorCompleto(doc.id, processos)}
            </div>
        `;
    } else {
        // ✅ MODO VISUALIZAÇÃO: Apenas o conteúdo (com comentários LCA/LCC dentro)
        html += `
            <div class="toggle-buttons-container">
                <button class="btn-toggle-content" onclick="toggleConteudoDocumento(${doc.id})" id="btnToggleConteudo">
                    ${shouldBeOpen ? '📊 Hide Document Content' : '📊 Show Document Content'}
                </button>
                <button class="btn-toggle-content" onclick="carregarHistorico(${doc.id})">
                    📜 Version History
                </button>
            </div>
            <div id="historicoVersoes" style="margin-top:0;margin-bottom:16px;"></div>
            <div id="conteudoDocumento" style="display:${shouldBeOpen ? 'block' : 'none'};margin-top:12px;">
                ${renderConteudoDocumento(doc.dados, processos, shouldBeOpen, doc.id)}
            </div>
        `;
    }

    // ============================================================
    // BOTÕES DE AÇÃO - BAIXO
    // ============================================================
    html += gerarBotoesAcao(doc.id, 'baixo');

    html += `
        </div>
    `;

    container.innerHTML = html;

    // ============================================================
    // CARREGAR CONTAGEM DE COMENTÁRIOS
    // ============================================================
    const tipos = ['lca', 'lcc', 'imagem'];
    tipos.forEach(tipo => {
        const badge = document.getElementById(`badgeTipo_${doc.id}_${tipo}`);
        if (badge) {
            fetch(`${API_URL}/documentos/${doc.id}/comentarios?tipo=${tipo}`, {
                headers: getAuthHeaders()
            })
            .then(response => response.json())
            .then(comentarios => {
                badge.textContent = comentarios.length;
                if (comentarios.length > 0) {
                    const key = `${doc.id}_${tipo}`;
                    if (!comentariosCarregadosTipo[key]) {
                        carregarComentariosTipo(doc.id, tipo);
                    }
                }
            })
            .catch(error => {
                console.error(`Error loading ${tipo} comment count:`, error);
            });
        }
    });

    // ============================================================
    // SINCRONIZAR INPUTS
    // ============================================================
    setTimeout(() => {
        syncEditorInputs();
        setupCheckboxListener();
    }, 100);

    if (shouldBeOpen && !isEditing) {
        setTimeout(() => {
            const conteudo = document.getElementById('conteudoDocumento');
            if (conteudo) {
                const details = conteudo.querySelectorAll('details');
                details.forEach(d => d.setAttribute('open', ''));
            }
        }, 100);
    }
}

// =====================================================
// CONTEÚDO DO DOCUMENTO (LCA/LCC)
// =====================================================

function renderConteudoDocumento(dados, processos, allOpen = false, docId = null) {
    if (!docId && state.docSelecionado) {
        docId = state.docSelecionado;
    }
    
    let html = '';

    // ============================================================
    // BOTÕES PARA ALTERNAR ENTRE LCA E LCC
    // ============================================================
    html += `
        <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;">
            <button class="btn btn-primary btn-sm" onclick="alternarSecaoDocumento('lca', ${docId})" id="btnSecaoLCA" style="background:linear-gradient(135deg, #2e7d32, #388e3c);">
                🌱 LCA - Life Cycle Assessment
            </button>
            <button class="btn btn-secondary btn-sm" onclick="alternarSecaoDocumento('lcc', ${docId})" id="btnSecaoLCC" style="background:rgba(255,255,255,0.08);">
                💰 LCC - Life Cycle Cost
            </button>
            <button class="btn btn-secondary btn-sm" onclick="alternarSecaoDocumento('ambas', ${docId})" id="btnSecaoAmbas" style="background:rgba(255,255,255,0.05);">
                📊 Show Both
            </button>
        </div>
        
        <div id="conteudoLCA" style="display:block;">
    `;

    // ============================================================
    // LCA SECTION
    // ============================================================
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

    // ✅ COMENTÁRIOS LCA - SEMPRE VISÍVEIS (dentro da secção LCA)
    if (docId) {
        html += `
            <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;" id="comentariosLCAWrapper_${docId}">
                ${gerarCaixaComentariosTipo(docId, 'lca', 'LCA', '🌱', 'lca')}
            </div>
        `;
    }

    html += `
        </div>
        
        <div id="conteudoLCC" style="display:none;">
    `;

    // ============================================================
    // LCC SECTION
    // ============================================================
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

    // ✅ COMENTÁRIOS LCC - SEMPRE VISÍVEIS (dentro da secção LCC)
    if (docId) {
        html += `
            <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;" id="comentariosLCCWrapper_${docId}">
                ${gerarCaixaComentariosTipo(docId, 'lcc', 'LCC', '💰', 'lcc')}
            </div>
        `;
    }

    html += `
        </div>
    `;

    return html;
}

// =====================================================
// ALTERNAR ENTRE SECÇÕES LCA / LCC
// =====================================================

let secaoAtiva = 'lca';

function alternarSecaoDocumento(secao, docId) {
    const lcaContainer = document.getElementById('conteudoLCA');
    const lccContainer = document.getElementById('conteudoLCC');
    const btnLCA = document.getElementById('btnSecaoLCA');
    const btnLCC = document.getElementById('btnSecaoLCC');
    const btnAmbas = document.getElementById('btnSecaoAmbas');

    if (!lcaContainer || !lccContainer) return;

    secaoAtiva = secao;

    // Resetar estilos dos botões
    if (btnLCA) btnLCA.style.background = 'rgba(255,255,255,0.08)';
    if (btnLCC) btnLCC.style.background = 'rgba(255,255,255,0.08)';
    if (btnAmbas) btnAmbas.style.background = 'rgba(255,255,255,0.05)';

    if (secao === 'lca') {
        lcaContainer.style.display = 'block';
        lccContainer.style.display = 'none';
        if (btnLCA) btnLCA.style.background = 'linear-gradient(135deg, #2e7d32, #388e3c)';
        
        // ✅ Carregar comentários LCA se necessário
        if (docId) {
            const key = `${docId}_lca`;
            if (!comentariosCarregadosTipo[key]) {
                carregarComentariosTipo(docId, 'lca');
            }
        }
    } else if (secao === 'lcc') {
        lcaContainer.style.display = 'none';
        lccContainer.style.display = 'block';
        if (btnLCC) btnLCC.style.background = 'linear-gradient(135deg, #0d47a1, #1565c0)';
        
        // ✅ Carregar comentários LCC se necessário
        if (docId) {
            const key = `${docId}_lcc`;
            if (!comentariosCarregadosTipo[key]) {
                carregarComentariosTipo(docId, 'lcc');
            }
        }
    } else { // 'ambas'
        lcaContainer.style.display = 'block';
        lccContainer.style.display = 'block';
        if (btnAmbas) btnAmbas.style.background = 'rgba(255,255,255,0.12)';
        if (btnLCA) btnLCA.style.background = 'linear-gradient(135deg, #2e7d32, #388e3c)';
        if (btnLCC) btnLCC.style.background = 'linear-gradient(135deg, #0d47a1, #1565c0)';
        
        // ✅ Carregar ambos os comentários se necessário
        if (docId) {
            const keyLCA = `${docId}_lca`;
            if (!comentariosCarregadosTipo[keyLCA]) {
                carregarComentariosTipo(docId, 'lca');
            }
            const keyLCC = `${docId}_lcc`;
            if (!comentariosCarregadosTipo[keyLCC]) {
                carregarComentariosTipo(docId, 'lcc');
            }
        }
    }

    const conteudoContainer = document.getElementById('conteudoDocumento');
    if (conteudoContainer) {
        setTimeout(() => {
            conteudoContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

function toggleConteudoDocumento(docId) {
    const container = document.getElementById('conteudoDocumento');
    const btn = document.getElementById('btnToggleConteudo');
    const actionsBaixo = document.getElementById('actionsContainer_baixo');
    
    if (!container) return;

    const isVisible = container.style.display !== 'none' && container.style.display !== '';
    
    if (isVisible) {
        // FECHAR
        container.style.display = 'none';
        if (btn) btn.innerHTML = '📊 Show Document Content';
        if (actionsBaixo) actionsBaixo.style.display = 'none';
    } else {
        // ABRIR
        container.style.display = 'block';
        if (btn) btn.innerHTML = '📊 Hide Document Content';
        if (actionsBaixo) actionsBaixo.style.display = 'flex';
        
        // ✅ Buscar o documento e renderizar o conteúdo com os comentários
        fetch(`${API_URL}/documentos/${docId}`, {
            headers: getAuthHeaders()
        })
        .then(response => response.json())
        .then(doc => {
            const processos = getProcessosFromData(doc.dados);
            // ✅ Passar o docId para renderConteudoDocumento
            container.innerHTML = renderConteudoDocumento(doc.dados, processos, true, docId);
            
            // Abrir todos os details
            const details = container.querySelectorAll('details');
            details.forEach(d => d.setAttribute('open', ''));
            
            // ✅ Carregar comentários LCA e LCC
            setTimeout(() => {
                // Carregar comentários LCA
                const keyLCA = `${docId}_lca`;
                if (!comentariosCarregadosTipo[keyLCA]) {
                    carregarComentariosTipo(docId, 'lca');
                }
                
                // Carregar comentários LCC
                const keyLCC = `${docId}_lcc`;
                if (!comentariosCarregadosTipo[keyLCC]) {
                    carregarComentariosTipo(docId, 'lcc');
                }
            }, 300);
        })
        .catch(error => {
            console.error('Error loading document content:', error);
            showToast('Error loading document content', 'error');
        });
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
    if (state.perfil !== 'parceiro') {
        showToast('Only partners can edit documents.', 'error');
        return;
    }

    console.log('📤 Opening editor for document:', docId);

    // ✅ Limpar qualquer estado anterior
    state.editData = null;
    state.imagemUrl = null;

    fetch(`${API_URL}/documentos/${docId}`, {
        headers: getAuthHeaders()
    })
    .then(response => {
        if (!response.ok) throw new Error('Error loading document');
        return response.json();
    })
    .then(doc => {
        console.log('📥 Document loaded:', doc);
        const processos = getProcessosFromData(doc.dados);
        state.editData = ensureEstruturaCompleta(doc.dados, processos);
        state.imagemUrl = doc.imagem_url || null;
        console.log('📊 state.editData initialized');
        console.log('🖼️ Image URL:', state.imagemUrl);
        
        // ✅ Recarregar o detalhe - agora isEditing = true, a visualização desaparece
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
// RENDER EDITOR SECAO
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

    const isReadOnlyField = (key) => {
        if (secao === 'lca' && campo === 'processes' && (key === 'tipo' || key === 'unit')) {
            return true;
        }
        if (secao === 'lcc' && campo === 'materials' && key === 'unit') {
            return true;
        }
        if (secao === 'lcc' && campo === 'outputs' && key === 'unit') {
            return true;
        }
        return false;
    };

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
                const keys = Object.keys(item);
                const grupos = [];
                for (let i = 0; i < keys.length; i += 3) {
                    grupos.push(keys.slice(i, i + 3));
                }

                html += `
                    <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:12px 14px;margin:6px 0 8px;border:1px solid rgba(255,255,255,0.05);" data-item-idx="${idx}">
                `;

                grupos.forEach(grupo => {
                    html += `
                        <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px 16px;margin-bottom:4px;">
                    `;
                    grupo.forEach(key => {
                        const value = item[key] || '';
                        const label = fieldLabels[key] || key.charAt(0).toUpperCase() + key.slice(1);
                        const isReadOnly = isReadOnlyField(key);

                        if (key === 'datasource') {
                            html += `
                                <div style="display:flex;flex-direction:column;gap:2px;">
                                    <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                                    <select data-section="${secao}" data-campo="${campo}" data-proc="${proc}" data-idx="${idx}" data-key="${key}" 
                                            class="editor-select"
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
                                               class="editor-input"
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
                                               class="editor-input"
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

function renderEditorCompleto(docId, processos) {
    const dados = state.editData;
    if (!dados) {
        return `<div style="color:rgba(255,255,255,0.5);padding:20px;text-align:center;">No data to edit</div>`;
    }

    let html = `
        <div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:20px;border:1px solid rgba(254,200,0,0.2);">
            <h4 style="color:#fec800;margin:0 0 16px;">✏️ Editing Document</h4>
            
            <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;">
                <button class="btn btn-primary btn-sm" onclick="alternarEditorSecao('lca')" id="btnEditorLCA" style="background:linear-gradient(135deg, #2e7d32, #388e3c);">
                    🌱 LCA - Life Cycle Assessment
                </button>
                <button class="btn btn-secondary btn-sm" onclick="alternarEditorSecao('lcc')" id="btnEditorLCC" style="background:rgba(255,255,255,0.08);">
                    💰 LCC - Life Cycle Cost
                </button>
                <button class="btn btn-secondary btn-sm" onclick="alternarEditorSecao('ambas')" id="btnEditorAmbas" style="background:rgba(255,255,255,0.05);">
                    📊 Show Both
                </button>
            </div>
            
            <div id="editorLCA" style="display:block;">
                <h5 style="color:#fff;">🌱 LCA</h5>
                ${renderEditorSecao('lca', 'inputs', docId, processos)}
                ${renderEditorSecao('lca', 'processes', docId, processos)}
                ${renderEditorSecao('lca', 'outputs', docId, processos)}
                
                <!-- ✅ COMENTÁRIOS LCA DENTRO DO EDITOR -->
                <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;">
                    ${gerarCaixaComentariosTipo(docId, 'lca', 'LCA', '🌱', 'lca')}
                </div>
            </div>
            
            <div id="editorLCC" style="display:none;">
                <h5 style="color:#fff;margin-top:20px;">💰 LCC</h5>
                ${renderEditorSecao('lcc', 'materials', docId, processos)}
                ${renderEditorSecao('lcc', 'equipment', docId, processos)}
                ${renderEditorSecao('lcc', 'labour', docId, processos)}
                ${renderEditorSecao('lcc', 'outputs', docId, processos)}
                
                <!-- ✅ COMENTÁRIOS LCC DENTRO DO EDITOR -->
                <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;">
                    ${gerarCaixaComentariosTipo(docId, 'lcc', 'LCC', '💰', 'lcc')}
                </div>
            </div>
    `;

    html += `
        <div style="margin-top:20px;padding:16px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(254,200,0,0.15);">
            <label style="display:flex;align-items:flex-start;gap:12px;cursor:pointer;color:rgba(255,255,255,0.85);font-size:14px;line-height:1.5;">
                <input type="checkbox" id="confirmSubmissionCheckbox" style="width:18px;height:18px;margin-top:2px;cursor:pointer;accent-color:#fec800;" />
                <span>
                    <strong>I confirm that all data provided is in accordance with the Functional Unit?</strong>
                    <br>
                    <span style="color:rgba(255,255,255,0.5);font-size:12px;">This confirmation is required to submit the document. You can save the document without confirming.</span>
                </span>
            </label>
        </div>
    `;

    html += `
        <div style="display:flex;gap:12px;margin-top:20px;flex-wrap:wrap;">
            <button class="btn btn-primary" onclick="salvarEdicao(${docId})">💾 Save Draft</button>
            <button class="btn btn-success" id="submitBtn_${docId}" onclick="submeterEdicao(${docId})">📤 Submit for Review</button>
            <button class="btn btn-secondary" onclick="cancelarEdicao()">✖ Cancel</button>
        </div>
    `;

    html += `</div>`;
    return html;
}

// =====================================================
// ALTERNAR ENTRE SECÇÕES LCA / LCC NO EDITOR
// =====================================================

let editorSecaoAtiva = 'lca';

function alternarEditorSecao(secao) {
    const lcaContainer = document.getElementById('editorLCA');
    const lccContainer = document.getElementById('editorLCC');
    const btnLCA = document.getElementById('btnEditorLCA');
    const btnLCC = document.getElementById('btnEditorLCC');
    const btnAmbas = document.getElementById('btnEditorAmbas');

    if (!lcaContainer || !lccContainer) return;

    editorSecaoAtiva = secao;

    btnLCA.style.background = 'rgba(255,255,255,0.08)';
    btnLCC.style.background = 'rgba(255,255,255,0.08)';
    btnAmbas.style.background = 'rgba(255,255,255,0.05)';

    if (secao === 'lca') {
        lcaContainer.style.display = 'block';
        lccContainer.style.display = 'none';
        btnLCA.style.background = 'linear-gradient(135deg, #2e7d32, #388e3c)';
    } else if (secao === 'lcc') {
        lcaContainer.style.display = 'none';
        lccContainer.style.display = 'block';
        btnLCC.style.background = 'linear-gradient(135deg, #0d47a1, #1565c0)';
    } else {
        lcaContainer.style.display = 'block';
        lccContainer.style.display = 'block';
        btnAmbas.style.background = 'rgba(255,255,255,0.12)';
        btnLCA.style.background = 'linear-gradient(135deg, #2e7d32, #388e3c)';
        btnLCC.style.background = 'linear-gradient(135deg, #0d47a1, #1565c0)';
    }

    const editorContainer = document.querySelector('.editor-container');
    if (editorContainer) {
        setTimeout(() => {
            editorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// =====================================================
// ADICIONAR ITEM
// =====================================================

function adicionarItemEditor(secao, campo, proc) {
    if (!state.editData) {
        showToast('No document data to add item.', 'error');
        return;
    }
    
    if (!state.editData[secao]) state.editData[secao] = {};
    if (!state.editData[secao][campo]) state.editData[secao][campo] = {};
    if (!state.editData[secao][campo][proc]) state.editData[secao][campo][proc] = [];

    const currentItems = state.editData[secao][campo][proc];
    let newItem = {};
    
    if (currentItems.length > 0) {
        const firstItem = currentItems[0];
        Object.keys(firstItem).forEach(key => {
            newItem[key] = '';
        });
    } else {
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

    const newIdx = currentItems.length;
    currentItems.push(newItem);

    const containerId = `${secao}_${campo}_${proc}_container`;
    const container = document.getElementById(containerId);
    
    if (container) {
        const keys = Object.keys(newItem);
        const grupos = [];
        for (let i = 0; i < keys.length; i += 3) {
            grupos.push(keys.slice(i, i + 3));
        }

        let itemHtml = `
            <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:12px 14px;margin:6px 0 8px;border:1px solid rgba(255,255,255,0.05);" data-item-idx="${newIdx}">
        `;

        grupos.forEach(grupo => {
            itemHtml += `
                <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px 16px;margin-bottom:4px;">
            `;
            grupo.forEach(key => {
                const label = key.charAt(0).toUpperCase() + key.slice(1);
                const isReadOnly = (secao === 'lca' && campo === 'processes' && (key === 'tipo' || key === 'unit')) ||
                                  (secao === 'lcc' && campo === 'materials' && key === 'unit') ||
                                  (secao === 'lcc' && campo === 'outputs' && key === 'unit');

                if (key === 'datasource') {
                    itemHtml += `
                        <div style="display:flex;flex-direction:column;gap:2px;">
                            <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                            <select data-section="${secao}" data-campo="${campo}" data-proc="${proc}" data-idx="${newIdx}" data-key="${key}" 
                                    class="editor-select"
                                    style="width:100%;max-width:180px;background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.15);border-radius:5px;padding:6px 10px;font-size:13px;font-family:'Inter',sans-serif;">
                                ${DATASOURCE_OPTIONS.map(opt => `<option value="${opt}" style="background:#1a2a4a;color:#fff;">${opt}</option>`).join('')}
                            </select>
                        </div>
                    `;
                } else {
                    itemHtml += `
                        <div style="display:flex;flex-direction:column;gap:2px;">
                            <span style="color:rgba(255,255,255,0.5);font-size:11px;font-weight:500;letter-spacing:0.3px;text-transform:uppercase;">${label}</span>
                            <input type="text" value="" 
                                   data-section="${secao}" data-campo="${campo}" data-proc="${proc}" data-idx="${newIdx}" data-key="${key}"
                                   placeholder="${label}"
                                   class="editor-input"
                                   ${isReadOnly ? 'disabled style="width:100%;max-width:180px;background:rgba(255,255,255,0.07);color:#fff;border:1px solid rgba(255,255,255,0.12);border-radius:5px;padding:6px 10px;font-size:13px;font-family:\'Inter\',sans-serif;opacity:0.8;cursor:not-allowed;"' : 'style="width:100%;max-width:180px;background:rgba(255,255,255,0.07);color:#fff;border:1px solid rgba(255,255,255,0.12);border-radius:5px;padding:6px 10px;font-size:13px;font-family:\'Inter\',sans-serif;"'} />
                        </div>
                    `;
                }
            });
            itemHtml += `
                </div>
            `;
        });

        itemHtml += `
                <div style="display:flex;justify-content:flex-end;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.05);">
                    <button class="btn btn-danger btn-sm" onclick="removerItemEditor('${secao}','${campo}','${proc}',${newIdx})" style="padding:3px 10px;font-size:11px;border-radius:4px;">✕ Remove</button>
                </div>
            </div>
        `;

        const addButton = container.parentElement.querySelector('.btn-secondary');
        if (addButton) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = itemHtml;
            const newItemElement = tempDiv.firstElementChild;
            if (newItemElement) {
                addButton.parentElement.insertBefore(newItemElement, addButton);
            }
        }

        const countSpan = container.parentElement.querySelector('span[style*="color:rgba(255,255,255,0.35)"]');
        if (countSpan) {
            const match = countSpan.textContent.match(/\d+/);
            if (match) {
                const currentCount = parseInt(match[0]);
                countSpan.textContent = `${currentCount + 1} items`;
            }
        }

        setTimeout(() => {
            syncEditorInputs();
        }, 100);

        showToast('✅ New item added!', 'success');
    } else {
        const docId = state.docSelecionado;
        if (docId) {
            carregarDocumentoDetalhe(docId);
        }
    }
}

function removerItemEditor(secao, campo, proc, idx) {
    if (!state.editData) return;
    if (!state.editData[secao]?.[campo]?.[proc]) return;

    state.editData[secao][campo][proc].splice(idx, 1);

    const container = document.getElementById(`${secao}_${campo}_${proc}_container`);
    if (container) {
        const items = container.querySelectorAll('[data-item-idx]');
        let itemToRemove = null;
        
        for (const item of items) {
            const itemIdx = parseInt(item.getAttribute('data-item-idx'));
            if (itemIdx === idx) {
                itemToRemove = item;
                break;
            }
        }
        
        if (itemToRemove) {
            itemToRemove.remove();
            
            const remainingItems = container.querySelectorAll('[data-item-idx]');
            remainingItems.forEach((item, newIdx) => {
                item.setAttribute('data-item-idx', newIdx);
            });
            
            const countSpan = container.parentElement.querySelector('span[style*="color:rgba(255,255,255,0.35)"]');
            if (countSpan) {
                const match = countSpan.textContent.match(/\d+/);
                if (match) {
                    const currentCount = parseInt(match[0]);
                    const newCount = Math.max(0, currentCount - 1);
                    countSpan.textContent = `${newCount} items`;
                }
            }

            const allInputs = container.querySelectorAll('input[data-idx], select[data-idx]');
            allInputs.forEach(input => {
                const oldIdx = parseInt(input.getAttribute('data-idx'));
                if (oldIdx > idx) {
                    input.setAttribute('data-idx', oldIdx - 1);
                }
            });
            
            const removeButtons = container.parentElement.querySelectorAll('.btn-danger');
            removeButtons.forEach((btn) => {
                const onclickAttr = btn.getAttribute('onclick');
                if (onclickAttr) {
                    const match = onclickAttr.match(/removerItemEditor\('([^']+)','([^']+)','([^']+)',(\d+)\)/);
                    if (match) {
                        const oldIdx = parseInt(match[4]);
                        if (oldIdx > idx) {
                            const newOnclick = `removerItemEditor('${match[1]}','${match[2]}','${match[3]}',${oldIdx - 1})`;
                            btn.setAttribute('onclick', newOnclick);
                        }
                    }
                }
            });
            
            showToast('✅ Item removed!', 'success');
        } else {
            const docId = state.docSelecionado;
            if (docId) {
                carregarDocumentoDetalhe(docId);
            }
        }
    } else {
        const docId = state.docSelecionado;
        if (docId) {
            carregarDocumentoDetalhe(docId);
        }
    }
}

// =====================================================
// SALVAR E SUBMETER EDIÇÃO
// =====================================================

function salvarEdicao(docId) {
    if (state.perfil !== 'parceiro') {
        showToast('Only partners can edit documents.', 'error');
        return;
    }

    const dados = state.editData;
    if (!dados) {
        showToast('No data to save.', 'warning');
        return;
    }

    console.log('📤 Saving partner data:', JSON.stringify(dados, null, 2));

    fetch(`${API_URL}/documentos/${docId}/editar`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ dados: dados })
    })
    .then(response => {
        console.log('📥 Save response - Status:', response.status);
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Error saving'); });
        }
        return response.json();
    })
    .then((doc) => {
        console.log('✅ Document saved successfully!');
        showToast('✅ Document saved successfully!', 'success');
        state.editData = null;
        state.imagemUrl = null;
        carregarDocumentoDetalhe(docId);
        carregarDocumentos();
    })
    .catch(error => {
        console.error('❌ Error saving:', error);
        showToast('Error saving: ' + error.message, 'error');
    });
}

function submeterEdicao(docId) {
    if (state.perfil !== 'parceiro') {
        showToast('Only partners can submit documents.', 'error');
        return;
    }

    const checkbox = document.getElementById('confirmSubmissionCheckbox');
    if (!checkbox || !checkbox.checked) {
        showToast('⚠️ Please confirm that all data is in accordance with the Functional Unit before submitting.', 'warning');
        if (checkbox) {
            checkbox.style.outline = '2px solid #ff6b6b';
            checkbox.style.outlineOffset = '2px';
            setTimeout(() => {
                checkbox.style.outline = 'none';
            }, 3000);
        }
        return;
    }

    const dados = state.editData;
    if (!dados) {
        showToast('No data to submit.', 'warning');
        return;
    }

    console.log('📤 Submitting partner data:', JSON.stringify(dados, null, 2));

    showConfirm('Submit this document for review?', function() {
        fetch(`${API_URL}/documentos/${docId}/editar`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({ dados: dados })
        })
        .then(response => {
            console.log('📥 Save response - Status:', response.status);
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.detail || 'Error saving'); });
            }
            return response.json();
        })
        .then((savedDoc) => {
            console.log('✅ Document saved before submitting:', savedDoc);
            return fetch(`${API_URL}/documentos/${docId}/submeter`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
        })
        .then(response => {
            console.log('📥 Submit response - Status:', response.status);
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.detail || 'Error submitting'); });
            }
            return response.json();
        })
        .then((submittedDoc) => {
            console.log('✅ Document submitted successfully!');
            showToast('✅ Document submitted successfully!', 'success');
            state.editData = null;
            state.imagemUrl = null;
            state.docSelecionado = null;
            carregarDocumentos();
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showToast('Error: ' + error.message, 'error');
        });
    });
}

function cancelarEdicao() {
    // ✅ Limpar estado de edição
    state.editData = null;
    state.imagemUrl = null;
    
    // ✅ Recarregar o documento para mostrar a visualização
    if (state.docSelecionado) {
        carregarDocumentoDetalhe(state.docSelecionado);
    }
}

// =====================================================
// AÇÕES DOS DOCUMENTOS
// =====================================================

async function submeterDocumento(docId) {
    showConfirm('Are you sure you want to submit this document for review?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/submeter`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) throw new Error('Error submitting');

            showToast('✅ Document submitted successfully!', 'success');
            state.docSelecionado = null;
            state.editData = null;
            carregarDocumentos();
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function iniciarRevisao(docId) {
    showConfirm('Start review for this document?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/iniciar-revisao`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) throw new Error('Error starting review');

            showToast('✅ Review started!', 'success');
            
            await carregarDocumentoDetalhe(docId);
            carregarDocumentos();
            
            setTimeout(() => {
                const container = document.getElementById('conteudoDocumento');
                if (container) {
                    container.style.display = 'block';
                    const details = container.querySelectorAll('details');
                    details.forEach(d => d.setAttribute('open', ''));
                }
            }, 500);
            
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function aprovarDocumento(docId) {
    showConfirm('Approve this document?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/aprovar`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) throw new Error('Error approving');

            showToast('✅ Document approved!', 'success');
            state.docSelecionado = null;
            state.editData = null;
            carregarDocumentos();
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function pedirAlteracoes(docId) {
    const comentario = document.getElementById('comentarioAlteracoes_topo')?.value?.trim() || 
                       document.getElementById('comentarioAlteracoes_baixo')?.value?.trim();
    
    if (!comentario) {
        showToast('Please enter a reason for the changes.', 'warning');
        return;
    }

    showConfirm('Request changes for this document?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/pedir-alteracoes`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ comentario: comentario })
            });

            if (!response.ok) throw new Error('Error requesting changes');

            showToast('✅ Changes requested!', 'success');
            state.docSelecionado = null;
            state.editData = null;
            carregarDocumentos();
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function reabrirDocumento(docId) {
    showConfirm('Reopen this document?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/reabrir`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) throw new Error('Error reopening');

            showToast('✅ Document reopened!', 'success');
            state.docSelecionado = null;
            state.editData = null;
            carregarDocumentos();
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function arquivarDocumento(docId) {
    showConfirm('Archive this document?', async function() {
        try {
            const response = await fetch(`${API_URL}/documentos/${docId}/arquivar`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) throw new Error('Error archiving');

            showToast('✅ Document archived!', 'success');
            state.docSelecionado = null;
            state.editData = null;
            carregarDocumentos();
        } catch (error) {
            console.error('Error:', error);
            showToast('Error: ' + error.message, 'error');
        }
    });
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

    if (topParceiros && topParceiros.length > 0) {
        html += `
            <div style="background:#f7f7f8;border-radius:16px;padding:16px;margin-bottom:24px;">
                <h4 style="color:#17345a;margin:0 0 12px;">🏆 Top Partners</h4>
                <div id="chartTop" style="height:250px;"></div>
            </div>
        `;
    }

    container.innerHTML = html;
    renderGraficos(estados, topParceiros);
}

function renderGraficos(estados, topParceiros) {
    const config = {
        displaylogo: false,
        responsive: true,
        staticPlot: false,
        modeBarButtonsToRemove: [
            'zoom2d', 'pan2d', 'select2d', 'lasso2d',
            'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
            'hoverClosestCartesian', 'hoverCompareCartesian',
            'toImage', 'sendDataToCloud', 'toggleSpikelines',
            'resetViews', 'toggleHover'
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

    window.parceirosSelecionados = [];

    let html = `
        <div style="background:rgba(255,255,255,0.05);border-radius:16px;padding:24px;margin:20px 0;max-width:100%;overflow:hidden;">
            <h3 style="color:#fff;margin:0 0 16px;">📝 Create New Document</h3>
            <p style="color:rgba(255,255,255,0.6);margin-bottom:20px;">
                Company creating a document for partners to fill in.
            </p>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">Document Title *</label>
                    <input type="text" id="novoTitulo" placeholder="Ex: LCA/LCC NEO-CYCLE" style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;font-size:14px;box-sizing:border-box;" />
                </div>

                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">Functional Unit *</label>
                    <input type="text" id="novoFunctionalUnit" placeholder="Ex: 1 kg of product..." style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;font-size:14px;box-sizing:border-box;" />
                </div>

                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">System Boundary *</label>
                    <input type="text" id="novoSystemBoundary" placeholder="Ex: Cradle-to-gate..." style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;font-size:14px;box-sizing:border-box;" />
                </div>

                <div class="form-group" style="margin:0;">
                    <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">Partners *</label>
                    <select id="novoParceiroSelect" style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.15);color:#fff;font-size:14px;box-sizing:border-box;">
                        <option value="" style="background:#1a2a4a;color:rgba(255,255,255,0.6);">Select a partner...</option>
                        ${parceiros.map(p => `<option value="${p.username}" style="background:#1a2a4a;color:#fff;padding:8px;">${p.username} - ${p.nome_completo}</option>`).join('')}
                    </select>
                    <button class="btn btn-secondary btn-sm" onclick="adicionarParceiroSelecionado()" style="margin-top:4px;width:100%;">➕ Add Partner</button>
                    <div id="parceirosSelecionadosContainer" style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;">
                        ${window.parceirosSelecionados.map(p => `
                            <span class="status-tag status-submitted" style="padding:4px 12px;font-size:13px;display:inline-flex;align-items:center;gap:6px;">
                                ${p}
                                <span style="cursor:pointer;color:#ff6b6b;font-weight:bold;" onclick="removerParceiroSelecionado('${p}')">✕</span>
                            </span>
                        `).join('')}
                    </div>
                    <p style="color:rgba(255,255,255,0.4);font-size:11px;margin-top:4px;">Select partners and click "Add Partner" to add them</p>
                </div>
            </div>

            <!-- Upload de Imagem -->
            <div class="form-group" style="margin-top:16px;">
                <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">Document Image (optional)</label>
                <p style="color:rgba(255,255,255,0.4);font-size:12px;margin-bottom:8px;">Upload an image to be displayed with the document (JPG, PNG, GIF, max 5MB)</p>
                <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
                    <input type="file" id="imagemUpload" accept="image/*" style="color:rgba(255,255,255,0.8);padding:8px;background:rgba(255,255,255,0.05);border-radius:6px;border:1px solid rgba(255,255,255,0.1);flex:1;min-width:200px;" />
                    <button class="btn btn-secondary btn-sm" onclick="uploadImagem()" style="white-space:nowrap;">📤 Upload</button>
                </div>
                <div id="previewImagemContainer" style="margin-top:10px;display:none;">
                    <img id="previewImagem" src="" alt="Preview" style="max-width:200px;max-height:150px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);" />
                    <br>
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;">Image uploaded successfully! Click "Upload" to change.</span>
                </div>
                <input type="hidden" id="imagemUrl" value="" />
            </div>

            <div class="form-group" style="margin-top:16px;">
                <label style="color:rgba(255,255,255,0.8);display:block;margin-bottom:4px;font-size:13px;">Processes</label>
                <p style="color:rgba(255,255,255,0.4);font-size:12px;margin-bottom:8px;">Select the processes that will be available in this document</p>
                <div class="processo-check-container" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:6px;">
                    ${PROCESSOS_PADRAO.map(proc => `
                        <label style="color:rgba(255,255,255,0.7);font-size:13px;display:flex;align-items:center;gap:8px;cursor:pointer;">
                            <input type="checkbox" value="${proc}" class="processo-check" style="width:15px;height:15px;cursor:pointer;" />
                            ${proc}
                        </label>
                    `).join('')}
                </div>
                <div style="margin-top:8px;display:flex;gap:8px;">
                    <input type="text" id="novoProcessoInput" placeholder="Add custom process..." style="flex:1;padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#fff;font-size:13px;box-sizing:border-box;" />
                    <button class="btn btn-secondary btn-sm" onclick="adicionarProcessoCustom()" style="white-space:nowrap;">Add</button>
                </div>
                <div id="processosCustom" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;"></div>
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

// =====================================================
// UPLOAD DE IMAGEM
// =====================================================

let imagemBase64 = null;

function uploadImagem() {
    const fileInput = document.getElementById('imagemUpload');
    const previewContainer = document.getElementById('previewImagemContainer');
    const previewImg = document.getElementById('previewImagem');
    const hiddenInput = document.getElementById('imagemUrl');
    
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
        showToast('Please select an image first.', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    
    if (file.size > 5 * 1024 * 1024) {
        showToast('Image must be less than 5MB.', 'error');
        return;
    }
    
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
    if (!validTypes.includes(file.type)) {
        showToast('Please select a valid image (JPG, PNG, GIF, WEBP, SVG).', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        imagemBase64 = e.target.result;
        previewImg.src = imagemBase64;
        previewContainer.style.display = 'block';
        hiddenInput.value = imagemBase64;
        showToast('✅ Image uploaded successfully!', 'success');
    };
    reader.onerror = function() {
        showToast('Error reading image file.', 'error');
    };
    reader.readAsDataURL(file);
}

function limparImagem() {
    imagemBase64 = null;
    document.getElementById('previewImagemContainer').style.display = 'none';
    document.getElementById('imagemUrl').value = '';
    document.getElementById('imagemUpload').value = '';
}

// =====================================================
// CRIAR DOCUMENTO
// =====================================================

async function criarDocumento() {
    const titulo = document.getElementById('novoTitulo')?.value.trim();
    const functionalUnit = document.getElementById('novoFunctionalUnit')?.value.trim();
    const systemBoundary = document.getElementById('novoSystemBoundary')?.value.trim();
    const parceirosIds = window.parceirosSelecionados || [];
    const imagemUrl = document.getElementById('imagemUrl')?.value || null;

    if (!titulo) {
        showToast('Please enter a document title.', 'warning');
        return;
    }

    if (!functionalUnit) {
        showToast('Please enter the Functional Unit.', 'warning');
        return;
    }

    if (!systemBoundary) {
        showToast('Please enter the System Boundary.', 'warning');
        return;
    }

    if (!parceirosIds || parceirosIds.length === 0) {
        showToast('Please select at least one partner.', 'warning');
        return;
    }

    const processos = getProcessosSelecionados();
    
    if (processos.length === 0) {
        showToast('Please select at least one process.', 'warning');
        return;
    }

    const dados = criarEstruturaDocumento(processos);
    dados.functional_unit = functionalUnit;
    dados.system_boundary = systemBoundary;

    const payload = {
        titulo: titulo,
        parceiros_ids: parceirosIds,
        empresa_id: state.username,
        dados: dados,
        imagem_url: imagemUrl
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
        
        window.parceirosSelecionados = [];
        
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
    console.log('📦 Criando estrutura para processos:', processos);
    
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
        console.log('📝 A criar estrutura para processo:', p);
        
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
    window.parceirosSelecionados = [];
    carregarDocumentos();
}

function adicionarProcessoCustom() {
    const input = document.getElementById('novoProcessoInput');
    if (!input || !input.value.trim()) return;

    const nome = input.value.trim();
    const container = document.getElementById('processosCustom');
    if (!container) return;

    const existingCheck = document.querySelector(`.processo-check[value="${nome}"]`);
    if (existingCheck) {
        showToast('This process already exists in the list.', 'warning');
        return;
    }

    const existing = container.querySelector(`[data-processo="${nome}"]`);
    if (existing) {
        showToast('This process already exists.', 'warning');
        return;
    }

    const chip = document.createElement('span');
    chip.className = 'status-tag status-draft';
    chip.setAttribute('data-processo', nome);
    chip.innerHTML = `${nome} <span style="cursor:pointer;margin-left:4px;color:#ff6b6b;" onclick="removerProcessoCustom(this)">✕</span>`;
    container.appendChild(chip);
    input.value = '';
    
    const checkboxContainer = document.querySelector('.processo-check-container');
    if (checkboxContainer) {
        const label = document.createElement('label');
        label.style.cssText = 'color:rgba(255,255,255,0.7);font-size:14px;display:flex;align-items:center;gap:8px;cursor:pointer;';
        label.innerHTML = `
            <input type="checkbox" value="${nome}" checked class="processo-check" style="width:16px;height:16px;cursor:pointer;" />
            ${nome}
        `;
        checkboxContainer.appendChild(label);
    }
    
    showToast(`✅ Process '${nome}' added!`, 'success');
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
        const nome = el.getAttribute('data-processo');
        if (nome && !processos.includes(nome)) {
            processos.push(nome);
        }
    });

    console.log('📋 Processos selecionados:', processos);
    return processos;
}

// =====================================================
// MODAL DE ZOOM DA IMAGEM
// =====================================================

function abrirModalImagem(imagemUrl) {
    const oldModal = document.getElementById('modalImagem');
    if (oldModal) {
        oldModal.remove();
        document.body.style.overflow = '';
    }

    const modal = document.createElement('div');
    modal.id = 'modalImagem';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.85);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(4px);
        animation: fadeIn 0.3s ease;
        padding: 20px;
        box-sizing: border-box;
    `;

    const imgContainer = document.createElement('div');
    imgContainer.style.cssText = `
        max-width: 90vw;
        max-height: 90vh;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    `;

    const img = document.createElement('img');
    img.src = imagemUrl;
    img.style.cssText = `
        max-width: 90vw;
        max-height: 85vh;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.6);
        cursor: default;
        background: rgba(0,0,0,0.3);
        user-select: none;
        -webkit-user-select: none;
    `;

    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕ Close';
    closeBtn.style.cssText = `
        position: fixed;
        top: 24px;
        right: 30px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: #fff;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        z-index: 1000000;
        letter-spacing: 0.3px;
    `;
    
    closeBtn.onmouseover = function() {
        this.style.background = 'rgba(255,255,255,0.25)';
        this.style.borderColor = 'rgba(255,255,255,0.4)';
        this.style.transform = 'scale(1.05)';
    };
    closeBtn.onmouseout = function() {
        this.style.background = 'rgba(255,255,255,0.12)';
        this.style.borderColor = 'rgba(255,255,255,0.2)';
        this.style.transform = 'scale(1)';
    };

    const closeBtnAlt = document.createElement('button');
    closeBtnAlt.textContent = '✕';
    closeBtnAlt.style.cssText = `
        position: fixed;
        top: 20px;
        left: 24px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: #fff;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        font-size: 20px;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        z-index: 1000000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    closeBtnAlt.onmouseover = function() {
        this.style.background = 'rgba(255,255,255,0.2)';
        this.style.borderColor = 'rgba(255,255,255,0.3)';
        this.style.transform = 'scale(1.1)';
    };
    closeBtnAlt.onmouseout = function() {
        this.style.background = 'rgba(255,255,255,0.08)';
        this.style.borderColor = 'rgba(255,255,255,0.15)';
        this.style.transform = 'scale(1)';
    };

    function fecharModal() {
        const modalEl = document.getElementById('modalImagem');
        if (modalEl) {
            modalEl.style.animation = 'fadeOut 0.2s ease';
            setTimeout(() => {
                modalEl.remove();
                document.body.style.overflow = '';
                document.removeEventListener('keydown', keyHandler);
            }, 200);
        }
    }

    function keyHandler(e) {
        if (e.key === 'Escape') {
            fecharModal();
        }
    }

    closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        fecharModal();
    });

    closeBtnAlt.addEventListener('click', function(e) {
        e.stopPropagation();
        fecharModal();
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            fecharModal();
        }
    });

    document.addEventListener('keydown', keyHandler);

    imgContainer.appendChild(img);
    modal.appendChild(imgContainer);
    modal.appendChild(closeBtn);
    modal.appendChild(closeBtnAlt);
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

function fecharModalImagem() {
    const modal = document.getElementById('modalImagem');
    if (modal) {
        modal.style.animation = 'fadeOut 0.2s ease';
        setTimeout(() => {
            modal.remove();
            document.body.style.overflow = '';
            document.removeEventListener('keydown', keyHandler);
        }, 200);
    }
}

// =====================================================
// COMENTÁRIOS POR TIPO (LCA, LCC, IMAGEM)
// =====================================================

let comentariosCarregadosTipo = {};

// ✅ Remover a função gerarTodasCaixasComentarios - já não é necessária

function gerarCaixaComentariosTipo(docId, tipo, label, icon, colorClass) {
    // ✅ Verificar se a API_URL está definida
    if (!API_URL) {
        console.error('❌ API_URL não definida!');
        return `<div style="color:#ff6b6b;padding:10px;">Error: API_URL not defined</div>`;
    }
    
    // ✅ Títulos personalizados para cada tipo
    const titulos = {
        'imagem': 'Comment Box Image',
        'lca': 'Comment Box LCA',
        'lcc': 'Comment Box LCC'
    };
    
    const titulo = titulos[tipo] || `Comment Box ${label}`;
    
    return `
        <div class="comentarios-tipo-container" data-doc-id="${docId}" data-tipo="${tipo}">
            <div class="comentarios-tipo-header" onclick="toggleComentariosTipo(${docId}, '${tipo}')">
                <span class="tipo-label ${colorClass}">
                    ${icon} ${titulo}
                    <span class="badge-tipo" id="badgeTipo_${docId}_${tipo}">0</span>
                </span>
                <span class="toggle-icon" id="toggleIconTipo_${docId}_${tipo}">▼</span>
            </div>
            <div class="comentarios-tipo-body" id="comentariosTipoBody_${docId}_${tipo}">
                <div class="comentarios-tipo-list" id="comentariosTipoList_${docId}_${tipo}">
                    <div class="comentario-vazio-tipo">⏳ Loading comments...</div>
                </div>
                <div class="comentario-input-area-tipo">
                    <textarea 
                        class="comentario-textarea-tipo"
                        data-doc-id="${docId}"
                        data-tipo="${tipo}"
                        placeholder="Write a message about ${label}..."
                        rows="1"
                    ></textarea>
                    <button class="btn-enviar-tipo" onclick="enviarComentarioTipo(${docId}, '${tipo}')">
                        📤 Send
                    </button>
                </div>
            </div>
        </div>
    `;
}


function toggleComentariosTipo(docId, tipo) {
    const body = document.getElementById(`comentariosTipoBody_${docId}_${tipo}`);
    const icon = document.getElementById(`toggleIconTipo_${docId}_${tipo}`);
    
    if (!body) return;
    
    const isOpen = body.classList.contains('open');
    
    if (isOpen) {
        body.classList.remove('open');
        if (icon) icon.classList.remove('open');
    } else {
        body.classList.add('open');
        if (icon) icon.classList.add('open');
        
        const key = `${docId}_${tipo}`;
        if (!comentariosCarregadosTipo[key]) {
            carregarComentariosTipo(docId, tipo);
        }
    }
}

async function carregarComentariosTipo(docId, tipo) {
    const key = `${docId}_${tipo}`;
    
    console.log(`📥 Carregando comentários ${tipo} para documento ${docId}`);
    
    try {
        const token = sessionStorage.getItem('doc_token');
        if (!token) {
            console.warn('⚠️ Token não encontrado');
            return;
        }
        
        const url = `${API_URL}/documentos/${docId}/comentarios?tipo=${tipo}`;
        console.log(`📥 URL:`, url);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log(`📥 Resposta ${tipo} status:`, response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`❌ Erro ${tipo}:`, errorText);
            throw new Error('Error loading comments');
        }
        
        const comentarios = await response.json();
        console.log(`📥 Comentários ${tipo} carregados:`, comentarios.length);
        
        comentariosCarregadosTipo[key] = true;
        
        // ✅ Verificar se a função escapeHtml existe
        if (typeof escapeHtml === 'undefined') {
            console.warn('⚠️ escapeHtml não definida, a definir...');
            window.escapeHtml = function(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            };
        }
        
        renderComentariosTipo(docId, tipo, comentarios);
        
        const badge = document.getElementById(`badgeTipo_${docId}_${tipo}`);
        if (badge) {
            badge.textContent = comentarios.length;
        }
        
    } catch (error) {
        console.error(`❌ Error loading ${tipo} comments:`, error);
        const container = document.getElementById(`comentariosTipoList_${docId}_${tipo}`);
        if (container) {
            container.innerHTML = `
                <div style="color:#ff6b6b;font-size:12px;text-align:center;padding:8px;">
                    ❌ Error loading comments: ${error.message}
                </div>
            `;
        }
    }
}

function renderComentariosTipo(docId, tipo, comentarios) {
    const container = document.getElementById(`comentariosTipoList_${docId}_${tipo}`);
    if (!container) {
        console.warn(`⚠️ Container não encontrado para ${tipo} no documento ${docId}`);
        return;
    }
    
    const currentUser = state.username;
    const perfilMap = {
        'empresa': 'company',
        'parceiro': 'partner',
        'admin': 'admin'
    };
    
    if (!comentarios || comentarios.length === 0) {
        container.innerHTML = `
            <div class="comentario-vazio-tipo">
                💬 No comments yet
            </div>
        `;
        return;
    }
    
    let html = '';
    
    comentarios.forEach(c => {
        const isOwn = c.username === currentUser;
        const perfilClass = perfilMap[state.perfil] || 'partner';
        const initials = c.username.substring(0, 2).toUpperCase();
        
        const tipoClass = {
            'lca': 'tipo-lca',
            'lcc': 'tipo-lcc',
            'imagem': 'tipo-imagem',
            'geral': 'tipo-geral'
        }[c.tipo] || 'tipo-geral';
        
        html += `
            <div class="comentario-item ${isOwn ? 'comentario-proprio' : ''} ${tipoClass}">
                <div class="avatar">${initials}</div>
                <div class="comentario-content">
                    <div class="comentario-header">
                        <span class="comentario-username">
                            ${c.username}
                            <span class="perfil-tag ${perfilClass}">${perfilClass}</span>
                        </span>
                        <span class="comentario-data">${c.created_at}</span>
                    </div>
                    <div class="comentario-mensagem">${escapeHtml(c.mensagem)}</div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    const body = document.getElementById(`comentariosTipoBody_${docId}_${tipo}`);
    if (body) {
        body.scrollTop = body.scrollHeight;
    }
}

async function enviarComentarioTipo(docId, tipo) {
    const textarea = document.querySelector(`.comentario-textarea-tipo[data-doc-id="${docId}"][data-tipo="${tipo}"]`);
    const btn = textarea?.parentElement?.querySelector('.btn-enviar-tipo');
    
    if (!textarea || !btn) return;
    
    const mensagem = textarea.value.trim();
    
    if (!mensagem) {
        showToast('Please write a message.', 'warning');
        return;
    }
    
    btn.disabled = true;
    btn.textContent = '⏳';
    
    try {
        const token = sessionStorage.getItem('doc_token');
        if (!token) {
            showToast('Session expired. Please login again.', 'error');
            window.location.href = 'login.html';
            return;
        }
        
        const url = `${API_URL}/documentos/${docId}/comentarios`;
        console.log(`📤 Enviando comentário ${tipo} para:`, url);
        console.log(`📤 Mensagem:`, mensagem);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                mensagem: mensagem,
                tipo: tipo 
            })
        });
        
        console.log(`📥 Resposta status:`, response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Erro resposta:', errorText);
            let errorMessage = 'Error sending comment';
            try {
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.detail || errorMessage;
            } catch (e) {
                errorMessage = errorText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        console.log('✅ Comentário enviado:', result);
        
        textarea.value = '';
        textarea.style.height = '36px';
        
        comentariosCarregadosTipo[`${docId}_${tipo}`] = false;
        await carregarComentariosTipo(docId, tipo);
        
        const body = document.getElementById(`comentariosTipoBody_${docId}_${tipo}`);
        const icon = document.getElementById(`toggleIconTipo_${docId}_${tipo}`);
        if (body) body.classList.add('open');
        if (icon) icon.classList.add('open');
        
        showToast('✅ Comment sent!', 'success');
    } catch (error) {
        console.error('❌ Error sending comment:', error);
        showToast('❌ Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '📤 Send';
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
// AUTO-RESIZE PARA TEXTAREAS DE TIPO
// =====================================================

document.addEventListener('input', function(e) {
    if (e.target.classList && e.target.classList.contains('comentario-textarea-tipo')) {
        e.target.style.height = '36px';
        e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px';
    }
});

// =====================================================
// ENTER PARA ENVIAR COMENTÁRIOS POR TIPO
// =====================================================

document.addEventListener('keydown', function(e) {
    if (e.target.classList && e.target.classList.contains('comentario-textarea-tipo')) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const docId = e.target.getAttribute('data-doc-id');
            const tipo = e.target.getAttribute('data-tipo');
            if (docId && tipo) {
                enviarComentarioTipo(parseInt(docId), tipo);
            }
        }
    }
});

// =====================================================
// INICIALIZAÇÃO
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

// =====================================================
// EXPORTAÇÕES GLOBAIS
// =====================================================

window.abrirFormCriar = abrirFormCriar;
window.carregarDocumentos = carregarDocumentos;
window.aplicarFiltros = aplicarFiltros;
window.limparFiltros = limparFiltros;
window.toggleFiltros = toggleFiltros;
window.abrirDocumento = abrirDocumento;
window.fecharDocumento = fecharDocumento;
window.submeterDocumento = submeterDocumento;
window.iniciarRevisao = iniciarRevisao;
window.aprovarDocumento = aprovarDocumento;
window.pedirAlteracoes = pedirAlteracoes;
window.reabrirDocumento = reabrirDocumento;
window.arquivarDocumento = arquivarDocumento;
window.exportarExcel = exportarExcel;
window.abrirEdicaoDocumento = abrirEdicaoDocumento;
window.salvarEdicao = salvarEdicao;
window.submeterEdicao = submeterEdicao;
window.cancelarEdicao = cancelarEdicao;
window.adicionarItemEditor = adicionarItemEditor;
window.removerItemEditor = removerItemEditor;
window.carregarHistorico = carregarHistorico;
window.toggleConteudoDocumento = toggleConteudoDocumento;
window.alternarSecaoDocumento = alternarSecaoDocumento;
window.alternarEditorSecao = alternarEditorSecao;
window.carregarDashboard = carregarDashboard;
window.carregarNotificacoes = carregarNotificacoes;
window.marcarLida = marcarLida;
window.marcarTodasLidas = marcarTodasLidas;
window.irParaDocumento = irParaDocumento;
window.adicionarProcessoCustom = adicionarProcessoCustom;
window.removerProcessoCustom = removerProcessoCustom;
window.criarDocumento = criarDocumento;
window.fecharFormCriar = fecharFormCriar;
window.mudarAdminView = mudarAdminView;
window.carregarUtilizadores = carregarUtilizadores;
window.abrirFormCriarUser = abrirFormCriarUser;
window.criarUtilizador = criarUtilizador;
window.abrirFormAlterarPassword = abrirFormAlterarPassword;
window.alterarPassword = alterarPassword;
window.eliminarUtilizador = eliminarUtilizador;
window.eliminarDocumento = eliminarDocumento;
window.showToast = showToast;
window.adicionarParceiroSelecionado = adicionarParceiroSelecionado;
window.removerParceiroSelecionado = removerParceiroSelecionado;
window.atualizarParceirosSelecionados = atualizarParceirosSelecionados;
window.uploadImagem = uploadImagem;
window.limparImagem = limparImagem;
window.abrirModalImagem = abrirModalImagem;
window.fecharModalImagem = fecharModalImagem;
window.toggleComentariosTipo = toggleComentariosTipo;
window.carregarComentariosTipo = carregarComentariosTipo;
window.enviarComentarioTipo = enviarComentarioTipo;