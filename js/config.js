// =====================================================
// CONFIGURAÇÃO CENTRAL - Holoss Document Platform
// =====================================================

(function() {
    // DETECTAR AMBIENTE AUTOMATICAMENTE
    const hostname = window.location.hostname;
    const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
    
    // URL do backend
    let API_URL;
    if (isLocal) {
        API_URL = 'http://localhost:8000';
    } else {
        // Em produção (Render), usa o nome do serviço
        API_URL = 'https://plataforma-documentos-backend.onrender.com';
    }
    
    // URLs do frontend
    const FRONTEND_URL = window.location.origin;
    
    // Expor globalmente
    window.CONFIG = {
        API_URL: API_URL,
        FRONTEND_URL: FRONTEND_URL,
        IS_LOCAL: isLocal,
        IS_RENDER: !isLocal,
        ENVIRONMENT: isLocal ? 'development' : 'production'
    };
    
    console.log('📋 Configuração carregada:');
    console.log('   🌐 Ambiente:', window.CONFIG.ENVIRONMENT);
    console.log('   🔗 API URL:', window.CONFIG.API_URL);
    console.log('   📱 Frontend:', window.CONFIG.FRONTEND_URL);
})();