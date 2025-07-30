import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse

from agentwebsearch import AgentWebSearch
from agentwebsearch.websearch.response import WebSearchResponse
from agentwebsearch.websearch.request import WebSearchRequest
from agentwebsearch.search.client import DefaultSearchClient
from agentwebsearch.webscraper import DefaultWebScraper
from agentwebsearch.indexsearch import HNSWInMemoryIndexDB
from agentwebsearch.llm import OpenAIChatModel
from agentwebsearch.embedding import OpenAIEmbeddingModel

load_dotenv(".env")

# uvicorn rest.server:app --reload --app-dir testing
# uvicorn agentwebsearch.rest.server:app --reload --app-dir src
app = FastAPI()

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_CHAT_MODEL_NAME = os.getenv("AI_CHAT_MODEL_NAME", "gpt-4o")
AI_EMBEDDING_MODEL_NAME = os.getenv("AI_EMBEDDING_MODEL_NAME", "text-embedding-3-large")
CHUNK_TOKEN_SIZE = int(os.getenv("AI_TEXT_CHUNK_TOKEN_SIZE", 800)),
CHUNK_OVERLAP_SIZE = int(os.getenv("AI_TEXT_CHUNK_OVERLAP_TOKEN_SIZE", 100))
SEARCHAPI_API_KEY = os.getenv("SEARCHAPI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


assert OPENAI_API_KEY is not None


# Initialize the LLM and embedding model
embedding_model = OpenAIEmbeddingModel(
    model="text-embedding-3-large",
    api_key=OPENAI_API_KEY
)

llm = OpenAIChatModel(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.7
)

index_db = HNSWInMemoryIndexDB(embedding_model=embedding_model)
search_client = DefaultSearchClient()
scraper = DefaultWebScraper()

websearch = AgentWebSearch(
    search_client=search_client,
    index_db=index_db,
    scraper=scraper,
    llm=llm,
    embedding_model=embedding_model
)


@app.post("/websearch", response_model=WebSearchResponse)
async def web_search(req: WebSearchRequest = Depends()):
    if req.response.stream:
        async def stream_response():
            async for r in websearch.execute_stream(req):
                yield r

        return StreamingResponse(
            stream_response(),
            media_type="application/json"
        )
    else:
        return await websearch.execute(req)
