import multiprocessing

from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, AsyncGenerator

from agentwebsearch.websearch.request import WebSearchRequest
from agentwebsearch.websearch.response import (
    WebSearchResponse,
    ResponseSearch,
    ResponseReference
)
from agentwebsearch.search.client import DefaultSearchClient, SearchResult
from agentwebsearch.websearch.dto import LLMQuestionQueries
from agentwebsearch.websearch.prompts import PromptGenerator
from agentwebsearch.webscraper.base import BaseWebScraper, WebPageResult
from agentwebsearch.webscraper import DefaultWebScraper
from agentwebsearch.search.client.base import BaseSearchClient
from agentwebsearch.indexsearch.base import BaseInMemoryIndexDB
from agentwebsearch.indexsearch import HNSWInMemoryIndexDB
from agentwebsearch.embedding.base import BaseEmbeddingModel
from agentwebsearch.embedding.utils import chunk_text_with_overlap
from agentwebsearch.llm.base import BaseChatModel
from agentwebsearch.logger import logger


class AgentWebSearch:
    def __init__(
            self,
            embedding_model: BaseEmbeddingModel,
            llm: BaseChatModel,
            search_client: BaseSearchClient = None,
            scraper: BaseWebScraper = None,
            index_db: BaseInMemoryIndexDB = None,
            chunk_size: int = 800,
            chunk_overlap: int = 200
    ):
        self._llm = llm
        self._embedding_model = embedding_model
        self._search_client = search_client or DefaultSearchClient()
        self._scraper = scraper or DefaultWebScraper()
        self._index = index_db or HNSWInMemoryIndexDB(
            embedding_model=embedding_model
        )
        self._prompts = PromptGenerator()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def execute(
            self,
            req: WebSearchRequest
    ) -> WebSearchResponse:
        async for result in self._execute(req):
            final = result
        return final

    async def execute_stream(
            self,
            req: WebSearchRequest
    ) -> AsyncGenerator[WebSearchResponse, None]:
        async for result in self._execute(req, stream=True):
            yield result

    async def _execute(
            self,
            req: WebSearchRequest,
            stream: bool = False
    ) -> AsyncGenerator[bytes, None]:
        # 1. Initialize response
        self._index = self._index.new()
        response = WebSearchResponse.empty()

        # 2. Generate search queries
        queries = self._generate_google_and_vector_search_queries(req)
        if queries is None:
            if stream:
                yield response.to_yield()
                return
            yield response
            return

        google_queries, vector_queries_args, vector_queries = queries
        response.search = ResponseSearch(
            google=google_queries,
            vector=vector_queries
        )

        if stream:
            yield response.to_yield()

        # 3. Perform Google search
        search_results = self._fetch_google_links(google_queries, req)
        response.references = self._create_init_response_references(search_results)

        if stream:
            yield response.to_yield()

        # 4. Scrape web pages and perform vector search in parallel
        processes = min(multiprocessing.cpu_count(), len(search_results))
        with ThreadPoolExecutor(max_workers=processes) as pool:
            pages_results, pages_text_chunks, err_urls = self._scrape_web_pages(search_results, response, pool)

            if stream:
                yield response.to_yield()

            self._index_web_pages(pages_results, pages_text_chunks, pool)
            vector_results = self._perform_vector_search(vector_queries_args, pool)

        # 5. Prepare response
        response.results = vector_results
        response.error_references = err_urls

        if stream:
            yield response.to_yield()

        # 6. Summarize results if enabled
        if req.response.summarization.enabled:
            if stream:
                for summary in self._summarize_results(req, response, stream):
                    response.summary = summary
                    yield response.to_yield()
            else:
                response.summary = self._summarize_results(req, response, stream)

        if stream:
            yield response.to_yield()
            return
        yield response

    def _generate_google_and_vector_search_queries(
        self,
        req: WebSearchRequest,
        max_retry: int = 1,
        retry_count: int = 0
    ) -> tuple[list[str], list[tuple[str, int, bool]], list[str]] | None:
        try:
            messages = self._prompts.gen_search_queries_messages(
                chat_messages=req.query.messages,
                prompt_context=req.query.search.prompt_context
            )

            queries_raw = self._llm.submit(messages)
            queries = LLMQuestionQueries.from_lmm_response(queries_raw)

            if not queries.has_queries():
                return None

            google_queries = queries.google_search_queries
            vector_queries = queries.vector_search_queries

            vector_queries_args = [
                (query, req.query.search.vector.result_count, True)
                for query in vector_queries
            ]

            return google_queries, vector_queries_args, vector_queries
        except Exception as e:
            if retry_count < max_retry:
                retry_count += 1
                logger.warning(
                    f"Failed to generate search queries: {e}. Retrying ({retry_count}/{max_retry})..."
                )
                return self._generate_google_and_vector_search_queries(req, max_retry, retry_count)
            raise e

    def _fetch_google_links(self, queries: list[str], req: WebSearchRequest) -> list[SearchResult]:
        return self._search_client.search(queries, req.query.search.google.max_result_count)

    def _create_init_response_references(
            self,
            search_results: list[SearchResult]
    ) -> dict[str, ResponseReference]:
        return {
            search_result.url: ResponseReference(
                url=search_result.url,
                title=search_result.title,
                description=search_result.description,
                document_links=[]
            )
            for search_result in search_results
        }

    def _scrape_web_pages(
        self,
        search_results: list[SearchResult],
        response: WebSearchResponse,
        pool: ThreadPoolExecutor
    ) -> tuple[list[WebPageResult], list[list[str]], list[str]]:
        urls = [result.url for result in search_results]
        scraped_pages: list[WebPageResult] = list(pool.map(self._scraper.scrape, urls))
        pages_results, pages_text_chunks, err_urls = self._prepare_page_results(scraped_pages)

        for page_result in pages_results:
            ref = response.references[page_result.url]
            ref.document_links = page_result.document_links
            ref.finished = True

        return pages_results, pages_text_chunks, err_urls

    def _index_web_pages(
        self,
        pages_results: list[WebPageResult],
        pages_text_chunks: list[list[str]],
        pool: ThreadPoolExecutor
    ):
        pages_embeddings = list(pool.map(self._embedding_model.embed_batch, pages_text_chunks))

        for page, chunks, embeddings in zip(pages_results, pages_text_chunks, pages_embeddings):
            self._index.add_batch(reference=page.url, texts=chunks, embeddings=embeddings)

    def _prepare_page_results(
        self,
        page_results: list[WebPageResult]
    ) -> tuple[list[WebPageResult], list[list[str]], list[str]]:
        prep_results = []
        pages_text_chunks = []
        err_urls = []

        for page in page_results:
            if page.content is not None:
                prep_results.append(page)
                page_chunks = chunk_text_with_overlap(
                    text=page.content,
                    chunk_size=self._chunk_size,
                    chunk_overlap=self._chunk_overlap,
                    model_name=self._embedding_model.model_name()
                )
                pages_text_chunks.append(page_chunks)
            else:
                err_urls.append(page.url)

        return prep_results, pages_text_chunks, err_urls

    def _perform_vector_search(
        self,
        vector_queries_args: list[tuple[str, int, bool]],
        pool: ThreadPoolExecutor
    ) -> list[dict]:
        return list(pool.map(self._vector_search_wrapper, vector_queries_args))

    def _vector_search_wrapper(self, args: tuple[str, int, bool]) -> list[dict]:
        query, k, as_dict = args
        return self._index.search(query, k=k, as_dict=as_dict)

    def _summarize_results(
            self,
            req: WebSearchRequest,
            resp: WebSearchResponse,
            stream: bool
    ) -> str | Iterator[str]:
        messages = self._prompts.gen_web_search_response_summary_messages(
            req=req,
            resp=resp
        )
        if not stream:
            summary = self._llm.submit(messages)
            return summary

        yield from self._llm.submit_stream(messages)
