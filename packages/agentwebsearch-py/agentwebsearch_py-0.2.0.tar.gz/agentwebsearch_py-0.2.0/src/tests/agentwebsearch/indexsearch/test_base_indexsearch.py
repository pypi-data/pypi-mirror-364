import pytest
import numpy as np

from agentwebsearch.indexsearch.base import (
    IndexDBDocument,
    IndexDBDocumentResult,
    BaseInMemoryIndexDB
)


def test_indexdbdocument_to_result_and_dict():
    doc = IndexDBDocument(
        id=1,
        reference="ref1",
        text="Testtext",
        embedding=np.array([1.0, 2.0, 3.0])
    )
    result = doc.to_result(query="frage", distance=0.5)
    assert isinstance(result, IndexDBDocumentResult)
    assert result.reference == "ref1"
    assert result.text == "Testtext"
    assert result.query == "frage"
    assert result.distance == 0.5


def test_to_result_dict_returns_expected_dict():
    doc = IndexDBDocument(
        id=42,
        reference="ref42",
        text="Beispieltext",
        embedding=np.array([0.1, 0.2, 0.3])
    )
    result_dict = doc.to_result_dict(query="testfrage", distance=1.23)
    assert isinstance(result_dict, dict)
    assert result_dict["reference"] == "ref42"
    assert result_dict["text"] == "Beispieltext"
    assert result_dict["query"] == "testfrage"
    assert result_dict["distance"] == 1.23


def test_missing_new_raises_typeerror():
    class NoNew(BaseInMemoryIndexDB):
        def add(self, reference, texts, embedding): pass
        def add_batch(self, reference, texts, embedding): pass
        def search(self, query, k=5, as_dict=False): pass
    with pytest.raises(TypeError):
        NoNew()


def test_missing_add_raises_typeerror():
    class NoAdd(BaseInMemoryIndexDB):
        def new(self): pass
        def add_batch(self, reference, texts, embedding): pass
        def search(self, query, k=5, as_dict=False): pass
    with pytest.raises(TypeError):
        NoAdd()


def test_missing_add_batch_raises_typeerror():
    class NoAddBatch(BaseInMemoryIndexDB):
        def new(self): pass
        def add(self, reference, texts, embedding): pass
        def search(self, query, k=5, as_dict=False): pass
    with pytest.raises(TypeError):
        NoAddBatch()


def test_missing_search_raises_typeerror():
    class NoSearch(BaseInMemoryIndexDB):
        def new(self): pass
        def add(self, reference, texts, embedding): pass
        def add_batch(self, reference, texts, embedding): pass
    with pytest.raises(TypeError):
        NoSearch()
