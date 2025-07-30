from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse

from agentwebsearch import AgentWebSearch
from agentwebsearch.websearch.response import WebSearchResponse
from agentwebsearch.websearch.request import WebSearchRequest


class WebSearchFastAPI(FastAPI):
    def __init__(
            self,
            websearch: AgentWebSearch,
            route_prefix: str = "/websearch",
            **fastapi_kwargs
    ):
        super().__init__(**fastapi_kwargs)
        self._route_prefix = route_prefix
        self._websearch = websearch
        self.post(
            path=route_prefix,
            response_model=WebSearchResponse
        )(self.web_search)

    async def web_search(self, req: WebSearchRequest = Depends()):
        if req.response.stream:
            async def stream_response():
                async for r in self._websearch.execute_stream(req):
                    yield r

            return StreamingResponse(
                stream_response(),
                media_type="application/json"
            )
        else:
            return await self._websearch.execute(req)
