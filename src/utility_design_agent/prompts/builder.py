"""PromptBuilder — 构造结构化 Prompt"""

from __future__ import annotations

from ..models import NPCData
from .templates import FEW_SHOT_EXAMPLES, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class PromptBuilder:
    """将 NPCData 组装为 LLM 调用所需的消息列表"""

    def __init__(
        self,
        system_prompt: str | None = None,
        few_shot_examples: list[dict[str, str]] | None = None,
    ) -> None:
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self.few_shot_examples = few_shot_examples if few_shot_examples is not None else FEW_SHOT_EXAMPLES

    def build(self, npc: NPCData) -> list[dict[str, str]]:
        """构造 messages 列表（OpenAI chat 格式）

        Returns:
            [{"role": "system", "content": ...}, {"role": "user", "content": ...}, ...]
        """
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
        ]
        # messages.extend(self.few_shot_examples)
        messages.append({
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                name=npc.name,
                personality_tags=", ".join(npc.personality_tags),
                needs=", ".join(npc.needs),
                design_intent=npc.design_intent,
                age=npc.age,
                features=", ".join(npc.features),
            ),
        })
        return messages
