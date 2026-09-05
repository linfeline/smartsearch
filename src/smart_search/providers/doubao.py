import json
import time
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_random_exponential

from .base import BaseSearchProvider
from ..config import config
from ..logger import log_info
from ..provider_errors import ProviderCallError, classify_provider_exception


RETRYABLE_STATUS_CODES = {408, 500, 502, 503, 504}
DOUBAO_DEFAULT_API_URL = "https://open.feedcoopapi.com"
DOUBAO_SEARCH_PATH = "/search_api/web_search"
DOUBAO_MAX_QUERY_CHARS = 100
DOUBAO_MAX_WEB_COUNT = 50


def _is_retryable_exception(exc) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    return False


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _normalize_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _first_text(item, "Title", "title"),
        "url": _first_text(item, "Url", "url", "Link", "link"),
        "description": _first_text(item, "Summary", "summary", "Snippet", "snippet", "Content", "content"),
        "provider": "doubao",
        "source": _first_text(item, "SiteName", "site_name", "siteName", "HostName", "host_name"),
        "published_date": _first_text(item, "PublishTime", "publish_time", "published", "PublishDate"),
        "icon": _first_text(item, "LogoUrl", "logo_url", "LogoURL"),
    }


def _error_payload(exc: Exception, api_key: str = "") -> dict[str, Any]:
    error_type, error = classify_provider_exception(exc, additional_secrets=(api_key,))
    return {"error_type": error_type, "error": error}


def _api_error_message(data: dict[str, Any]) -> str:
    meta = data.get("ResponseMetadata") or data.get("ResponseMetaData") or {}
    err = meta.get("Error") if isinstance(meta, dict) else None
    if isinstance(err, dict) and (err.get("Code") or err.get("Message")):
        code = str(err.get("Code") or "").strip()
        message = str(err.get("Message") or "").strip()
        return f"{code}: {message}".strip(": ")
    code = data.get("code", data.get("Code"))
    if code not in (None, 0, "0", "Success", "success", ""):
        message = str(data.get("message") or data.get("Message") or "").strip()
        return f"{code}: {message}".strip(": ") if message else str(code)
    return ""


def _result_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[Any] = [data.get("Result"), data.get("result"), data.get("data"), data]
    for block in blocks:
        if isinstance(block, list):
            return [item for item in block if isinstance(item, dict)]
        if not isinstance(block, dict):
            continue
        for key in ("WebResults", "web_results", "ResultList", "result_list", "SearchResults", "results"):
            items = block.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
    return []


def _request_id(data: dict[str, Any]) -> str:
    meta = data.get("ResponseMetadata") or data.get("ResponseMetaData") or {}
    if isinstance(meta, dict):
        value = meta.get("RequestId") or meta.get("RequestID") or meta.get("request_id")
        if value:
            return str(value)
    return str(data.get("RequestId") or data.get("request_id") or "")


class DoubaoWebSearchProvider(BaseSearchProvider):
    def __init__(self, api_url: str, api_key: str, timeout: float = 30.0):
        super().__init__(api_url.rstrip("/"), api_key)
        self.timeout = timeout

    def get_provider_name(self) -> str:
        return "Doubao Search"

    async def search(
        self,
        query: str,
        count: int = 10,
        time_range: str = "",
        sites: str = "",
        auth_level: int = 0,
        need_content: bool = True,
        ctx=None,
    ) -> str:
        normalized_query = (query or "").strip()[:DOUBAO_MAX_QUERY_CHARS]
        endpoint = f"{self.api_url}{DOUBAO_SEARCH_PATH}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Traffic-Tag": "smart_search_doubao_search",
        }
        payload: dict[str, Any] = {
            "Query": normalized_query,
            "SearchType": "web",
            "Count": max(1, min(int(count or 10), DOUBAO_MAX_WEB_COUNT)),
        }
        filters: dict[str, Any] = {"NeedContent": bool(need_content), "NeedUrl": True}
        if int(auth_level or 0) == 1:
            filters["AuthInfoLevel"] = 1
        if sites.strip():
            filters["Sites"] = sites.strip()
        payload["Filter"] = filters
        if time_range.strip():
            payload["TimeRange"] = time_range.strip()

        await log_info(ctx, f"Doubao search: {normalized_query}", config.debug_enabled)
        start_time = time.time()
        try:
            if not normalized_query:
                raise ProviderCallError("parameter_error", "Query 不能为空")
            data = await self._request_with_retry(endpoint, headers, payload)
            api_error = _api_error_message(data)
            if api_error:
                raise ProviderCallError("provider_error", api_error, additional_secrets=(self.api_key,))
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            results = [_normalize_result(item) for item in _result_items(data)]
            output = {
                "ok": True,
                "query": query,
                "provider": "doubao",
                "search_engine": "doubao-search",
                "results": results,
                "total": len(results),
                "request_id": _request_id(data),
                "elapsed_ms": elapsed_ms,
            }
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            error = _error_payload(e, self.api_key)
            output = {
                "ok": False,
                "query": query,
                "provider": "doubao",
                "error_type": error["error_type"],
                "error": error["error"],
                "elapsed_ms": elapsed_ms,
            }
        return json.dumps(output, ensure_ascii=False, indent=2)

    async def _request_with_retry(self, endpoint: str, headers: dict, payload: dict) -> dict[str, Any]:
        timeout = httpx.Timeout(connect=6.0, read=self.timeout, write=10.0, pool=None)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(config.retry_max_attempts + 1),
                wait=wait_random_exponential(multiplier=config.retry_multiplier, max=config.retry_max_wait),
                retry=retry_if_exception(_is_retryable_exception),
                reraise=True,
            ):
                with attempt:
                    response = await client.post(endpoint, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()
        return {}
