from agentwebsearch.search.client import DefaultSearchClient


def test_instanciate_default_search_client():
    client = DefaultSearchClient()
    assert isinstance(client, DefaultSearchClient)
    assert hasattr(client, "search")
    assert callable(client.search)
