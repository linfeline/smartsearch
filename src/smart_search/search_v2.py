from __future__ import annotations

import asyncio
import time
from typing import Any

from .evidence import build_evidence_prompt, evidence_assessment, fuse_source_groups, mark_fetched


async def _run_docs_evidence(svc: Any, query: str, provider_order: list[str], fallback: str):
    attempts: list[dict[str, Any]] = []
    selected = provider_order[:1] if fallback == "off" else provider_order
    for provider in selected:
        started = time.time()
        if provider == "context7":
            data = await svc.context7_library(query, query)
            if data.get("ok"):
                candidate = svc._select_context7_library_candidate(data.get("results"), query)
                library_id = (candidate or {}).get("id", "")
                if library_id:
                    docs = await svc.context7_docs(library_id, query)
                    if docs.get("ok") and docs.get("content"):
                        attempts.append(svc._attempt("docs_search", "context7", "ok", started, result_count=1))
                        return [{
                            "url": f"context7:{library_id}",
                            "title": (candidate or {}).get("title") or library_id,
                            "description": str(docs.get("content") or "")[:1200],
                            "verified_content": str(docs.get("content") or ""),
                            "verified": True,
                        }], attempts
                attempts.append(svc._attempt("docs_search", "context7", "empty", started))
            else:
                attempts.append(svc._attempt(
                    "docs_search", "context7", svc._attempt_status_for_result(data), started,
                    error_type=data.get("error_type", ""), error=data.get("error", ""),
                ))
        elif provider == "exa":
            data = await svc.exa_search(query, num_results=5, include_highlights=True)
            if data.get("ok"):
                rows = svc._normalize_source_results(data.get("results"), "exa")
                attempts.append(svc._attempt("docs_search", "exa", "ok" if rows else "empty", started, result_count=len(rows)))
                if rows:
                    return rows, attempts
            else:
                attempts.append(svc._attempt(
                    "docs_search", "exa", svc._attempt_status_for_result(data), started,
                    error_type=data.get("error_type", ""), error=data.get("error", ""),
                ))
    return [], attempts


async def _run_web_hedged(
    svc: Any,
    query: str,
    provider_order: list[str],
    validation: str,
    fallback: str,
    count: int,
):
    providers = provider_order[:1] if fallback == "off" else provider_order[:2]
    if not providers:
        return [], [], []

    async def one(provider: str):
        return await svc._run_web_search_fallback(query, count=count, providers=provider, fallback="off")

    attempts: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    primary = asyncio.create_task(one(providers[0]))

    if validation == "fast" or len(providers) == 1:
        sources, local = await primary
        attempts.extend(local)
        if sources:
            groups.append({"provider": providers[0], "capability": "web_search", "query": query, "sources": sources})
        return sources, attempts, groups

    secondary = None
    if validation == "strict":
        secondary = asyncio.create_task(one(providers[1]))
    else:
        try:
            sources, local = await asyncio.wait_for(asyncio.shield(primary), timeout=0.8)
            attempts.extend(local)
            if sources:
                groups.append({"provider": providers[0], "capability": "web_search", "query": query, "sources": sources})
                return sources, attempts, groups
        except asyncio.TimeoutError:
            secondary = asyncio.create_task(one(providers[1]))

    tasks = [primary] + ([secondary] if secondary else [])
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)
    merged: list[dict[str, Any]] = []
    for provider, result in zip(providers, raw_results):
        if isinstance(result, BaseException):
            attempts.append(svc._attempt_from_exception("web_search", provider, time.time(), result))
            continue
        sources, local = result
        attempts.extend(local)
        if sources:
            merged.extend(sources)
            groups.append({"provider": provider, "capability": "web_search", "query": query, "sources": sources})
    return merged, attempts, groups


async def _synthesize(
    svc: Any,
    query: str,
    evidence: list[dict[str, Any]],
    assessment: dict[str, Any],
    configs: list[dict[str, Any]],
    fallback: str,
    budget: Any,
):
    prompt = build_evidence_prompt(query, evidence, assessment)
    attempts: list[dict[str, Any]] = []
    selected = configs if fallback != "off" else configs[:1]
    for raw_config in selected:
        candidate = dict(raw_config)
        candidate["tools"] = []
        candidate["stream"] = False
        provider = svc._main_search_providers([candidate], fallback="off")[0]
        started = time.time()
        try:
            raw = await asyncio.wait_for(provider.search(prompt, ""), timeout=max(0.001, budget.remaining_seconds()))
            text = raw if isinstance(raw, str) else str(raw)
            answer, _ = svc.split_answer_and_sources(text)
            if answer.strip():
                attempts.append(svc._attempt("synthesis", provider.get_provider_name(), "ok", started, result_count=1))
                return answer.strip(), attempts, candidate.get("provider", ""), candidate.get("model", "")
            attempts.append(svc._attempt("synthesis", provider.get_provider_name(), "empty", started))
        except Exception as exc:
            attempts.append(svc._attempt_from_exception("synthesis", provider.get_provider_name(), started, exc))

    fallback_items = [{
        "url": item.get("url", ""),
        "title": item.get("title", ""),
        "provider": ",".join(item.get("providers_seen") or []),
        "content": item.get("content") or item.get("snippet") or "",
    } for item in evidence[:5]]
    gaps = [{"subquestion_id": "", "reason": gap} for gap in assessment.get("gaps") or []]
    return svc._evidence_only_synthesis(query, fallback_items, gaps), attempts, "", ""


async def run_search_v2(
    query: str,
    platform: str = "",
    model: str = "",
    extra_sources: int = 0,
    validation: str = "",
    fallback: str = "",
    providers: str = "auto",
    stream: bool | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    from . import service as svc

    started = time.time()
    session_id = svc.new_session_id()
    try:
        effective_timeout = svc._resolve_search_timeout(timeout_seconds)
        budget = svc.SearchBudget(effective_timeout)
        execution = svc.SearchExecutionState(budget)
        validation_level = (validation or svc.config.validation_level).strip().lower()
        fallback_mode = (fallback or svc.config.fallback_mode).strip().lower()
        if validation_level not in svc.config._ALLOWED_VALIDATION_LEVELS:
            raise ValueError(f"Invalid validation level: {validation_level}")
        if fallback_mode not in svc.config._ALLOWED_FALLBACK_MODES:
            raise ValueError(f"Invalid fallback mode: {fallback_mode}")
    except ValueError as exc:
        return svc._empty_search_result(started, session_id, query, "parameter_error", str(exc), extra={"timeout_seconds": timeout_seconds})

    minimum = svc.validate_minimum_profile()
    if not minimum.get("ok"):
        return svc._empty_search_result(
            started, session_id, query, minimum.get("error_type", "config_error"),
            minimum.get("error", svc.MINIMUM_PROFILE_ERROR),
            extra={
                "capability_status": minimum.get("capability_status", {}),
                "minimum_profile_ok": False,
                "validation_level": validation_level,
                **execution.telemetry(),
            },
        )

    try:
        main_configs = svc._main_search_provider_configs(model_override=model, providers=providers)
    except ValueError as exc:
        return svc._empty_search_result(started, session_id, query, "parameter_error", str(exc), extra={"validation_level": validation_level, **execution.telemetry()})
    if not main_configs:
        return svc._empty_search_result(started, session_id, query, "config_error", "No configured main_search provider matches --providers.", extra={"validation_level": validation_level, **execution.telemetry()})

    router_started = time.monotonic()
    router = svc.IntentRouter(svc.config)
    try:
        route = await router.route(query, validation_level=validation_level, allow_remote=True)
    except Exception:
        route = await router.route(query, validation_level=validation_level, allow_remote=False)
        route.degraded = True
        route.degraded_reason = "remote router unavailable; using local rules"
    if not route.primary_capability:
        route.primary_capability = "web_search"
        if "web_search" not in route.required_capabilities:
            route.required_capabilities.append("web_search")
        route.query_plan.setdefault("web_search", [query])
    route.supplemental_capabilities = [cap for cap in route.required_capabilities if cap != route.primary_capability]
    route.supplemental_paths = list(route.required_capabilities)
    execution.record("router", "ok", router_started, min(svc.config.intent_router_timeout, effective_timeout), details={"primary_capability": route.primary_capability})

    routes = svc._research_capability_routes(
        query,
        {"intent_signals": dict(route.intent_signals)},
        fallback_mode,
        route_result=route,
    )
    planned = [route.primary_capability] + [cap for cap in route.supplemental_capabilities if cap != route.primary_capability]
    urls = svc._extract_urls(query)
    provider_attempts: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []

    async def run_capability(capability: str):
        if capability == "web_search":
            order = routes["capabilities"]["web_search"]["providers"]
            return await _run_web_hedged(svc, query, order, validation_level, fallback_mode, max(3, extra_sources or 5))
        if capability == "docs_search":
            order = routes["capabilities"]["docs_search"]["providers"]
            rows, attempts = await _run_docs_evidence(svc, query, order, fallback_mode)
            provider = attempts[-1].get("provider") if attempts else "docs"
            local = [{"provider": provider, "capability": capability, "query": query, "sources": rows}] if rows else []
            return rows, attempts, local
        if capability == "vertical_search":
            order = routes["capabilities"]["vertical_search"]["providers"]
            rows, attempts = await svc._run_vertical_search_fallback(
                query,
                providers=",".join(order) if order else "auto",
                fallback=fallback_mode,
            )
            provider = rows[0].get("provider") if rows else "anysearch"
            local = [{"provider": provider, "capability": capability, "query": query, "sources": rows}] if rows else []
            return rows, attempts, local
        if capability == "web_fetch":
            fetched = []
            attempts: list[dict[str, Any]] = []
            fetch_tasks = []
            for url in urls:
                fetch_tasks.append(asyncio.create_task(
                    svc._run_web_fetch_fallback(
                        url,
                        fallback=fallback_mode,
                        preferred_order=svc._research_fetch_order(query, url),
                    )
                ))
            for url, task in zip(urls, fetch_tasks):
                item, local = await task
                attempts.extend(local)
                if item:
                    fetched.append({
                        "url": item["url"], "title": item["url"],
                        "description": item["content"][:1200],
                        "verified_content": item["content"], "verified": True,
                    })
            local = [{"provider": "known-url-fetch", "capability": capability, "query": query, "sources": fetched}] if fetched else []
            return fetched, attempts, local
        return [], [], []

    retrieval_started = time.monotonic()
    task_results = await asyncio.gather(
        *(asyncio.create_task(run_capability(capability)) for capability in planned),
        return_exceptions=True,
    )
    for result in task_results:
        if isinstance(result, BaseException):
            continue
        _, attempts, local_groups = result
        provider_attempts.extend(attempts)
        groups.extend(local_groups)
    execution.record("retrieval", "ok", retrieval_started, max(0.0, budget.remaining_seconds()), details={"capabilities": planned})

    evidence = fuse_source_groups(groups)
    fetch_limit = 0 if validation_level == "fast" else (3 if validation_level == "strict" else 2)
    candidates = [
        item for item in evidence
        if not item.get("verified") and str(item.get("url") or "").startswith(("http://", "https://"))
    ][:fetch_limit]
    fetched_rows: list[dict[str, Any]] = []
    if candidates:
        fetch_started = time.monotonic()

        async def fetch_candidate(item: dict[str, Any]):
            data, attempts = await svc._run_web_fetch_fallback(
                str(item["url"]),
                fallback=fallback_mode,
                preferred_order=svc._research_fetch_order(query, str(item["url"])),
            )
            return item, data, attempts

        fetched = await asyncio.gather(*(fetch_candidate(item) for item in candidates), return_exceptions=True)
        for row in fetched:
            if isinstance(row, BaseException):
                continue
            original, data, attempts = row
            provider_attempts.extend(attempts)
            if data:
                fetched_rows.append({
                    "url": data["url"],
                    "title": original.get("title") or data["url"],
                    "content": data["content"],
                    "provider": data["provider"],
                })
        mark_fetched(evidence, fetched_rows)
        execution.record("fetch_evidence", "ok", fetch_started, max(0.0, budget.remaining_seconds()), details={"requested": len(candidates), "fetched": len(fetched_rows)})

    verification_query = any(token in query.lower() for token in ("核验", "验证", "真假", "verify", "fact check", "是否真的"))
    assessment = evidence_assessment(
        evidence,
        validation=validation_level,
        primary_capability=route.primary_capability,
        known_url=bool(urls),
        verification_query=verification_query,
    )

    sources = [{
        "url": item.get("url"), "title": item.get("title"),
        "provider": ",".join(item.get("providers_seen") or []),
        "verified": bool(item.get("verified")),
    } for item in evidence if item.get("url")]

    if validation_level == "strict" and not assessment.get("sufficient"):
        result = svc._empty_search_result(started, session_id, query, "evidence_error", "strict 模式证据不足")
        result.update({
            "routing_decision": {**route.to_dict(), "provider_routes": routes.get("capabilities", {})},
            "provider_attempts": provider_attempts,
            "providers_used": svc._provider_names_from_attempts(provider_attempts),
            "fallback_used": svc._fallback_used(provider_attempts),
            "validation_level": validation_level,
            "sources": sources,
            "sources_count": len(sources),
            "evidence_assessment": assessment,
            "minimum_profile_ok": minimum.get("ok", False),
            "capability_status": minimum.get("capability_status", {}),
            **execution.telemetry(partial_success=bool(evidence)),
            "elapsed_ms": svc._elapsed_ms(started),
        })
        return result

    synthesis_started = time.monotonic()
    answer, synth_attempts, synth_provider, effective_model = await _synthesize(
        svc, query, evidence, assessment, main_configs, fallback_mode, budget,
    )
    provider_attempts.extend(synth_attempts)
    execution.record("synthesis", "ok" if answer else "error", synthesis_started, max(0.0, budget.remaining_seconds()), details={"provider": synth_provider})

    primary_sources = [
        source for source in sources
        if next((item.get("capability") for item in evidence if item.get("url") == source.get("url")), "") == route.primary_capability
    ]
    extra_source_items = [source for source in sources if source not in primary_sources]
    ok = bool(answer and evidence)
    return {
        "ok": ok,
        "error_type": "" if ok else "evidence_error",
        "error": "" if ok else "search did not produce usable evidence",
        "session_id": session_id,
        "query": query,
        "platform": platform,
        "model": effective_model or (main_configs[0].get("model") or ""),
        "primary_api_mode": main_configs[0].get("mode", ""),
        "content": answer,
        "sources": sources,
        "sources_count": len(sources),
        "primary_sources": primary_sources,
        "primary_sources_count": len(primary_sources),
        "extra_sources": extra_source_items,
        "extra_sources_count": len(extra_source_items),
        "source_warning": "",
        "routing_decision": {**route.to_dict(), "provider_routes": routes.get("capabilities", {})},
        "retrieval": {
            "capabilities": planned,
            "evidence_count": len(evidence),
            "hedging_enabled": validation_level != "fast",
        },
        "evidence_assessment": assessment,
        "synthesis": {"provider": synth_provider, "grounded": True},
        "providers_used": svc._provider_names_from_attempts(provider_attempts),
        "provider_attempts": provider_attempts,
        "fallback_used": svc._fallback_used(provider_attempts),
        "transport_fallback_used": False,
        "model_fallback_used": False,
        "validation_level": validation_level,
        "minimum_profile_ok": minimum.get("ok", False),
        "capability_status": minimum.get("capability_status", {}),
        **execution.telemetry(partial_success=bool(evidence) and not ok),
        "elapsed_ms": svc._elapsed_ms(started),
    }
