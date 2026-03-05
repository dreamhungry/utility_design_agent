# Utility Design Agent

> NPC 效用函数自动生成库 + CLI 工具

一个基于 LLM 的智能效用函数设计工具，帮助游戏开发者快速生成和优化 NPC 决策逻辑的效用函数。

---

## ✨ 特性

- 📊 **多源数据读取**：支持飞书多维表格、本地 Excel/JSON/YAML 文件
- 🤖 **智能公式生成**：利用 LLM（OpenAI/LiteLLM）自动设计效用函数
- 🧮 **公式计算引擎**：内置 Python 表达式求值引擎，支持常见数学函数
- 📈 **可视化分析**：自动生成函数曲线图，直观展示效用函数特性
- 📦 **灵活导出**：支持导出为 Excel、JSON、可视化图表等多种格式
- 🎯 **命令行友好**：提供直观的 CLI 工具，支持多种工作流

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/dreamhungry/utility_design_agent.git
cd utility-design-agent
```

### 2. 创建虚拟环境（推荐）

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 基础安装（生产依赖）
pip install -e .

# 完整安装（包含开发/测试工具）
pip install -e ".[dev]"
```

### 4. 配置环境变量

复制 `.env.example` 并重命名为 `.env`，填写必要的配置：

```bash
cp .env.example .env
```

**必填配置：**

```env
# LLM 配置
LLM_BACKEND=openai          # 或 litellm
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o         # 或其他模型

# 可选配置
OPENAI_API_BASE=            # 例如: http://your-proxy.com/v1
OUTPUT_DIR=output           # 输出目录
```

**如需使用飞书数据源（可选）：**

```env
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
```

### 5. 运行示例

**快速运行（推荐）：**
```bash
# Windows
run_example.bat

# Linux/macOS
chmod +x run_example.sh
./run_example.sh
```

**或手动运行：**
```bash
# 运行完整示例流程
python example.py

# 使用 CLI 工具
utility-design --help
utility-design process-local input.xlsx --output output.xlsx --visualize
```

> 💡 **提示**: 详细的环境设置说明请查看 [SETUP.md](SETUP.md)

---

## 📖 使用指南

### CLI 命令

#### 1. `process-local` - 处理本地文件

从本地文件读取数据并生成效用函数：

```bash
utility-design process-local <input-file> [选项]
```

**参数：**
- `input-file`：输入文件路径（支持 `.xlsx`, `.json`, `.yaml`）

**选项：**
- `--output, -o`：输出文件路径（默认：`output.xlsx`）
- `--visualize, -v`：生成可视化图表
- `--format, -f`：输出格式（`excel` | `json`，默认：`excel`）

**示例：**

```bash
# 基础用法
utility-design process-local data.xlsx

# 生成 JSON 并可视化
utility-design process-local data.xlsx -o result.json -f json -v

# 完整工作流
utility-design process-local data.xlsx -o output.xlsx --visualize
```

#### 2. `process-feishu` - 处理飞书数据

从飞书多维表格读取数据并生成效用函数：

```bash
utility-design process-feishu <app-token> <table-id> [选项]
```

**参数：**
- `app-token`：飞书文档的 app token
- `table-id`：多维表格的 table id

**选项：**
- `--output, -o`：输出文件路径
- `--visualize, -v`：生成可视化图表
- `--format, -f`：输出格式（`excel` | `json`）

#### 3. `visualize` - 生成可视化图表

为已生成的效用函数创建可视化图表：

```bash
utility-design visualize <input-file> [选项]
```

**参数：**
- `input-file`：包含效用函数的文件（`.xlsx` 或 `.json`）

**选项：**
- `--output-dir, -o`：图表输出目录（默认：`./output/charts`）

---

## 📁 项目结构

```
utility-design-agent/
├── src/
│   └── utility_design_agent/
│       ├── __init__.py           # 包初始化
│       ├── cli.py                # CLI 命令行工具
│       ├── config.py             # 配置管理
│       ├── models.py             # 数据模型（Pydantic）
│       ├── formula_engine.py     # 公式计算引擎
│       ├── exporter.py           # 数据导出器
│       ├── visualizer.py         # 可视化生成器
│       ├── llm_backend/          # LLM 后端
│       │   ├── base.py           # 抽象基类
│       │   ├── openai_backend.py # OpenAI 实现
│       │   └── litellm_backend.py# LiteLLM 实现
│       ├── prompts/              # Prompt 工程
│       │   ├── templates.py      # Prompt 模板
│       │   └── builder.py        # Prompt 构建器
│       └── readers/              # 数据读取器
│           ├── base.py           # 抽象基类
│           ├── local_reader.py   # 本地文件读取器
│           ├── feishu_reader.py  # 飞书 API 读取器
│           └── dict_reader.py    # 字典数据读取器
├── tests/                        # 单元测试
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略规则
├── pyproject.toml                # 项目配置
└── README.md                     # 项目文档
```

---

## 🔧 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_formula_engine.py

# 显示详细输出
pytest -v
```

### 代码结构说明

#### 数据模型（`models.py`）

使用 Pydantic 定义强类型数据模型：

- `UtilityVariable`：效用变量定义
- `UtilityFunction`：效用函数定义
- `UtilityDocument`：完整文档结构

#### 读取器（`readers/`）

实现了策略模式，支持多种数据源：

- `LocalReader`：读取 Excel/JSON/YAML 文件
- `FeishuReader`：通过飞书 API 读取多维表格
- `DictReader`：从 Python 字典读取（用于测试）

#### LLM 后端（`llm_backend/`）

抽象了 LLM 调用逻辑，便于切换不同的 LLM 提供商：

- `OpenAIBackend`：官方 OpenAI API
- `LiteLLMBackend`：支持多种 LLM（Claude、Gemini 等）

#### 公式引擎（`formula_engine.py`）

安全地计算数学表达式，支持：

- 基础运算：`+`, `-`, `*`, `/`, `**`, `//`, `%`
- 数学函数：`sin`, `cos`, `sqrt`, `abs`, `log`, `exp` 等
- 逻辑函数：`max`, `min`, `clamp`

---

## 📝 数据格式规范

### 输入格式（Excel/JSON）

#### Excel 格式

| variable_id | variable_name | description | range | ... |
|-------------|---------------|-------------|-------|-----|
| health      | 生命值         | 当前生命值   | 0-100 | ... |
| distance    | 距离          | 与目标距离   | 0-50  | ... |

#### JSON 格式

```json
{
  "variables": [
    {
      "variable_id": "health",
      "variable_name": "生命值",
      "description": "当前生命值",
      "range": "0-100"
    }
  ]
}
```

### 输出格式

生成的效用函数包含：

- `formula`：Python 表达式（如 `health / 100`）
- `description`：公式说明
- `design_rationale`：设计思路
- `example_values`：示例计算结果
- `visualization`：可视化图表路径（可选）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件



---

## 🙏 致谢

本项目使用了以下优秀的开源项目：

- [Typer](https://typer.tiangolo.com/) - 命令行工具框架
- [Pydantic](https://docs.pydantic.dev/) - 数据验证
- [Rich](https://rich.readthedocs.io/) - 终端美化
- [OpenAI](https://openai.com/) / [LiteLLM](https://litellm.ai/) - LLM 服务
- [Matplotlib](https://matplotlib.org/) - 数据可视化
