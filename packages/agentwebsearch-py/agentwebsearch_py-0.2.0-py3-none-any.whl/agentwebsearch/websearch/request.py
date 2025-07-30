from pydantic import BaseModel, Field
from typing import List


class RequestQueryMessage(BaseModel):
    role: str
    content: str


# class RequestWebDocumentSearch(BaseModel):
#     enabled: bool = False
#     max_documents: int = 5
#     max_document_mb_size: int = 1 * 1024 * 1024  # 1 MB

#     def __post_init__(self):
#         if self.max_documents < 1:
#             raise ValueError("Max documents must be greater than 0.")
#         if self.max_document_mb_size < 1:
#             raise ValueError("Max document size must be greater than 0.")


class RequestQueryGoogleSearch(BaseModel):
    max_result_count: int = 5
    # web_document_search: RequestWebDocumentSearch = Field(default_factory=RequestWebDocumentSearch)


class RequestQueryVectorSearch(BaseModel):
    result_count: int = 3


class RequestQuerySearch(BaseModel):
    prompt_context: str | None = None
    google: RequestQueryGoogleSearch = Field(default_factory=RequestQueryGoogleSearch)
    vector: RequestQueryVectorSearch = Field(default_factory=RequestQueryVectorSearch)


class RequestQuery(BaseModel):
    messages: List[RequestQueryMessage]
    search: RequestQuerySearch = Field(default_factory=RequestQuerySearch)


class RequestDeepWebSearch(BaseModel):
    enabled: bool
    max_depth: int


class RequestResponseSummarization(BaseModel):
    enabled: bool = False
    prompt_context: str | None = None


class RequestResponse(BaseModel):
    stream: bool = False
    summarization: RequestResponseSummarization = Field(default_factory=RequestResponseSummarization)


class WebSearchRequest(BaseModel):
    query: RequestQuery
    response: RequestResponse = Field(default_factory=RequestResponse)

    def validate(self) -> None:
        if self.query.search.google.max_result_count < 1:
            raise ValueError("Google search result count must be greater than 0.")
        if self.query.search.vector.result_count < 1:
            raise ValueError("Vector search result count must be greater than 0.")
