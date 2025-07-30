import pytest
import json

from fastapi.testclient import TestClient
from fastapi.responses import Response
from agentwebsearch.rest.server import WebSearchFastAPI


class DummyWebSearch:
    async def execute(self, req):
        return Response(json.dumps({
            "search": "dummy",
            "references": [],
            "error_references": [],
            "results": []
        }), status_code=200)


@pytest.fixture
def client():
    app = WebSearchFastAPI(websearch=DummyWebSearch())
    return TestClient(app)


def test_websearch_post_returns_result(client: TestClient):
    response: Response = client.post("/websearch", json={
        "query": {
            "messages": [{"role": "user", "content": "test"}],
        },
        "response": {"stream": False},
    })
    assert response.status_code == 200
