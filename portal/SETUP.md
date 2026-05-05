# Portal Login — Setup Guide

## Files to add to your repo

```
portal/
  login.html    ← new login page (drop in)
  auth.js       ← new auth utility (drop in)
  index.html    ← existing portal — add ONE line (see below)
```

---

## Step 1 — Add auth.js to index.html

Open `portal/index.html`. Add this line as the **very first `<script>` tag** inside `<head>`:

```html
<script src="auth.js"></script>
```

That's it. The script auto-runs and redirects unauthenticated visitors to `login.html`.

---

## Step 2 — Set your password

The default placeholder in `login.html` is **not a real hash**. You must set your own.

1. Open `portal/login.html` in your browser
2. Open DevTools → Console
3. Paste and run:

```javascript
async function hashPw(pw) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(pw));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2,'0')).join('');
}
hashPw('yourChosenPassword').then(h => console.log(h));
```

4. Copy the 64-character hex string
5. In `login.html`, find the line:
   ```js
   const CORRECT_HASH = 'a1c9e4b3...';
   ```
6. Replace the value with your new hash

---

## Step 3 — Add a logout button (optional)

In `portal/index.html`, add this wherever you want the logout control:

```html
<button onclick="Auth.logout()">Sign Out</button>
```

You can style it however you like — `Auth.logout()` clears the session and
sends the user back to the login screen.

---

## How it works

| Layer | Mechanism |
|---|---|
| Password storage | SHA-256 hash in `login.html` source |
| Session | `sessionStorage` (cleared when browser tab closes) |
| Guard | `auth.js` checks session before page renders |
| Redirect | Unauthenticated → `login.html`; Authenticated → `index.html` |

> **Note:** This is a lightweight access gate appropriate for an internal
> tool on GitHub Pages. It is not enterprise-grade authentication — the hash
> is visible in the page source, so do not use this to protect highly
> sensitive production credentials. For a more secure solution, consider
> Cloudflare Access (free tier) or Netlify Identity sitting in front of
> the Pages deployment.

---

## Cloudflare Access (stronger option, still free)

If you proxy the GitHub Pages site through Cloudflare:

1. Cloudflare Dashboard → Access → Applications → Add Application
2. Choose "Self-hosted", point to `jeremiah9980.github.io/Next-Gen-IT/portal`
3. Set a policy: "Email ends in @yourdomain.com" or specific email list
4. Users receive a one-time email code — no password to manage

This keeps the client-side code clean and adds a real auth layer.
