import pytest

from smart_search.sources import (
    sanitize_answer_text,
    split_answer_and_sources,
    merge_sources,
)


class TestSanitizeAnswerText:
    def test_removes_think_blocks(self):
        text = "<think>reasoning here</think>The actual answer."
        result = sanitize_answer_text(text)
        assert "think" not in result.lower()
        assert "The actual answer." in result

    def test_removes_nested_think_blocks(self):
        text = "Before<think>some\nmultiline\nthinking</think>After"
        result = sanitize_answer_text(text)
        assert result == "Before\n\nAfter" or "After" in result
        assert "thinking" not in result

    def test_removes_policy_blocks(self):
        text = "I cannot comply with that request.\n\nHere is the actual answer."
        result = sanitize_answer_text(text)
        assert "cannot comply" not in result
        assert "actual answer" in result

    def test_removes_chinese_policy_blocks(self):
        text = "我无法遵从这个请求。\n\n这是实际回答。"
        result = sanitize_answer_text(text)
        assert "无法遵从" not in result
        assert "实际回答" in result

    def test_preserves_normal_text(self):
        text = "This is a normal answer with no think blocks or policy text."
        result = sanitize_answer_text(text)
        assert result == text

    def test_empty_input(self):
        assert sanitize_answer_text("") == ""
        assert sanitize_answer_text(None) == ""

    def test_think_block_only(self):
        result = sanitize_answer_text("<think>only reasoning</think>")
        assert result == ""


class TestSplitAnswerAndSources:
    def test_no_sources(self):
        answer, sources = split_answer_and_sources("Just a plain answer.")
        assert answer == "Just a plain answer."
        assert sources == []

    def test_empty_input(self):
        answer, sources = split_answer_and_sources("")
        assert answer == ""
        assert sources == []

    def test_none_input(self):
        answer, sources = split_answer_and_sources(None)
        assert answer == ""
        assert sources == []

    def test_heading_sources(self):
        text = "Here is the answer.\n\n## Sources\n- [Example](https://example.com)\n- [Test](https://test.com)"
        answer, sources = split_answer_and_sources(text)
        assert "Here is the answer" in answer
        assert len(sources) >= 2
        urls = [s["url"] for s in sources]
        assert "https://example.com" in urls
        assert "https://test.com" in urls

    def test_function_call_sources(self):
        text = 'The answer is here.\n\nsources([{"url": "https://example.com", "title": "Ex"}])'
        answer, sources = split_answer_and_sources(text)
        assert "The answer is here" in answer
        assert len(sources) == 1
        assert sources[0]["url"] == "https://example.com"

    def test_inline_citation_sources_are_extracted_and_answer_keeps_links(self):
        text = "The answer cites [[1]](https://example.com/a) and [[2]](https://example.com/b)."
        answer, sources = split_answer_and_sources(text)
        assert answer == text
        assert [s["url"] for s in sources] == ["https://example.com/a", "https://example.com/b"]

    def test_inline_citation_sources_deduplicate_by_url(self):
        text = "A [[1]](https://example.com/a) and again [[2]](https://example.com/a)."
        answer, sources = split_answer_and_sources(text)
        assert answer == text
        assert len(sources) == 1
        assert sources[0]["url"] == "https://example.com/a"

    def test_inline_citations_merge_with_function_sources(self):
        text = 'A [[1]](https://example.com/a).\n\nsources([{"url": "https://example.com/a"}, {"url": "https://example.com/b"}])'
        answer, sources = split_answer_and_sources(text)
        assert "[[1]](https://example.com/a)" in answer
        assert [s["url"] for s in sources] == ["https://example.com/a", "https://example.com/b"]


class TestMergeSources:
    def test_deduplicates_by_url(self):
        a = [{"url": "https://a.com"}, {"url": "https://b.com"}]
        b = [{"url": "https://b.com"}, {"url": "https://c.com"}]
        merged = merge_sources(a, b)
        urls = [s["url"] for s in merged]
        assert urls == ["https://a.com", "https://b.com", "https://c.com"]

    def test_empty_inputs(self):
        assert merge_sources([], []) == []
        assert merge_sources(None, None) == []

    def test_skips_invalid_entries(self):
        sources = [{"url": ""}, {"url": None}, {}, {"url": "https://valid.com"}]
        merged = merge_sources(sources)
        assert len(merged) == 1
        assert merged[0]["url"] == "https://valid.com"

    def test_normalizes_markdown_and_cjk_url_artifacts(self):
        sources = [
            {"url": "https://react.dev/blog/2025/10/01/react-19-2](https://react.dev/blog/2025/10/01/react-19-2)"},
            {"url": "https://react.dev/blog/2025/10/01/react-19-2**"},
            {"url": "https://www.rfc-editor.org/rfc/rfc9110.html（可查看"},
        ]
        merged = merge_sources(sources)
        assert [item["url"] for item in merged] == [
            "https://react.dev/blog/2025/10/01/react-19-2",
            "https://www.rfc-editor.org/rfc/rfc9110.html",
        ]
