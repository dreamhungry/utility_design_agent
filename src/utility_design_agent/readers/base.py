"""BaseReader 抽象基类"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import NPCData


class BaseReader(ABC):
    """数据源读取器抽象基类"""

    @abstractmethod
    async def read(self, **kwargs: Any) -> list[NPCData]:
        """读取数据源并返回 NPCData 列表"""
        ...
