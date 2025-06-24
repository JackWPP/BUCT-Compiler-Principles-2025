#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析程序发布包创建脚本

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def 创建发布目录():
    """创建发布目录结构"""
    print("=== 创建发布目录结构 ===")
    
    发布根目录 = Path("L属性文法语义分析程序_发布包")
    
    # 清理旧的发布目录
    if 发布根目录.exists():
        print(f"删除旧的发布目录: {发布根目录}")
        shutil.rmtree(发布根目录)
    
    # 创建目录结构
    目录结构 = [
        发布根目录,
        发布根目录 / "程序文件",
        发布根目录 / "文档",
        发布根目录 / "示例文件",
        发布根目录 / "测试文件"
    ]
    
    for 目录 in 目录结构:
        目录.mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {目录}")
    
    return 发布根目录

def 复制程序文件(发布根目录: Path):
    """复制程序文件"""
    print("\n=== 复制程序文件 ===")
    
    程序目录 = 发布根目录 / "程序文件"
    
    # 主程序文件
    主程序文件 = [
        "l_attribute_main.py",
        "启动L属性文法语义分析器.bat"
    ]
    
    for 文件 in 主程序文件:
        if os.path.exists(文件):
            目标路径 = 程序目录 / 文件
            print(f"复制程序文件: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)
        else:
            print(f"警告: 程序文件不存在 - {文件}")

def 复制文档文件(发布根目录: Path):
    """复制文档文件"""
    print("\n=== 复制文档文件 ===")
    
    文档目录 = 发布根目录 / "文档"
    
    # 文档文件列表
    文档文件 = [
        "README.md",
        "用户手册.md",
        "技术文档.md",
        "项目完成报告.md",
        "版本信息.md",
        "requirements.txt"
    ]
    
    for 文件 in 文档文件:
        if os.path.exists(文件):
            目标路径 = 文档目录 / 文件
            print(f"复制文档文件: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)
        else:
            print(f"警告: 文档文件不存在 - {文件}")

def 复制示例文件(发布根目录: Path):
    """复制示例文件"""
    print("\n=== 复制示例文件 ===")
    
    示例目录 = 发布根目录 / "示例文件"
    
    # 示例文件列表
    示例文件 = [
        "sample_grammar.txt",
        "test_cases.txt"
    ]
    
    for 文件 in 示例文件:
        if os.path.exists(文件):
            目标路径 = 示例目录 / 文件
            print(f"复制示例文件: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)
        else:
            print(f"警告: 示例文件不存在 - {文件}")

def 复制测试文件(发布根目录: Path):
    """复制测试文件"""
    print("\n=== 复制测试文件 ===")
    
    测试目录 = 发布根目录 / "测试文件"
    
    # 测试文件列表
    测试文件 = [
        "test_l_attribute.py",
        "comprehensive_test.py"
    ]
    
    for 文件 in 测试文件:
        if os.path.exists(文件):
            目标路径 = 测试目录 / 文件
            print(f"复制测试文件: {文件} -> {目标路径}")
            shutil.copy2(文件, 目标路径)
        else:
            print(f"警告: 测试文件不存在 - {文件}")

def 创建启动脚本(发布根目录: Path):
    """创建启动脚本"""
    print("\n=== 创建启动脚本 ===")
    
    # Windows批处理脚本
    bat_内容 = """@echo off
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
if not exist "程序文件\\l_attribute_main.py" (
    echo 错误: 找不到主程序文件
    echo 请确保程序文件完整
    echo.
    pause
    exit /b 1
)

REM 运行程序
cd 程序文件
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
"""
    
    bat_文件 = 发布根目录 / "启动L属性文法语义分析器.bat"
    with open(bat_文件, 'w', encoding='gbk') as f:
        f.write(bat_内容)
    
    print(f"创建启动脚本: {bat_文件}")
    
    # Linux/macOS shell脚本
    sh_内容 = """#!/bin/bash

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
"""
    
    sh_文件 = 发布根目录 / "启动L属性文法语义分析器.sh"
    with open(sh_文件, 'w', encoding='utf-8') as f:
        f.write(sh_内容)
    
    # 设置执行权限
    try:
        os.chmod(sh_文件, 0o755)
    except:
        pass  # Windows系统可能不支持chmod
    
    print(f"创建启动脚本: {sh_文件}")

def 创建说明文件(发布根目录: Path):
    """创建发布说明文件"""
    print("\n=== 创建发布说明文件 ===")
    
    当前时间 = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    说明内容 = f"""# L属性文法语义分析程序 - 发布包

## 发布信息
- **版本**: v1.0.0
- **发布日期**: {当前时间}
- **开发者**: 王海翔 (学号: 2021060187, 班级: 计科2203)

## 目录结构
```
L属性文法语义分析程序_发布包/
├── 启动L属性文法语义分析器.bat    # Windows启动脚本
├── 启动L属性文法语义分析器.sh     # Linux/macOS启动脚本
├── 发布说明.md                   # 本文件
├── 程序文件/                     # 主程序文件
│   ├── l_attribute_main.py       # 主程序
│   └── 启动L属性文法语义分析器.bat
├── 文档/                         # 项目文档
│   ├── README.md                 # 项目说明
│   ├── 用户手册.md               # 详细使用说明
│   ├── 技术文档.md               # 技术实现文档
│   ├── 项目完成报告.md           # 项目总结报告
│   ├── 版本信息.md               # 版本详细信息
│   └── requirements.txt          # 依赖包列表
├── 示例文件/                     # 示例和测试文件
│   ├── sample_grammar.txt        # 示例文法定义
│   └── test_cases.txt            # 测试用例说明
└── 测试文件/                     # 测试脚本
    ├── test_l_attribute.py       # 功能测试脚本
    └── comprehensive_test.py     # 综合测试脚本
```

## 快速开始

### Windows用户
1. 确保已安装Python 3.7或更高版本
2. 双击 `启动L属性文法语义分析器.bat` 文件
3. 程序将自动启动

### Linux/macOS用户
1. 确保已安装Python 3.7或更高版本
2. 在终端中运行: `./启动L属性文法语义分析器.sh`
3. 程序将自动启动

### 手动启动
1. 进入 `程序文件` 目录
2. 运行命令: `python l_attribute_main.py`

## 功能特性
- ✅ 完整的L属性文法支持
- ✅ 可视化语义分析过程
- ✅ 智能L属性特性验证
- ✅ 完善的符号表管理
- ✅ 中文本地化界面

## 系统要求
- **Python版本**: 3.7 或更高版本
- **操作系统**: Windows 7+, macOS 10.12+, Ubuntu 18.04+
- **内存**: 至少 512MB
- **磁盘空间**: 至少 100MB

## 使用说明
详细的使用说明请参考 `文档/用户手册.md` 文件。

## 技术支持
如果在使用过程中遇到问题，请参考：
1. `文档/用户手册.md` - 详细使用说明
2. `文档/技术文档.md` - 技术实现细节
3. `示例文件/` - 示例文法和测试用例

## 测试验证
运行测试脚本验证程序功能：
```bash
# 进入测试文件目录
cd 测试文件

# 运行功能测试
python test_l_attribute.py

# 运行综合测试
python comprehensive_test.py
```

## 许可证
本程序仅供学术和教育目的使用。

---
**发布时间**: {当前时间}
**程序版本**: v1.0.0
**文档版本**: 1.0
"""
    
    说明文件 = 发布根目录 / "发布说明.md"
    with open(说明文件, 'w', encoding='utf-8') as f:
        f.write(说明内容)
    
    print(f"创建发布说明: {说明文件}")

def 创建压缩包(发布根目录: Path):
    """创建压缩包"""
    print("\n=== 创建压缩包 ===")
    
    当前时间 = datetime.now().strftime("%Y%m%d_%H%M%S")
    压缩包名称 = f"L属性文法语义分析程序_v1.0.0_{当前时间}.zip"
    
    with zipfile.ZipFile(压缩包名称, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(发布根目录):
            for file in files:
                文件路径 = os.path.join(root, file)
                相对路径 = os.path.relpath(文件路径, 发布根目录.parent)
                zipf.write(文件路径, 相对路径)
                print(f"添加到压缩包: {相对路径}")
    
    print(f"\n压缩包创建完成: {压缩包名称}")
    print(f"压缩包大小: {os.path.getsize(压缩包名称) / 1024 / 1024:.2f} MB")
    
    return 压缩包名称

def 主函数():
    """主函数"""
    print("L属性文法语义分析程序 - 发布包创建脚本")
    print("=" * 60)
    
    try:
        # 创建发布目录
        发布根目录 = 创建发布目录()
        
        # 复制各类文件
        复制程序文件(发布根目录)
        复制文档文件(发布根目录)
        复制示例文件(发布根目录)
        复制测试文件(发布根目录)
        
        # 创建启动脚本和说明文件
        创建启动脚本(发布根目录)
        创建说明文件(发布根目录)
        
        # 创建压缩包
        压缩包名称 = 创建压缩包(发布根目录)
        
        print("\n" + "=" * 60)
        print("发布包创建完成！")
        print(f"发布目录: {发布根目录}")
        print(f"压缩包: {压缩包名称}")
        print("\n发布包包含:")
        print("- 完整的程序文件")
        print("- 详细的项目文档")
        print("- 丰富的示例文件")
        print("- 完整的测试脚本")
        print("- 跨平台启动脚本")
        
        return True
        
    except Exception as e:
        print(f"\n发布包创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        成功 = 主函数()
        if 成功:
            print("\n🎉 发布包创建成功！")
        else:
            print("\n❌ 发布包创建失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序运行异常: {e}")
        sys.exit(1)
