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
    
    # PyInstaller命令参数
    命令 = [
        "pyinstaller",
        "--onefile",                    # 打包为单个文件
        "--windowed",                   # Windows下隐藏控制台窗口
        "--name=L属性文法语义分析器",    # 可执行文件名称
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--add-data=sample_grammar.txt;.",  # 包含示例文法文件
        "--add-data=test_cases.txt;.",      # 包含测试用例文件
        "--distpath=发布包",            # 输出目录
        "l_attribute_main.py"           # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        命令.remove("--icon=icon.ico")
    
    try:
        print(f"执行命令: {' '.join(命令)}")
        subprocess.check_call(命令)
        print("构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def 复制附加文件():
    """复制附加文件到发布目录"""
    print("\n=== 复制附加文件 ===")

    发布目录 = Path("发布包")

    # 要复制的文件列表
    附加文件 = [
        "sample_grammar.txt",
        "test_cases.txt",
        "requirements.txt",
        "README.md",
        "用户手册.md",
        "技术文档.md",
        "项目完成报告.md"
    ]

    for 文件 in 附加文件:
        if os.path.exists(文件):
            目标路径 = 发布目录 / 文件
            print(f"复制文件: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)
        else:
            print(f"文件不存在，跳过: {文件}")

    # 创建文档目录
    文档目录 = 发布目录 / "文档"
    文档目录.mkdir(exist_ok=True)

    # 复制文档文件到文档目录
    文档文件 = [
        "用户手册.md",
        "技术文档.md",
        "项目完成报告.md"
    ]

    for 文件 in 文档文件:
        if os.path.exists(文件):
            目标路径 = 文档目录 / 文件
            print(f"复制文档: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)

def 创建启动脚本():
    """创建启动脚本"""
    print("\n=== 创建启动脚本 ===")
    
    发布目录 = Path("发布包")
    
    # Windows批处理脚本
    bat_内容 = """@echo off
chcp 65001 > nul
echo 启动L属性文法语义分析器...
echo.
L属性文法语义分析器.exe
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)
"""
    
    bat_文件 = 发布目录 / "启动L属性文法语义分析器.bat"
    with open(bat_文件, 'w', encoding='gbk') as f:
        f.write(bat_内容)
    
    print(f"创建启动脚本: {bat_文件}")

def 创建使用说明():
    """创建使用说明文件"""
    print("\n=== 创建使用说明 ===")
    
    发布目录 = Path("发布包")
    
    使用说明 = """# L属性文法语义分析程序 - 使用说明

## 运行程序
双击 `L属性文法语义分析器.exe` 或 `启动L属性文法语义分析器.bat` 即可运行程序。

## 功能说明
1. **L属性文法输入**: 定义L属性文法的产生式、属性和语义规则
2. **语义分析过程**: 执行语义分析并查看详细步骤
3. **符号表管理**: 查看和管理符号表内容
4. **使用帮助**: 查看详细的使用说明和示例

## 核心功能
- ✅ L属性文法的定义和解析
- ✅ 语义规则的执行和属性计算
- ✅ 符号表的管理和维护
- ✅ 语义分析过程的可视化展示
- ✅ L属性特性的验证

## 示例文件
- `sample_grammar.txt`: 示例L属性文法定义
- `test_cases.txt`: 详细测试用例说明

## 技术信息
- 开发语言: Python 3.7+
- GUI框架: tkinter
- 打包工具: PyInstaller

## 作者信息
- 作者: 王海翔
- 学号: 2021060187
- 班级: 计科2203
- 课程: 编译原理
- 完成时间: 2025年6月

## 系统要求
- Windows 7/8/10/11
- 无需安装Python环境
- 内存: 至少512MB
- 磁盘空间: 至少100MB

## 故障排除
如果程序无法启动，请检查：
1. 是否有杀毒软件阻止程序运行
2. 是否有足够的系统权限
3. 系统是否支持该程序

如有问题，请联系开发者。
"""
    
    说明文件 = 发布目录 / "使用说明.txt"
    with open(说明文件, 'w', encoding='utf-8') as f:
        f.write(使用说明)
    
    print(f"创建使用说明: {说明文件}")

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
    
    # 复制附加文件
    复制附加文件()
    
    # 创建启动脚本
    创建启动脚本()
    
    # 创建使用说明
    创建使用说明()
    
    print("\n=== 打包完成 ===")
    print("发布文件位于 '发布包' 目录中")
    print("可执行文件: 发布包/L属性文法语义分析器.exe")
    print("启动脚本: 发布包/启动L属性文法语义分析器.bat")
    
    return True

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
