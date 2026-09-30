from __future__ import annotations

from collections import defaultdict
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .url_utils import normalize_extracted_url

_TRACKING_KEYS = {"gclid", "fbclid", "mc_cid", "mc_eid"}


def canonicalize_url(url: str) -> str:
    value = normalize_extracted_url(url)
    if not value or not value.startswith(("http://", "https://")):
        return value
    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        host = (parsed.hostname or "").lower()
        if not host:
            return value
        port = parsed.port
        netloc = host
        if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            netloc = f"{host}:{port}"
        query = []
        for key, item in parse_qsl(parsed.query, keep_blank_values=True):
            lower = key.lower()
            if lower.startswith("utm_") or lower in _TRACKING_KEYS:
                continue
            query.append((key, item))
        return urlunsplit((scheme, netloc, parsed.path or "/", urlencode(query, doseq=True), ""))
    except (TypeError, ValueError):
        return value


def fuse_source_groups(groups: list[dict[str, Any]], *, k: int = 60) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    scores: defaultdict[str, float] = defaultdict(float)
    for group in groups:
        provider = str(group.get("provider") or "")
        capability = str(group.get("capability") or "")
        query = str(group.get("query") or "")
        for rank, raw in enumerate(group.get("sources") or [], start=1):
            if not isinstance(raw, dict):
                continue
            url = str(raw.get("url") or "").strip()
            if not url:
                continue
            key = canonicalize_url(url) or url
            scores[key] += 1.0 / (k + rank)
            item = fused.get(key)
            if item is None:
                item = {
                    "url": url,
                    "canonical_url": canonicalize_url(url),
                    "title": str(raw.get("title") or url),
                    "snippet": str(raw.get("description") or raw.get("snippet") or raw.get("content") or ""),
                    "content": str(raw.get("verified_content") or ""),
                    "verified": bool(raw.get("verified") or raw.get("verified_content")),
                    "capability": capability,
                    "retrieval_query": query,
                    "providers_seen": [],
                    "provider_ranks": {},
                    "published_date": raw.get("published_date") or "",
                }
                fused[key] = item
            if provider and provider not in item["providers_seen"]:
                item["providers_seen"].append(provider)
            if provider:
                item["provider_ranks"][provider] = rank
            if raw.get("verified_content"):
                item["content"] = str(raw["verified_content"])
                item["verified"] = True
                item["capability"] = capability or item["capability"]
    ranked = []
    for key, item in fused.items():
        item["rrf_score"] = scores[key]
        agreement = max(0, len(item["providers_seen"]) - 1)
        item["final_score"] = scores[key] * (1.0 + min(agreement, 2) * 0.15)
        ranked.append(item)
    ranked.sort(key=lambda row: row["final_score"], reverse=True)
    return ranked


def mark_fetched(evidence: list[dict[str, Any]], fetched: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {canonicalize_url(str(item.get("url") or "")): item for item in evidence}
    for item in fetched:
        url = str(item.get("url") or "")
        key = canonicalize_url(url)
        target = by_key.get(key)
        if target is None:
            target = {
                "url": url, "canonical_url": key, "title": str(item.get("title") or url),
                "snippet": "", "content": "", "verified": False, "capability": "web_fetch",
                "retrieval_query": "", "providers_seen": [], "provider_ranks": {},
                "published_date": "", "rrf_score": 0.0, "final_score": 0.0,
            }
            evidence.append(target)
            by_key[key] = target
        content = str(item.get("content") or "")
        if content.strip():
            target["content"] = content
            target["verified"] = True
        provider = str(item.get("provider") or "")
        if provider and provider not in target["providers_seen"]:
            target["providers_seen"].append(provider)
    return evidence


def evidence_assessment(
    evidence: list[dict[str, Any]],
    *,
    validation: str,
    primary_capability: str,
    known_url: bool,
    verification_query: bool,
) -> dict[str, Any]:
    verified = [item for item in evidence if item.get("verified") and str(item.get("content") or "").strip()]
    domains = set()
    for item in verified:
        url = str(item.get("url") or "")
        if url.startswith(("http://", "https://")):
            domains.add((urlsplit(url).hostname or "").lower())
        elif url.startswith("context7:"):
            domains.add("context7")
    authoritative = sum(
        1 for item in verified
        if item.get("capability") == "docs_search" or str(item.get("url") or "").startswith("context7:")
    )
    if validation == "fast":
        sufficient = bool(evidence)
    elif known_url:
        sufficient = bool(verified)
    elif primary_capability == "docs_search":
        sufficient = authoritative >= 1 or len(verified) >= 1
    elif validation == "strict" and verification_query:
        sufficient = len(domains) >= 2 or authoritative >= 1
    elif validation == "strict":
        sufficient = len(verified) >= 1 and (authoritative >= 1 or len(domains) >= 2)
    else:
        sufficient = bool(verified) or len(evidence) >= 2
    return {
        "sufficient": bool(sufficient),
        "useful_sources": len(evidence),
        "fetched_count": len(verified),
        "independent_domains": len(domains),
        "authoritative_count": authoritative,
        "coverage_score": round(min(1.0, len(verified) * 0.35 + len(domains) * 0.2 + authoritative * 0.25), 3),
        "gaps": [] if sufficient else ["insufficient verified evidence for selected validation level"],
    }


def build_evidence_prompt(
    query: str,
    evidence: list[dict[str, Any]],
    assessment: dict[str, Any],
    *,
    max_items: int = 8,
) -> str:
    lines = [
        "Answer the user using ONLY the evidence supplied below.",
        "Do not browse, search, or add unsupported factual claims.",
        "If evidence is insufficient for part of the question, state that limitation explicitly.",
        "Use concise Markdown and cite supporting evidence inline as [E1], [E2], etc.",
        "",
        f"User question: {query}",
        "",
        "Evidence:",
    ]
    for index, item in enumerate(evidence[:max_items], start=1):
        content = str(item.get("content") or item.get("snippet") or "").strip()
        lines.extend([
            f"[E{index}]",
            f"Title: {item.get('title') or item.get('url')}",
            f"URL: {item.get('url')}",
            f"Verified: {bool(item.get('verified'))}",
            f"Content: {content[:5000]}",
            "",
        ])
    if not assessment.get("sufficient"):
        lines.append("Evidence assessment reports gaps; do not hide them.")
    return "\n".join(lines).strip()
