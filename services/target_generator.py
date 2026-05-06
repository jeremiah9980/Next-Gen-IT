"""AI-driven target list generator for Next-Gen-IT outreach.

Builds a primary list of real estate companies in Central Texas and a
secondary list of smaller title companies in the same region. Uses the
Anthropic / OpenAI API when a key is configured; otherwise falls back to a
curated seed dataset so the component is always usable offline.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

CENTRAL_TEXAS_REGION = "Central Texas"
CENTRAL_TEXAS_CITIES: tuple[str, ...] = (
    "Austin",
    "Round Rock",
    "Cedar Park",
    "Pflugerville",
    "Georgetown",
    "Leander",
    "Hutto",
    "Buda",
    "Kyle",
    "San Marcos",
    "New Braunfels",
    "Bastrop",
    "Lakeway",
    "Dripping Springs",
    "Belton",
    "Temple",
    "Killeen",
    "Waco",
)


@dataclass
class Target:
    name: str
    category: str  # "real_estate" | "title_company"
    tier: str  # "primary" | "secondary"
    city: str
    state: str = "TX"
    region: str = CENTRAL_TEXAS_REGION
    domain: str | None = None
    website: str | None = None
    estimated_size: str | None = None  # "small" | "mid" | "large"
    notes: str | None = None
    source: str = "seed"

    def __post_init__(self) -> None:
        if self.domain and not self.website:
            self.website = f"https://{self.domain}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TargetList:
    generated_at: str
    region: str
    primary_targets: list[Target] = field(default_factory=list)
    secondary_targets: list[Target] = field(default_factory=list)
    model: str | None = None
    source: str = "seed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "region": self.region,
            "model": self.model,
            "source": self.source,
            "primary_targets": [t.to_dict() for t in self.primary_targets],
            "secondary_targets": [t.to_dict() for t in self.secondary_targets],
            "counts": {
                "primary": len(self.primary_targets),
                "secondary": len(self.secondary_targets),
            },
        }


# ── Seed data ────────────────────────────────────────────────────────────────
# Curated list of real, well-known Central Texas firms. The AI step enriches
# and expands on this baseline; if no API key is set, the seed list is
# returned directly so the feature is never empty.

SEED_REAL_ESTATE: list[Target] = [
    Target("Moreland Properties", "real_estate", "primary", "Austin",
           domain="moreland.com",
           estimated_size="mid",
           notes="Boutique luxury brokerage focused on Austin metro."),
    Target("Realty Austin", "real_estate", "primary", "Austin",
           domain="realtyaustin.com",
           estimated_size="large",
           notes="One of the largest independent brokerages in Central TX."),
    Target("Compass RE Texas - Austin", "real_estate", "primary", "Austin",
           domain="compass.com",
           estimated_size="large"),
    Target("Keller Williams Realty - Lake Travis", "real_estate", "primary",
           "Lakeway", domain="kw.com", estimated_size="mid"),
    Target("Den Property Group", "real_estate", "primary", "Austin",
           domain="denpg.com", estimated_size="small"),
    Target("Bramlett Residential", "real_estate", "primary", "Austin",
           domain="bramlettresidential.com", estimated_size="mid"),
    Target("Spyglass Realty", "real_estate", "primary", "Austin",
           domain="spyglassrealty.com", estimated_size="small"),
    Target("Twelve Rivers Realty", "real_estate", "primary", "Austin",
           domain="twelveriversrealty.com", estimated_size="small"),
    Target("Gottesman Residential Real Estate", "real_estate", "primary",
           "Austin", domain="gottesmanresidential.com", estimated_size="mid"),
    Target("Kuper Sotheby's International Realty - Austin", "real_estate",
           "primary", "Austin", domain="kuperrealty.com",
           estimated_size="mid"),
    Target("JBGoodwin REALTORS", "real_estate", "primary", "Austin",
           domain="jbgoodwin.com", estimated_size="mid"),
    Target("Dochen Realty Group", "real_estate", "primary", "Austin",
           domain="dochenrealtors.com", estimated_size="small"),
    Target("Reilly Realtors", "real_estate", "primary", "Austin",
           domain="reillyrealtors.com", estimated_size="small"),
    Target("Stanberry & Associates", "real_estate", "primary", "Austin",
           domain="stanberry.com", estimated_size="mid"),
    Target("All City Real Estate", "real_estate", "primary", "Round Rock",
           domain="allcityagents.com", estimated_size="mid"),
    Target("ERA Colonial Real Estate", "real_estate", "primary",
           "Georgetown", domain="eracolonial.com", estimated_size="mid"),
    Target("Magnolia Realty - Waco", "real_estate", "primary", "Waco",
           domain="magnoliarealty.com", estimated_size="mid"),
    Target("Camille Abbott Real Estate", "real_estate", "primary", "Waco",
           domain="camilleabbott.com", estimated_size="small"),
    Target("Coldwell Banker D'Ann Harper - New Braunfels", "real_estate",
           "primary", "New Braunfels", domain="cbharper.com",
           estimated_size="mid"),
    Target("Pure Realty", "real_estate", "primary", "Pflugerville",
           domain="purerealty.com", estimated_size="small"),
]

SEED_TITLE_COMPANIES: list[Target] = [
    Target("Independence Title", "title_company", "secondary", "Austin",
           domain="independencetitle.com", estimated_size="mid",
           notes="Strong Central TX footprint; often partners with indie brokers."),
    Target("Texas National Title", "title_company", "secondary", "Austin",
           domain="texasnationaltitle.com", estimated_size="mid"),
    Target("Capital Title of Texas - Austin", "title_company", "secondary",
           "Austin", domain="ctot.com", estimated_size="mid"),
    Target("Heritage Title Company of Austin", "title_company", "secondary",
           "Austin", domain="heritage-title.com", estimated_size="small"),
    Target("Patten Title Company", "title_company", "secondary", "Austin",
           domain="pattentitle.com", estimated_size="small"),
    Target("Gracy Title", "title_company", "secondary", "Austin",
           domain="gracytitle.com", estimated_size="mid"),
    Target("Longhorn Title Company", "title_company", "secondary",
           "Round Rock", domain="longhorntitle.com", estimated_size="small"),
    Target("Hill Country Title", "title_company", "secondary",
           "Dripping Springs", domain="hillcountrytitle.com",
           estimated_size="small"),
    Target("Texas Pride Title", "title_company", "secondary", "Buda",
           domain="texaspridetitle.com", estimated_size="small"),
    Target("Lone Star Title Company of El Paso d/b/a Lone Star Title",
           "title_company", "secondary", "Killeen",
           domain="lonestartitle.net", estimated_size="small"),
    Target("Bell County Title Company", "title_company", "secondary",
           "Belton", domain="bellcountytitle.com", estimated_size="small"),
    Target("Comal County Abstract & Title", "title_company", "secondary",
           "New Braunfels", domain="comalcountytitle.com",
           estimated_size="small"),
    Target("Hays County Abstract & Title", "title_company", "secondary",
           "San Marcos", domain="hayscountytitle.com",
           estimated_size="small"),
    Target("Bastrop County Abstract Co.", "title_company", "secondary",
           "Bastrop", estimated_size="small"),
    Target("First Texas Title", "title_company", "secondary", "Georgetown",
           domain="firsttexastitle.com", estimated_size="small"),
]


# ── Prompt construction ──────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a B2B sales-research assistant for Next-Gen IT, an MSP that "
    "sells managed IT and domain-health auditing to small real-estate "
    "operations and title companies. You produce structured JSON only — no "
    "prose. Only include companies that genuinely operate in Central Texas "
    "(Austin metro, Williamson, Hays, Travis, Bastrop, Comal, Bell, "
    "McLennan counties, etc). Never invent domains; leave domain null if "
    "unsure."
)


def _build_user_prompt(primary_count: int, secondary_count: int) -> str:
    cities = ", ".join(CENTRAL_TEXAS_CITIES)
    return (
        f"Build a target prospect list for Central Texas (cities include: "
        f"{cities}).\n\n"
        f"PRIMARY TARGETS: {primary_count} real-estate companies "
        "(brokerages, agencies, property-management firms). Prefer "
        "independent / boutique firms in the small-to-mid range — avoid "
        "national franchise mega-offices unless they're locally branded.\n\n"
        f"SECONDARY TARGETS: {secondary_count} SMALLER title companies "
        "operating in Central Texas. Smaller = independent or regional, "
        "not a national title underwriter HQ. Bias toward firms that "
        "would plausibly use an outside MSP.\n\n"
        "Return a single JSON object with this exact shape:\n"
        "{\n"
        '  "primary_targets": [\n'
        '    {"name": str, "city": str, "domain": str|null, '
        '"estimated_size": "small"|"mid"|"large", "notes": str}\n'
        "  ],\n"
        '  "secondary_targets": [\n'
        '    {"name": str, "city": str, "domain": str|null, '
        '"estimated_size": "small"|"mid"|"large", "notes": str}\n'
        "  ]\n"
        "}\n"
        "JSON only. No markdown, no commentary."
    )


# ── AI providers ─────────────────────────────────────────────────────────────

def _call_anthropic(primary_count: int, secondary_count: int) -> tuple[dict[str, Any], str] | None:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        logger.info("anthropic SDK not installed; skipping Anthropic provider")
        return None

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user",
                       "content": _build_user_prompt(primary_count, secondary_count)}],
        )
    except Exception as exc:
        logger.warning("Anthropic call failed: %s", exc)
        return None

    text = "".join(
        block.text for block in message.content if getattr(block, "type", "") == "text"
    ).strip()
    payload = _extract_json(text)
    if payload is None:
        logger.warning("Anthropic response was not valid JSON")
        return None
    return payload, model


def _call_openai(primary_count: int, secondary_count: int) -> tuple[dict[str, Any], str] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        logger.info("openai SDK not installed; skipping OpenAI provider")
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": _build_user_prompt(primary_count, secondary_count)},
            ],
        )
    except Exception as exc:
        logger.warning("OpenAI call failed: %s", exc)
        return None

    text = completion.choices[0].message.content or ""
    payload = _extract_json(text)
    if payload is None:
        logger.warning("OpenAI response was not valid JSON")
        return None
    return payload, model


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        # strip ```json fences if present
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
    return None


# ── Public API ───────────────────────────────────────────────────────────────

def _coerce_targets(
    items: Iterable[dict[str, Any]],
    *,
    category: str,
    tier: str,
    source: str,
) -> list[Target]:
    out: list[Target] = []
    for raw in items or []:
        name = (raw.get("name") or "").strip()
        if not name:
            continue
        city = (raw.get("city") or "").strip() or "Austin"
        domain = raw.get("domain")
        if isinstance(domain, str):
            domain = domain.strip().lower().lstrip("https://").lstrip("http://").rstrip("/") or None
        website = f"https://{domain}" if domain else None
        out.append(Target(
            name=name,
            category=category,
            tier=tier,
            city=city,
            domain=domain,
            website=website,
            estimated_size=(raw.get("estimated_size") or "").strip() or None,
            notes=(raw.get("notes") or "").strip() or None,
            source=source,
        ))
    return out


def generate_target_list(
    primary_count: int = 20,
    secondary_count: int = 15,
    *,
    use_ai: bool = True,
) -> TargetList:
    """Generate the AI-curated Central Texas target list.

    Falls back to a curated seed dataset if no API key is configured or the
    API call fails. The result is always populated.
    """
    generated_at = datetime.now(timezone.utc).isoformat()

    if use_ai:
        for provider in (_call_anthropic, _call_openai):
            result = provider(primary_count, secondary_count)
            if result is None:
                continue
            payload, model = result
            primary = _coerce_targets(
                payload.get("primary_targets", []),
                category="real_estate",
                tier="primary",
                source=f"ai:{model}",
            )
            secondary = _coerce_targets(
                payload.get("secondary_targets", []),
                category="title_company",
                tier="secondary",
                source=f"ai:{model}",
            )
            if primary or secondary:
                return TargetList(
                    generated_at=generated_at,
                    region=CENTRAL_TEXAS_REGION,
                    primary_targets=primary[:primary_count],
                    secondary_targets=secondary[:secondary_count],
                    model=model,
                    source="ai",
                )

    return TargetList(
        generated_at=generated_at,
        region=CENTRAL_TEXAS_REGION,
        primary_targets=SEED_REAL_ESTATE[:primary_count],
        secondary_targets=SEED_TITLE_COMPANIES[:secondary_count],
        model=None,
        source="seed",
    )


def save_target_list(target_list: TargetList, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = output_dir / f"central-tx-targets-{stamp}.json"
    path.write_text(json.dumps(target_list.to_dict(), indent=2))
    return path
