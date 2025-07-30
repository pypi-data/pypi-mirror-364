import pytest
import numpy as np
from agentwebsearch.indexsearch.hnsw import HNSWInMemoryIndexDB
from agentwebsearch.indexsearch.base import BaseInMemoryIndexDB
from agentwebsearch.embedding.base import BaseEmbeddingModel


class DummyEmbeddingModel(BaseEmbeddingModel):
    def model_name(self) -> str:
        return "dummy"

    def embed(self, text: str) -> np.ndarray:
        # Return a fixed vector for testing
        return np.array([1.0, 2.0, 3.0], dtype=np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return np.array([self.embed(t) for t in texts], dtype=np.float32)


@pytest.fixture
def index_db() -> BaseInMemoryIndexDB:
    model = DummyEmbeddingModel()
    return HNSWInMemoryIndexDB(embedding_model=model)


def test_add_and_search_single(index_db: BaseInMemoryIndexDB):
    index_db.add(reference="ref1", text="text1", embedding=np.array([1.0, 2.0, 3.0], dtype=np.float32))
    results = index_db.search(query="test", k=1)
    assert len(results) == 1
    assert results[0].reference == "ref1"
    assert results[0].text == "text1"
    assert results[0].query == "test"


def test_add_batch_and_search(index_db: BaseInMemoryIndexDB):
    texts = ["text1", "text2"]
    embeddings = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
    index_db.add_batch(reference="ref_batch", texts=texts, embeddings=embeddings)
    results = index_db.search(query="test", k=2)
    assert len(results) == 2
    assert all(r.reference == "ref_batch" for r in results)


def test_search_empty_index(index_db: BaseInMemoryIndexDB):
    results = index_db.search(query="test", k=1)
    assert results == []


def test_search_empty_query(index_db: BaseInMemoryIndexDB):
    index_db.add(reference="ref1", text="text1", embedding=np.array([1.0, 2.0, 3.0], dtype=np.float32))
    results = index_db.search(query="", k=1)
    assert results == []


def test_search_as_dict(index_db: BaseInMemoryIndexDB):
    index_db.add(reference="ref1", text="text1", embedding=np.array([1.0, 2.0, 3.0], dtype=np.float32))
    results = index_db.search(query="test", k=1, as_dict=True)
    assert isinstance(results[0], dict)
    assert results[0]["reference"] == "ref1"
    assert results[0]["text"] == "text1"
