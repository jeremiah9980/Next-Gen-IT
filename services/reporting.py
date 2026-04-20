from __future__ import annotations

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
