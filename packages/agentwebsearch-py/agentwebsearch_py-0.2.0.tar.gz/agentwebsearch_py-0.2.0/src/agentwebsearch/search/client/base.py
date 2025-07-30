from dataclasses import dataclass
from abc import ABC, abstractmethod
from urllib.parse import urlparse


@dataclass
class SearchResult:
    url: str
    title: str = None
    description: str = None


class BaseSearchClient(ABC):
    @abstractmethod
    def search(
        queries: list[str],
        max_count: int) -> list[SearchResult]: pass

    def _unique_links(self, results: list[SearchResult], max_link_count: int) -> list[str]:
        seen = set()
        search_links = [
            result
            for result in results
            if not (
                urlparse(result.url).path in seen or
                seen.add(urlparse(result.url).path)
            )
        ][:max_link_count]

        return search_links

    def _filter_condition(self, link: str) -> bool:
        return (
            link.startswith("http") and
            not link.startswith("https://www.google.com/search?") and
            ".pdf" not in link
        )

    def _n_results(self, n: int, i: int) -> int:
        max_num = int(n * 2)
        num = int(n + (n * i) / 3)
        return num if num < max_num else max_num
