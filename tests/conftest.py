"""pytest fixtures — mock LLM、示例 NPCData 等"""

from __future__ import annotations

import pytest

from utility_design_agent.models import NPCCurveConfig, NPCData, UtilityFunction


@pytest.fixture
def sample_npc() -> NPCData:
    return NPCData(
        name="哥布林",
        personality_tags=["胆小", "贪婪"],
        behavior_preferences=["逃跑", "拾取"],
        design_intent="生命值低时倾向逃跑，周围有掉落物时优先拾取",
    )


@pytest.fixture
def sample_npc_list() -> list[NPCData]:
    return [
        NPCData(
            name="哥布林",
            personality_tags=["胆小", "贪婪"],
            behavior_preferences=["逃跑", "拾取"],
            design_intent="生命值低时倾向逃跑",
        ),
        NPCData(
            name="骑士",
            personality_tags=["勇敢", "正义"],
            behavior_preferences=["攻击", "防御"],
            design_intent="优先保护队友",
        ),
    ]


@pytest.fixture
def sample_utility_functions() -> list[UtilityFunction]:
    return [
        UtilityFunction(
            behavior="逃跑",
            formula="1 / (1 + math.exp(-10 * (x - 0.3)))",
            description="危险值超过0.3后急剧上升",
        ),
        UtilityFunction(
            behavior="拾取",
            formula="math.pow(x, 0.5)",
            description="拾取欲望平滑上升",
        ),
    ]


@pytest.fixture
def sample_curve_config(sample_utility_functions: list[UtilityFunction]) -> NPCCurveConfig:
    return NPCCurveConfig(
        npc_name="哥布林",
        personality_tags=["胆小", "贪婪"],
        utility_functions=sample_utility_functions,
        metadata={"model": "gpt-4o", "backend": "openai"},
    )
