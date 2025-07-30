# AgentWebSearch Package
[![CI](https://github.com/enricogoerlitz/agentwebsearch-py/actions/workflows/ci.yml/badge.svg)](https://github.com/enricogoerlitz/agentwebsearch-py/actions/workflows/ci.yml)
[![CD](https://github.com/enricogoerlitz/agentwebsearch-py/actions/workflows/release.yml/badge.svg)](https://github.com/enricogoerlitz/agentwebsearch-py/actions/workflows/release.yml)

## Description

...

## Quickstart

### Create a AgentWebSearch Object

```python
from agentwebsearch import AgentWebSearch
from agentwebsearch.websearch.request import WebSearchRequest
from agentwebsearch.search.client import DefaultSearchClient
from agentwebsearch.webscraper import DefaultWebScraper
from agentwebsearch.indexsearch import HNSWInMemoryIndexDB
from agentwebsearch.llm import OpenAIChatModel
from agentwebsearch.embedding import OpenAIEmbeddingModel


embedding_model = OpenAIEmbeddingModel(
    model="text-embedding-3-large",
    api_key="YOUR_OPENAI_API_KEY"
)

llm = OpenAIChatModel(
    model="gpt-4o",
    api_key="YOUR_OPENAI_API_KEY",
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
```

### Execute AgentWebSearch

```python
from agentwebsearch.websearch.request import RequestQuery, RequestQueryMessage

req = WebSearchRequest(
    query=RequestQuery(
        messages=[
            RequestQueryMessage(
                role="user",
                content="Wann wurde der Bundeskanzler 2025 gewählt?"
            )
        ]
    )
)

result = websearch.execute(req)
# or
for result in websearch.execute(req, stream=True):
    print(result)
    yield result
```

### Deploy as MCP-Server

```python
# server.py
from agentwebsearch.mcp import WebSearchFastMCP

mcp = WebSearchFastMCP("Demo 🚀")


@mcp.tool
def other_tool():
    return "Other tool"


if __name__ == "__main__":
    # available tools:
    #   - websearch
    #   - other_tool

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        path="/mcp"
    )

# python run server.py
```