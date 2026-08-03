// =====================================================
// AUTH - Verificação centralizada de autenticação
// VERSÃO CORRIGIDA - NÃO BLOQUEIA A PÁGINA DE LOGIN
// =====================================================

(function() {
    // Lista de páginas que NÃO precisam de autenticação
    const PUBLIC_PAGES = ['login.html', 'index.html'];
    
    // Obter o nome da página atual
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Verificar autenticação (sessionStorage)
    const token = sessionStorage.getItem('doc_token');
    const username = sessionStorage.getItem('doc_username');
    const isAuthenticated = token && username;
    
    console.log('🔐 Auth Check:', {
        page: currentPage,
        isPublic: PUBLIC_PAGES.includes(currentPage),
        isAuthenticated: isAuthenticated,
        token: token ? '✅' : '❌',
        username: username || '❌'
    });
    
    // ✅ SE ESTIVER NA PÁGINA DE LOGIN, NÃO FAZ NADA (deixa o login.js trabalhar)
    if (currentPage === 'login.html' || currentPage === 'index.html') {
        console.log('📄 Página de login - a permitir acesso');
        // Expor estado de autenticação globalmente
        window.AUTH = {
            isAuthenticated: isAuthenticated,
            token: token,
            username: username,
            perfil: sessionStorage.getItem('doc_perfil'),
            nome: sessionStorage.getItem('doc_nome'),
            isLoginPage: true
        };
        return;
    }
    
    // Se NÃO estiver autenticado E NÃO for uma página pública → REDIRECIONAR
    if (!isAuthenticated && !PUBLIC_PAGES.includes(currentPage)) {
        console.log('🔒 Sem autenticação - redirecionar para login');
        window.location.replace('login.html');
        return;
    }
    
    console.log('✅ Autenticação OK');
    
    // Expor estado de autenticação globalmente
    window.AUTH = {
        isAuthenticated: isAuthenticated,
        token: token,
        username: username,
        perfil: sessionStorage.getItem('doc_perfil'),
        nome: sessionStorage.getItem('doc_nome'),
        isLoginPage: false
    };
})();