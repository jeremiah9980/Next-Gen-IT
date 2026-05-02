from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dns.exception
import dns.resolver
import requests


COMMON_DKIM_SELECTORS = [
    "google",
    "selector1",
    "selector2",
    "default",
    "k1",
    "smtp",
]


@dataclass
class ScanResult:
    domain: str
    mx_records: list[str]
    txt_records: list[str]
    spf_record: str | None
    dmarc_record: str | None
    dkim_selectors_found: list[str]
    mail_provider: str
    website_status: str
    website_server: str | None
    findings: list[dict[str, Any]]
    raw: dict[str, Any]


def resolve_txt(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "TXT")
        values: list[str] = []
        for answer in answers:
            values.append("".join(part.decode() for part in answer.strings))
        return values
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        return []


def resolve_mx(domain: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return sorted(str(answer.exchange).rstrip(".") for answer in answers)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        return []


def infer_mail_provider(mx_records: list[str]) -> str:
    joined = " ".join(mx_records).lower()
    if "google.com" in joined or "googlemail.com" in joined:
        return "Google Workspace"
    if "outlook.com" in joined or "protection.outlook.com" in joined:
        return "Microsoft 365"
    if "zoho.com" in joined:
        return "Zoho Mail"
    if not mx_records:
        return "Unknown"
    return "Custom / Other"


def check_website(domain: str) -> tuple[str, str | None]:
    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}"
        try:
            response = requests.get(url, timeout=6, allow_redirects=True)
            server = response.headers.get("server")
            return f"{response.status_code} via {scheme.upper()}", server
        except requests.RequestException:
            continue
    return "unreachable", None


def parse_spf(txt_records: list[str]) -> str | None:
    for record in txt_records:
        if record.lower().startswith("v=spf1"):
            return record
    return None


def parse_dmarc(domain: str) -> str | None:
    records = resolve_txt(f"_dmarc.{domain}")
    for record in records:
        if record.lower().startswith("v=dmarc1"):
            return record
    return None


def discover_dkim_selectors(domain: str) -> list[str]:
    selectors: list[str] = []
    for selector in COMMON_DKIM_SELECTORS:
        records = resolve_txt(f"{selector}._domainkey.{domain}")
        if any("k=rsa" in record.lower() or "p=" in record.lower() for record in records):
            selectors.append(selector)
    return selectors


def derive_findings(
    domain: str,
    mx_records: list[str],
    spf_record: str | None,
    dmarc_record: str | None,
    dkim_selectors: list[str],
    website_status: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if not mx_records:
        findings.append(
            {
                "code": "NO_MX",
                "title": "No MX records detected",
                "category": "mail",
                "severity": "high",
                "description": "The domain does not expose MX records, so business email routing is unclear.",
                "recommendation": "Confirm the intended mail platform and publish valid MX records.",
                "evidence": "No MX records were returned from DNS.",
            }
        )

    if not spf_record:
        findings.append(
            {
                "code": "SPF_MISSING",
                "title": "SPF record missing",
                "category": "security",
                "severity": "high",
                "description": "The domain does not publish an SPF record, which weakens sender validation.",
                "recommendation": "Publish an SPF record for the approved mail senders and use a restrictive policy.",
                "evidence": "No TXT record beginning with v=spf1 was found on the root domain.",
            }
        )
    elif "+all" in spf_record.lower():
        findings.append(
            {
                "code": "SPF_PERMISSIVE",
                "title": "SPF is overly permissive",
                "category": "security",
                "severity": "high",
                "description": "The SPF record contains +all, which effectively allows any sender.",
                "recommendation": "Replace +all with a restrictive policy such as ~all or -all after validation.",
                "evidence": spf_record,
            }
        )

    if not dmarc_record:
        findings.append(
            {
                "code": "DMARC_MISSING",
                "title": "DMARC record missing",
                "category": "security",
                "severity": "critical",
                "description": "The domain does not publish DMARC, making spoofing detection and enforcement much weaker.",
                "recommendation": "Publish a DMARC record and begin with monitoring or quarantine before moving to reject.",
                "evidence": f"No v=DMARC1 record was found at _dmarc.{domain}.",
            }
        )
    else:
        lower = dmarc_record.lower()
        if "p=none" in lower:
            findings.append(
                {
                    "code": "DMARC_POLICY_NONE",
                    "title": "DMARC is not enforced",
                    "category": "security",
                    "severity": "high",
                    "description": "DMARC exists but is set to p=none, so spoofed messages are only monitored, not blocked.",
                    "recommendation": "Move to quarantine, then reject, after validating legitimate senders.",
                    "evidence": dmarc_record,
                }
            )
        if "rua=" not in lower:
            findings.append(
                {
                    "code": "DMARC_REPORTING_MISSING",
                    "title": "DMARC aggregate reporting not configured",
                    "category": "security",
                    "severity": "medium",
                    "description": "DMARC is present but aggregate reporting is not obvious.",
                    "recommendation": "Add an rua mailbox or external reporting service to monitor authentication failures.",
                    "evidence": dmarc_record,
                }
            )

    if not dkim_selectors:
        findings.append(
            {
                "code": "DKIM_NOT_VERIFIED",
                "title": "DKIM could not be publicly verified",
                "category": "security",
                "severity": "medium",
                "description": "No common DKIM selectors were discoverable, so outbound signing could not be confirmed.",
                "recommendation": "Confirm the mail provider's DKIM selectors and verify active signing.",
                "evidence": "Common selectors checked: " + ", ".join(COMMON_DKIM_SELECTORS),
            }
        )

    if website_status == "unreachable":
        findings.append(
            {
                "code": "WEBSITE_UNREACHABLE",
                "title": "Website was not reachable during the scan",
                "category": "web",
                "severity": "low",
                "description": "The public website could not be reached over HTTP or HTTPS during the audit.",
                "recommendation": "Confirm site availability and public access controls.",
                "evidence": "HTTP and HTTPS requests failed.",
            }
        )

    return findings


def scan_domain(domain: str) -> ScanResult:
    domain = domain.strip().lower()
    mx_records = resolve_mx(domain)
    txt_records = resolve_txt(domain)
    spf_record = parse_spf(txt_records)
    dmarc_record = parse_dmarc(domain)
    dkim_selectors = discover_dkim_selectors(domain)
    mail_provider = infer_mail_provider(mx_records)
    website_status, website_server = check_website(domain)
    findings = derive_findings(
        domain=domain,
        mx_records=mx_records,
        spf_record=spf_record,
        dmarc_record=dmarc_record,
        dkim_selectors=dkim_selectors,
        website_status=website_status,
    )

    raw = {
        "domain": domain,
        "mx_records": mx_records,
        "txt_records": txt_records,
        "spf_record": spf_record,
        "dmarc_record": dmarc_record,
        "dkim_selectors_found": dkim_selectors,
        "mail_provider": mail_provider,
        "website_status": website_status,
        "website_server": website_server,
    }
    return ScanResult(
        domain=domain,
        mx_records=mx_records,
        txt_records=txt_records,
        spf_record=spf_record,
        dmarc_record=dmarc_record,
        dkim_selectors_found=dkim_selectors,
        mail_provider=mail_provider,
        website_status=website_status,
        website_server=website_server,
        findings=findings,
        raw=raw,
    )
