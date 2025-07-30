from agentwebsearch.search.client import SerpApiClient


def test_instanciate_serp_api_client():
    client = SerpApiClient(api_key="dummy_key")
    assert isinstance(client, SerpApiClient)
    assert client._api_key == "dummy_key"
    assert hasattr(client, "search")
    assert callable(client.search)
