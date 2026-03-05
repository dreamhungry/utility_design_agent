@echo off
REM 快速启动脚本 - Windows

echo ========================================
echo 激活虚拟环境并运行示例
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在！
    echo 请先运行: python -m venv venv
    echo 然后运行: venv\Scripts\activate.bat
    echo 最后运行: pip install -e .
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查是否安装了依赖
python -c "import utility_design_agent" 2>nul
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -e .
)

REM 运行示例
echo.
echo [运行] python example.py
echo.
python example.py

echo.
echo ========================================
echo 完成！虚拟环境仍然激活中
echo 输入 'deactivate' 退出虚拟环境
echo ========================================
