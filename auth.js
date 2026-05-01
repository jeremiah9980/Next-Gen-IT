/**
 * ══════════════════════════════════════════════════════════
 *  Next-Gen IT · auth.js
 *  Shared session-auth utility used by the portal.
 *
 *  Include this script in portal/index.html BEFORE any other JS:
 *    <script src="auth.js"></script>
 *
 *  It will immediately redirect to login.html if the session
 *  is not authenticated. No flash of portal content.
 * ══════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  const SESSION_KEY = 'ngit_portal_auth';
  const LOGIN_URL   = './login.html';

  /**
   * Call at the top of index.html to guard the portal.
   * Redirects to login.html if not authenticated.
   */
  function requireAuth() {
    if (sessionStorage.getItem(SESSION_KEY) !== '1') {
      window.location.replace(LOGIN_URL);
    }
  }

  /**
   * Sign the current session out and redirect to login.
   * Wire to a logout button: Auth.logout()
   */
  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    window.location.replace(LOGIN_URL);
  }

  /**
   * Returns true if the session is authenticated.
   */
  function isAuthenticated() {
    return sessionStorage.getItem(SESSION_KEY) === '1';
  }

  // Expose public API
  window.Auth = { requireAuth, logout, isAuthenticated };

  // Auto-guard: if this script is loaded, enforce auth immediately
  requireAuth();
})();
