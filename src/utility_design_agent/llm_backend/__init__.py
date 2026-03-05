"""LLM 后端子包 — 工厂函数"""

from __future__ import annotations

from typing import Any

from .base import LLMBackend
from .litellm_backend import LiteLLMBackend
from .openai_backend import OpenAIBackend

__all__ = ["LLMBackend", "OpenAIBackend", "LiteLLMBackend", "create_llm_backend"]


def create_llm_backend(
    backend_type: str = "openai",
    *,
    api_key: str = "",
    api_base: str | None = None,
    model: str = "gpt-4o",
    **kwargs: Any,
) -> LLMBackend:
    """工厂函数：创建 LLM 后端实例

    Args:
        backend_type: "openai" | "litellm"
        api_key: API 密钥
        api_base: 自定义 API 端点（可选）
        model: 模型名称
    """
    if backend_type == "openai":
        return OpenAIBackend(api_key=api_key, api_base=api_base, model=model, **kwargs)
    elif backend_type == "litellm":
        return LiteLLMBackend(api_key=api_key, model=model, **kwargs)
    else:
        raise ValueError(f"不支持的 LLM 后端: {backend_type!r}，可选值: openai, litellm")
