@echo off
chcp 65001 >nul
echo ========================================
echo    SLR(1)完整的语法分析方法
echo    编译原理作业 - 王海翔
echo ========================================
echo.
echo 正在启动SLR(1)语法分析器...
echo.

python slr1_main.py

if %errorlevel% neq 0 (
    echo.
    echo 程序运行出错，请检查Python环境和依赖包
    echo 请确保已安装以下依赖：
    echo - matplotlib
    echo - networkx
    echo - numpy
    echo.
    echo 可以运行以下命令安装依赖：
    echo pip install -r requirements.txt
    echo.
    pause
)
