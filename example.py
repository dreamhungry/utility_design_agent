"""示例脚本 - 演示完整的效用函数生成流程

这个脚本展示如何使用 utility-design-agent 库生成 NPC 效用函数。
调用 LLM 生成效用函数 → 解析响应 → 公式校验 → 导出 → 可视化。
可以直接运行：python example.py
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path

# 设置输出编码为 UTF-8（解决 Windows 控制台问题）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utility_design_agent import (
    NPCData,
    DictReader,
    create_llm_backend,
    PromptBuilder,
    FormulaEngine,
    Exporter,
    Visualizer,
)
from utility_design_agent.config import AppConfig
from utility_design_agent.models import UtilityFunction, NPCCurveConfig


# ---------------------------------------------------------------------------
# LLM 响应解析（复用 cli.py 中的逻辑）
# ---------------------------------------------------------------------------

def parse_llm_response(raw: str) -> list[dict]:
    """从 LLM 响应中提取 JSON 数组/对象，返回 list[dict]"""
    text = raw.strip()
    # 1) 提取 ```json ... ``` 代码块
    if "```" in text:
        start = text.find("```")
        end = text.rfind("```")
        if start != end:
            inner = text[start:end]
            lines = inner.split("\n", 1)
            text = lines[1] if len(lines) > 1 else lines[0]
    # 2) 尝试找到 JSON 数组 [...]
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1:
        text = text[bracket_start : bracket_end + 1]
        return json.loads(text)
    # 3) 尝试找到 JSON 对象 {...}（prompt 模板示例返回的是 dict）
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1:
        text = text[brace_start : brace_end + 1]
        obj = json.loads(text)
        if isinstance(obj, dict):
            # 将 {"need_name": {formula, description}, ...} 转为 list
            result = []
            for need_name, value in obj.items():
                if isinstance(value, dict):
                    value["need"] = need_name
                    result.append(value)
            return result
        return obj
    return json.loads(text)


def build_utility_functions(parsed: list[dict], engine: FormulaEngine) -> list[UtilityFunction]:
    """将解析出的 dict 列表转换为 UtilityFunction 列表，逐条校验公式"""
    functions = []
    for item in parsed:
        # LLM 返回的字段可能是 need/behavior，统一映射到 behavior
        behavior = item.get("need") or item.get("behavior") or "unknown"
        formula = item.get("formula", "")
        description = item.get("description", "")
        
        # 支持 LLM 返回自定义值域，提供默认值
        input_range = tuple(item.get("input_range", [0.0, 100.0]))
        output_range = tuple(item.get("output_range", [0.0, 1.0]))

        # AST 白名单校验 + 编译
        try:
            engine.validate_and_compile(formula)
        except Exception as e:
            print(f"      [WARN] [{behavior}] 公式校验失败，跳过: {e}")
            print(f"             公式: {formula}")
            continue

        functions.append(UtilityFunction(
            behavior=behavior,
            formula=formula,
            description=description,
            input_range=input_range,  # type: ignore
            output_range=output_range,  # type: ignore
        ))
    return functions


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

MAX_RETRIES = 3  # LLM 生成失败重试次数


async def main():
    print("=" * 60)
    print("NPC 效用函数生成示例")
    print("=" * 60)
    print()

    # ========================================
    # 1. 准备 NPC 数据
    # ========================================
    print("[步骤 1] 准备 NPC 数据")
    print("-" * 60)

    npc_data_list = [
        {
            "name": "捏捏扭",
            "personality_tags": ["孩子王"],
            "features": ["扭扭捏捏爱哭鬼"],
            "needs": ["野生(探索欲)", "饱腹", "口渴", "温度", "运动"],
            "age": 15,
            "design_intent": "扭扭捏捏的小姑娘，害怕孤独和尴尬。常年被不自信的乌云笼罩，眼睛总是处于湿漉漉的梅雨季。其实她并没有近视喔，眼镜只是装饰物，是一种自我保护机制。",
        },
        {
            "name": "莓衣",
            "personality_tags": ["孩子王"],
            "features": ["外表甜美性格火爆的小姑娘", "吐槽役"],
            "needs": ["野生(探索欲)", "饱腹", "口渴", "温度", "运动"],
            "age": 12,
            "design_intent": "总是皱着\u201c莓\u201d头的呛口的小不点，有着草莓一般的甜美外表和辣椒似的的爆辣内心。不要看她小就轻视她哦，她会呛得你分不清东南西北！",
        },
    ]

    reader = DictReader()
    npcs = await reader.read(data=npc_data_list)

    print(f"[OK] 成功加载 {len(npcs)} 个 NPC 数据")
    for npc in npcs:
        print(f"   - {npc.name}: {', '.join(npc.personality_tags)} | 需求: {', '.join(npc.needs)}")
    print()

    # ========================================
    # 2. 配置 LLM 后端
    # ========================================
    print("[步骤 2] 配置 LLM 后端")
    print("-" * 60)

    config = AppConfig()
    print(f"   LLM 后端: {config.llm_backend}")
    print(f"   模型: {config.openai_model}")

    try:
        llm = create_llm_backend(
            backend_type=config.llm_backend,
            api_key=config.openai_api_key,
            model=config.openai_model,
            api_base=config.openai_api_base,
        )
        print("[OK] LLM 后端初始化成功")
    except Exception as e:
        print(f"[ERROR] LLM 后端初始化失败: {e}")
        traceback.print_exc()
        print("\n请检查 .env 文件中的 LLM 配置后重试。")
        return
    print()

    # ========================================
    # 3. 调用 LLM 生成效用函数并解析
    # ========================================
    print("[步骤 3] 生成效用函数（调用 LLM）")
    print("-" * 60)

    prompt_builder = PromptBuilder()
    engine = FormulaEngine()
    all_configs: list[NPCCurveConfig] = []

    for npc in npcs:
        print(f"\n   >>> 正在为 [{npc.name}] 生成效用函数...")
        messages = prompt_builder.build(npc)

        utility_functions: list[UtilityFunction] = []
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # 调用 LLM
                raw_response = await llm.generate(messages)
                print(f"   [OK] 第 {attempt} 次调用成功，响应长度: {len(raw_response)} 字符")
                print(f"   --- LLM 原始响应 ---")
                # 只打印前 500 字符预览
                preview = raw_response[:500] + ("..." if len(raw_response) > 500 else "")
                print(f"   {preview}")
                print(f"   --- 响应结束 ---")

                # 解析 JSON
                parsed = parse_llm_response(raw_response)
                print(f"   [OK] 解析出 {len(parsed)} 条效用函数定义")

                # 逐条校验公式并构造 UtilityFunction
                utility_functions = build_utility_functions(parsed, engine)
                print(f"   [OK] 校验通过 {len(utility_functions)} 条公式")

                if utility_functions:
                    success = True
                    break
                else:
                    print(f"   [WARN] 无有效公式，重试...")

            except json.JSONDecodeError as e:
                print(f"   [ERROR] 第 {attempt} 次: JSON 解析失败 - {e}")
                if attempt < MAX_RETRIES:
                    print(f"   正在重试...")
            except Exception as e:
                print(f"   [ERROR] 第 {attempt} 次生成失败: {e}")
                traceback.print_exc()
                if attempt < MAX_RETRIES:
                    print(f"   正在重试...")

        if not success:
            print(f"   [ERROR] [{npc.name}] 经过 {MAX_RETRIES} 次重试仍失败，跳过该 NPC")
            continue

        # 构造 NPCCurveConfig
        cfg = NPCCurveConfig(
            npc_name=npc.name,
            personality_tags=npc.personality_tags,
            utility_functions=utility_functions,
            metadata={"personality": npc.personality_tags},
        ).with_metadata(model=config.openai_model, backend=config.llm_backend)
        all_configs.append(cfg)

        # 打印生成结果摘要
        print(f"\n   [{npc.name}] 效用函数列表:")
        for uf in utility_functions:
            print(f"      - {uf.behavior}: {uf.formula}")
            print(f"        {uf.description}")

    print()
    if not all_configs:
        print("[ERROR] 没有成功生成任何 NPC 的效用函数，流程终止。")
        return

    print(f"[OK] 共生成 {len(all_configs)} 个 NPC 的效用函数配置")
    print()

    # ========================================
    # 4. 验证公式（对生成结果做二次验证 + 采样测试）
    # ========================================
    print("[步骤 4] 验证公式")
    print("-" * 60)

    for cfg in all_configs:
        print(f"   验证 [{cfg.npc_name}] 的公式:")
        for uf in cfg.utility_functions:
            try:
                engine.validate_and_compile(uf.formula)
                test_value = engine.evaluate(uf.formula, 0.5)
                print(f"      [OK] {uf.behavior}: f(0.5) = {test_value:.4f}")
            except Exception as e:
                print(f"      [ERROR] {uf.behavior}: 验证失败 - {e}")
    print()

    # ========================================
    # 5. 导出数据
    # ========================================
    print("[步骤 5] 导出数据")
    print("-" * 60)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    exporter = Exporter(output_dir=str(output_dir))
    config_path, samples_path = exporter.export(all_configs, n_points=50)

    print(f"   [OK] 配置文件: {config_path}")
    print(f"   [OK] 采样数据: {samples_path}")
    print()

    # ========================================
    # 6. 生成可视化
    # ========================================
    print("[步骤 6] 生成可视化")
    print("-" * 60)

    visualizer = Visualizer(n_points=100)

    for cfg in all_configs:
        print(f"   生成 [{cfg.npc_name}] 的曲线图...")
        try:
            fig = visualizer.plot_npc_summary(cfg)
            chart_dir = output_dir / "charts"
            chart_dir.mkdir(exist_ok=True)
            output_path = chart_dir / f"{cfg.npc_name}_curves.png"
            saved_path = visualizer.save(fig, output_path, fmt="png")
            print(f"      [OK] 保存到: {saved_path}")
        except Exception as e:
            print(f"      [ERROR] 生成失败: {e}")
            traceback.print_exc()
    print()

    # ========================================
    # 7. 总结
    # ========================================
    print("=" * 60)
    print("完成！")
    print("=" * 60)
    print(f"输出目录: {output_dir.absolute()}")
    print(f"   - 配置文件: {config_path.name}")
    print(f"   - 采样数据: {samples_path.name}")
    print(f"   - 可视化图表: charts/ 目录")
    print()


if __name__ == "__main__":
    asyncio.run(main())
