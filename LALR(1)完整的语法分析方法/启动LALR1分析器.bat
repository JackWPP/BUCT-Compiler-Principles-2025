@echo off
chcp 65001 > nul
title LALR(1)语法分析器
echo.
echo ========================================
echo    LALR(1)完整的语法分析方法
echo ========================================
echo.
echo 作者: 王海翔
echo 学号: 2021060187  
echo 班级: 计科2203
echo.
echo 正在启动LALR(1)语法分析器...
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境
    echo 请安装Python 3.7或更高版本
    echo.
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
python -c "import tkinter, matplotlib, networkx, numpy" > nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 缺少必要的依赖包
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖包安装失败
        echo 请手动运行: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

REM 启动程序
echo 启动程序...
python lalr1_main.py

REM 程序结束
echo.
echo 程序已退出
pause
