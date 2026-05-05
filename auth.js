/**
 * ══════════════════════════════════════════════════════════
 *  Next-Gen IT · auth.js
 *  Shared session-auth utility used by the portal.
 *
 *  Include this script before protected portal/app JavaScript.
 *  It redirects unauthenticated users to the portal login page.
 * ══════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  const SESSION_KEY = 'ngit_portal_auth';
  const LEGACY_SESSION_KEY = 'ngit_auth';

  function getLoginUrl() {
    const path = window.location.pathname || '';
    return path.includes('/portal/') ? './login.html' : './portal/login.html';
  }

  function markAuthenticated() {
    sessionStorage.setItem(SESSION_KEY, '1');
    sessionStorage.setItem(LEGACY_SESSION_KEY, '1');
  }

  /**
   * Call at the top of protected pages to guard the portal.
   * Redirects to login.html if not authenticated.
   */
  function requireAuth() {
    const current = sessionStorage.getItem(SESSION_KEY) === '1';
    const legacy = sessionStorage.getItem(LEGACY_SESSION_KEY) === '1';

    if (legacy && !current) {
      sessionStorage.setItem(SESSION_KEY, '1');
      return;
    }

    if (!current) {
      window.location.replace(getLoginUrl());
    }
  }

  /**
   * Sign the current session out and redirect to login.
   * Wire to a logout button: Auth.logout()
   */
  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(LEGACY_SESSION_KEY);
    window.location.replace(getLoginUrl());
  }

  /**
   * Returns true if the session is authenticated.
   */
  function isAuthenticated() {
    return sessionStorage.getItem(SESSION_KEY) === '1' || sessionStorage.getItem(LEGACY_SESSION_KEY) === '1';
  }

  // Expose public API
  window.Auth = { requireAuth, logout, isAuthenticated, markAuthenticated };

  // Auto-guard: if this script is loaded, enforce auth immediately.
  requireAuth();
})();
