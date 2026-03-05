"""原生 openai SDK 后端"""

from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

from .base import LLMBackend

logger = logging.getLogger(__name__)


class OpenAIBackend(LLMBackend):
    """通过原生 openai Python SDK 调用 LLM"""

    def __init__(
        self,
        api_key: str = "",
        api_base: str | None = None,
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> None:
        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if api_base:
            client_kwargs["base_url"] = api_base
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = model
        self.extra_kwargs = kwargs

    async def generate(self, messages: list[dict[str, str]]) -> str:
        logger.debug("OpenAI 请求 model=%s messages=%d", self.model, len(messages))
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.7,
            **self.extra_kwargs,
        )
        content = response.choices[0].message.content or ""
        logger.debug("OpenAI 响应: %s", content[:200])
        return content
