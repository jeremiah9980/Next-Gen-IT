from __future__ import annotations

import traceback
from threading import Thread

from ..repository import (
    add_finding,
    clear_findings,
    get_audit,
    save_audit_outcome,
    set_audit_status,
)
from .dns_audit import scan_domain
from .reporting import generate_report
from .scoring import score_findings


def build_summary(scan: dict, findings: list[dict], score: int) -> str:
    highest = findings[0]["title"] if findings else "No major issues detected"
    return (
        f"Mail provider: {scan.get('mail_provider', 'Unknown')}. "
        f"Security score: {score}/100. "
        f"Top issue: {highest}. "
        f"Findings found: {len(findings)}."
    )


def run_audit_job(audit_id: str) -> None:
    audit = get_audit(audit_id)
    if not audit:
        return

    try:
        set_audit_status(audit_id, "running")
        scan_result = scan_domain(audit["domain"])
        findings = scan_result.findings
        clear_findings(audit_id)
        for finding in findings:
            add_finding(audit_id, finding)
        score = score_findings(findings)
        summary = build_summary(scan_result.raw, findings, score)
        report_path = generate_report(
            audit_id=audit_id,
            domain=audit["domain"],
            company_name=audit.get("company_name"),
            scan=scan_result.raw,
            findings=findings,
            score=score,
        )
        save_audit_outcome(audit_id, summary, score, report_path)
        set_audit_status(audit_id, "completed")
    except Exception as exc:  # pragma: no cover - defensive path
        error_text = f"{exc}\n\n{traceback.format_exc()}"
        set_audit_status(audit_id, "failed", error_text)


def start_audit_thread(audit_id: str) -> None:
    thread = Thread(target=run_audit_job, args=(audit_id,), daemon=True)
    thread.start()
