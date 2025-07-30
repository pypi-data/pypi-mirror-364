import pytest

from agentwebsearch.webscraper.base import BaseWebScraper, WebPageResult


def test_webpageresult_fields():
    result = WebPageResult(
        url="http://example.com",
        content="Testinhalt",
        links=["http://example.com/a", "http://example.com/b"],
        document_links=["http://example.com/file.pdf"]
    )
    assert result.url == "http://example.com"
    assert result.content == "Testinhalt"
    assert result.links == ["http://example.com/a", "http://example.com/b"]
    assert result.document_links == ["http://example.com/file.pdf"]


def test_webpageresult_defaults_none_content():
    result = WebPageResult(
        url="http://example.com",
        content=None,
        links=[],
        document_links=[]
    )
    assert result.content is None
    assert result.links == []
    assert result.document_links == []


def test_scrape_implemented_runs_without_error():
    class DummyScraper(BaseWebScraper):
        def scrape(self, url: str) -> WebPageResult:
            return WebPageResult(url, "content", [], [])
    scraper = DummyScraper()
    result = scraper.scrape("http://example.com")
    assert isinstance(result, WebPageResult)
    assert result.url == "http://example.com"


def test_missing_scrape_raises_typeerror():
    class NoScrape(BaseWebScraper):
        pass
    with pytest.raises(TypeError):
        NoScrape()
