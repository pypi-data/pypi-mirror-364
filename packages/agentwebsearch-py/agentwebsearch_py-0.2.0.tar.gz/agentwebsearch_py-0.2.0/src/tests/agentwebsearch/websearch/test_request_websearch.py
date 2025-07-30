import pytest

from agentwebsearch.websearch.request import (
    RequestQueryMessage,
    RequestQueryGoogleSearch,
    RequestQueryVectorSearch,
    RequestQuerySearch,
    RequestQuery,
    RequestResponseSummarization,
    RequestResponse,
    WebSearchRequest
)


def test_request_query_message_fields():
    msg = RequestQueryMessage(role="user", content="Hallo")
    assert msg.role == "user"
    assert msg.content == "Hallo"


def test_request_query_google_search_defaults():
    google = RequestQueryGoogleSearch()
    assert google.max_result_count == 5


def test_request_query_vector_search_defaults():
    vector = RequestQueryVectorSearch()
    assert vector.result_count == 3


def test_request_query_search_defaults():
    search = RequestQuerySearch()
    assert search.prompt_context is None
    assert isinstance(search.google, RequestQueryGoogleSearch)
    assert isinstance(search.vector, RequestQueryVectorSearch)


def test_request_query_fields():
    msg = RequestQueryMessage(role="user", content="Test")
    query = RequestQuery(messages=[msg])
    assert isinstance(query.search, RequestQuerySearch)
    assert query.messages[0].role == "user"


def test_request_response_summarization_defaults():
    summ = RequestResponseSummarization()
    assert summ.enabled is False
    assert summ.prompt_context is None


def test_request_response_defaults():
    resp = RequestResponse()
    assert resp.stream is False
    assert isinstance(resp.summarization, RequestResponseSummarization)


def test_websearchrequest_validates_success():
    msg = RequestQueryMessage(role="user", content="Test")
    req = WebSearchRequest(
        query=RequestQuery(messages=[msg]),
        response=RequestResponse()
    )
    req.validate()  # Should not raise


def test_websearchrequest_invalid_google_count_raises():
    msg = RequestQueryMessage(role="user", content="Test")
    query = RequestQuery(
        messages=[msg],
        search=RequestQuerySearch(
            google=RequestQueryGoogleSearch(max_result_count=0)
        )
    )
    req = WebSearchRequest(query=query)
    with pytest.raises(ValueError):
        req.validate()


def test_websearchrequest_invalid_vector_count_raises():
    msg = RequestQueryMessage(role="user", content="Test")
    query = RequestQuery(
        messages=[msg],
        search=RequestQuerySearch(
            vector=RequestQueryVectorSearch(result_count=0)
        )
    )
    req = WebSearchRequest(query=query)
    with pytest.raises(ValueError):
        req.validate()
