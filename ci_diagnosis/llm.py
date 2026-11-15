"""Language model access behind one small interface (decision 6).

Any provider with an OpenAI-compatible chat API works by changing the
AI_API_BASE_URL and AI_MODEL repository variables, without a commit: GitHub
Models, Ollama, OpenAI, and many others. A provider without that API needs one
new class implementing LLMClient.
"""

from typing import Protocol

from openai import OpenAI


class LLMClient(Protocol):
    def complete(self, system_prompt: str, user_content: str) -> str:
        """Return the model's raw text answer."""
        ...


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self._model = model
        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=60.0,
            max_retries=2,
        )

    def complete(self, system_prompt: str, user_content: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            # JSON mode is widely supported; the shape is validated by Pydantic.
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1200,
        )
        return response.choices[0].message.content or ""
