import json
import time
from typing import Any

import httpx

from .base import BaseSearchProvider
from ..provider_errors import ProviderCallError, classify_provider_exception


KEENABLE_DEFAULT_API_URL = "https://api.keenable.ai/v1/search"
KEENABLE_DEFAULT_TITLE = "smart-search"


def _normalize_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(item.get("title") or "").strip(),
        "url": str(item.get("url") or "").strip(),
        "description": str(item.get("description") or item.get("snippet") or "").strip(),
        "provider": "keenable",
        "published_date": str(item.get("published_at") or item.get("published_date") or item.get("acquired_at") or "").strip(),
    }


class KeenableWebSearchProvider(BaseSearchProvider):
    def __init__(self, api_url: str, api_key: str = "", timeout: float = 30.0, title: str = KEENABLE_DEFAULT_TITLE):
        super().__init__(api_url.rstrip("/"), api_key)
        self.timeout = timeout
        self.title = title or KEENABLE_DEFAULT_TITLE

    def get_provider_name(self) -> str:
        return "Keenable Search"

    async def search(self, query: str, count: int = 10, ctx=None) -> str:
        normalized_query = (query or "").strip()
        started = time.time()
        try:
            if not normalized_query:
                raise ProviderCallError("parameter_error", "Query cannot be empty")
            max_results = max(1, min(int(count or 10), 50))
            endpoint = self.api_url
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if self.api_key:
                headers["X-API-Key"] = self.api_key
                if endpoint.endswith("/public"):
                    endpoint = endpoint[: -len("/public")]
            else:
                headers["X-Keenable-Title"] = self.title
                if not endpoint.endswith("/public"):
                    endpoint = f"{endpoint}/public"
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.post(endpoint, headers=headers, json={"query": normalized_query, "max_results": max_results})
                response.raise_for_status()
                data = response.json()
            results = data.get("results")
            if not isinstance(results, list):
                raise ProviderCallError("parse_error", "Keenable search response is missing results")
            normalized = [_normalize_result(item) for item in results[: max(1, int(count or 10))] if isinstance(item, dict)]
            output = {
                "ok": True,
                "query": query,
                "provider": "keenable",
                "search_engine": "keenable-search",
                "results": normalized,
                "total": len(normalized),
                "elapsed_ms": round((time.time() - started) * 1000, 2),
            }
        except Exception as exc:
            error_type, error = classify_provider_exception(exc, additional_secrets=(self.api_key,))
            output = {
                "ok": False,
                "query": query,
                "provider": "keenable",
                "error_type": error_type,
                "error": error,
                "elapsed_ms": round((time.time() - started) * 1000, 2),
            }
        return json.dumps(output, ensure_ascii=False, indent=2)
