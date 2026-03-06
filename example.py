"""示例脚本 - 演示完整的效用函数生成流程

这个脚本展示如何使用 utility-design-agent 库生成 NPC 效用函数。
可以直接运行：python example.py
"""

import asyncio
import sys
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
            "personality_tags": ["孩子王", ],
            "features": ["扭扭捏捏爱哭鬼"],
            "needs": ["野生(探索欲)", "饱腹", "口渴", "温度", "运动"],
            "age": 15,
            "design_intent": "扭扭捏捏的小姑娘，害怕孤独和尴尬。常年被不自信的乌云笼罩，眼睛总是处于湿漉漉的梅雨季。其实她并没有近视喔，眼镜只是装饰物，是一种自我保护机制。",
        },
        {
            "name": "莓衣",
            "personality_tags": ["孩子王", ],
            "features": ["外表甜美性格火爆的小姑娘", "吐槽役"],
            "needs": ["野生(探索欲)", "饱腹", "口渴", "温度", "运动"],
            "age": 12,
            "design_intent": "总是皱着“莓”头的呛口的小不点，有着草莓一般的甜美外表和辣椒似的的爆辣内心。不要看她小就轻视她哦，她会呛得你分不清东南西北！",
        },
    ]
    
    # 使用 DictReader 读取数据
    reader = DictReader()
    npcs = await reader.read(data=npc_data_list)
    
    print(f"[OK] 成功加载 {len(npcs)} 个 NPC 数据")
    for npc in npcs:
        print(f"   - {npc.name}: {', '.join(npc.personality_tags)}")
    print()

    # ========================================
    # 2. 配置 LLM 后端
    # ========================================
    print("[步骤 2] 配置 LLM 后端")
    print("-" * 60)
    
    config = AppConfig()
    print(f"   LLM 后端: {config.llm_backend}")
    print(f"   模型: {config.openai_model}")
    
    # 创建 LLM 后端（这里需要真实的 API Key）
    # 如果没有配置，会跳过实际调用
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
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        print("   将使用模拟数据继续演示...")
        llm = None
    print()

    # ========================================
    # 3. 生成效用函数
    # ========================================
    print("[步骤 3] 生成效用函数")
    print("-" * 60)
    
    prompt_builder = PromptBuilder()
    all_configs = []
    
    for npc in npcs:
        print(f"   正在为 [{npc.name}] 生成效用函数...")
        
        if llm:
            # 构建 prompt
            messages = prompt_builder.build(npc)
            
            # 调用 LLM 生成
            try:
                response = await llm.generate(messages)
                print(f"   [OK] 生成成功")
                # print(f"      响应预览: {response[:100]}...")
                print(f"      响应预览: {response}")
                
                # 这里需要解析 LLM 返回的 JSON
                # 简化示例，假设返回了效用函数列表
                # 实际使用中需要添加 JSON 解析逻辑
                
            except Exception as e:
                print(f"   [ERROR] 生成失败: {e}")
                import traceback
                print("   详细错误信息:")
                traceback.print_exc()
        else:
            print(f"   [INFO] 跳过 LLM 调用（使用模拟数据）")
        continue
        # 使用模拟数据进行演示
        from utility_design_agent.models import UtilityFunction, NPCCurveConfig
        
        if npc.name == "哥布林":
            utility_functions = [
                UtilityFunction(
                    behavior="逃跑",
                    formula="1 / (1 + math.exp(-10 * (x - 0.3)))",
                    description="生命值越低，逃跑效用越高（S 曲线，拐点 30%）",
                    input_range=(0.0, 1.0),
                    output_range=(0.0, 1.0),
                ),
                UtilityFunction(
                    behavior="拾取宝物",
                    formula="x * 0.8",
                    description="线性增长，但有上限约束",
                    input_range=(0.0, 1.0),
                    output_range=(0.0, 0.8),
                ),
            ]
        else:
            utility_functions = [
                UtilityFunction(
                    behavior="防守",
                    formula="math.pow(x, 0.5)",
                    description="防守优先级稳定增长",
                    input_range=(0.0, 1.0),
                    output_range=(0.0, 1.0),
                ),
                UtilityFunction(
                    behavior="支援队友",
                    formula="1 / (1 + math.exp(-8 * (x - 0.4)))",
                    description="队友生命值低于 40% 时快速提升支援效用",
                    input_range=(0.0, 1.0),
                    output_range=(0.0, 1.0),
                ),
            ]
        
        config = NPCCurveConfig(
            npc_name=npc.name,
            utility_functions=utility_functions,
            metadata={"personality": npc.personality_tags},
        )
        all_configs.append(config)
    return
    print(f"[OK] 共生成 {len(all_configs)} 个 NPC 的效用函数配置")
    print()

    # ========================================
    # 4. 验证公式
    # ========================================
    print("[步骤 4] 验证公式")
    print("-" * 60)
    
    engine = FormulaEngine()
    
    for config in all_configs:
        print(f"   验证 [{config.npc_name}] 的公式:")
        for uf in config.utility_functions:
            try:
                engine.validate_and_compile(uf.formula)
                # 测试几个点
                test_value = engine.evaluate(uf.formula, 0.3)
                print(f"      [OK] {uf.behavior}: {uf.formula[:50]}...")
                print(f"         测试 x=0.3 => {test_value:.3f}")
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
    
    for config in all_configs:
        print(f"   生成 [{config.npc_name}] 的曲线图...")
        try:
            fig = visualizer.plot_npc_summary(config)
            
            # 保存图表
            chart_dir = output_dir / "charts"
            chart_dir.mkdir(exist_ok=True)
            
            output_path = chart_dir / f"{config.npc_name}_curves.png"
            saved_path = visualizer.save(fig, output_path, fmt="png")
            print(f"      [OK] 保存到: {saved_path}")
        except Exception as e:
            print(f"      [ERROR] 生成失败: {e}")
            import traceback
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
    print("提示:")
    print("   1. 配置 .env 文件中的 OPENAI_API_KEY 可使用真实 LLM 生成")
    print("   2. 查看 output/ 目录了解输出格式")
    print("   3. 使用 CLI 工具处理更多数据: utility-design --help")
    print()


if __name__ == "__main__":
    # 运行主流程
    asyncio.run(main())
