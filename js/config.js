// =====================================================
// CONFIGURAÇÃO CENTRAL - Holoss Document Platform
// =====================================================

(function() {
    // URL FIXA para desenvolvimento local
    const API_URL = 'http://localhost:8000';
    
    // URLs do frontend
    const FRONTEND_URL = window.location.origin;
    
    // Expor globalmente
    window.CONFIG = {
        API_URL: API_URL,
        FRONTEND_URL: FRONTEND_URL,
        IS_LOCAL: true,
        IS_RENDER: false,
        ENVIRONMENT: 'development'
    };
    
    console.log('📋 Configuração carregada:');
    console.log('   🌐 Ambiente:', window.CONFIG.ENVIRONMENT);
    console.log('   🔗 API URL:', window.CONFIG.API_URL);
    console.log('   📱 Frontend:', window.CONFIG.FRONTEND_URL);
})();