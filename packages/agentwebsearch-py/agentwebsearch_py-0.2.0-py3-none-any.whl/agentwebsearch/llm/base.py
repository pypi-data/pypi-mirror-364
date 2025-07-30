from typing import Iterator
from abc import ABC, abstractmethod


class BaseChatModel(ABC):
    @abstractmethod
    def model_name(self) -> str: pass

    @abstractmethod
    def submit(self, messages: list[dict]) -> str: pass

    @abstractmethod
    def submit_stream(self, messages: list[dict]) -> Iterator[str]: pass
