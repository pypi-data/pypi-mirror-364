import json
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMQuestionQueries:
    extracted_questions: list[str]
    google_search_queries: list[str]
    vector_search_queries: list[str]

    def __post_init__(self):
        if (
            (len(self.extracted_questions) != len(self.google_search_queries)) or
            (len(self.extracted_questions) != len(self.vector_search_queries))
        ):
            raise Exception("LLMQuestionQueries: The number of extracted questions must match the number of Google and vector search queries.")

    @staticmethod
    def from_lmm_response(response: str) -> "LLMQuestionQueries":
        try:
            response_dict = json.loads(response)
            return LLMQuestionQueries(
                extracted_questions=response_dict["extracted_questions"],
                google_search_queries=response_dict["google_search_queries"],
                vector_search_queries=response_dict["vector_search_queries"]
            )
        except Exception as e:
            raise Exception(f"Failed to parse LLM response to QuestionQueries: {e}, Response: {response}")

    def has_queries(self) -> bool:
        return len(self.extracted_questions) > 0
