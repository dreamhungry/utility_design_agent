"""数据模型测试"""

import pytest
from pydantic import ValidationError

from utility_design_agent.models import NPCCurveConfig, NPCData, UtilityFunction


class TestNPCData:
    def test_basic_creation(self):
        npc = NPCData(
            name="哥布林",
            personality_tags=["胆小", "贪婪"],
            needs=["逃跑", "拾取"],
            design_intent="生命值低时逃跑",
        )
        assert npc.name == "哥布林"
        assert len(npc.personality_tags) == 2

    def test_defaults(self):
        npc = NPCData(name="测试NPC")
        assert npc.personality_tags == []
        assert npc.needs == []
        assert npc.design_intent == ""

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            NPCData()  # type: ignore[call-arg]


class TestUtilityFunction:
    def test_basic_creation(self):
        uf = UtilityFunction(
            behavior="逃跑",
            formula="1 / (1 + math.exp(-10 * (x - 0.3)))",
            description="S 曲线",
        )
        assert uf.behavior == "逃跑"
        assert "math.exp" in uf.formula

    def test_defaults(self):
        uf = UtilityFunction(behavior="攻击", formula="x")
        assert uf.input_range == (0.0, 1.0)
        assert uf.output_range == (0.0, 1.0)
        assert uf.description == ""


class TestNPCCurveConfig:
    def test_with_metadata(self, sample_curve_config: NPCCurveConfig):
        updated = sample_curve_config.with_metadata(extra_key="test")
        assert "extra_key" in updated.metadata
        assert "generated_at" in updated.metadata

    def test_empty_utility_functions(self):
        cfg = NPCCurveConfig(npc_name="空NPC")
        assert cfg.utility_functions == []
        assert cfg.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
