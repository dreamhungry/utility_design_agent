"""Prompt 构造测试"""

from utility_design_agent.models import NPCData
from utility_design_agent.prompts import PromptBuilder, SYSTEM_PROMPT


class TestPromptBuilder:
    def test_build_messages(self, sample_npc: NPCData):
        builder = PromptBuilder()
        messages = builder.build(sample_npc)

        assert len(messages) >= 3  # system + few-shot + user
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert "哥布林" in messages[-1]["content"]

    def test_custom_system_prompt(self, sample_npc: NPCData):
        builder = PromptBuilder(system_prompt="自定义提示词")
        messages = builder.build(sample_npc)
        assert messages[0]["content"] == "自定义提示词"

    def test_no_few_shot(self, sample_npc: NPCData):
        builder = PromptBuilder(few_shot_examples=[])
        messages = builder.build(sample_npc)
        assert len(messages) == 2  # system + user

    def test_includes_personality_tags(self, sample_npc: NPCData):
        builder = PromptBuilder()
        messages = builder.build(sample_npc)
        user_msg = messages[-1]["content"]
        assert "胆小" in user_msg
        assert "贪婪" in user_msg

    def test_includes_behaviors(self, sample_npc: NPCData):
        builder = PromptBuilder()
        messages = builder.build(sample_npc)
        user_msg = messages[-1]["content"]
        assert "逃跑" in user_msg
        assert "拾取" in user_msg
