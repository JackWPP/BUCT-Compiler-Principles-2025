# -*- coding: utf-8 -*-
"""
依赖图语义分析程序打包脚本

使用PyInstaller将Python程序打包为可执行文件

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # Windows下不显示控制台
        '--name=依赖图语义分析器',        # 可执行文件名称
        '--add-data=sample_grammar.txt;.',  # 添加示例文件
        '--add-data=test_cases.txt;.',      # 添加测试用例文件
        'dependency_graph_main.py'          # 主程序文件
    ]

    try:
        # 执行PyInstaller命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_release_package():
    """创建发布包"""
    print("创建发布包...")
    
    # 创建发布包目录
    release_dir = Path("发布包")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_file = Path("dist/依赖图语义分析器.exe")
    if exe_file.exists():
        shutil.copy2(exe_file, release_dir / "依赖图语义分析器.exe")
        print("✓ 复制可执行文件")
    else:
        print("✗ 可执行文件不存在")
        return False
    
    # 复制文档文件
    docs_to_copy = [
        "sample_grammar.txt",
        "test_cases.txt",
        "requirements.txt"
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir / doc)
            print(f"✓ 复制文档: {doc}")
    
    # 创建使用说明文件
    create_usage_guide(release_dir)
    
    # 创建启动脚本
    create_launch_script(release_dir)
    
    # 创建发布说明
    create_release_notes(release_dir)
    
    print("✓ 发布包创建完成")
    return True

def create_usage_guide(release_dir):
    """创建使用说明文件"""
    usage_content = """依赖图语义分析器 - 使用说明

快速开始：
1. 双击"依赖图语义分析器.exe"启动程序
2. 在"属性文法输入"标签页中输入属性文法
3. 点击"解析文法"按钮解析文法
4. 在"依赖图构建"标签页中输入语法分析结果
5. 点击"构建依赖图"按钮构建依赖图
6. 在"语义分析过程"标签页中执行语义分析
7. 在"依赖图可视化"标签页中查看依赖图

系统要求：
- Windows 7/8/10/11
- 无需安装Python环境
- 无需安装额外依赖

文法格式：
属性文法包含三个部分：

[文法]
- 使用 -> 分隔左部和右部
- 使用 | 分隔多个候选
- 支持 ε 产生式

[属性定义]
- 格式：符号名.属性名 : 属性类型
- 属性类型：综合属性 或 继承属性

[语义规则]
- 格式：目标属性 := 表达式 # 产生式编号
- 支持属性引用和算术表达式

示例文法：
E -> E + T | T
T -> T * F | F
F -> ( E ) | id

E.val : 综合属性
T.val : 综合属性
F.val : 综合属性
id.lexval : 综合属性

E.val := E.val + T.val  # 0
E.val := T.val          # 1
T.val := T.val * F.val  # 2
T.val := F.val          # 3
F.val := E.val          # 4
F.val := id.lexval      # 5

功能说明：
- 属性文法输入：输入和编辑属性文法
- 依赖图构建：根据语法分析结果构建依赖图
- 语义分析过程：执行基于依赖图的语义分析
- 依赖图可视化：查看依赖图的图形表示
- 帮助：详细的使用说明和理论介绍

技术支持：
如有问题请联系：
作者：王海翔
学号：2021060187
班级：计科2203
"""
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print("✓ 创建使用说明文件")

def create_launch_script(release_dir):
    """创建启动脚本"""
    script_content = """@echo off
chcp 65001 > nul
title 依赖图语义分析器
echo 启动依赖图语义分析器...
echo.
start "" "依赖图语义分析器.exe"
"""
    
    with open(release_dir / "启动依赖图语义分析器.bat", 'w', encoding='gbk') as f:
        f.write(script_content)
    
    print("✓ 创建启动脚本")

def create_release_notes(release_dir):
    """创建发布说明"""
    notes_content = """依赖图语义分析器 - 发布说明

版本信息：
- 版本号：v1.0
- 发布日期：2024年12月
- 作者：王海翔 (2021060187)

主要功能：
✓ 完整的依赖图语义分析实现
✓ 属性文法解析和验证
✓ 依赖图构建和可视化
✓ 循环依赖检测
✓ 拓扑排序算法
✓ 基于依赖图的语义分析
✓ 直观的GUI界面
✓ 完整的测试用例

技术特点：
- 支持综合属性和继承属性
- 自动检测循环依赖
- 可视化依赖关系
- 完整的错误检测机制
- 支持复杂属性表达式

文件说明：
- 依赖图语义分析器.exe：主程序
- sample_grammar.txt：示例文法
- test_cases.txt：测试用例
- 使用说明.txt：快速使用指南
- 启动依赖图语义分析器.bat：启动脚本

安装说明：
1. 解压所有文件到同一目录
2. 双击"依赖图语义分析器.exe"或"启动依赖图语义分析器.bat"
3. 无需安装Python或其他依赖

更新日志：
v1.0 (2024-12)
- 初始版本发布
- 实现完整的依赖图语义分析功能
- 提供GUI界面和可视化功能
- 包含完整的测试用例

技术支持：
如遇到问题，请检查：
1. 文法格式是否正确
2. 语法分析结果是否有效
3. 系统是否支持（Windows 7+）

联系方式：
作者：王海翔
学号：2021060187
班级：计科2203
"""
    
    with open(release_dir / "发布说明.txt", 'w', encoding='utf-8') as f:
        f.write(notes_content)
    
    print("✓ 创建发布说明")

def get_file_size(file_path):
    """获取文件大小（MB）"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    return "未知"

def main():
    """主函数"""
    print("依赖图语义分析器打包脚本")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        return
    
    # 创建发布包
    if not create_release_package():
        return
    
    # 显示结果
    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"可执行文件大小: {get_file_size('dist/依赖图语义分析器.exe')}")
    print(f"发布包位置: {os.path.abspath('发布包')}")
    print("\n可以运行以下命令测试：")
    print("cd 发布包")
    print("依赖图语义分析器.exe")

if __name__ == "__main__":
    main()
