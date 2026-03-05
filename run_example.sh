#!/bin/bash
# 快速启动脚本 - Linux/macOS

echo "========================================"
echo "激活虚拟环境并运行示例"
echo "========================================"
echo

# 检查虚拟环境是否存在
if [ ! -f "venv/bin/activate" ]; then
    echo "[错误] 虚拟环境不存在！"
    echo "请先运行: python3 -m venv venv"
    echo "然后运行: source venv/bin/activate"
    echo "最后运行: pip install -e ."
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否安装了依赖
python -c "import utility_design_agent" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[警告] 依赖未安装，正在安装..."
    pip install -e .
fi

# 运行示例
echo
echo "[运行] python example.py"
echo
python example.py

echo
echo "========================================"
echo "完成！虚拟环境仍然激活中"
echo "输入 'deactivate' 退出虚拟环境"
echo "========================================"
