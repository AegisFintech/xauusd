import pytest

from xauusd.firecrawl_research import FirecrawlConfig, FirecrawlResearchClient, InMemorySourceStore, firecrawl_fetch_tool


def client(store, content="# Gold update"):
    return FirecrawlResearchClient(FirecrawlConfig("not-a-real-key", ("reuters.com",), max_content_chars=20), store,
                                   transport=lambda payload, timeout: {"data": {"markdown": content}})


def test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance():
    store = InMemorySourceStore(); result = client(store).fetch("https://www.reuters.com/world/?topic=gold")
    assert result["source_url"] == "https://www.reuters.com/world/?topic=gold"
    assert result["trust"] == "untrusted_external_content" and len(result["content_digest"]) == 64
    assert store.records[0]["content_digest"] == result["content_digest"]


@pytest.mark.parametrize("url", ["http://reuters.com/news", "https://evil.example/news", "https://key@reuters.com/news", "https://reuters.com/news?api_key=x"])
def test_firecrawl_rejects_unscoped_or_sensitive_source_urls(url):
    with pytest.raises(ValueError): client(InMemorySourceStore()).fetch(url)


def test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit():
    store = InMemorySourceStore(); tool = firecrawl_fetch_tool(client(store, "x" * 100))
    result = tool.handler({"url": "https://reuters.com/markets"})
    assert result["trust"] == "untrusted_external_content" and len(result["content"]) == 20
