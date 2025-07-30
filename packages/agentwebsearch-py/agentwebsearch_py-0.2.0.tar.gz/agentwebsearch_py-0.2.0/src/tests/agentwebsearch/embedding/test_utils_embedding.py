from agentwebsearch.embedding.utils import chunk_text_with_overlap


def test_chunk_text_with_overlap_basic():
    text = "Dies ist ein Testtext, der in mehrere Teile zerlegt werden soll."
    chunks = chunk_text_with_overlap(
        text,
        chunk_size=5,
        chunk_overlap=2,
        model_name="text-embedding-3-large"
    )
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert len(chunks) > 0


def test_chunk_text_with_overlap_empty_text():
    chunks = chunk_text_with_overlap(
        "",
        chunk_size=5,
        chunk_overlap=2,
        model_name="text-embedding-3-large"
    )
    assert chunks == []


def test_chunk_text_with_overlap_overlap_greater_than_chunk():
    text = "Kurzer Text"
    chunks = chunk_text_with_overlap(
        text,
        chunk_size=2,
        chunk_overlap=5,
        model_name="text-embedding-3-large"
    )
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert len(chunks) > 0
