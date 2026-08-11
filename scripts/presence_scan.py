#!/usr/bin/env python3
"""
presence_scan.py — Quick-mode presence scanner for the Next-Gen-IT dashboard.

Reads targets.csv, runs concurrent DNS + HTTP posture checks per domain,
computes score deltas against the previous presence.json, and atomically
writes data/presence.json for the dashboard to poll.

Usage:
    python scripts/presence_scan.py --targets targets.csv --out data/presence.json
    python scripts/presence_scan.py --targets targets.csv --out data/presence.json --limit 5

Dependencies:
    pip install httpx dnspython

Compatible with Python 3.9+.
"""

from __future__ import annotations  # allows `str | None` hints on Python 3.9

import argparse
import asyncio
import csv
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
import dns.asyncresolver
import dns.resolver
import dns.exception

# ---------------------------------------------------------------- config

CONCURRENCY = 10          # simultaneous domains
DNS_TIMEOUT = 5.0         # seconds per DNS query
HTTP_TIMEOUT = 10.0       # seconds for site check
DOMAIN_TIMEOUT = 90.0     # hard cap per domain (all checks combined)
DKIM_SELECTORS = [        # common selectors to probe when none is known
    "default", "selector1", "selector2", "google", "k1", "s1", "s2",
    "mail", "smtp", "dkim", "mandrill", "everlytickey1", "zmail",
]
SCORE_DROP_ALERT = 10     # flag domains whose score fell by this much


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- DNS checks

def make_resolver() -> dns.asyncresolver.Resolver:
    r = dns.asyncresolver.Resolver()
    r.timeout = DNS_TIMEOUT
    r.lifetime = DNS_TIMEOUT
    # Cloudflare + Google, matching what the client-side DoH scanners see
    r.nameservers = ["1.1.1.1", "8.8.8.8"]
    return r


async def query_txt(resolver, name: str) -> list:
    """TXT record strings for name; [] on NXDOMAIN/NoAnswer; raises on timeout."""
    try:
        ans = await resolver.resolve(name, "TXT")
        out = []
        for rr in ans:
            out.append("".join(
                s.decode() if isinstance(s, bytes) else s for s in rr.strings
            ))
        return out
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []


async def check_spf(resolver, domain: str) -> dict:
    txts = await query_txt(resolver, domain)
    spf_records = [t for t in txts if t.lower().startswith("v=spf1")]
    if not spf_records:
        return {"status": "missing", "record": None}
    if len(spf_records) > 1:
        # multiple SPF records = permanent error per RFC 7208
        return {"status": "invalid_multiple", "record": spf_records[0]}
    rec = spf_records[0]
    if re.search(r"[?+]all\b", rec):
        status = "weak"            # neutral/pass-all: effectively no protection
    elif "~all" in rec:
        status = "softfail"
    elif "-all" in rec:
        status = "pass"
    else:
        status = "no_all_mechanism"
    return {"status": status, "record": rec}


async def check_dmarc(resolver, domain: str) -> dict:
    txts = await query_txt(resolver, "_dmarc." + domain)
    recs = [t for t in txts if t.lower().startswith("v=dmarc1")]
    if not recs:
        return {"status": "missing", "policy": None, "record": None}
    rec = recs[0]
    m = re.search(r"\bp\s*=\s*(none|quarantine|reject)", rec, re.I)
    policy = m.group(1).lower() if m else "unparseable"
    status = {"reject": "enforcing", "quarantine": "enforcing",
              "none": "monitoring"}.get(policy, "invalid")
    return {"status": status, "policy": policy, "record": rec}


async def check_dkim(resolver, domain: str, extra_selector: Optional[str] = None) -> dict:
    """Probe common selectors. Absence of all probes != proof DKIM is absent."""
    selectors = list(DKIM_SELECTORS)
    if extra_selector and extra_selector not in selectors:
        selectors.insert(0, extra_selector)
    found = []

    async def probe(sel: str) -> Optional[str]:
        try:
            txts = await query_txt(resolver, sel + "._domainkey." + domain)
        except dns.exception.Timeout:
            return None
        if any("v=dkim1" in t.lower() or "k=rsa" in t.lower() for t in txts):
            return sel
        return None

    results = await asyncio.gather(*[probe(s) for s in selectors])
    found = [s for s in results if s]
    if found:
        return {"status": "found", "selectors": found}
    # honest evidence language: we can only say no common selector responded
    return {"status": "not_detected", "selectors": []}


async def check_mx(resolver, domain: str) -> dict:
    try:
        ans = await resolver.resolve(domain, "MX")
        hosts = sorted(str(rr.exchange).rstrip(".") for rr in ans)
        provider = infer_mail_provider(hosts)
        return {"status": "present", "hosts": hosts, "provider": provider}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return {"status": "missing", "hosts": [], "provider": None}


def infer_mail_provider(hosts: list) -> Optional[str]:
    joined = " ".join(hosts).lower()
    if "google" in joined:
        return "google_workspace"
    if "outlook" in joined or "protection.office" in joined:
        return "microsoft_365"
    if "secureserver" in joined:
        return "godaddy"
    if "zoho" in joined:
        return "zoho"
    return None


# ---------------------------------------------------------------- HTTP check

async def check_site(client: httpx.AsyncClient, domain: str) -> dict:
    """HEAD (fallback GET) against https:// then http://."""
    for scheme in ("https", "http"):
        url = scheme + "://" + domain + "/"
        try:
            t0 = time.monotonic()
            resp = await client.head(url, follow_redirects=True)
            if resp.status_code in (405, 501):  # some servers reject HEAD
                resp = await client.get(url, follow_redirects=True)
            ms = int((time.monotonic() - t0) * 1000)
            return {
                "up": resp.status_code < 500,
                "https": str(resp.url).startswith("https://"),
                "status_code": resp.status_code,
                "response_ms": ms,
                "final_url": str(resp.url),
            }
        except httpx.HTTPError:
            continue
    return {"up": False, "https": False, "status_code": None,
            "response_ms": None, "final_url": None}


# ---------------------------------------------------------------- scoring

def compute_score(email: dict, website: dict) -> tuple:
    """
    Quick-mode score out of 100, weighted toward email auth
    (the wire-fraud angle). This is a presence heartbeat,
    not the full 30-point audit report.
    """
    score = 0
    flags = []

    # SPF — 20
    spf = email["spf"]["status"]
    if spf == "pass":
        score += 20
    elif spf == "softfail":
        score += 15
    elif spf in ("weak", "no_all_mechanism"):
        score += 8
        flags.append("spf_weak")
    elif spf == "invalid_multiple":
        flags.append("spf_invalid_multiple")
    else:
        flags.append("spf_missing")

    # DKIM — 20 (probe-based, so absence is soft evidence)
    if email["dkim"]["status"] == "found":
        score += 20
    else:
        score += 5   # benefit of the doubt: selector may be nonstandard
        flags.append("dkim_not_detected")

    # DMARC — 30, the heavyweight
    dmarc = email["dmarc"]
    if dmarc["status"] == "enforcing":
        score += 30
    elif dmarc["status"] == "monitoring":
        score += 15
        flags.append("dmarc_not_enforcing")
    else:
        flags.append("dmarc_missing")

    # MX sanity — 5
    if email["mx"]["status"] == "present":
        score += 5
    else:
        flags.append("no_mx")

    # Website — 25
    if website["up"]:
        score += 15
        if website["https"]:
            score += 10
        else:
            flags.append("no_https")
        if website.get("response_ms") and website["response_ms"] > 3000:
            flags.append("slow_site")
    else:
        flags.append("site_down")

    return score, flags


# ---------------------------------------------------------------- per-domain

async def scan_domain(domain: str, company: str, dkim_selector: Optional[str],
                      sem: asyncio.Semaphore, client: httpx.AsyncClient,
                      prev: dict) -> dict:
    async with sem:
        resolver = make_resolver()
        entry = {
            "domain": domain,
            "company": company or None,
            "last_scanned": utcnow(),
            "error": None,
        }
        try:
            spf, dmarc, dkim, mx, site = await asyncio.wait_for(
                asyncio.gather(
                    check_spf(resolver, domain),
                    check_dmarc(resolver, domain),
                    check_dkim(resolver, domain, dkim_selector),
                    check_mx(resolver, domain),
                    check_site(client, domain),
                ),
                timeout=DOMAIN_TIMEOUT,
            )
            email = {"spf": spf, "dkim": dkim, "dmarc": dmarc, "mx": mx}
            score, flags = compute_score(email, site)
            entry.update({
                "score": score,
                "prev_score": prev.get("score"),
                "email": email,
                "website": site,
                "flags": flags,
                "report_url": prev.get("report_url"),  # preserve full-report link
            })
            if prev.get("score") is not None and prev["score"] - score >= SCORE_DROP_ALERT:
                entry["flags"].append("score_dropped")
        except asyncio.TimeoutError:
            entry["error"] = "timeout"
            # carry forward last known state rather than blanking the card
            for k in ("score", "email", "website", "flags", "report_url"):
                if k in prev:
                    entry[k] = prev[k]
            entry["prev_score"] = prev.get("prev_score")
        except Exception as e:  # one bad domain must not kill the run
            entry["error"] = ("%s: %s" % (type(e).__name__, e))[:200]
            entry["prev_score"] = prev.get("score")
        return entry


# ---------------------------------------------------------------- I/O

def load_targets(path: Path, limit: Optional[int]) -> list:
    """CSV with a 'domain' column (company / dkim_selector optional),
    or one domain per line."""
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        first_line = sample.splitlines()[0].lower() if sample.strip() else ""
        if "," in sample and "domain" in first_line:
            for row in csv.DictReader(f):
                lowered = {(k or "").strip().lower(): (v or "").strip()
                           for k, v in row.items()}
                d = lowered.get("domain", "")
                if d:
                    rows.append((normalize(d),
                                 lowered.get("company", ""),
                                 lowered.get("dkim_selector") or None))
        else:
            for line in f:
                d = line.strip().lower()
                if d and not d.startswith("#"):
                    rows.append((normalize(d), "", None))
    seen, out = set(), []
    for d, c, sel in rows:
        if d not in seen:
            seen.add(d)
            out.append((d, c, sel))
    return out[:limit] if limit else out


def normalize(domain: str) -> str:
    domain = re.sub(r"^https?://", "", domain.strip().lower())
    domain = domain.split("/")[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def load_previous(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return {d["domain"]: d for d in data.get("domains", [])}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


# ---------------------------------------------------------------- main

async def run(targets_path: Path, out_path: Path, limit: Optional[int]) -> int:
    t0 = time.monotonic()
    if not targets_path.exists():
        print("Targets file not found: %s" % targets_path, file=sys.stderr)
        return 1
    targets = load_targets(targets_path, limit)
    if not targets:
        print("No targets found in %s" % targets_path, file=sys.stderr)
        return 1
    prev = load_previous(out_path)
    print("Scanning %d domains (concurrency=%d)..." % (len(targets), CONCURRENCY))

    sem = asyncio.Semaphore(CONCURRENCY)
    headers = {"User-Agent":
               "NextGenIT-PresenceBot/1.0 (+https://nextgenitpros.com)"}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers=headers) as client:
        results = await asyncio.gather(*[
            scan_domain(d, c, sel, sem, client, prev.get(d, {}))
            for d, c, sel in targets
        ])

    results.sort(key=lambda r: (r.get("score") is None, -(r.get("score") or 0)))
    errors = [r for r in results if r.get("error")]
    duration = round(time.monotonic() - t0, 1)

    payload = {
        "generated_at": utcnow(),
        "pipeline": {
            "status": "degraded" if errors else "ok",
            "last_run_id": os.environ.get("GITHUB_RUN_ID"),
            "duration_sec": duration,
            "scanned": len(results),
            "errors": len(errors),
        },
        "domains": results,
    }
    atomic_write(out_path, payload)

    print("Done in %ss — %d domains, %d errors → %s"
          % (duration, len(results), len(errors), out_path))
    for r in errors:
        print("  ! %s: %s" % (r["domain"], r["error"]), file=sys.stderr)
    for r in results:
        if "score_dropped" in (r.get("flags") or []):
            print("  v %s: %s → %s" % (r["domain"], r["prev_score"], r["score"]))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Next-Gen-IT presence scanner")
    ap.add_argument("--targets", type=Path, default=Path("targets.csv"))
    ap.add_argument("--out", type=Path, default=Path("data/presence.json"))
    ap.add_argument("--limit", type=int, default=None,
                    help="scan only first N domains (smoke test)")
    args = ap.parse_args()
    sys.exit(asyncio.run(run(args.targets, args.out, args.limit)))


if __name__ == "__main__":
    main()
