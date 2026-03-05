# 开发环境设置指南

本文档介绍如何正确设置项目的开发环境。

## 1. 创建虚拟环境

### Windows (PowerShell)

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果遇到权限问题，运行：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows (CMD)

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat
```

### Linux / macOS

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

## 2. 安装依赖

激活虚拟环境后，安装项目依赖：

```bash
# 安装生产依赖（可编辑模式）
pip install -e .

# 或者安装开发依赖（包含测试工具）
pip install -e ".[dev]"

# 升级 pip（推荐）
pip install --upgrade pip
```

## 3. 验证安装

```bash
# 检查安装的包
pip list

# 测试 CLI 工具
utility-design --help

# 运行示例脚本
python example.py

# 运行测试
pytest
```

## 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写必要的配置
# - OPENAI_API_KEY
# - OPENAI_MODEL
# - OPENAI_API_BASE（可选）
```

## 5. 退出虚拟环境

```bash
deactivate
```

## 常见问题

### Q: 为什么需要虚拟环境？

A: 虚拟环境可以：
- 隔离项目依赖，避免版本冲突
- 确保可复现的开发环境
- 防止污染全局 Python 环境

### Q: 虚拟环境文件夹应该提交到 Git 吗？

A: 不应该。`venv/` 已在 `.gitignore` 中，不会被提交。每个开发者应该自己创建虚拟环境。

### Q: 如何在 IDE 中使用虚拟环境？

A: 
- **VS Code**: 按 `Ctrl+Shift+P` → `Python: Select Interpreter` → 选择 `venv/Scripts/python.exe`
- **PyCharm**: Settings → Project → Python Interpreter → Add → Existing → 选择 `venv/Scripts/python.exe`

### Q: 虚拟环境激活后命令行提示符有什么变化？

A: 会在命令行前显示 `(venv)`，例如：
```
(venv) PS D:\sgra_work\utility-design-agent>
```

## 目录结构

```
utility-design-agent/
├── venv/                    # 虚拟环境（不提交到 Git）
├── src/
│   └── utility_design_agent/
├── tests/
├── output/                  # 输出目录
├── .env                     # 环境变量（不提交到 Git）
├── .env.example             # 环境变量模板
├── example.py               # 示例脚本
├── pyproject.toml           # 项目配置
├── README.md                # 项目文档
└── SETUP.md                 # 本文档
```
