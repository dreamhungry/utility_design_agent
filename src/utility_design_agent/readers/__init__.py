"""数据源子包 — 统一接口 + 工厂函数"""

from __future__ import annotations

from typing import Any

from .base import BaseReader
from .dict_reader import DictReader
from .feishu_reader import FeishuReader
from .local_reader import LocalReader

__all__ = [
    "BaseReader",
    "FeishuReader",
    "LocalReader",
    "DictReader",
    "create_reader",
]


def create_reader(source_type: str, **kwargs: Any) -> BaseReader:
    """工厂函数：根据 source_type 创建对应 Reader 实例

    Args:
        source_type: "feishu" | "local" | "dict"
        **kwargs: 传给具体 Reader 构造函数的参数

    Returns:
        BaseReader 子类实例
    """
    readers = {
        "feishu": FeishuReader,
        "local": LocalReader,
        "dict": DictReader,
    }
    cls = readers.get(source_type)
    if cls is None:
        raise ValueError(
            f"不支持的数据源类型: {source_type!r}，"
            f"可选值: {', '.join(readers.keys())}"
        )
    return cls(**kwargs)
