"""Guard the fork's two search providers on the upstream Jev engine."""

import pytest

from smart_search import service
from smart_search.jev_search import ChannelExecutor, available_channels, fallback_channels


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,config,method", [
    ("doubao", {"DOUBAO_SEARCH_API_KEY": "doubao-test"}, "doubao_search"),
    ("keenable", {"KEENABLE_API_KEY": "keenable-test", "KEENABLE_ENABLED": "true"}, "keenable_search"),
])
async def test_fork_provider_executes_through_upstream_channel(monkeypatch, provider, config, method):
    for key, value in config.items():
        monkeypatch.setenv(key, value)
    calls = []

    async def fake_search(query, count=5):
        calls.append((query, count))
        return {"ok": True, "results": [{
            "url": f"https://{provider}.example.com/result", "title": provider,
            "content": "relevant result",
        }]}

    monkeypatch.setattr(service, method, fake_search)
    channels = available_channels(service, "最新新闻", [], providers=provider)
    assert len(channels) == 1
    assert channels[0]["provider"] == provider
    executor = ChannelExecutor(service, None, count=3)
    results = await executor.execute(channels[0], "最新新闻")
    assert calls == [("最新新闻", 3)]
    assert results and results[0]["url"] == f"https://{provider}.example.com/result"


def test_chinese_web_fallback_keeps_doubao_first(monkeypatch):
    monkeypatch.setenv("DOUBAO_SEARCH_API_KEY", "doubao-test")
    monkeypatch.setenv("ZHIPU_API_KEY", "zhipu-test")
    monkeypatch.setenv("KEENABLE_API_KEY", "keenable-test")
    monkeypatch.setenv("KEENABLE_ENABLED", "true")
    candidates = available_channels(service, "今天中国政策新闻", [])
    selected = fallback_channels(service, "今天中国政策新闻", candidates, limit=3)
    assert selected
    assert selected[0]["provider"] == "doubao"
