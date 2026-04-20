import time
from collections.abc import Mapping
from typing import Any, Optional

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from openai.types.chat import ChatCompletionUserMessageParam


def render_prompt_template(template: str, data: Mapping[str, object]) -> str:
    rendered = template
    for key, value in data.items():
        rendered = rendered.replace(f"{{{{.{key}}}}}", str(value))
    return rendered


def _extract_response_text(response: Any) -> str:
    content = response.choices[0].message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts)
    raise ValueError("OpenAI response did not contain text content")


def _should_retry_with_max_completion_tokens(error: APIStatusError) -> bool:
    return (
        (error.status_code or 0) == 400
        and "unsupported parameter" in str(error).lower()
        and "max_tokens" in str(error)
        and "max_completion_tokens" in str(error)
    )


class OpenAITextClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        base_url: Optional[str] = None,
        max_retries: int = 6,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def infer(self, template: str, data: Mapping[str, object]) -> str:
        prompt = render_prompt_template(template, data)
        delay = self.retry_delay_seconds
        use_max_completion_tokens = False

        for attempt in range(self.max_retries + 1):
            try:
                messages: list[ChatCompletionUserMessageParam] = [
                    {"role": "user", "content": prompt}
                ]
                if use_max_completion_tokens:
                    response = self._client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_completion_tokens=self.max_tokens,
                    )
                else:
                    response = self._client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )
                return _extract_response_text(response)
            except (
                RateLimitError,
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
            ):
                if attempt == self.max_retries:
                    raise
            except APIStatusError as exc:
                if (
                    not use_max_completion_tokens
                    and _should_retry_with_max_completion_tokens(exc)
                ):
                    use_max_completion_tokens = True
                    continue

                status_code = exc.status_code or 0
                if status_code not in {408, 409, 429} and status_code < 500:
                    raise
                if attempt == self.max_retries:
                    raise

            time.sleep(delay)
            delay *= 2

        raise RuntimeError("OpenAI request exhausted retries")
