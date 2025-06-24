#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析程序打包脚本
使用PyInstaller将Python程序打包为可执行文件

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def 检查环境():
    """检查打包环境"""
    print("=== 检查打包环境 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("警告: 未安装PyInstaller，正在尝试安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller安装成功")
        except subprocess.CalledProcessError:
            print("错误: PyInstaller安装失败")
            return False
    
    return True

def 清理旧文件():
    """清理之前的构建文件"""
    print("\n=== 清理旧文件 ===")
    
    清理目录 = ["build", "dist", "__pycache__"]

    for 目录 in 清理目录:
        if os.path.exists(目录):
            print(f"删除目录: {目录}")
            shutil.rmtree(目录)

    # 删除spec文件
    for spec_file in Path(".").glob("*.spec"):
        print(f"删除文件: {spec_file}")
        spec_file.unlink()

def 构建可执行文件():
    """构建可执行文件"""
    print("\n=== 构建可执行文件 ===")

    # PyInstaller命令参数 - 使用python -m PyInstaller
    命令 = [
        sys.executable, '-m', 'PyInstaller',
        "--onefile",                    # 打包为单个文件
        "--windowed",                   # Windows下隐藏控制台窗口
        "--name=L属性文法语义分析器",    # 可执行文件名称
        "--add-data=sample_grammar.txt;.",  # 包含示例文法文件
        "--add-data=test_cases.txt;.",      # 包含测试用例文件
        "l_attribute_main.py"           # 主程序文件
    ]

    try:
        print(f"执行命令: {' '.join(命令)}")
        result = subprocess.run(命令, check=True, capture_output=True, text=True)
        print("✓ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def 创建发布包():
    """创建发布包"""
    print("\n=== 创建发布包 ===")

    # 创建发布包目录
    发布目录 = Path("发布包")
    if 发布目录.exists():
        shutil.rmtree(发布目录)
    发布目录.mkdir()

    # 复制可执行文件
    exe_file = Path("dist/L属性文法语义分析器.exe")
    if exe_file.exists():
        shutil.copy2(exe_file, 发布目录 / "L属性文法语义分析器.exe")
        print("✓ 复制可执行文件")
    else:
        print("✗ 可执行文件不存在")
        return False

    # 复制文档文件
    文档文件列表 = [
        "README.md",
        "用户手册.md",
        "技术文档.md",
        "项目完成报告.md",
        "版本信息.md",
        "作业要求.md",
        "sample_grammar.txt",
        "test_cases.txt",
        "requirements.txt"
    ]

    for 文档 in 文档文件列表:
        if os.path.exists(文档):
            shutil.copy2(文档, 发布目录 / 文档)
            print(f"✓ 复制文档: {文档}")

    # 创建使用说明文件
    创建使用说明(发布目录)

    # 创建启动脚本
    创建启动脚本(发布目录)

    # 创建发布说明
    创建发布说明(发布目录)

    print("✓ 发布包创建完成")
    return True

def 创建使用说明(发布目录):
    """创建使用说明文件"""
    使用说明内容 = """L属性文法语义分析器 - 使用说明

快速开始：
1. 双击"L属性文法语义分析器.exe"启动程序
2. 在"L属性文法输入"标签页中输入文法定义
3. 点击"解析文法"和"验证L属性"
4. 在"语义分析过程"标签页中输入测试字符串
5. 点击"开始语义分析"查看分析过程

系统要求：
- Windows 7/8/10/11
- 无需安装Python环境
- 无需安装额外依赖

文法格式：
[文法]
D -> T L
T -> int | float
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"

[语义规则]
L.in := T.type
addtype(id.name, L.in)

功能说明：
- L属性文法输入：定义和编辑L属性文法
- 语义分析过程：执行语义分析并查看详细步骤
- 符号表管理：查看和管理符号表内容
- 使用帮助：详细的使用说明和示例

技术支持：
作者：王海翔
学号：2021060187
班级：计科2203
"""

    with open(发布目录 / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(使用说明内容)

    print("✓ 创建使用说明文件")

def 创建启动脚本(发布目录):
    """创建启动脚本"""
    script_content = """@echo off
chcp 65001 > nul
title L属性文法语义分析器
echo 启动L属性文法语义分析器...
echo.
start "" "L属性文法语义分析器.exe"
"""

    with open(发布目录 / "启动L属性文法语义分析器.bat", 'w', encoding='gbk') as f:
        f.write(script_content)

    print("✓ 创建启动脚本")

def 创建发布说明(发布目录):
    """创建发布说明"""
    发布说明内容 = """L属性文法语义分析器 - 发布说明

版本信息：
- 版本号：v1.0.0
- 发布日期：2025年6月
- 作者：王海翔 (2021060187)

主要功能：
✓ 完整的L属性文法支持
✓ 可视化语义分析过程
✓ 智能L属性特性验证
✓ 完善的符号表管理
✓ 中文本地化界面

技术特点：
- 支持标准BNF格式文法
- 自动验证L属性特性
- 详细的分析步骤展示
- 完整的错误处理机制
- 用户友好的GUI界面

文件说明：
- L属性文法语义分析器.exe：主程序
- README.md：详细说明文档
- 用户手册.md：用户操作指南
- sample_grammar.txt：示例文法
- test_cases.txt：测试用例
- 使用说明.txt：快速使用指南
- 启动L属性文法语义分析器.bat：启动脚本

安装说明：
1. 解压所有文件到同一目录
2. 双击"L属性文法语义分析器.exe"或启动脚本
3. 无需安装Python或其他依赖

联系方式：
作者：王海翔
学号：2021060187
班级：计科2203
"""

    with open(发布目录 / "发布说明.txt", 'w', encoding='utf-8') as f:
        f.write(发布说明内容)

    print("✓ 创建发布说明")



def 主函数():
    """主函数"""
    print("L属性文法语义分析程序 - 打包脚本")
    print("=" * 50)
    
    # 检查环境
    if not 检查环境():
        print("环境检查失败，退出打包")
        return False
    
    # 清理旧文件
    清理旧文件()
    
    # 构建可执行文件
    if not 构建可执行文件():
        print("构建失败，退出打包")
        return False

    # 创建发布包
    if not 创建发布包():
        print("发布包创建失败，退出打包")
        return False

    # 显示结果
    print("\n=== 打包完成 ===")
    print(f"可执行文件大小: {获取文件大小('dist/L属性文法语义分析器.exe')}")
    print(f"发布包位置: {os.path.abspath('发布包')}")
    print("\n可以运行以下命令测试：")
    print("cd 发布包")
    print("L属性文法语义分析器.exe")

    return True

def 获取文件大小(文件路径):
    """获取文件大小（MB）"""
    if os.path.exists(文件路径):
        size_bytes = os.path.getsize(文件路径)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    return "未知"

if __name__ == "__main__":
    try:
        成功 = 主函数()
        if 成功:
            print("\n打包成功！")
        else:
            print("\n打包失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n用户中断打包过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n打包过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
