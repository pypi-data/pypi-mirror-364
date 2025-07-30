import pytest
from agentwebsearch.webscraper.default import DefaultWebScraper
from agentwebsearch.webscraper.base import WebPageResult
from agentwebsearch.webscraper.base import BaseWebScraper


class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


@pytest.fixture
def scraper():
    return DefaultWebScraper()


def test_instanciate_default_webscraper_client():
    client = DefaultWebScraper()
    assert isinstance(client, DefaultWebScraper)
    assert hasattr(client, "scrape")
    assert callable(client.scrape)


def test_scrape_success(monkeypatch, scraper: BaseWebScraper):
    html = """
    <html>
        <body>
            <a href="http://example.com/page1">Link1</a>
            <a href="/file.pdf">PDF</a>
            <a href="nothttp">Invalid</a>
        </body>
    </html>
    """

    def dummy_get(url, timeout):
        return DummyResponse(html)

    monkeypatch.setattr("requests.get", dummy_get)
    result = scraper.scrape("http://example.com")
    assert isinstance(result, WebPageResult)
    assert result.url == "http://example.com"
    assert "Link1" in result.content
    assert "PDF" in result.content
    assert "http://example.com/page1" in result.links
    assert any(".pdf" in _ for _ in result.document_links)


def test_scrape_non_200(monkeypatch, scraper: BaseWebScraper):
    def dummy_get(url, timeout):
        return DummyResponse("", status_code=404)
    monkeypatch.setattr("requests.get", dummy_get)
    result = scraper.scrape("http://example.com")
    assert result.content is None
    assert result.links is None
    assert result.document_links is None


def test_scrape_exception(monkeypatch, scraper: BaseWebScraper):
    def dummy_get(url, timeout):
        raise Exception("Network error")

    monkeypatch.setattr("requests.get", dummy_get)
    result = scraper.scrape("http://example.com")
    assert result.content is None
    assert result.links is None
    assert result.document_links is None


def test_prepare_pdf_link_absolute(scraper: BaseWebScraper):
    url = "http://example.com/file.pdf"
    host_url = "http://example.com/"
    assert scraper._prepare_pdf_link(host_url, url) == url


def test_prepare_pdf_link_relative(scraper: BaseWebScraper):
    url = "/file.pdf"
    host_url = "http://example.com/"
    assert scraper._prepare_pdf_link(host_url, url) == "http://example.com//file.pdf"
