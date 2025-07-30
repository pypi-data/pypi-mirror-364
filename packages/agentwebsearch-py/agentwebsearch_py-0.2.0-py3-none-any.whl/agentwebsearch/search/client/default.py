import googlesearch

from typing import Iterator

from agentwebsearch.search.client.base import (
    BaseSearchClient, SearchResult
)


class DefaultSearchClient(BaseSearchClient):
    def search(self, queries: list[str], n: int) -> list[SearchResult]:
        search_links = [
            SearchResult(url=link) for i, query in enumerate(queries)
            for link in self._search(query, n, i)
            if self._filter_condition(link)
        ]

        max_link_count = len(queries) * n
        self._unique_links(search_links, max_link_count)

        return search_links

    def _search(self, query: str, n: int, i: int) -> Iterator[str]:
        yield from googlesearch.search(
            term=query.strip(),
            num_results=self._n_results(n, i)
        )
