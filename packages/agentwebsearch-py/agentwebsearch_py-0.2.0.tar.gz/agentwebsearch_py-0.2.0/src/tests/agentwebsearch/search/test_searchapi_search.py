from agentwebsearch.search.client import SearchApiClient


def test_instanciate_search_api_client():
    client = SearchApiClient(api_key="dummy_key")
    assert isinstance(client, SearchApiClient)
    assert client._api_key == "dummy_key"
    assert hasattr(client, "search")
    assert callable(client.search)
