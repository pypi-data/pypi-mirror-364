import pytest
from agentwebsearch.websearch.dto import LLMQuestionQueries


def test_llmquestionqueries_valid_init():
    queries = LLMQuestionQueries(
        extracted_questions=["Q1", "Q2"],
        google_search_queries=["G1", "G2"],
        vector_search_queries=["V1", "V2"]
    )
    assert queries.extracted_questions == ["Q1", "Q2"]
    assert queries.google_search_queries == ["G1", "G2"]
    assert queries.vector_search_queries == ["V1", "V2"]
    assert queries.has_queries() is True


def test_llmquestionqueries_invalid_init_raises():
    with pytest.raises(Exception) as exc:
        LLMQuestionQueries(
            extracted_questions=["Q1"],
            google_search_queries=["G1", "G2"],
            vector_search_queries=["V1"]
        )
    assert "must match the number" in str(exc.value)


def test_from_lmm_response_valid():
    response = '{"extracted_questions": ["Q1"], "google_search_queries": ["G1"], "vector_search_queries": ["V1"]}'
    queries = LLMQuestionQueries.from_lmm_response(response)
    assert queries.extracted_questions == ["Q1"]
    assert queries.google_search_queries == ["G1"]
    assert queries.vector_search_queries == ["V1"]


def test_from_lmm_response_invalid_json_raises():
    response = '{"extracted_questions": ["Q1"], "google_search_queries": ["G1"]}'  # missing vector_search_queries
    with pytest.raises(Exception) as exc:
        LLMQuestionQueries.from_lmm_response(response)
    assert "Failed to parse" in str(exc.value)


def test_has_queries_false_for_empty():
    queries = LLMQuestionQueries(
        extracted_questions=[],
        google_search_queries=[],
        vector_search_queries=[]
    )
    assert queries.has_queries() is False
