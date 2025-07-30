import requests

from typing import Iterator

from agentwebsearch.search.client.base import (
    BaseSearchClient,
    SearchResult,
)


class SerpApiClient(BaseSearchClient):
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._url = "https://serpapi.com/search.json"

    def search(self, queries: list[str], n: int) -> list[SearchResult]:
        search_links = [
            result for i, query in enumerate(queries)
            for result in self._search(query, n, i)
            if self._filter_condition(result.url)
        ]

        max_link_count = len(queries) * n
        self._unique_links(search_links, max_link_count)

        return search_links

    def _search(self, query: str, n: int, i: int) -> Iterator[SearchResult]:
        params = {
            "engine": "google",
            "q": query.strip(),
            "num": self._n_results(n, i),
            "api_key": self._api_key
        }

        response = requests.get(self._url, params=params)
        response.raise_for_status()
        data: dict = response.json()

        results: list[dict] = data.get("organic_results", [])
        for result in results:
            yield SearchResult(
                url=result.get("link"),
                title=result.get("title"),
                description=result.get("snippet")
            )
