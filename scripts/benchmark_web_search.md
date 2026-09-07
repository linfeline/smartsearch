# Tavily vs Keenable Web Search Benchmark

Date: 2026-09-06

Command:

```bash
PYTHONPATH=src .venv/bin/python scripts/benchmark_web_search.py --runs 3 --summary
```

Scope: 20 global web-search queries, 10 results/provider, three repeated runs (60 paired query cases). Tavily uses `search_depth=advanced`; Keenable uses the documented default REST Search API. The query set emphasizes official documentation, GitHub/open-source discovery, standards, company sources, and current authoritative sources. Hit/MRR scoring uses the expected authoritative domain; the three GitHub repository cases additionally require the expected repository URL path rather than accepting any `github.com` result.

| Metric | Tavily | Keenable |
| --- | ---: | ---: |
| Success rate | 100% | 100% |
| Hit@5 | 85% | 100% |
| MRR@5 | 0.5558 | 0.8833 |
| Rank-1 hit rate | 40% | 80% |
| Avg. unique domains@5 | 3.75 | 3.40 |
| P50 latency | 935–950 ms | 820–837 ms |
| P95 latency | 1,028–1,218 ms | 872–1,115 ms |
| Mean Top-5 URL overlap | \- | 0.35 URLs/query |

Decision: use **Keenable as the broad/global research/supplemental `web_search` primary** and keep **Tavily as same-capability fallback**. Preserve Doubao/Zhipu ahead of both for Chinese/current/locale routing, keep the explicit `search --extra-sources` diversification path independent, and keep Tavily's `web_fetch` / `site_map` roles.

This is a project-specific routing benchmark, not a universal search-engine ranking. Re-run it when provider APIs, pricing, query mix, or routing requirements materially change.
