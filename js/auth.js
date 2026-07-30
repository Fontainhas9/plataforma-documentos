// =====================================================
// AUTH - Verificação centralizada de autenticação
// VERSÃO DEFINITIVA - SESSÃO POR SEPARADOR (NÃO PARTILHADA)
// =====================================================

(function() {
    // Lista de páginas que NÃO precisam de autenticação
    const PUBLIC_PAGES = ['login.html', 'index.html'];
    
    // Obter o nome da página atual
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // ✅ USAR sessionStorage EM VEZ DE localStorage
    // sessionStorage é EXCLUSIVO por separador/janela
    const token = sessionStorage.getItem('doc_token');
    const username = sessionStorage.getItem('doc_username');
    const isAuthenticated = token && username;
    
    console.log('🔐 Auth Check (sessionStorage):', {
        page: currentPage,
        isPublic: PUBLIC_PAGES.includes(currentPage),
        isAuthenticated: isAuthenticated,
        token: token ? '✅' : '❌',
        username: username || '❌',
        storageType: 'sessionStorage (separador único)'
    });
    
    // Se NÃO estiver autenticado E NÃO for uma página pública → REDIRECIONAR
    if (!isAuthenticated && !PUBLIC_PAGES.includes(currentPage)) {
        console.log('🔒 Sem sessão neste separador - redirecionar para login');
        window.location.replace('login.html');
        throw new Error('Redirecting to login');
    }
    
    // Se estiver autenticado E estiver na página de login → REDIRECIONAR PARA DOCUMENTOS
    if (isAuthenticated && currentPage === 'login.html') {
        console.log('✅ Já autenticado neste separador, redirecionando para documentos...');
        window.location.replace('documentos.html');
        throw new Error('Redirecting to documents');
    }
    
    console.log('✅ Autenticação OK neste separador');
    
    // Expor estado de autenticação globalmente
    window.AUTH = {
        isAuthenticated: isAuthenticated,
        token: token,
        username: username,
        perfil: sessionStorage.getItem('doc_perfil'),
        nome: sessionStorage.getItem('doc_nome'),
        storageType: 'sessionStorage'
    };
})();