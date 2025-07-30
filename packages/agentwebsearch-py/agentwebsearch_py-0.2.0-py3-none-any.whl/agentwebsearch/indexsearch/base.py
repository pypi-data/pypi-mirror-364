import numpy as np

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class IndexDBDocumentResult:
    reference: str
    text: str
    query: str
    distance: float


@dataclass(frozen=True)
class IndexDBDocument:
    id: int
    reference: str
    text: str
    embedding: np.ndarray

    def to_result(self, query: str, distance: float) -> IndexDBDocumentResult:
        return IndexDBDocumentResult(
            query=query,
            reference=self.reference,
            text=self.text,
            distance=float(distance)
        )

    def to_result_dict(self, query: str, distance: float) -> dict:
        return asdict(self.to_result(query, distance))


class BaseInMemoryIndexDB(ABC):
    @abstractmethod
    def new(self) -> 'BaseInMemoryIndexDB': pass

    @abstractmethod
    def add(
        self,
        reference: str,
        texts: str,
        embedding: np.ndarray) -> None: pass

    @abstractmethod
    def add_batch(
        self,
        reference: str,
        texts: list[str],
        embedding: np.ndarray[np.ndarray]) -> None: pass

    @abstractmethod
    def search(
        self,
        query: str,
        k: int = 5,
        as_dict: bool = False) -> list[IndexDBDocumentResult] | list[dict]: pass
