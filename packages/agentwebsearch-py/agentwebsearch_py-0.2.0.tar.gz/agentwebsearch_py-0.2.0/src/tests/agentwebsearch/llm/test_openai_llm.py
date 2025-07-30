import pytest

from agentwebsearch.llm.openai import OpenAIChatModel


class DummyResponse:
    class Choice:
        class Message:
            content = "Antwort"
        message = Message()
    choices = [Choice()]


@pytest.fixture
def mock_openai(monkeypatch):
    def dummy_create(model, messages, temperature, stream=False):
        if stream:
            # Simulate streaming chunks
            return [
                {"choices": [{"delta": {"content": "Ant"}}]},
                {"choices": [{"delta": {"content": "wort"}}]}
            ]
        return DummyResponse()
    monkeypatch.setattr("openai.chat.completions.create", dummy_create)


def test_model_name():
    model = OpenAIChatModel(model="gpt-test", api_key="sk-test")
    assert model.model_name() == "gpt-test"


def test_submit_returns_response(mock_openai):
    model = OpenAIChatModel(model="gpt-test", api_key="sk-test")
    messages = [{"role": "user", "content": "Hallo"}]
    response = model.submit(messages)
    assert response == "Antwort"


def test_submit_stream_returns_chunks(mock_openai):
    model = OpenAIChatModel(model="gpt-test", api_key="sk-test")
    messages = [{"role": "user", "content": "Hallo"}]
    chunks = list(model.submit_stream(messages))
    assert "".join(chunks) == "Antwort"
    assert all(isinstance(chunk, str) for chunk in chunks)
