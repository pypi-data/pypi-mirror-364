from agentwebsearch.websearch.response import (
    ResponseSearch,
    ResponseReference,
    WebSearchResponse
)


def test_responsesearch_fields():
    search = ResponseSearch(google=["g1", "g2"], vector=["v1"])
    assert search.google == ["g1", "g2"]
    assert search.vector == ["v1"]


def test_responsereference_fields_and_defaults():
    ref = ResponseReference(
        url="http://example.com",
        title="Title",
        description="Desc",
        document_links=["doc1.pdf", "doc2.pdf"]
    )
    assert ref.url == "http://example.com"
    assert ref.title == "Title"
    assert ref.description == "Desc"
    assert ref.document_links == ["doc1.pdf", "doc2.pdf"]
    assert ref.finished is False


def test_websearchresponse_fields_and_empty():
    search = ResponseSearch(google=["g"], vector=["v"])
    references = {
        "ref1": ResponseReference(
            url="http://example.com",
            title="T",
            description="D",
            document_links=[]
        )
    }
    resp = WebSearchResponse(
        search=search,
        references=references,
        error_references=["err1"],
        results=[[{"result": "r"}]],
        summary="summary"
    )
    assert resp.search == search
    assert resp.references == references
    assert resp.error_references == ["err1"]
    assert resp.results == [[{"result": "r"}]]
    assert resp.summary == "summary"

    empty_resp = WebSearchResponse.empty()
    assert isinstance(empty_resp, WebSearchResponse)
    assert empty_resp.search.google == []
    assert empty_resp.search.vector == []
    assert empty_resp.references == {}
    assert empty_resp.error_references == []
    assert empty_resp.results == []
    assert empty_resp.summary is None


def test_websearchresponse_to_dict_and_to_yield():
    resp = WebSearchResponse.empty()
    d = resp.to_dict()
    assert isinstance(d, dict)
    y = resp.to_yield()
    assert isinstance(y, str)
    assert y.endswith("\n")
    assert '"google": []' in y
