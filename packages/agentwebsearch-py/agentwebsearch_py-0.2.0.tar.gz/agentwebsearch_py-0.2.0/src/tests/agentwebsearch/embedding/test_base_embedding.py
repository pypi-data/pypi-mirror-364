import pytest
import numpy as np

from agentwebsearch.embedding.base import BaseEmbeddingModel


class TestEmbeddingModel(BaseEmbeddingModel):
    def model_name(self) -> str:
        return "dummy-model"

    def embed(self, text: str) -> np.ndarray:
        # Returns a fixed vector for testing
        return np.array([1.0, 2.0, 3.0])

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        # Returns a batch of fixed vectors
        return np.array([self.embed(text) for text in texts])


def test_model_name():
    model = TestEmbeddingModel()
    assert model.model_name() == "dummy-model"


def test_embed_returns_ndarray():
    model = TestEmbeddingModel()
    vec = model.embed("test")
    assert isinstance(vec, np.ndarray)
    assert np.allclose(vec, np.array([1.0, 2.0, 3.0]))


def test_embed_batch_returns_ndarray():
    model = TestEmbeddingModel()
    texts = ["a", "b"]
    batch = model.embed_batch(texts)
    assert isinstance(batch, np.ndarray)
    assert batch.shape == (2, 3)
    assert np.allclose(batch[0], np.array([1.0, 2.0, 3.0]))
    assert np.allclose(batch[1], np.array([1.0, 2.0, 3.0]))


def test_missing_model_name_raises_typeerror():
    class NoModelName(BaseEmbeddingModel):
        def embed(self, text: str) -> np.ndarray:
            return np.array([1.0])

        def embed_batch(self, texts: list[str]) -> np.ndarray:
            return np.array([self.embed(t) for t in texts])

    with pytest.raises(TypeError):
        NoModelName()


def test_missing_embed_raises_typeerror():
    class NoEmbed(BaseEmbeddingModel):
        def model_name(self) -> str:
            return "no-embed"

        def embed_batch(self, texts: list[str]) -> np.ndarray:
            return np.array([[0.0]])

    with pytest.raises(TypeError):
        NoEmbed()


def test_missing_embed_batch_raises_typeerror():
    class NoEmbedBatch(BaseEmbeddingModel):
        def model_name(self) -> str:
            return "no-embed-batch"

        def embed(self, text: str) -> np.ndarray:
            return np.array([0.0])

    with pytest.raises(TypeError):
        NoEmbedBatch()
