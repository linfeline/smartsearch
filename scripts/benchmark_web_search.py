#!/usr/bin/env python3
import argparse
import asyncio
import json
import statistics
import time
from urllib.parse import urlparse

from smart_search import service


CASES = [
    ("OpenAI Responses API documentation", ["platform.openai.com"]),
    ("Python 3.14 what's new official documentation", ["docs.python.org"]),
    ("Kubernetes Gateway API official documentation", ["gateway-api.sigs.k8s.io"]),
    ("React 19.2 official release blog", ["react.dev"]),
    ("Rust Cargo book official documentation", ["doc.rust-lang.org"]),
    ("uv Python package manager GitHub repository", ["github.com"]),
    ("vLLM GitHub repository official", ["github.com"]),
    ("Model Context Protocol Python SDK GitHub", ["github.com"]),
    ("Cloudflare Workers pricing official", ["developers.cloudflare.com", "cloudflare.com"]),
    ("NVIDIA CUDA Toolkit release notes official", ["docs.nvidia.com"]),
    ("PostgreSQL 18 release notes official", ["postgresql.org"]),
    ("AWS Bedrock pricing official", ["aws.amazon.com"]),
    ("Stripe API idempotent requests documentation", ["docs.stripe.com"]),
    ("RFC 9110 HTTP Semantics", ["rfc-editor.org"]),
    ("NIST AI Risk Management Framework official", ["nist.gov"]),
    ("Federal Reserve FOMC meeting calendar 2026", ["federalreserve.gov"]),
    ("WHO mpox disease outbreak news latest", ["who.int"]),
    ("Tesla investor relations quarterly update 2026", ["ir.tesla.com"]),
    ("Apple security releases latest official", ["support.apple.com"]),
    ("GitHub Actions OIDC AWS official documentation", ["docs.github.com", "aws.amazon.com"]),
]


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def _matches(url: str, expected_domains: list[str]) -> bool:
    host = _host(url)
    return any(host == domain or host.endswith(f".{domain}") for domain in expected_domains)


def _score(results: list[dict], expected_domains: list[str]) -> dict:
    urls = [str(item.get("url") or "") for item in results if item.get("url")][:5]
    rank = next((index for index, url in enumerate(urls, 1) if _matches(url, expected_domains)), 0)
    return {
        "hit_at_5": bool(rank),
        "rank": rank,
        "rr": 1.0 / rank if rank else 0.0,
        "unique_domains_at_5": len({_host(url) for url in urls if _host(url)}),
        "urls": urls,
    }


async def _call_tavily(query: str, count: int) -> tuple[list[dict], float, str]:
    started = time.perf_counter()
    try:
        return (await service.call_tavily_search(query, count) or []), (time.perf_counter() - started) * 1000, ""
    except Exception as exc:
        return [], (time.perf_counter() - started) * 1000, f"{type(exc).__name__}: {exc}"


async def _call_keenable(query: str, count: int) -> tuple[list[dict], float, str]:
    started = time.perf_counter()
    try:
        data = await service.keenable_search(query, count=count)
        error = "" if data.get("ok") else f"{data.get('error_type', '')}: {data.get('error', '')}"
        return data.get("results") or [], (time.perf_counter() - started) * 1000, error
    except Exception as exc:
        return [], (time.perf_counter() - started) * 1000, f"{type(exc).__name__}: {exc}"


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _summary(rows: list[dict], provider: str) -> dict:
    items = [row[provider] for row in rows]
    successful = [item for item in items if not item["error"]]
    failed = [item for item in items if item["error"]]
    error_types: dict[str, int] = {}
    for item in failed:
        error_type = item["error"].split(":", 1)[0].strip() or "unknown"
        error_types[error_type] = error_types.get(error_type, 0) + 1
    latencies = [item["elapsed_ms"] for item in successful]
    return {
        "success_rate": round(len(successful) / len(items), 4),
        "failure_count": len(failed),
        "error_types": error_types,
        "hit_at_5_rate": round(sum(item["hit_at_5"] for item in items) / len(items), 4),
        "mrr_at_5": round(sum(item["rr"] for item in items) / len(items), 4),
        "rank1_rate": round(sum(item["rank"] == 1 for item in items) / len(items), 4),
        "avg_unique_domains_at_5": round(statistics.mean(item["unique_domains_at_5"] for item in items), 2),
        "latency_p50_ms": round(_percentile(latencies, 0.50), 2),
        "latency_p95_ms": round(_percentile(latencies, 0.95), 2),
    }


async def run(count: int) -> dict:
    rows = []
    for query, expected_domains in CASES:
        tavily_result, keenable_result = await asyncio.gather(
            _call_tavily(query, count),
            _call_keenable(query, count),
        )
        tavily_results, tavily_ms, tavily_error = tavily_result
        keenable_results, keenable_ms, keenable_error = keenable_result
        tavily_score = _score(tavily_results, expected_domains)
        keenable_score = _score(keenable_results, expected_domains)
        overlap = len(set(tavily_score["urls"]) & set(keenable_score["urls"]))
        rows.append(
            {
                "query": query,
                "expected_domains": expected_domains,
                "tavily": {**tavily_score, "elapsed_ms": round(tavily_ms, 2), "error": tavily_error},
                "keenable": {**keenable_score, "elapsed_ms": round(keenable_ms, 2), "error": keenable_error},
                "top5_url_overlap": overlap,
            }
        )
    summary = {
        "tavily": _summary(rows, "tavily"),
        "keenable": _summary(rows, "keenable"),
        "mean_top5_url_overlap": round(statistics.mean(row["top5_url_overlap"] for row in rows), 2),
        "cases": len(rows),
        "count_per_provider": count,
        "tavily_search_depth": "advanced",
        "keenable_search": "default REST search",
    }
    return {"summary": summary, "cases": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B benchmark Tavily Advanced vs Keenable Search on global web-search cases.")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--summary", action="store_true", help="Print only the aggregate summary.")
    args = parser.parse_args()
    result = asyncio.run(run(max(5, args.count)))
    print(json.dumps(result["summary"] if args.summary else result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
