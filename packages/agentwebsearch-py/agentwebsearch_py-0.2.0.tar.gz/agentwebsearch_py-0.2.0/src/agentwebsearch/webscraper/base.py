from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class WebPageResult:
    url: str
    content: str | None
    links: list[str]
    document_links: list[str]


class BaseWebScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> WebPageResult: pass
