/* ── AI Assistant — Next-Gen-IT Chat Widget ─────────────────
 *
 *  This is a demo implementation with simulated responses.
 *  To connect a real AI backend, replace the `getAIResponse`
 *  function (see "API INTEGRATION" section below).
 *
 *  Quick-start (Claude / Anthropic API):
 *  -----------------------------------------------
 *  Replace the mock `getAIResponse` body with a call to your
 *  backend proxy, e.g.:
 *
 *    const res = await fetch('/api/chat', {
 *      method: 'POST',
 *      headers: { 'Content-Type': 'application/json' },
 *      body: JSON.stringify({ message: userText }),
 *    });
 *    const { reply } = await res.json();
 *    return reply;
 *
 *  Your backend proxy should call the Anthropic Messages API:
 *    POST https://api.anthropic.com/v1/messages
 *  with your ANTHROPIC_API_KEY kept server-side (never in JS).
 * ─────────────────────────────────────────────────────────── */

(function () {
  "use strict";

  /* ── Demo knowledge base ─────────────────────────────────
   *  Keyword → response pairs for the mock assistant.
   *  Extend or replace with real API calls (see above).
   * ───────────────────────────────────────────────────────── */
  const DEMO_RESPONSES = [
    {
      keywords: ["hello", "hi", "hey", "greetings", "howdy"],
      reply:
        "Hello! I'm the Next-Gen-IT assistant. I can help you understand audit findings, explain recommendations, or walk you through the runbook workflow. What would you like to know?",
    },
    {
      keywords: ["audit", "run audit", "start audit", "domain audit"],
      reply:
        "To run an audit, enter your API base URL, company name, and target domain in the **Start New Audit** card, then click **Run Audit**. The engine will scan DNS records, SSL certificates, open ports, and more. Results typically appear within 30–60 seconds.",
    },
    {
      keywords: ["finding", "findings", "vulnerability", "issue", "risk"],
      reply:
        "Findings are color-coded by severity: **Critical/High** (red) need immediate action, **Medium** (yellow) should be addressed soon, and **Low** (blue) are informational. Click any finding card to see the full description, recommendation, and evidence.",
    },
    {
      keywords: ["report", "download", "export", "pdf"],
      reply:
        "Once an audit completes you'll see a **Download Report** button in the Audit Status card. The report is a standalone HTML file you can save or print to PDF. It includes an executive summary, all findings, and scoring breakdowns.",
    },
    {
      keywords: ["runbook", "client", "share", "steps", "remediation"],
      reply:
        "The runbook is a client-facing remediation guide. Use **Open Runbook** to preview it, or **Share with Client** to get a public link you can send directly to your client. Each runbook section maps to a specific finding with step-by-step fix instructions.",
    },
    {
      keywords: ["evidence", "upload", "file", "attachment", "proof"],
      reply:
        "You can attach supporting files (screenshots, logs, config exports) in the **Upload Evidence** card. Uploaded files are stored server-side and linked to the current audit so reviewers can verify findings later.",
    },
    {
      keywords: ["note", "notes", "comment", "annotation"],
      reply:
        "Use the **Add Notes** card to capture interview answers, tool ownership details, or workflow observations. Notes are saved to the audit record and appear in the final report for context.",
    },
    {
      keywords: ["gap", "question", "follow-up", "followup", "missing"],
      reply:
        "The **AI-Ready Follow-Up Questions** section surfaces gaps in the current data — things like missing SPF/DMARC policies or unverified SSL chains — as targeted questions you can ask the client in your next call.",
    },
    {
      keywords: ["api", "backend", "server", "endpoint", "localhost"],
      reply:
        "The portal connects to a FastAPI backend (default: `http://localhost:8000`). You can change the API Base URL in the Start New Audit card at any time. The URL is saved to `localStorage` so you won't need to re-enter it each session.",
    },
    {
      keywords: ["score", "scoring", "seo", "grade", "rating"],
      reply:
        "Each audit produces scores across categories: **SEO**, **Security**, **Marketing**, **Tech/CRM**, and **Infrastructure**. Scores are out of 10 and roll up into an overall grade shown at the top of the executive report.",
    },
    {
      keywords: ["ssl", "tls", "https", "certificate", "cert"],
      reply:
        "The audit checks SSL/TLS configuration including certificate validity, expiry date, cipher strength, and HSTS headers. A failing certificate is flagged as **High** severity since it directly impacts user trust and browser security warnings.",
    },
    {
      keywords: ["dns", "mx", "spf", "dmarc", "dkim", "email"],
      reply:
        "Email authentication findings (SPF, DKIM, DMARC) are among the most common issues. Missing or misconfigured records leave the domain open to spoofing. The runbook includes copy-paste DNS record examples to fix them.",
    },
    {
      keywords: ["history", "past", "previous", "load"],
      reply:
        "Click **Load History** to retrieve all past audits from the backend. Each row in the Audit History table links back to the full audit record so you can re-download reports or review findings from earlier engagements.",
    },
    {
      keywords: ["login", "auth", "access", "portal"],
      reply:
        "Portal access is managed through the login page. Once authenticated your session token is stored and used automatically for all API calls. Token expiry or invalid credentials will redirect you back to the login screen.",
    },
    {
      keywords: ["help", "what can you do", "capabilities", "features"],
      reply:
        "I can help with:\n• Running and understanding audits\n• Interpreting findings & severity levels\n• Generating and sharing runbooks\n• Uploading evidence & adding notes\n• Understanding scores and reports\n• DNS, SSL, and email security questions\n\nJust ask anything about the portal!",
    },
  ];

  const FALLBACK_RESPONSES = [
    "That's a great question. Could you give me a bit more detail so I can point you to the right part of the portal?",
    "I'm still learning the nuances of that topic. For now, the best resource is the **Findings** section — it usually contains the most relevant context.",
    "I want to make sure I give you accurate information. Could you rephrase that, or ask about a specific audit step?",
    "Hmm, I don't have a ready answer for that. Feel free to check the runbook or reach out to the Next-Gen-IT team directly.",
  ];

  let fallbackIndex = 0;

  /* ── API INTEGRATION ─────────────────────────────────────
   *  Replace the body of this function to call a real backend.
   *  The function must return a Promise<string>.
   * ───────────────────────────────────────────────────────── */
  async function getAIResponse(userText) {
    // Simulate network latency
    await new Promise((resolve) =>
      setTimeout(resolve, 700 + Math.random() * 600)
    );

    const lower = userText.toLowerCase();

    for (const { keywords, reply } of DEMO_RESPONSES) {
      if (keywords.some((kw) => lower.includes(kw))) {
        return reply;
      }
    }

    // Rotate through fallbacks
    const response = FALLBACK_RESPONSES[fallbackIndex % FALLBACK_RESPONSES.length];
    fallbackIndex++;
    return response;
  }

  /* ── Render helpers ─────────────────────────────────────── */
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  /** Very light markdown: **bold** and newlines → <br> */
  function renderMarkdown(text) {
    return escapeHtml(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  /* ── Build DOM ──────────────────────────────────────────── */
  function buildWidget() {
    // Wrapper keeps toggle + window together
    const wrapper = document.createElement("div");
    wrapper.setAttribute("id", "chat-widget");

    wrapper.innerHTML = `
      <!-- Toggle button -->
      <button
        class="chat-toggle"
        id="chat-toggle-btn"
        aria-label="Open AI assistant"
        aria-expanded="false"
        aria-controls="chat-panel"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M4.913 2.658c2.075-.27 4.19-.408 6.337-.408 2.147 0 4.262.14 6.337.408 1.922.25 3.291 1.861 3.405 3.727a4.403 4.403 0 0 0-1.032-.211 50.89 50.89 0 0 0-8.42 0c-2.358.196-4.04 2.19-4.04 4.434v4.286a4.47 4.47 0 0 0 2.433 3.984L7.28 21.53A.75.75 0 0 1 6 21v-4.03a48.527 48.527 0 0 1-1.087-.128C2.905 16.58 1.5 14.833 1.5 12.862V6.638c0-1.97 1.405-3.718 3.413-3.979z" />
          <path d="M15.75 7.5c-1.376 0-2.739.057-4.086.169C10.124 7.797 9 9.103 9 10.609v4.285c0 1.507 1.128 2.814 2.67 2.94 1.243.102 2.5.157 3.768.165l2.782 2.781a.75.75 0 0 0 1.28-.53v-2.39l.33-.026c1.542-.125 2.67-1.433 2.67-2.94v-4.286c0-1.505-1.125-2.811-2.664-2.94A49.392 49.392 0 0 0 15.75 7.5z" />
        </svg>
        <span class="chat-badge" id="chat-badge" aria-hidden="true" style="display:none">1</span>
      </button>

      <!-- Chat window -->
      <div
        class="chat-window"
        id="chat-panel"
        role="dialog"
        aria-label="AI assistant chat"
        aria-modal="false"
      >
        <div class="chat-header">
          <div class="chat-header-avatar" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5zM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="chat-header-info">
            <div class="chat-header-name">Next-Gen-IT Assistant</div>
            <div class="chat-header-status">● Online</div>
          </div>
          <button class="chat-close-btn" id="chat-close-btn" aria-label="Close chat">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <div class="chat-messages" id="chat-messages" aria-live="polite"></div>

        <div class="chat-input-row">
          <textarea
            class="chat-input"
            id="chat-input"
            placeholder="Ask about audits, findings, runbooks…"
            rows="1"
            aria-label="Message input"
          ></textarea>
          <button class="chat-send-btn" id="chat-send-btn" aria-label="Send message" disabled>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z" />
            </svg>
          </button>
        </div>
        <div class="chat-footer-note">AI demo mode · responses are illustrative</div>
      </div>
    `;

    document.body.appendChild(wrapper);
  }

  /* ── Chat state ─────────────────────────────────────────── */
  let isOpen = false;
  let isBusy = false;

  function appendMessage(role, text) {
    const messagesEl = document.getElementById("chat-messages");

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${role}`;
    msgDiv.innerHTML = `<div class="chat-msg-bubble">${renderMarkdown(text)}</div>`;
    messagesEl.appendChild(msgDiv);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return msgDiv;
  }

  function showTyping() {
    const messagesEl = document.getElementById("chat-messages");
    const el = document.createElement("div");
    el.className = "chat-typing";
    el.id = "chat-typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById("chat-typing");
    if (el) el.remove();
  }

  function openChat() {
    isOpen = true;
    document.getElementById("chat-panel").classList.add("chat-open");
    document.getElementById("chat-toggle-btn").setAttribute("aria-expanded", "true");
    document.getElementById("chat-badge").style.display = "none";
    document.getElementById("chat-input").focus();
  }

  function closeChat() {
    isOpen = false;
    document.getElementById("chat-panel").classList.remove("chat-open");
    document.getElementById("chat-toggle-btn").setAttribute("aria-expanded", "false");
  }

  async function handleSend() {
    if (isBusy) return;

    const inputEl = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    const text = inputEl.value.trim();
    if (!text) return;

    isBusy = true;
    inputEl.value = "";
    inputEl.style.height = "";
    sendBtn.disabled = true;

    appendMessage("user", text);
    showTyping();

    try {
      const reply = await getAIResponse(text);
      hideTyping();
      appendMessage("assistant", reply);
    } catch {
      hideTyping();
      appendMessage("assistant", "Sorry, I ran into an issue. Please try again.");
    }

    isBusy = false;
    inputEl.focus();
  }

  /* ── Wire up events ─────────────────────────────────────── */
  function init() {
    buildWidget();

    // Open / close toggle
    document.getElementById("chat-toggle-btn").addEventListener("click", () => {
      isOpen ? closeChat() : openChat();
    });

    document.getElementById("chat-close-btn").addEventListener("click", closeChat);

    // Send on button click
    document.getElementById("chat-send-btn").addEventListener("click", handleSend);

    // Send on Enter (Shift+Enter for newline), enable button on input
    const inputEl = document.getElementById("chat-input");
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    inputEl.addEventListener("input", () => {
      const sendBtn = document.getElementById("chat-send-btn");
      sendBtn.disabled = inputEl.value.trim() === "" || isBusy;

      // Auto-grow textarea
      inputEl.style.height = "auto";
      inputEl.style.height = Math.min(inputEl.scrollHeight, 100) + "px";
    });

    // Greet the user after a short delay (shows badge while closed)
    setTimeout(() => {
      const messagesEl = document.getElementById("chat-messages");
      if (messagesEl.children.length === 0) {
        appendMessage(
          "assistant",
          "👋 Hi there! I'm the Next-Gen-IT assistant. Ask me anything about audits, findings, or the runbook workflow."
        );
        if (!isOpen) {
          document.getElementById("chat-badge").style.display = "flex";
        }
      }
    }, 1200);
  }

  // Initialize after the DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
