import pytest
from agentwebsearch.search.client.base import BaseSearchClient, SearchResult


def test_searchresult_fields():
    result = SearchResult(
        url="http://example.com/page1",
        title="Example Title",
        description="Example Description"
    )
    assert result.url == "http://example.com/page1"
    assert result.title == "Example Title"
    assert result.description == "Example Description"


def test_searchresult_defaults():
    result = SearchResult(url="http://example.com/page2")
    assert result.url == "http://example.com/page2"
    assert result.title is None
    assert result.description is None


class DummySearchClient(BaseSearchClient):
    def search(self, queries, max_count):
        return [
            SearchResult(url="http://example.com/page1"),
            SearchResult(url="http://example.com/page2"),
            SearchResult(url="http://example.com/page1"),  # duplicate path
            SearchResult(url="https://www.google.com/search?q=test"),
            SearchResult(url="http://example.com/file.pdf"),
        ]


def test_search_implemented_runs_without_error():
    client = DummySearchClient()
    results = client.search(["test"], 2)
    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


def test_missing_search_raises_typeerror():
    class NoSearch(BaseSearchClient):
        pass

    with pytest.raises(TypeError):
        NoSearch()


def test_unique_links_removes_duplicates():
    client = DummySearchClient()
    results = [
        SearchResult(url="http://example.com/page1"),
        SearchResult(url="http://example.com/page1"),
        SearchResult(url="http://example.com/page2"),
    ]
    unique = client._unique_links(results, max_link_count=10)
    assert len(unique) == 2
    assert all(isinstance(r, SearchResult) for r in unique)


def test_filter_condition_filters_google_and_pdf():
    client = DummySearchClient()
    assert client._filter_condition("http://example.com/page") is True
    assert client._filter_condition("https://www.google.com/search?q=test") is False
    assert client._filter_condition("http://example.com/file.pdf") is False


def test_n_results_limits_maximum():
    client = DummySearchClient()
    assert client._n_results(5, 0) == 5
    assert client._n_results(5, 3) == 10  # max_num = 10
    assert client._n_results(5, 10) == 10  # should not exceed max_num
