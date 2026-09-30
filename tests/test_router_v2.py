from smart_search.intent_router import build_rules_route


def test_url_summary_is_hard_fetch_primary():
    route = build_rules_route("总结 https://example.com/a")
    assert route.primary_capability == "web_fetch"
    assert route.hard_route is True
    assert "web_fetch" in route.required_capabilities


def test_docs_latest_has_docs_primary_and_web_supplement():
    route = build_rules_route("React 19 最新官方文档", validation_level="balanced")
    assert route.primary_capability == "docs_search"
    assert "web_search" in route.supplemental_capabilities


def test_current_web_is_primary_when_no_stronger_route():
    route = build_rules_route("今天国内 AI 新闻")
    assert route.primary_capability == "web_search"
