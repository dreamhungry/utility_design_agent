"""litellm 统一调用后端"""

from __future__ import annotations

import logging
from typing import Any

from .base import LLMBackend

logger = logging.getLogger(__name__)


class LiteLLMBackend(LLMBackend):
    """通过 litellm 统一调用多种 LLM Provider"""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.extra_kwargs = kwargs

    async def generate(self, messages: list[dict[str, str]]) -> str:
        import litellm

        logger.debug("LiteLLM 请求 model=%s messages=%d", self.model, len(messages))
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            api_key=self.api_key,
            temperature=0.7,
            **self.extra_kwargs,
        )
        content = response.choices[0].message.content or ""  # type: ignore[union-attr]
        logger.debug("LiteLLM 响应: %s", content[:200])
        return content
