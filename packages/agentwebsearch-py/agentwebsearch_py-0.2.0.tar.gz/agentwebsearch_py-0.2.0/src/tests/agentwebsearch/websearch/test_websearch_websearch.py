import pytest
from agentwebsearch.websearch.websearch import AgentWebSearch
from agentwebsearch.search.client.base import SearchResult
from agentwebsearch.webscraper.base import WebPageResult
from agentwebsearch.websearch.response import ResponseReference


class DummyEmbeddingModel:
    def model_name(self): return "text-embedding-3-large"


@pytest.fixture
def agent():
    # Minimal AgentWebSearch für die privaten Methoden
    return AgentWebSearch(
        embedding_model=DummyEmbeddingModel(),
        llm=None
    )


def test_create_init_response_references(agent):
    results = [
        SearchResult(url="http://example.com", title="T1", description="D1"),
        SearchResult(url="http://example.org", title="T2", description="D2"),
    ]
    refs = agent._create_init_response_references(results)
    assert isinstance(refs, dict)
    assert "http://example.com" in refs
    assert "http://example.org" in refs
    assert isinstance(refs["http://example.com"], ResponseReference)
    assert refs["http://example.com"].title == "T1"
    assert refs["http://example.com"].description == "D1"
    assert refs["http://example.com"].document_links == []


def test_prepare_page_results(agent):
    pages = [
        WebPageResult(
            url="http://example.com",
            content="Dies ist ein Testinhalt.",
            links=[],
            document_links=[]
        ),
        WebPageResult(
            url="http://example.org",
            content=None,
            links=[],
            document_links=[]
        ),
    ]
    prep_results, pages_text_chunks, err_urls = agent._prepare_page_results(pages)
    assert isinstance(prep_results, list)
    assert isinstance(pages_text_chunks, list)
    assert isinstance(err_urls, list)
    assert len(prep_results) == 1
    assert prep_results[0].url == "http://example.com"
    assert len(pages_text_chunks) == 1
    assert isinstance(pages_text_chunks[0], list)
    assert err_urls
