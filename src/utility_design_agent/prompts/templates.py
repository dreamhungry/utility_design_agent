"""Prompt 模板字符串常量"""

SYSTEM_PROMPT = """\
你是一个游戏 AI 设计专家，专门为 NPC 行为设计效用函数（Utility Function）。

你的任务是根据 NPC 的性格标签、行为偏好和设计意图，为每个行为生成一个 Python 数学表达式。

## 约束
1. 表达式必须是合法的 Python 表达式，变量名只能使用 `x`（表示输入值，范围 0~1）
2. 只能使用以下 math 模块函数：math.exp, math.log, math.log10, math.pow, math.sqrt, math.sin, math.cos, math.tan, math.fabs
3. 可以使用基本运算符：+ - * / **
4. 表达式的输出值应当在 0~1 范围内（当 x 在 0~1 时）
5. 不要使用任何其他函数、import 语句或变量

## 输出格式
以 JSON 数组返回，每个元素包含：
- behavior: 行为名称（字符串）
- formula: Python 数学表达式（字符串）
- description: 对该曲线形状和设计意图的简要说明（字符串）
"""

USER_PROMPT_TEMPLATE = """\
## NPC 信息
- 名称: {name}
- 性格标签: {personality_tags}
- 行为偏好: {behavior_preferences}
- 设计意图: {design_intent}

请为该 NPC 的每个行为偏好生成对应的效用函数表达式。
"""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": (
            "## NPC 信息\n"
            "- 名称: 哥布林\n"
            "- 性格标签: 胆小, 贪婪\n"
            "- 行为偏好: 逃跑, 拾取\n"
            "- 设计意图: 生命值低时倾向逃跑，周围有掉落物时优先拾取\n\n"
            "请为该 NPC 的每个行为偏好生成对应的效用函数表达式。"
        ),
    },
    {
        "role": "assistant",
        "content": (
            '[{"behavior": "逃跑", '
            '"formula": "1 / (1 + math.exp(-10 * (x - 0.3)))", '
            '"description": "当危险值(x)较低时效用接近0，超过0.3阈值后急剧上升，体现胆小性格下的逃跑倾向"}, '
            '{"behavior": "拾取", '
            '"formula": "math.pow(x, 0.5)", '
            '"description": "对掉落物的兴趣随距离/价值平滑上升，体现贪婪性格下的拾取偏好"}]'
        ),
    },
]
