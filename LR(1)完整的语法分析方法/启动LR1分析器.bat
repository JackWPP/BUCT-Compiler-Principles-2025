@echo off
chcp 65001 >nul
title LR(1)语法分析器

echo ========================================
echo    LR(1)完整的语法分析方法
echo ========================================
echo 作者: 王海翔
echo 学号: 2021060187
echo 班级: 计科2203
echo ========================================
echo.

echo 正在启动LR(1)语法分析器...
python lr1_main.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败！请检查：
    echo 1. 是否已安装Python
    echo 2. 是否已安装依赖包 ^(pip install -r requirements.txt^)
    echo 3. 文件是否完整
    echo.
    pause
)
