import openai
import numpy as np

from agentwebsearch.embedding.base import BaseEmbeddingModel


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model: str, api_key: str) -> None:
        self._api_key = api_key
        self._model = model
        openai.api_key = api_key

    def model_name(self):
        return self._model

    def embed(self, text: str) -> list[float]:
        embedding = self.embed_batch([text])

        return embedding[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = openai.embeddings.create(
            input=texts,
            model=self._model
        )

        embeddings = np.array([record.embedding for record in resp.data], dtype=np.float32)

        return embeddings
