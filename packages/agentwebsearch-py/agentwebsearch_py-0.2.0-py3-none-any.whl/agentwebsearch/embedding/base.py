import numpy as np

from abc import ABC, abstractmethod


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def model_name(self) -> str: pass

    @abstractmethod
    def embed(self, text: str) -> np.ndarray: pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> np.ndarray[np.ndarray]: pass
