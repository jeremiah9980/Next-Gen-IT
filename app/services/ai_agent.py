from __future__ import annotations

from typing import Any

from ..config import settings

_OPENAI_AVAILABLE = False
try:
    from openai import OpenAI  # type: ignore[import-untyped]

    _OPENAI_AVAILABLE = True
except ImportError:
    pass


_SYSTEM_PROMPT_TEMPLATE = """You are a senior IT advisor for Next-Gen-IT, a managed IT services consultancy. \
You are reviewing a completed IT security audit and helping the client understand results and take action.

## Audit Context
- Company: {company}
- Domain: {domain}
- Security Score: {score}/100
- Summary: {summary}

## Findings ({finding_count} total)
{findings_text}

## Evidence on File
{evidence_summary}

## Client Notes
{notes_summary}

## Instructions
- Be concise, friendly, and practical — prioritize by business risk.
- Reference the client's specific domain and findings when relevant.
- Explain technical terms in plain language.
- For fix steps, be specific and sequential.
- Keep responses under 300 words unless a detailed plan is explicitly requested.
- If the client has no findings, affirm their good posture and suggest proactive improvements.
"""


def _build_system_prompt(
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> str:
    company = audit.get("company_name") or audit.get("domain", "Unknown")
    domain = audit.get("domain", "Unknown")
    score = audit.get("score", 0)
    summary = audit.get("summary") or "Not yet available."

    if findings:
        lines = [
            f"  [{f['severity'].upper()}] {f['code']} – {f['title']}"
            for f in findings
        ]
        findings_text = "\n".join(lines)
    else:
        findings_text = "  None detected — domain appears well-configured."

    evidence_summary = (
        ", ".join(item["filename"] for item in evidence_items)
        if evidence_items
        else "None uploaded yet."
    )

    if notes:
        notes_text = " | ".join(n["content"][:120] for n in notes[:5])
    else:
        notes_text = "None added yet."

    return _SYSTEM_PROMPT_TEMPLATE.format(
        company=company,
        domain=domain,
        score=score,
        summary=summary,
        finding_count=len(findings),
        findings_text=findings_text,
        evidence_summary=evidence_summary,
        notes_summary=notes_text,
    )


def _fallback_response(
    message: str,
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
) -> str:
    """Smart rule-based fallback when no OpenAI API key is configured."""
    msg = message.lower()
    finding_codes = {f["code"] for f in findings}
    domain = audit.get("domain", "your domain")
    score = audit.get("score", 0)

    if any(kw in msg for kw in ["score", "rating", "grade", "how secure", "security"]):
        label = "excellent" if score >= 80 else "good" if score >= 60 else "moderate" if score >= 40 else "needs immediate attention"
        return (
            f"**Security Score: {score}/100 ({label})**\n\n"
            f"The score for **{domain}** is calculated by deducting points for each finding:\n"
            "- Critical: −40 pts &nbsp;|&nbsp; High: −20 pts &nbsp;|&nbsp; Medium: −10 pts &nbsp;|&nbsp; Low: −5 pts\n\n"
            f"You have **{len(findings)} finding(s)**. Fixing critical and high severity items first will have the biggest impact on your score."
        )

    if any(kw in msg for kw in ["dmarc", "spoofing", "spoof"]):
        has_issue = "DMARC_MISSING" in finding_codes or "DMARC_POLICY_NONE" in finding_codes
        if has_issue:
            return (
                f"**DMARC Issue Detected on {domain}**\n\n"
                "DMARC tells receiving mail servers what to do with emails that fail authentication — preventing spoofing attacks.\n\n"
                "**Steps to fix:**\n"
                f"1. Add a DNS TXT record at `_dmarc.{domain}` with value:\n"
                f"   `v=DMARC1; p=none; rua=mailto:dmarc@{domain}`\n"
                "2. Monitor aggregate reports for 2–4 weeks\n"
                "3. Progress to `p=quarantine` then `p=reject` once all senders pass\n\n"
                "**Priority: Critical** — without DMARC, your domain can be used in phishing attacks."
            )
        return f"DMARC is present on **{domain}**. Consider moving to `p=reject` once you've verified all legitimate senders pass authentication."

    if any(kw in msg for kw in ["spf", "sender policy"]):
        has_issue = "SPF_MISSING" in finding_codes or "SPF_PERMISSIVE" in finding_codes
        if has_issue:
            return (
                f"**SPF Issue Detected on {domain}**\n\n"
                "SPF (Sender Policy Framework) lists the mail servers authorised to send email for your domain.\n\n"
                "**Steps to fix:**\n"
                "1. Identify every service that sends email on your behalf (e.g., Google Workspace, Mailchimp, your CRM)\n"
                f"2. Add a DNS TXT record on `{domain}`, e.g.:\n"
                "   `v=spf1 include:_spf.google.com ~all`\n"
                "3. Use `~all` (soft fail) initially, then tighten to `-all` after testing\n\n"
                "**Priority: High** — missing or permissive SPF lets anyone forge your domain as a sender."
            )
        return f"SPF is configured for **{domain}**. Ensure it lists all legitimate sending services and uses `-all` for strict enforcement."

    if any(kw in msg for kw in ["dkim", "signing", "sign", "domainkeys"]):
        has_issue = "DKIM_NOT_VERIFIED" in finding_codes
        if has_issue:
            return (
                f"**DKIM Not Verified for {domain}**\n\n"
                "DKIM adds a cryptographic signature to outgoing emails, proving they originated from your authorised mail server.\n\n"
                "**Steps to verify:**\n"
                "1. Log into your email provider (Google Workspace, Microsoft 365, etc.)\n"
                "2. Navigate to email authentication / DKIM settings and enable signing\n"
                "3. Copy the TXT record value and publish it in DNS at `<selector>._domainkey.{domain}`\n"
                "4. Common selectors to check: `google`, `selector1`, `selector2`, `default`\n\n"
                "**Priority: Medium** — DKIM is required for DMARC to enforce authentication effectively."
            )
        return f"DKIM selectors were found and verified on **{domain}**. Keep your keys rotated periodically as a best practice."

    if any(kw in msg for kw in ["mx", "mail", "email", "inbox", "exchange"]):
        has_mx_issue = "NO_MX" in finding_codes
        if has_mx_issue:
            return (
                f"**No MX Records Found for {domain}**\n\n"
                "MX (Mail Exchanger) records tell the internet which servers handle inbound email for your domain.\n\n"
                "**Steps to fix:**\n"
                "1. Log into your DNS provider\n"
                "2. Add MX records for your email platform, e.g.:\n"
                "   - Google Workspace: `ASPMX.L.GOOGLE.COM` (priority 1)\n"
                "   - Microsoft 365: `<yourdomain>.mail.protection.outlook.com`\n"
                "3. Allow up to 48 hours for DNS propagation\n\n"
                "**Priority: High** — without MX records, inbound email delivery will fail."
            )
        return f"Email routing appears configured for **{domain}**. Check the audit summary for your mail provider details."

    if any(kw in msg for kw in ["website", "web", "http", "https", "ssl", "tls", "cert", "site"]):
        has_issue = "WEBSITE_UNREACHABLE" in finding_codes
        if has_issue:
            return (
                f"**Website Unreachable for {domain}**\n\n"
                "The audit could not reach your website over HTTP or HTTPS.\n\n"
                "**Possible causes:**\n"
                "- The site is offline or under maintenance\n"
                "- DNS has not propagated\n"
                "- A firewall is blocking external access\n"
                "- This domain does not host a public website\n\n"
                "**Steps:**\n"
                "1. Test the site from multiple networks and browsers\n"
                "2. Check your hosting provider's status page\n"
                "3. Verify A/AAAA DNS records point to the correct server"
            )
        return f"Your website appears reachable. For deeper security analysis, consider an SSL/TLS scan via SSL Labs (ssllabs.com/ssltest)."

    if any(kw in msg for kw in [
        "priority", "first", "fix first", "where to start", "action plan",
        "roadmap", "what should i", "next step",
    ]):
        if not findings:
            return (
                f"Great news — no findings were detected for **{domain}** (score: {score}/100). "
                "Your domain is well-configured!\n\n"
                "**Proactive next steps:**\n"
                "- Upload tool invoices or screenshots for a full ecosystem audit\n"
                "- Schedule quarterly DNS and email authentication reviews\n"
                "- Consider a DMARC aggregate reporting service for ongoing monitoring"
            )
        critical = [f for f in findings if f["severity"] == "critical"]
        high = [f for f in findings if f["severity"] == "high"]
        medium = [f for f in findings if f["severity"] == "medium"]
        low = [f for f in findings if f["severity"] == "low"]

        plan_lines = [f"**Recommended Action Plan for {domain}** (Score: {score}/100)\n"]
        step = 1
        for finding in critical + high + medium + low:
            plan_lines.append(
                f"{step}. **[{finding['severity'].upper()}]** {finding['title']}\n"
                f"   → {finding['recommendation']}"
            )
            step += 1
        plan_lines.append("\nFix in this order to maximise your security score improvement.")
        return "\n".join(plan_lines)

    if any(kw in msg for kw in ["report", "download", "export", "pdf"]):
        return (
            "Your audit report is available as a Markdown file.\n\n"
            "Click the **Download Report** button in the Audit Status card (visible once the audit completes). "
            "The report includes your full findings, DNS snapshot, security score, and a Mermaid architecture diagram. "
            "You can render it in any Markdown viewer or convert it to PDF using tools like Pandoc or Typora."
        )

    if any(kw in msg for kw in ["evidence", "upload", "file", "document", "invoice"]):
        return (
            "**What to Upload as Evidence**\n\n"
            "Uploading evidence enables a deeper ecosystem audit. Useful files include:\n"
            "- **Tool list or inventory** — spreadsheet of software/SaaS subscriptions\n"
            "- **Invoices or receipts** — to identify duplicate spend and shadow IT\n"
            "- **Screenshots** — from admin consoles (email, DNS, cloud portals)\n"
            "- **Export files** — from CRM, billing, or identity platforms\n\n"
            "Use the **Upload Evidence** section above to add files to this audit."
        )

    if any(kw in msg for kw in ["help", "what can you", "what do you", "capabilities", "hi", "hello"]):
        return (
            "**Hi! I'm your Next-Gen-IT AI Advisor.**\n\n"
            "I can help you with:\n"
            "- 📊 Understanding your security score and what affects it\n"
            "- 🛡️ Explaining DMARC, SPF, and DKIM — and how to fix issues\n"
            "- 📧 Email authentication setup and troubleshooting\n"
            "- 🌐 Website and DNS issues\n"
            "- 📋 Building a prioritised action plan\n"
            "- 📤 Guidance on what evidence to upload\n\n"
            "Try asking: *'What should I fix first?'* or *'Explain my DMARC issue'* or *'Give me an action plan'*"
        )

    # Default: summarise findings
    if findings:
        top = findings[0]
        return (
            f"Your audit for **{domain}** found **{len(findings)} issue(s)** with a security score of **{score}/100**.\n\n"
            f"Your top priority is: **{top['title']}** ({top['severity']} severity)\n"
            f"> {top['recommendation']}\n\n"
            "Ask me about specific findings (e.g. *'Explain DMARC'*) or say **'action plan'** for a full prioritised list."
        )
    return (
        f"Your audit for **{domain}** found no major issues — score is **{score}/100**. "
        "Ask me about any topic like DMARC, SPF, DKIM, or your email configuration."
    )


def get_ai_response(
    message: str,
    history: list[dict[str, str]],
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> str:
    """Return an AI-generated response, using OpenAI when configured or the smart fallback otherwise."""
    if not _OPENAI_AVAILABLE or not settings.openai_api_key:
        return _fallback_response(message, audit, findings)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        system_prompt = _build_system_prompt(audit, findings, evidence_items, notes)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content or "Sorry, I could not generate a response."
    except Exception:
        return _fallback_response(message, audit, findings)


def generate_ai_follow_up_questions(
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> list[str]:
    """Generate follow-up questions using OpenAI if configured; returns empty list on fallback."""
    if not _OPENAI_AVAILABLE or not settings.openai_api_key:
        return []

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        company = audit.get("company_name") or audit.get("domain", "the domain")
        domain = audit.get("domain", "the domain")
        score = audit.get("score", 0)

        finding_summaries = [
            f"{f['code']}: {f['title']} ({f['severity']})" for f in findings
        ]

        prompt = (
            f"You are auditing IT infrastructure for {company} (domain: {domain}). "
            f"Security score: {score}/100. "
            f"Findings: {'; '.join(finding_summaries) if finding_summaries else 'none'}. "
            f"Evidence uploaded: {'yes' if evidence_items else 'no'}. "
            f"Client notes: {'yes' if notes else 'no'}.\n\n"
            "Generate exactly 5 short, specific follow-up questions to ask the client that will help "
            "resolve the findings or uncover additional risks. "
            "Each question on its own line. No numbering, no bullets, plain text only."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )
        content = response.choices[0].message.content or ""
        questions = [q.strip() for q in content.strip().splitlines() if q.strip()]
        return questions[:5]
    except Exception:
        return []
