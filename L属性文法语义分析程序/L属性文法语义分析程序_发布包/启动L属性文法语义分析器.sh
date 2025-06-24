#!/bin/bash

echo "================================================"
echo "L属性文法语义分析程序"
echo "编译原理作业 - 题目6.2"
echo "================================================"
echo
echo "作者: 王海翔"
echo "学号: 2021060187"
echo "班级: 计科2203"
echo
echo "正在启动程序..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python环境"
    echo "请确保已安装Python 3.7或更高版本"
    echo
    read -p "按Enter键退出..."
    exit 1
fi

# 检查主程序文件是否存在
if [ ! -f "程序文件/l_attribute_main.py" ]; then
    echo "错误: 找不到主程序文件"
    echo "请确保程序文件完整"
    echo
    read -p "按Enter键退出..."
    exit 1
fi

# 运行程序
cd 程序文件
python3 l_attribute_main.py

# 检查程序运行结果
if [ $? -ne 0 ]; then
    echo
    echo "程序运行出错，请检查错误信息"
    echo
    read -p "按Enter键退出..."
else
    echo
    echo "程序正常退出"
fi
