"""Dict 内存数据读取器 — 接受 list[dict] 直接构建 NPCData"""

from __future__ import annotations

from typing import Any

from ..models import NPCData
from .base import BaseReader


class DictReader(BaseReader):
    """从内存 dict 列表直接构建 NPCData，方便第三方集成"""

    async def read(self, *, data: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[NPCData]:
        """将 list[dict] 转换为 NPCData 列表

        Args:
            data: 字典列表，每个字典包含 name / personality_tags / needs / design_intent 字段

        Returns:
            NPCData 列表
        """
        if not data:
            return []
        return [NPCData.model_validate(item) for item in data]
