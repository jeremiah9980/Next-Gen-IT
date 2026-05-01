from __future__ import annotations

from html import escape
from pathlib import Path

from ..config import settings


def build_mermaid(scan: dict) -> str:
    provider = scan.get("mail_provider", "Unknown")
    website_status = scan.get("website_status", "unknown")
    return f"""graph TD
    A[Domain: {scan['domain']}] --> B[Mail Provider: {provider}]
    A --> C[Website: {website_status}]
    A --> D[SPF: {'present' if scan.get('spf_record') else 'missing'}]
    A --> E[DMARC: {'present' if scan.get('dmarc_record') else 'missing'}]
    A --> F[DKIM: {'selectors found' if scan.get('dkim_selectors_found') else 'not verified'}]
"""


def generate_report(
    audit_id: str,
    domain: str,
    company_name: str | None,
    scan: dict,
    findings: list[dict],
    score: int,
) -> Path:
    report_path = settings.report_dir / f"{audit_id}.md"
    title = company_name or domain
    report = f"""# Next-Gen-IT Audit Report

## Organization
- Name: {title}
- Domain: {domain}
- Security score: {score}/100

## Snapshot
- Mail provider: {scan.get('mail_provider', 'Unknown')}
- Website status: {scan.get('website_status', 'unknown')}
- MX records: {', '.join(scan.get('mx_records', [])) or 'none detected'}
- SPF: {scan.get('spf_record') or 'missing'}
- DMARC: {scan.get('dmarc_record') or 'missing'}
- DKIM selectors found: {', '.join(scan.get('dkim_selectors_found', [])) or 'none'}

## Findings
"""

    for finding in findings:
        report += f"""
### [{finding['severity'].upper()}] {finding['title']}
- Category: {finding['category']}
- Code: {finding['code']}
- Description: {finding['description']}
- Recommendation: {finding['recommendation']}
- Evidence: {finding['evidence']}
"""

    report += f"""
## Current-State Diagram
```mermaid
{build_mermaid(scan)}
```

## Next best actions
1. Fix the highest-severity mail authentication findings first.
2. Confirm all legitimate senders before tightening SPF and DMARC.
3. Upload invoices, screenshots, or tool exports to expand this into a full ecosystem audit.
"""

    report_path.write_text(report, encoding="utf-8")
    return report_path


def severity_rank(severity: str) -> int:
    return {"critical": 1, "high": 2, "medium": 3, "low": 4}.get(severity.lower(), 5)


def build_runbook_steps(finding: dict) -> list[dict[str, str]]:
    """Create a reusable runbook step list from one audit finding.

    The audit findings remain the source of truth. This function turns each
    finding into an operator-friendly template section that can be executed by
    a web admin, DNS admin, marketing owner, or implementation contractor.
    """

    title = finding.get("title", "Finding")
    code = finding.get("code", "GENERAL")
    recommendation = finding.get("recommendation", "Review and remediate this finding.")
    evidence = finding.get("evidence", "No evidence captured.")

    steps = [
        {
            "title": "Confirm Current State",
            "owner": "Audit Owner / Technical Lead",
            "action": f"Validate the finding: {title}. Review the audit evidence and compare it against the live domain configuration.",
            "command": f"# Evidence from audit\n{evidence}",
            "success": "The owner confirms whether the finding is valid, already fixed, or requires remediation.",
        },
        {
            "title": "Apply Recommended Fix",
            "owner": "System Owner / Website Admin / DNS Admin",
            "action": recommendation,
            "command": f"# Remediation reference\n# Finding code: {code}\n# Recommendation: {recommendation}",
            "success": "The configuration or website change has been applied in the correct production system.",
        },
        {
            "title": "Validate and Capture Proof",
            "owner": "Audit Owner",
            "action": "Re-run the scanner, capture screenshots or export results, and attach the evidence to the audit record.",
            "command": f"# Re-run validation for {code}\n# Save screenshot/export to the audit evidence folder.",
            "success": "The finding no longer appears, or the new scan shows a clear improvement with supporting evidence.",
        },
    ]

    lower_title = title.lower()
    lower_code = code.lower()

    if "spf" in lower_title or "spf" in lower_code:
        steps[1]["command"] = """# DNS TXT record for Google Workspace SPF
Host: @
Type: TXT
Value: v=spf1 include:_spf.google.com ~all
TTL: Automatic

# Important: keep only one SPF TXT record for the root domain."""
        steps[2]["command"] = """# Validate SPF
nslookup -type=txt example.com
# or use MXToolbox / Google Admin Toolbox."""

    if "dmarc" in lower_title or "dmarc" in lower_code:
        steps[1]["command"] = """# Start DMARC in monitoring mode
Host: _dmarc
Type: TXT
Value: v=DMARC1; p=none; rua=mailto:dmarc@example.com; pct=100
TTL: Automatic

# Later hardening path:
# p=none -> p=quarantine -> p=reject"""
        steps[2]["command"] = """# Validate DMARC
nslookup -type=txt _dmarc.example.com
# Confirm aggregate reports are received before enforcement."""

    if "dkim" in lower_title or "dkim" in lower_code:
        steps[1]["command"] = """# Google Workspace DKIM flow
Google Admin Console -> Apps -> Google Workspace -> Gmail -> Authenticate email
Generate a new DKIM record, then add the generated TXT record in DNS.

Host: google._domainkey
Type: TXT
Value: [Generated by Google Admin]
TTL: Automatic"""
        steps[2]["command"] = """# Validate DKIM after propagation
nslookup -type=txt google._domainkey.example.com
# Then click Start Authentication in Google Admin."""

    if "mx" in lower_title or "mx" in lower_code:
        steps[1]["command"] = """# Google Workspace MX
Host: @
Type: MX
Value: smtp.google.com
Priority: 1
TTL: Automatic

# Remove conflicting legacy MX records unless Google Workspace instructs otherwise."""
        steps[2]["command"] = """# Validate MX
nslookup -type=mx example.com
# Confirm mail receives successfully in Google Workspace."""

    return steps


def render_code_block(value: str) -> str:
    return f"<pre><code>{escape(value)}</code></pre>" if value else ""


def generate_runbook(
    audit_id: str,
    domain: str,
    company_name: str | None,
    scan: dict,
    findings: list[dict],
    score: int,
) -> Path:
    """Generate a standalone HTML runbook for technical remediation.

    This is intentionally separate from the executive report. The executive
    report explains risk and priority. The runbook explains execution,
    validation, rollback, and ownership.
    """

    runbook_path = settings.report_dir / f"{audit_id}-runbook.html"
    title = company_name or domain
    ordered_findings = sorted(findings, key=lambda item: severity_rank(item.get("severity", "low")))

    sections = []
    for index, finding in enumerate(ordered_findings, start=1):
        steps = build_runbook_steps(finding)
        step_cards = "".join(
            f"""
            <article class="step-card">
              <div class="step-label">Step {step_number}</div>
              <h4>{escape(step['title'])}</h4>
              <p><strong>Owner:</strong> {escape(step['owner'])}</p>
              <p>{escape(step['action'])}</p>
              {render_code_block(step.get('command', ''))}
              <p class="success"><strong>Success Criteria:</strong> {escape(step['success'])}</p>
            </article>
            """
            for step_number, step in enumerate(steps, start=1)
        )
        sections.append(
            f"""
            <section class="runbook-section">
              <div class="section-header">
                <div>
                  <p class="eyebrow">Runbook Item {index}</p>
                  <h3>{escape(finding.get('title', 'Finding'))}</h3>
                </div>
                <span class="badge badge-{escape(finding.get('severity', 'low').lower())}">{escape(finding.get('severity', 'low')).upper()}</span>
              </div>
              <div class="finding-grid">
                <div><strong>Category</strong><span>{escape(finding.get('category', 'General'))}</span></div>
                <div><strong>Code</strong><span>{escape(finding.get('code', 'N/A'))}</span></div>
                <div><strong>Evidence</strong><span>{escape(finding.get('evidence', 'No evidence captured.'))}</span></div>
              </div>
              <p class="description">{escape(finding.get('description', 'No description provided.'))}</p>
              <div class="steps">{step_cards}</div>
              <details>
                <summary>Rollback / Escalation Guidance</summary>
                <p>If the change causes service disruption, revert the last DNS, website, tracking, or portal change. Capture the timestamp, owner, and before/after values. Escalate to the domain administrator, website developer, or platform owner depending on the impacted system.</p>
              </details>
            </section>
            """
        )

    if not sections:
        sections.append(
            """
            <section class="runbook-section">
              <h3>No Findings Requiring Remediation</h3>
              <p>No remediation runbook items were generated because the audit did not return actionable findings.</p>
            </section>
            """
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(title)} Audit Runbook</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --ink: #162033;
      --muted: #5d6a7f;
      --card: #ffffff;
      --border: #d9e1ee;
      --accent: #2563eb;
      --critical: #b42318;
      --high: #c2410c;
      --medium: #a16207;
      --low: #1d4ed8;
      --success: #067647;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }}
    .shell {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 64px; }}
    .hero {{ background: linear-gradient(135deg, #0f172a, #1e3a8a); color: white; border-radius: 24px; padding: 32px; margin-bottom: 22px; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; color: #93c5fd; margin: 0 0 8px; }}
    h1, h2, h3, h4 {{ margin: 0 0 12px; }}
    .subhead {{ color: #dbeafe; max-width: 780px; line-height: 1.55; }}
    .summary-grid, .finding-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
    .summary-grid div, .finding-grid div {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; padding: 14px; }}
    .finding-grid div {{ background: #f8fafc; border-color: var(--border); }}
    .summary-grid strong, .finding-grid strong {{ display: block; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: #bfdbfe; margin-bottom: 6px; }}
    .finding-grid strong {{ color: var(--muted); }}
    .summary-grid span, .finding-grid span {{ overflow-wrap: anywhere; }}
    .notice {{ background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; border-radius: 16px; padding: 16px; margin-bottom: 18px; }}
    .runbook-section {{ background: var(--card); border: 1px solid var(--border); border-radius: 22px; padding: 22px; margin-bottom: 18px; box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08); }}
    .section-header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; border-bottom: 1px solid var(--border); padding-bottom: 14px; margin-bottom: 16px; }}
    .badge {{ border-radius: 999px; padding: 7px 12px; font-size: 12px; font-weight: 800; color: white; }}
    .badge-critical {{ background: var(--critical); }}
    .badge-high {{ background: var(--high); }}
    .badge-medium {{ background: var(--medium); }}
    .badge-low {{ background: var(--low); }}
    .description {{ color: var(--muted); line-height: 1.55; }}
    .steps {{ display: grid; gap: 14px; margin-top: 18px; }}
    .step-card {{ border: 1px solid var(--border); border-radius: 16px; padding: 16px; background: #fbfdff; }}
    .step-label {{ display: inline-block; background: #dbeafe; color: #1d4ed8; border-radius: 999px; padding: 5px 10px; font-size: 12px; font-weight: 800; margin-bottom: 10px; }}
    pre {{ background: #0f172a; color: #e2e8f0; border-radius: 14px; padding: 14px; overflow-x: auto; line-height: 1.45; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 13px; }}
    .success {{ color: var(--success); }}
    details {{ margin-top: 16px; border-top: 1px solid var(--border); padding-top: 12px; color: var(--muted); }}
    summary {{ cursor: pointer; color: var(--ink); font-weight: 700; }}
    .footer {{ color: var(--muted); font-size: 13px; margin-top: 26px; }}
    @media (max-width: 800px) {{ .summary-grid, .finding-grid {{ grid-template-columns: 1fr; }} .section-header {{ flex-direction: column; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">Next-Gen-IT Technical Remediation Runbook</p>
      <h1>{escape(title)} Domain Audit Runbook</h1>
      <p class="subhead">This file is generated alongside the executive audit report. Use the report for leadership review and this runbook for implementation, validation, rollback, and evidence capture.</p>
      <div class="summary-grid">
        <div><strong>Domain</strong><span>{escape(domain)}</span></div>
        <div><strong>Security Score</strong><span>{score}/100</span></div>
        <div><strong>Findings</strong><span>{len(findings)} actionable item(s)</span></div>
        <div><strong>Mail Provider</strong><span>{escape(str(scan.get('mail_provider', 'Unknown')))}</span></div>
        <div><strong>Website Status</strong><span>{escape(str(scan.get('website_status', 'unknown')))}</span></div>
        <div><strong>MX Records</strong><span>{escape(', '.join(scan.get('mx_records', [])) or 'none detected')}</span></div>
      </div>
    </header>

    <section class="notice">
      <strong>Template intent:</strong> Every audit should produce two outputs: an executive audit report for real estate leadership and this HTML runbook for the technical team or implementation partner. Keep placeholders, validation commands, and success criteria visible so the page can be executed like an SOP.
    </section>

    {''.join(sections)}

    <p class="footer">Generated by Next-Gen-IT Audit Portal. Audit ID: {escape(audit_id)}</p>
  </main>
</body>
</html>
"""

    runbook_path.write_text(html, encoding="utf-8")
    return runbook_path
