# 自定义效用函数输入值域

## 概述

从版本 v1.0 开始，`utility-design-agent` 支持为每个效用函数配置自定义的 x 输入值域。

## 默认值域

- **默认 input_range**: `[0, 100]`  
  表示 x 的取值范围为 0 到 100，其中：
  - `0` = 需求完全未满足
  - `100` = 需求完全满足

- **默认 output_range**: `[0, 1]`  
  表示效用值 U(x) 的输出范围为 0 到 1

## 使用方式

### 1. 在 LLM Prompt 中指定

当通过 LLM 生成效用函数时，可以在返回的 JSON 中包含 `input_range` 字段：

```json
{
  "野生": {
    "formula": "1 / (1 + math.exp(0.08 * (x - 60)))",
    "description": "【缓坡S型曲线】探索需求效用函数",
    "input_range": [0, 100],
    "output_range": [0, 1]
  },
  "生命值": {
    "formula": "1 - x / 10",
    "description": "生命值越低，危险感知越强",
    "input_range": [0, 10],
    "output_range": [0, 1]
  }
}
```

### 2. 在代码中手动指定

```python
from utility_design_agent.models import UtilityFunction

# 示例1: 使用默认值域 [0, 100]
uf1 = UtilityFunction(
    behavior="探索",
    formula="1 / (1 + math.exp(0.08 * (x - 60)))",
    description="探索需求"
)

# 示例2: 自定义值域 [0, 10]（例如生命值只有10点）
uf2 = UtilityFunction(
    behavior="逃跑",
    formula="1 - x / 10",
    description="生命值越低逃跑倾向越强",
    input_range=(0.0, 10.0)
)

# 示例3: 归一化值域 [0, 1]
uf3 = UtilityFunction(
    behavior="攻击",
    formula="math.pow(x, 2)",
    description="攻击欲望随距离平方增长",
    input_range=(0.0, 1.0)
)
```

### 3. 在 JSON 配置文件中指定

```json
{
  "npc_name": "哥布林",
  "utility_functions": [
    {
      "behavior": "逃跑",
      "formula": "1 / (1 + math.exp(-10 * (x - 3)))",
      "description": "生命值低于3时快速提升逃跑倾向",
      "input_range": [0, 10],
      "output_range": [0, 1]
    }
  ]
}
```

## 自动适配

所有相关模块都会自动使用配置的 `input_range`：

### FormulaEngine 采样
```python
engine = FormulaEngine()
# 自动使用 uf.input_range 作为采样范围
points = engine.sample(
    uf.formula,
    n_points=200,
    x_min=uf.input_range[0],
    x_max=uf.input_range[1]
)
```

### Visualizer 可视化
```python
visualizer = Visualizer()
# 自动使用 uf.input_range 设置 x 轴范围
fig = visualizer.plot_single(uf)
```

### Exporter 导出
```python
exporter = Exporter(output_dir="output")
# 导出的采样数据自动使用每个函数的 input_range
config_path, samples_path = exporter.export(all_configs)
```

## 常见场景

### 场景1: 百分比需求（饱腹度、口渴等）
```python
# 范围 [0, 100]，表示百分比
UtilityFunction(
    behavior="进食",
    formula="1 / (1 + math.exp(0.2 * (x - 30)))",
    input_range=(0.0, 100.0)
)
```

### 场景2: 固定数值（生命值、魔法值）
```python
# 假设生命值上限为 500
UtilityFunction(
    behavior="治疗",
    formula="1 - x / 500",
    input_range=(0.0, 500.0)
)
```

### 场景3: 归一化值域（距离、角度等）
```python
# 归一化距离 [0, 1]
UtilityFunction(
    behavior="追击",
    formula="1 - x",
    input_range=(0.0, 1.0)
)
```

### 场景4: 自定义范围
```python
# 温度范围 [-20, 40] 摄氏度
UtilityFunction(
    behavior="取暖",
    formula="1 / (1 + math.exp(0.3 * (x - 10)))",
    input_range=(-20.0, 40.0)
)
```

## 注意事项

1. **公式设计**: 确保公式在指定的 `input_range` 内输出值在 `output_range` 范围内
2. **类型检查**: `input_range` 和 `output_range` 必须是 `tuple[float, float]` 类型
3. **向后兼容**: 如果不指定，默认使用 `(0.0, 100.0)` 作为输入值域
4. **LLM 提示**: 在自定义 prompt 时，记得明确告知 LLM 使用何种值域

## 示例：不同值域的效用函数对比

```python
from utility_design_agent import FormulaEngine, Visualizer
from utility_design_agent.models import UtilityFunction

# 创建三个不同值域的效用函数
functions = [
    UtilityFunction(
        behavior="饱腹度 [0-100]",
        formula="1 / (1 + math.exp(0.1 * (x - 50)))",
        input_range=(0.0, 100.0)
    ),
    UtilityFunction(
        behavior="生命值 [0-500]",
        formula="1 / (1 + math.exp(0.02 * (x - 250)))",
        input_range=(0.0, 500.0)
    ),
    UtilityFunction(
        behavior="距离 [0-1]",
        formula="1 - x",
        input_range=(0.0, 1.0)
    ),
]

# 可视化对比（每条曲线会在各自的值域内绘制）
viz = Visualizer()
for uf in functions:
    fig = viz.plot_single(uf)
    viz.save(fig, f"output/{uf.behavior}.png")
```

## 更多信息

- [公式引擎文档](./formula_engine.md)
- [可视化文档](./visualizer.md)
- [API 参考](./api_reference.md)
