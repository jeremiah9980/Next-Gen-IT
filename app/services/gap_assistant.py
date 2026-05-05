from __future__ import annotations

from typing import Any

from .ai_agent import generate_ai_follow_up_questions


def _rule_based_questions(
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> list[str]:
    questions: list[str] = []

    if not evidence_items:
        questions.append(
            "Please upload a current tool list, invoices, or screenshots so the audit can detect duplicate spend and shadow IT."
        )

    if not notes:
        questions.append(
            "Who owns email, DNS, and shared files today, and which person actually makes changes in those systems?"
        )

    finding_codes = {finding["code"] for finding in findings}

    if "DKIM_NOT_VERIFIED" in finding_codes:
        questions.append(
            "Which email platform sends mail on behalf of the domain, and do you know the active DKIM selector names?"
        )

    if "DMARC_MISSING" in finding_codes or "DMARC_POLICY_NONE" in finding_codes:
        questions.append(
            "Do you send mail from any tools besides your primary inbox platform, such as CRM, newsletter, or transaction tools?"
        )

    if "SPF_MISSING" in finding_codes or "SPF_PERMISSIVE" in finding_codes:
        questions.append(
            "Please list every service allowed to send email from this domain so SPF can be safely tightened."
        )

    if len(questions) < 3:
        questions.append(
            "Which systems handle lead intake, deal tracking, document storage, and marketing today?"
        )

    return questions[:5]


def generate_follow_up_questions(
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> list[str]:
    """Return AI-generated follow-up questions when OpenAI is configured, else rule-based."""
    ai_questions = generate_ai_follow_up_questions(audit, findings, evidence_items, notes)
    if ai_questions:
        return ai_questions
    return _rule_based_questions(audit, findings, evidence_items, notes)
