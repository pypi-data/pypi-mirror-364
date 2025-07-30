from agentwebsearch.websearch.prompts.prompts import PromptGenerator
from agentwebsearch.websearch.request import (
    RequestResponse,
    RequestResponseSummarization,
    WebSearchRequest,
    RequestQuery,

)
from agentwebsearch.websearch.response import WebSearchResponse, ResponseSearch


def test_init_reads_prompts():
    gen = PromptGenerator()
    assert isinstance(gen._GENERATE_STRUCTURED_SEARCH_QUERIES_JSON, str)
    assert isinstance(gen._GENERATE_RESULTS_SUMMARIZATION, str)
    assert len(gen._GENERATE_STRUCTURED_SEARCH_QUERIES_JSON) > 0
    assert len(gen._GENERATE_RESULTS_SUMMARIZATION) > 0


def test_gen_search_queries_messages():
    gen = PromptGenerator()
    chat = [{"role": "user", "content": "Hallo"}]
    messages = gen.gen_search_queries_messages(chat, prompt_context="Kontext")
    assert isinstance(messages, list)
    assert messages[-1]["role"] == "system"
    assert "Kontext" in messages[-1]["content"]


def test_gen_web_search_response_summary_messages():
    gen = PromptGenerator()
    req = WebSearchRequest(
        query=RequestQuery(
            messages=[{"role": "user", "content": "Test"}],
        ),
        response=RequestResponse(
            summarization=RequestResponseSummarization(
                enabled=True,
                prompt_context="Zusammenfassungskontext"
            )
        )
    )
    resp = WebSearchResponse.empty()
    resp.search = ResponseSearch(google=["query1"], vector=["query2"])
    messages = gen.gen_web_search_response_summary_messages(req=req, resp=resp)
    assert isinstance(messages, list)
    assert messages[0]["role"] == "user"
    assert "Zusammenfassungskontext" in messages[0]["content"]
    assert "query1" in messages[0]["content"]
    assert "query2" in messages[0]["content"]
