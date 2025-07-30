import json

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ResponseSearch:
    google: list[str]
    vector: list[str]


@dataclass(frozen=False)
class ResponseReference:
    url: str
    title: str
    description: str
    document_links: list[str]
    finished: bool = False


@dataclass(frozen=False)
class WebSearchResponse:
    search: ResponseSearch
    references: dict[str, ResponseReference]
    error_references: list[str]
    results: list[list[dict]]
    summary: str | None = None

    @staticmethod
    def empty() -> "WebSearchResponse":
        return WebSearchResponse(
            search=ResponseSearch(google=[], vector=[]),
            references={},
            error_references=[],
            results=[],
            summary=None,
        )

    def to_yield(self) -> bytes:
        return (json.dumps(self.to_dict()) + "\n")

    def to_dict(self) -> dict:
        return asdict(self)
