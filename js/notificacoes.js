// =====================================================
// NOTIFICAÇÕES - Componente
// =====================================================

// Usar configuração central
const API_URL = window.CONFIG ? window.CONFIG.API_URL : 'http://localhost:8000';

function getAuthHeaders() {
    const token = localStorage.getItem('doc_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

async function getNotificacoesNaoLidas() {
    try {
        const response = await fetch(`${API_URL}/notificacoes/nao-lidas`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            return data.count || 0;
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
    return 0;
}

async function marcarNotificacaoLida(notificacaoId) {
    try {
        const response = await fetch(`${API_URL}/notificacoes/${notificacaoId}/ler`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });
        return response.ok;
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}

async function marcarTodasNotificacoesLidas() {
    try {
        const response = await fetch(`${API_URL}/notificacoes/ler-todas`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });
        return response.ok;
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}

// Exportar funções
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getNotificacoesNaoLidas,
        marcarNotificacaoLida,
        marcarTodasNotificacoesLidas
    };
}