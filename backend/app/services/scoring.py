from __future__ import annotations

SEVERITY_PENALTIES = {
    "critical": 40,
    "high": 20,
    "medium": 10,
    "low": 5,
}


def score_findings(findings: list[dict]) -> int:
    score = 100
    for finding in findings:
        score -= SEVERITY_PENALTIES.get(finding.get("severity", "low"), 5)
    return max(score, 0)
