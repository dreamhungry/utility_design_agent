"""LLMBackend 抽象基类"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """LLM 调用统一接口"""

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str:
        """调用 LLM 并返回原始文本响应

        Args:
            messages: OpenAI chat 格式的消息列表

        Returns:
            LLM 原始响应文本
        """
        ...
