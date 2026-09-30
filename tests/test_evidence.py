from smart_search.evidence import canonicalize_url, evidence_assessment, fuse_source_groups


def test_canonicalize_url_removes_tracking_but_keeps_semantic_query():
    assert canonicalize_url("https://Example.com/a?id=7&utm_source=x#part") == "https://example.com/a?id=7"


def test_rrf_rewards_cross_provider_agreement():
    rows = fuse_source_groups([
        {"provider": "a", "capability": "web_search", "query": "q", "sources": [
            {"url": "https://x.test/a"}, {"url": "https://x.test/b"}
        ]},
        {"provider": "b", "capability": "web_search", "query": "q", "sources": [
            {"url": "https://x.test/b"}, {"url": "https://x.test/c"}
        ]},
    ])
    assert rows[0]["url"] == "https://x.test/b"
    assert set(rows[0]["providers_seen"]) == {"a", "b"}


def test_strict_does_not_accept_unfetched_urls():
    assessment = evidence_assessment(
        [{"url": "https://a.test/x", "verified": False, "content": "", "capability": "web_search"}],
        validation="strict",
        primary_capability="web_search",
        known_url=False,
        verification_query=True,
    )
    assert assessment["sufficient"] is False
