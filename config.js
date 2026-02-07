
// LinkedIn OAuth Configuration
const CONFIG = {
  // Client ID من تطبيق LinkedIn
  clientId: '77n8awe98j70ci',
  
  // Redirect URI - يتغير حسب البيئة (local أو production)
  redirectUri: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5500/callback.html'
    : 'https://nadanagdy.github.io/Linkedin-Automation-/callback.html',
  
  // Scopes المطلوبة
  scope: 'openid profile email w_member_social r_organization_social w_organization_social',
  
  // Company Page ID
  companyId: '111716442',
  
  // API Endpoints
  apiEndpoints: {
    authorize: 'https://www.linkedin.com/oauth/v2/authorization',
    token: 'https://www.linkedin.com/oauth/v2/accessToken',
    userInfo: 'https://api.linkedin.com/v2/userinfo',
    me: 'https://api.linkedin.com/v2/me',
    share: 'https://api.linkedin.com/v2/ugcPosts'
  }
};

// Export للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
