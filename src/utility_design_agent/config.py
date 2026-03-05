"""配置管理 — 支持构造函数注入 + .env 备选"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """应用配置，优先使用构造函数注入，其次读取 .env"""

    # 飞书
    feishu_app_id: str = ""
    feishu_app_secret: str = ""

    # LLM
    llm_backend: Literal["openai", "litellm"] = "openai"
    openai_api_key: str = ""
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-4o"

    # 输出
    output_dir: str = "output"

    # 日志
    verbose: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
