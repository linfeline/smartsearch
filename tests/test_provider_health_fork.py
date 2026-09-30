from pathlib import Path

from smart_search import service
from smart_search.provider_health import ProviderHealthStore, provider_fingerprint


def test_hard_failure_cools_down_and_rekey_recovers(monkeypatch, tmp_path: Path):
    store = ProviderHealthStore(tmp_path / "health.json", cooldown_seconds=60, failure_threshold=2)
    monkeypatch.setattr(service, "provider_health", store)
    monkeypatch.setenv("KEENABLE_API_KEY", "bad-key")
    monkeypatch.setenv("KEENABLE_API_URL", "https://search.keenable.ai")
    first = service._record_provider_result("keenable", "error", "auth_error", "bad credential")
    assert first["provider_health"]["state"] == "cooldown"
    runnable, skipped = service._plan_provider_health("web_search", ["keenable", "tavily"])
    assert "keenable" not in runnable
    assert skipped and skipped[0]["provider"] == "keenable"
    old = service._provider_fingerprint("keenable")
    monkeypatch.setenv("KEENABLE_API_KEY", "fixed-key")
    assert service._provider_fingerprint("keenable") != old
    assert service._provider_health_status("keenable")["state"] == "closed"


def test_soft_failure_needs_threshold(monkeypatch, tmp_path: Path):
    store = ProviderHealthStore(tmp_path / "health.json", cooldown_seconds=60, failure_threshold=2)
    monkeypatch.setattr(service, "provider_health", store)
    monkeypatch.setenv("DOUBAO_SEARCH_API_KEY", "db-key")
    monkeypatch.setenv("DOUBAO_SEARCH_API_URL", "https://example.invalid")
    service._record_provider_result("doubao", "error", "timeout", "slow")
    assert service._provider_health_status("doubao")["state"] == "closed"
    second = service._record_provider_result("doubao", "error", "timeout", "slow again")
    assert second["provider_health"]["state"] == "cooldown"


def test_fingerprint_stable_and_non_reversible():
    one = provider_fingerprint("secret", "https://example.com")
    two = provider_fingerprint("secret", "https://example.com")
    other = provider_fingerprint("secret-2", "https://example.com")
    assert one == two
    assert one != other
    assert "secret" not in one
