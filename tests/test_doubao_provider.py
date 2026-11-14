import json

import httpx
import pytest

from smart_search.providers.doubao import DoubaoWebSearchProvider


@pytest.mark.asyncio
async def test_doubao_provider_normalizes_search_results(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            assert endpoint == "https://open.feedcoopapi.com/search_api/web_search"
            assert headers["Authorization"] == "Bearer key"
            assert json["Query"] == "hello"
            assert json["SearchType"] == "web"
            assert json["Filter"]["NeedUrl"] is True
            return httpx.Response(
                200,
                json={
                    "ResponseMetadata": {"RequestId": "r1"},
                    "Result": {
                        "WebResults": [
                            {
                                "Title": "Title",
                                "Snippet": "Snippet",
                                "Url": "https://example.com",
                                "SiteName": "Example",
                                "PublishTime": "2026-05-12",
                            }
                        ]
                    },
                },
                request=httpx.Request("POST", endpoint),
            )

    monkeypatch.setattr("smart_search.providers.doubao.httpx.AsyncClient", FakeAsyncClient)
    provider = DoubaoWebSearchProvider("https://open.feedcoopapi.com", "key")

    data = json.loads(await provider.search("hello"))

    assert data["ok"] is True
    assert data["results"][0]["url"] == "https://example.com"
    assert data["results"][0]["provider"] == "doubao"
    assert data["request_id"] == "r1"


@pytest.mark.asyncio
async def test_doubao_provider_reports_api_error_without_retry(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            calls.append(endpoint)
            return httpx.Response(
                200,
                json={"ResponseMetadata": {"Error": {"Code": "QuotaExceeded", "Message": "monthly quota"}}},
                request=httpx.Request("POST", endpoint),
            )

    monkeypatch.setattr("smart_search.providers.doubao.httpx.AsyncClient", FakeAsyncClient)
    provider = DoubaoWebSearchProvider("https://open.feedcoopapi.com", "key")

    data = json.loads(await provider.search("test"))

    assert data["ok"] is False
    assert data["error_type"] == "provider_error"
    assert "QuotaExceeded" in data["error"]
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_doubao_provider_reports_rate_limit_without_retry(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, timeout, follow_redirects=True):
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, endpoint, headers, json):
            calls.append(endpoint)
            return httpx.Response(
                429,
                json={"error": "rate limited"},
                request=httpx.Request("POST", endpoint),
            )

    monkeypatch.setattr("smart_search.providers.doubao.httpx.AsyncClient", FakeAsyncClient)
    provider = DoubaoWebSearchProvider("https://open.feedcoopapi.com", "key")

    data = json.loads(await provider.search("test"))

    assert data["ok"] is False
    assert data["error_type"] == "rate_limited"
    assert len(calls) == 1
