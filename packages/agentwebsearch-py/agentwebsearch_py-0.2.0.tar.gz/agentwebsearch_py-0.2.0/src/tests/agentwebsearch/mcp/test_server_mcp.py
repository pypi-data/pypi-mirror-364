from agentwebsearch.mcp.server import WebSearchFastMCP


def test_fastmcp_has_websearch():
    mcp = WebSearchFastMCP("test-mcp")
    assert mcp.name == "test-mcp"
    assert hasattr(mcp, "websearch")
    assert callable(mcp.websearch)
