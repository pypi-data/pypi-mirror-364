import pytest
from agentwebsearch.llm.base import BaseChatModel


def test_missing_model_name_raises_typeerror():
    class NoModelName(BaseChatModel):
        def submit(self, messages): return "ok"
        def submit_stream(self, messages): yield "ok"
    with pytest.raises(TypeError):
        NoModelName()


def test_missing_submit_raises_typeerror():
    class NoSubmit(BaseChatModel):
        def model_name(self): return "dummy"
        def submit_stream(self, messages): yield "ok"
    with pytest.raises(TypeError):
        NoSubmit()


def test_missing_submit_stream_raises_typeerror():
    class NoSubmitStream(BaseChatModel):
        def model_name(self): return "dummy"
        def submit(self, messages): return "ok"
    with pytest.raises(TypeError):
        NoSubmitStream()
