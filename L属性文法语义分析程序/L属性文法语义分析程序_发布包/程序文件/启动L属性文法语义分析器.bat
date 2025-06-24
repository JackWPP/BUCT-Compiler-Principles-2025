@echo off
chcp 65001 > nul
title L属性文法语义分析器

echo ================================================
echo L属性文法语义分析程序
echo 编译原理作业 - 题目6.2
echo ================================================
echo.
echo 作者: 王海翔
echo 学号: 2021060187
echo 班级: 计科2203
echo.
echo 正在启动程序...
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python环境
    echo 请确保已安装Python 3.7或更高版本
    echo.
    pause
    exit /b 1
)

REM 检查主程序文件是否存在
if not exist "l_attribute_main.py" (
    echo 错误: 找不到主程序文件 l_attribute_main.py
    echo 请确保在正确的目录中运行此脚本
    echo.
    pause
    exit /b 1
)

REM 运行程序
python l_attribute_main.py

REM 检查程序运行结果
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    echo.
    pause
) else (
    echo.
    echo 程序正常退出
)

echo.
echo 按任意键退出...
pause > nul
