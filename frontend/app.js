const state = {
  auditId: null,
  pollHandle: null,
};

const apiBaseInput = document.getElementById("apiBase");
const companyNameInput = document.getElementById("companyName");
const domainInput = document.getElementById("domain");
const flash = document.getElementById("flash");
const statusBox = document.getElementById("statusBox");
const summaryBox = document.getElementById("summaryBox");
const findingsBox = document.getElementById("findings");
const reportLink = document.getElementById("reportLink");
const actionsBox = document.getElementById("actions");
const historyBox = document.getElementById("history");
const evidenceList = document.getElementById("evidenceList");
const notesList = document.getElementById("notesList");
const gapQuestions = document.getElementById("gapQuestions");

const storedBase = localStorage.getItem("nextGenItApiBase");
apiBaseInput.value = storedBase || "http://localhost:8000";

function getApiBase() {
  const value = apiBaseInput.value.trim().replace(/\/$/, "");
  localStorage.setItem("nextGenItApiBase", value);
  return value;
}

function setFlash(message, isError = false) {
  flash.textContent = message;
  flash.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function setStatus(message, statusClass = "status-idle") {
  statusBox.className = `status ${statusClass}`;
  statusBox.textContent = message;
}

function clearPolling() {
  if (state.pollHandle) {
    clearInterval(state.pollHandle);
    state.pollHandle = null;
  }
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${getApiBase()}${path}`, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const payload = await response.json();
      if (payload.detail) message = payload.detail;
    } catch (_) {}
    throw new Error(message);
  }
  return response;
}

function renderFindings(findings) {
  if (!findings || findings.length === 0) {
    findingsBox.className = "findings empty";
    findingsBox.innerHTML = "No findings yet.";
    return;
  }

  findingsBox.className = "findings";
  findingsBox.innerHTML = findings.map((finding) => `
    <article class="finding">
      <div class="badge badge-${finding.severity}">${finding.severity}</div>
      <h3>${finding.title}</h3>
      <p><strong>Category:</strong> ${finding.category}</p>
      <p>${finding.description}</p>
      <p><strong>Recommendation:</strong> ${finding.recommendation}</p>
      <p class="meta"><strong>Evidence:</strong> ${finding.evidence}</p>
    </article>
  `).join("");
}

function renderEvidence(items) {
  if (!items || items.length === 0) {
    evidenceList.innerHTML = "<li>No evidence uploaded.</li>";
    return;
  }
  evidenceList.innerHTML = items
    .map((item) => `<li>${item.filename} <span class="meta">(${item.content_type})</span></li>`)
    .join("");
}

function renderNotes(items) {
  if (!items || items.length === 0) {
    notesList.innerHTML = "<li>No notes yet.</li>";
    return;
  }
  notesList.innerHTML = items
    .map((item) => `<li><strong>${item.source}:</strong> ${item.content}</li>`)
    .join("");
}

function renderQuestions(questions) {
  if (!questions || questions.length === 0) {
    gapQuestions.innerHTML = "<li>No follow-up questions yet.</li>";
    return;
  }
  gapQuestions.innerHTML = questions.map((q) => `<li>${q}</li>`).join("");
}

async function loadGapQuestions(auditId) {
  try {
    const response = await apiFetch(`/api/audits/${auditId}/gaps`);
    const payload = await response.json();
    renderQuestions(payload.questions || []);
  } catch (error) {
    renderQuestions([`Could not load follow-up questions: ${error.message}`]);
  }
}

async function loadAudit(auditId) {
  const response = await apiFetch(`/api/audits/${auditId}`);
  const audit = await response.json();
  state.auditId = audit.id;

  const statusClass = audit.status === "completed"
    ? "status-completed"
    : audit.status === "failed"
      ? "status-failed"
      : audit.status === "running" || audit.status === "queued"
        ? "status-running"
        : "status-idle";

  setStatus(`Audit ${audit.status}`, statusClass);

  if (audit.summary) {
    summaryBox.classList.remove("hidden");
    summaryBox.textContent = audit.summary;
  } else {
    summaryBox.classList.add("hidden");
    summaryBox.textContent = "";
  }

  actionsBox.classList.remove("hidden");

  if (audit.status === "completed") {
    reportLink.classList.remove("hidden");
    reportLink.href = `${getApiBase()}/api/audits/${audit.id}/report`;
    clearPolling();
  } else {
    reportLink.classList.add("hidden");
  }

  if (audit.status === "failed") {
    clearPolling();
    setFlash(audit.error || "Audit failed.", true);
  }

  renderFindings(audit.findings);
  renderEvidence(audit.evidence_items);
  renderNotes(audit.notes);
  await loadGapQuestions(audit.id);

  // Enable the AI chat and load its history for this audit
  setChatEnabled(true);
  await loadChatHistory(audit.id);
}

async function runAudit() {
  const domain = domainInput.value.trim();
  const companyName = companyNameInput.value.trim();
  if (!domain) {
    setFlash("Please enter a domain.", true);
    return;
  }

  setFlash("Starting audit...");
  setStatus("Submitting audit...", "status-running");
  renderFindings([]);
  renderEvidence([]);
  renderNotes([]);
  renderQuestions([]);
  clearPolling();

  try {
    const response = await apiFetch("/api/audits", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ domain, company_name: companyName || null }),
    });
    const payload = await response.json();
    state.auditId = payload.audit_id;
    await loadAudit(state.auditId);
    state.pollHandle = setInterval(() => loadAudit(state.auditId), 2500);
    setFlash(`Audit queued: ${state.auditId}`);
  } catch (error) {
    setFlash(error.message, true);
    setStatus("Audit could not be started.", "status-failed");
  }
}

async function loadHistory() {
  try {
    const response = await apiFetch("/api/audits");
    const audits = await response.json();
    if (!audits.length) {
      historyBox.className = "history empty";
      historyBox.textContent = "No audits found.";
      return;
    }

    historyBox.className = "history";
    historyBox.innerHTML = audits.map((audit) => `
      <div class="history-item">
        <div><strong>${audit.company_name || audit.domain}</strong></div>
        <div class="meta">${audit.domain} · ${audit.status} · score ${audit.score}</div>
        <div class="row">
          <button data-audit-id="${audit.id}" class="secondary history-load">Open</button>
        </div>
      </div>
    `).join("");

    document.querySelectorAll(".history-load").forEach((btn) => {
      btn.addEventListener("click", async (event) => {
        const auditId = event.target.dataset.auditId;
        await loadAudit(auditId);
      });
    });
  } catch (error) {
    historyBox.className = "history empty";
    historyBox.textContent = `Could not load history: ${error.message}`;
  }
}

async function uploadEvidence() {
  const fileInput = document.getElementById("evidenceFile");
  const file = fileInput.files[0];
  if (!state.auditId) {
    setFlash("Run or load an audit first.", true);
    return;
  }
  if (!file) {
    setFlash("Select a file to upload.", true);
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    await apiFetch(`/api/audits/${state.auditId}/evidence`, {
      method: "POST",
      body: formData,
    });
    setFlash("Evidence uploaded.");
    fileInput.value = "";
    await loadAudit(state.auditId);
  } catch (error) {
    setFlash(error.message, true);
  }
}

async function saveNote() {
  const noteText = document.getElementById("noteText");
  const content = noteText.value.trim();
  if (!state.auditId) {
    setFlash("Run or load an audit first.", true);
    return;
  }
  if (!content) {
    setFlash("Enter a note first.", true);
    return;
  }

  try {
    await apiFetch(`/api/audits/${state.auditId}/notes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ source: "portal", content }),
    });
    noteText.value = "";
    setFlash("Note saved.");
    await loadAudit(state.auditId);
  } catch (error) {
    setFlash(error.message, true);
  }
}

document.getElementById("runAuditBtn").addEventListener("click", runAudit);
document.getElementById("loadAuditsBtn").addEventListener("click", loadHistory);
document.getElementById("refreshBtn").addEventListener("click", async () => {
  if (!state.auditId) {
    setFlash("No audit selected.", true);
    return;
  }
  await loadAudit(state.auditId);
});
document.getElementById("uploadBtn").addEventListener("click", uploadEvidence);
document.getElementById("saveNoteBtn").addEventListener("click", saveNote);

// ── Chat ────────────────────────────────────────────────────────────────────

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");
const chatStatusBadge = document.getElementById("chatStatusBadge");

function setChatEnabled(enabled) {
  chatSendBtn.disabled = !enabled;
  chatInput.disabled = !enabled;
}

/**
 * Escape plain text so it is safe to insert as innerHTML.
 * This must be applied before any markdown-to-HTML transforms.
 */
function escapeHtml(text) {
  const node = document.createElement("span");
  node.textContent = text;
  return node.innerHTML;
}

/**
 * Convert a small subset of markdown to HTML.
 * Input MUST be HTML-escaped before calling this function.
 */
function markdownToHtml(escapedText) {
  return escapedText
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

function appendChatBubble(role, content) {
  const existing = chatMessages.querySelector(".chat-empty");
  if (existing) existing.remove();

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble chat-bubble-${role}`;

  const roleEl = document.createElement("div");
  roleEl.className = "chat-role";
  roleEl.textContent = role === "user" ? "You" : "AI Advisor";

  const contentEl = document.createElement("div");
  contentEl.className = "chat-content";
  // Escape first, then apply safe markdown transforms
  contentEl.innerHTML = markdownToHtml(escapeHtml(content));

  bubble.appendChild(roleEl);
  bubble.appendChild(contentEl);
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderChatHistory(history) {
  chatMessages.innerHTML = "";
  if (!history || history.length === 0) {
    const empty = document.createElement("div");
    empty.className = "chat-empty";
    empty.textContent = "Run or load an audit, then ask me anything about your IT security.";
    chatMessages.appendChild(empty);
    return;
  }
  history.forEach(({ role, content }) => appendChatBubble(role, content));
}

async function loadChatHistory(auditId) {
  try {
    const response = await apiFetch(`/api/audits/${auditId}/chat`);
    const history = await response.json();
    renderChatHistory(history);
  } catch (_) {
    // Non-critical — chat history load failure doesn't break the page
  }
}

async function sendChatMessage() {
  const message = chatInput.value.trim();
  if (!message) return;
  if (!state.auditId) {
    setFlash("Run or load an audit first.", true);
    return;
  }

  chatInput.value = "";
  appendChatBubble("user", message);

  // Show typing indicator
  const typingEl = document.createElement("div");
  typingEl.className = "chat-bubble chat-bubble-assistant chat-typing";
  const typingRole = document.createElement("div");
  typingRole.className = "chat-role";
  typingRole.textContent = "AI Advisor";
  const typingContent = document.createElement("div");
  typingContent.className = "chat-content";
  ["", "", ""].forEach(() => {
    const dot = document.createElement("span");
    dot.className = "typing-dot";
    typingContent.appendChild(dot);
  });
  typingEl.appendChild(typingRole);
  typingEl.appendChild(typingContent);
  chatMessages.appendChild(typingEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  chatSendBtn.disabled = true;
  chatStatusBadge.textContent = "⏳ Thinking…";

  try {
    const response = await apiFetch(`/api/audits/${state.auditId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const payload = await response.json();
    typingEl.remove();
    appendChatBubble("assistant", payload.reply);
  } catch (error) {
    typingEl.remove();
    appendChatBubble("assistant", `Sorry, I couldn't reach the AI advisor: ${error.message}`);
  } finally {
    chatSendBtn.disabled = false;
    chatStatusBadge.textContent = "⚡ Ready";
  }
}

chatSendBtn.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const msg = chip.dataset.msg;
    if (!msg) return;
    chatInput.value = msg;
    chatInput.focus();
    sendChatMessage();
  });
});
