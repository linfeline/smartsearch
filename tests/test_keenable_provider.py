import json

import httpx
import pytest

from smart_search.providers.keenable import KeenableWebSearchProvider


@pytest.mark.asyncio
async def test_keenable_provider_normalizes_public_search_results(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            assert endpoint == "https://api.keenable.ai/v1/search/public"
            assert headers["X-Keenable-Title"] == "smart-search"
            assert "X-API-Key" not in headers
            assert json == {"query": "hello", "max_results": 10}
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "title": "Title",
                            "url": "https://example.com",
                            "description": "Description",
                            "snippet": "Snippet",
                            "acquired_at": "2026-09-01T00:00:00Z",
                        }
                    ]
                },
                request=httpx.Request("POST", endpoint),
            )

    monkeypatch.setattr("smart_search.providers.keenable.httpx.AsyncClient", FakeAsyncClient)
    provider = KeenableWebSearchProvider("https://api.keenable.ai/v1/search/public")

    data = json.loads(await provider.search("hello"))

    assert data["ok"] is True
    assert data["results"][0]["url"] == "https://example.com"
    assert data["results"][0]["provider"] == "keenable"
    assert data["results"][0]["published_date"] == "2026-09-01T00:00:00Z"


@pytest.mark.asyncio
async def test_keenable_provider_sends_x_api_key_when_configured(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            assert endpoint == "https://api.keenable.ai/v1/search"
            assert headers["X-API-Key"] == "secret"
            assert "X-Keenable-Title" not in headers
            return httpx.Response(200, json={"results": []}, request=httpx.Request("POST", endpoint))

    monkeypatch.setattr("smart_search.providers.keenable.httpx.AsyncClient", FakeAsyncClient)
    provider = KeenableWebSearchProvider("https://api.keenable.ai/v1/search/public", "secret")

    data = json.loads(await provider.search("hello"))

    assert data["ok"] is True
    assert data["results"] == []


@pytest.mark.asyncio
async def test_keenable_provider_reports_rate_limit(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            return httpx.Response(
                429,
                json={"error": "rate limited"},
                request=httpx.Request("POST", endpoint),
            )

    monkeypatch.setattr("smart_search.providers.keenable.httpx.AsyncClient", FakeAsyncClient)
    provider = KeenableWebSearchProvider("https://api.keenable.ai/v1/search/public")

    data = json.loads(await provider.search("hello"))

    assert data["ok"] is False
    assert data["error_type"] == "rate_limited"
