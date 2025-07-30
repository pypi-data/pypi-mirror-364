import openai

from typing import Iterator

from agentwebsearch.llm.base import BaseChatModel


class OpenAIChatModel(BaseChatModel):
    def __init__(
            self,
            model: str,
            api_key: str,
            temperature: int = 0.7
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        openai.api_key = api_key

    def model_name(self):
        return self._model

    def submit(self, messages: list[dict]) -> str:
        resp = openai.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature
        )

        return resp.choices[0].message.content

    def submit_stream(self, messages: list[dict]) -> Iterator[str]:
        content = ""
        for chunk in openai.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            stream=True
        ):
            if "choices" in chunk and len(chunk["choices"]) > 0:
                new_content = chunk["choices"][0]["delta"].get("content", "")
                content += new_content
                yield new_content
