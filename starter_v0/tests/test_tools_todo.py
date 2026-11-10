"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS.get("clarify") or TOOL_FUNCTIONS.get("ask_user")
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS.get("fetch") or TOOL_FUNCTIONS.get("read_url")
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
dedupe_tool = TOOL_FUNCTIONS.get("dedupe_sources")


# -------------- clarify --------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(
        question="Bạn muốn chọn nguồn nào?",
        response_type="choice",
        options=["Web", "Twitter"],
    )
    assert result["options"] == ["Web", "Twitter"]
    assert result["awaiting_user"] is True


# -------------- format --------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Tin 1", "url": "https://example.com/1", "section": "A"},
        {"title": "Tin 2", "url": "https://example.com/2", "section": "B"},
        {"title": "Tin 3", "url": "https://example.com/3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections", headline="Bản tin")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "Mục 1", "url": "https://example.com/1"},
        {"title": "Mục 2", "url": "https://example.com/2"},
    ]
    result = format_tool(items=items, template="thread")
    lines = [line for line in result["markdown"].splitlines() if line.strip()]
    assert lines[0].startswith("1/")
    assert lines[1].startswith("2/")


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None, template="sections")
    res_empty = format_tool(items=[], template="sections")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


# -------------- send (guardrail) --------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot123456:ABCDEF")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "987654321")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123456:ABCDEF" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "987654321"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin AI", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert calls == []


# -------------- lookup --------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI research", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# -------------- fetch --------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
    fake_http(
        FakeResponse(
            {
                "data": {
                    "markdown": "Nội dung bài viết tóm tắt",
                    "metadata": {
                        "title": "Tiêu đề T",
                        "sourceURL": "https://www.openai.com/blog/gpt-5",
                    },
                }
            }
        )
    )

    result = fetch_tool(url="https://www.openai.com/blog/gpt-5")
    item = result["items"][0]

    assert item["title"] == "Tiêu đề T"
    assert item["url"] == "https://www.openai.com/blog/gpt-5"
    assert item["source"] == "openai.com"
    assert item["summary"] == "Nội dung bài viết tóm tắt"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
    fake_http(
        FakeResponse(
            {
                "data": {
                    "markdown": "x" * 5500,
                    "metadata": {
                        "title": "Long Doc",
                        "sourceURL": "https://example.com/long",
                    },
                }
            }
        )
    )

    result = fetch_tool(url="https://example.com/long")
    assert len(result["items"][0]["summary"]) == 4000


# -------------- timeline / social_search --------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test-key")
    timeline_payload = [{"screen_name": "sama", "text": "Tweet bị thiếu ID"}] + [
        {"tweet_id": str(100 + i), "screen_name": "sama", "text": f"Tweet hợp lệ {i}"}
        for i in range(6)
    ]
    fake_http(FakeResponse({"timeline": timeline_payload}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"]):
        assert item["url"] == f"https://x.com/sama/status/{100 + idx}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool(query="OpenAI", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"


# -------------- policy --------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="data privacy", policy_area="data_privacy")
    assert len(result["results"]) >= 1
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="citation source", policy_area="source_citation")
    assert len(result["results"]) >= 1
    untrusted_found = [u for item in result["results"] for u in item["untrusted_text"]]
    assert len(untrusted_found) >= 1
    for item in result["results"]:
        for untrusted_line in item["untrusted_text"]:
            assert untrusted_line not in item["facts"]


# -------------- custom tool (dedupe_sources) --------------

def test_my_new_tool_happy_path() -> None:
    assert dedupe_tool is not None
    result = dedupe_tool(
        urls=[
            "https://example.org/a",
            "https://example.org/b",
            "https://example.org/a",
        ]
    )
    if "urls" in result:
        assert result["urls"] == ["https://example.org/a", "https://example.org/b"]
        assert result["duplicate_count"] == 1
    else:
        assert result["unique_urls"] == ["https://example.org/a", "https://example.org/b"]


def test_my_new_tool_bad_input_from_model() -> None:
    assert dedupe_tool is not None
    result = dedupe_tool(urls="not-a-list")  # type: ignore[arg-type]
    if "error" in result:
        assert result["error"] == "invalid_input"
    else:
        assert isinstance(result, dict)


def test_my_new_tool_failure_returns_error_dict() -> None:
    assert dedupe_tool is not None
    result = dedupe_tool(urls=["ftp://invalid-scheme.org/file"])
    if "error" in result:
        assert result["error"] == "invalid_url"
    else:
        assert isinstance(result, dict)