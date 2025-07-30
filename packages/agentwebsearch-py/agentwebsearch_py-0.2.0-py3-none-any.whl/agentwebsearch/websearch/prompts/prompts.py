import os

from agentwebsearch.websearch.request import WebSearchRequest
from agentwebsearch.websearch.response import WebSearchResponse


class PromptGenerator:
    def __init__(self):
        self._GENERATE_STRUCTURED_SEARCH_QUERIES_JSON = \
            self._read_google_vector_search_prompt()
        self._GENERATE_RESULTS_SUMMARIZATION = \
            self._read_summarize_websearch_result_prompt()

    def _read_google_vector_search_prompt(self) -> str:
        file = "google_vector_search.md"
        path = self._full_path(file)
        return self._read_md_file(path)

    def _read_summarize_websearch_result_prompt(self) -> str:
        file = "summarize_websearch_result.md"
        path = self._full_path(file)
        return self._read_md_file(path)

    def _full_path(self, file_name: str) -> str:
        relativ_path = f"markdown/{file_name}"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, relativ_path)

    def _read_md_file(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    def gen_search_queries_messages(
            self,
            chat_messages: list[dict],
            prompt_context: str
    ) -> list[dict]:
        prompt = self._GENERATE_STRUCTURED_SEARCH_QUERIES_JSON.replace(
            "{PROMPT_CONTEXT}", prompt_context or ""
        )

        messages = [
            *chat_messages,
            {"role": "system", "content": prompt}
        ]

        return messages

    def gen_web_search_response_summary_messages(
            self,
            req: WebSearchRequest,
            resp: WebSearchResponse
    ) -> str:
        prompt = self._GENERATE_RESULTS_SUMMARIZATION.format(
            WEB_SEARCH_RESULTS=str(resp.results),
            GOOGLE_SEARCH_QUERIES=resp.search.google,
            VECTOR_SEARCH_QUERIES=resp.search.vector,
            ADDITIONAL_SUMMARIZATION_CONTEXT_PROMPT=req.response.summarization.prompt_context,
        )

        messages = [
            {"role": "user", "content": prompt},
        ]

        return messages
