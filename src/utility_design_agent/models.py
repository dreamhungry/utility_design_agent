"""Pydantic 数据模型定义"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NPCData(BaseModel):
    """从数据源解析出的单个 NPC 原始数据"""

    name: str = Field(..., description="NPC 名称")
    personality_tags: list[str] = Field(default_factory=list, description="性格标签列表")
    needs: list[str] = Field(default_factory=list, description="需求列表")
    design_intent: str = Field("", description="自然语言设计意图")
    age: int = Field(default=0, description="年龄")
    features: list[str] = Field(default_factory=list, description="特性")

class UtilityFunction(BaseModel):
    """LLM 生成的单条效用函数定义"""

    behavior: str = Field(..., description="行为名称")
    formula: str = Field(..., description="Python 数学表达式字符串")
    description: str = Field("", description="表达式含义说明")
    input_range: tuple[float, float] = Field(default=(0.0, 100), description="输入值域")
    output_range: tuple[float, float] = Field(default=(0.0, 1.0), description="输出值域")


class NPCCurveConfig(BaseModel):
    """单个 NPC 完整的效用函数配置输出"""

    npc_name: str
    personality_tags: list[str] = Field(default_factory=list)
    utility_functions: list[UtilityFunction] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def with_metadata(self, **kwargs: Any) -> "NPCCurveConfig":
        """追加元数据"""
        merged = {**self.metadata, **kwargs, "generated_at": datetime.now().isoformat()}
        return self.model_copy(update={"metadata": merged})
