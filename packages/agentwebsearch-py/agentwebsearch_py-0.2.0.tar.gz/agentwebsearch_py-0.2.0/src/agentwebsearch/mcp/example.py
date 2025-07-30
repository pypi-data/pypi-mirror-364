from agentwebsearch.mcp import WebSearchFastMCP


mcp = WebSearchFastMCP("Demo 🚀")


# python src/agentwebsearch/mcp/example.py
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        path="/mcp"
    )
