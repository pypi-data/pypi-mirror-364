import pytest
import numpy as np
from agentwebsearch.embedding.openai import OpenAIEmbeddingModel


class DummyResponse:
    def __init__(self, embeddings):
        self.data = [DummyRecord(e) for e in embeddings]


class DummyRecord:
    def __init__(self, embedding):
        self.embedding = embedding


@pytest.fixture
def mock_openai(monkeypatch):
    def dummy_create(input, model):
        # Return a dummy embedding for each input
        return DummyResponse([[float(i)] * 3 for i in range(len(input))])
    monkeypatch.setattr("openai.embeddings.create", dummy_create)


def test_model_name():
    model = OpenAIEmbeddingModel(model="test-model", api_key="sk-test")
    assert model.model_name() == "test-model"


def test_private_properties():
    model = OpenAIEmbeddingModel(model="test-model", api_key="sk-test")
    assert hasattr(model, "_api_key")
    assert hasattr(model, "_model")
    assert model._model == "test-model"
    assert model._api_key == "sk-test"


def test_embed_returns_embedding(mock_openai):
    model = OpenAIEmbeddingModel(model="test-model", api_key="sk-test")
    embedding = model.embed("hello")
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (3,)


def test_embed_batch_returns_embeddings(mock_openai):
    model = OpenAIEmbeddingModel(model="test-model", api_key="sk-test")
    texts = ["a", "b"]
    embeddings = model.embed_batch(texts)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 3)
