// config.js
const CONFIG = {
  clientId: '77n8awe98j70ci', // Client ID بتاعك
  
  // استخدم GitHub Pages URL في production
  redirectUri: window.location.hostname === 'localhost' 
    ? 'http://localhost:5500/callback.html'
    : 'https://nadanagdy.github.io/Linkedin-Automation-/callback.html',
  
  scope: 'openid profile email w_member_social r_organization_social w_organization_social',
  
  // Company Page ID
  companyId: '111716442'
};
