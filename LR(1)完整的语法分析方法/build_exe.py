# -*- coding: utf-8 -*-
"""
LR(1)语法分析器可执行文件构建脚本
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
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False

def build_executable():
    """构建可执行文件"""
    print("开始构建LR(1)语法分析器可执行文件...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # Windows下不显示控制台
        "--name=LR1语法分析器",          # 可执行文件名称
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--add-data=sample_input.txt;.", # 添加示例文件
        "--add-data=test_cases.txt;.",   # 添加测试用例
        "lr1_main.py"                   # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        print("执行构建命令...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
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
    exe_path = Path("dist/LR1语法分析器.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "LR1语法分析器.exe")
        print("✅ 可执行文件已复制")
    else:
        print("❌ 找不到可执行文件")
        return False
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "requirements.txt", 
        "sample_input.txt",
        "test_cases.txt",
        "项目总结.md",
        "作业要求.md"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"✅ {file_name} 已复制")
    
    # 创建使用说明文件
    create_usage_instructions(release_dir)
    
    # 创建发布说明文件
    create_release_notes(release_dir)
    
    print(f"✅ 发布包已创建在: {release_dir}")
    return True

def create_usage_instructions(release_dir):
    """创建使用说明文件"""
    usage_content = """LR(1)语法分析器使用说明

=== 快速开始 ===

1. 双击运行 LR1语法分析器.exe
2. 在"文法输入"标签页输入文法规则
3. 点击"解析文法"和"构建分析器"
4. 在"语法分析过程"标签页输入要分析的字符串
5. 点击"开始分析"查看结果

=== 文法格式 ===

格式: 左部 -> 右部1 | 右部2 | ...

示例:
E -> E + T | T
T -> T * F | F  
F -> ( E ) | id

=== 功能说明 ===

• 文法输入: 输入和编辑上下文无关文法
• LR(1)分析表: 查看生成的分析表和冲突信息
• 语法分析过程: 执行语法分析并查看详细步骤
• 自动机可视化: 查看LR(1)自动机状态转换图
• 帮助: 详细的使用说明和算法原理

=== 注意事项 ===

• 确保文法格式正确
• 区分终结符和非终结符
• 检查是否存在冲突
• 大型文法可视化可能较慢

=== 技术支持 ===

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""
    
    with open(release_dir / "使用说明.txt", "w", encoding="utf-8") as f:
        f.write(usage_content)

def create_release_notes(release_dir):
    """创建发布说明文件"""
    release_content = """LR(1)语法分析器发布说明

=== 版本信息 ===
版本: 1.0.0
发布日期: 2025年6月
作者: 王海翔 (2021060187)

=== 功能特性 ===

✅ 完整的LR(1)语法分析实现
✅ 现代化的GUI界面
✅ 自动机可视化功能
✅ 详细的分析步骤显示
✅ 冲突检测和报告
✅ 文件导入导出功能
✅ 完善的错误处理

=== 系统要求 ===

• Windows 7/8/10/11
• 无需安装Python环境
• 建议内存: 512MB以上
• 建议磁盘空间: 100MB以上

=== 文件说明 ===

• LR1语法分析器.exe - 主程序
• README.md - 项目说明
• sample_input.txt - 示例文法
• test_cases.txt - 测试用例
• 使用说明.txt - 详细使用说明
• requirements.txt - 依赖包列表（开发用）

=== 更新日志 ===

v1.0.0 (2025-06-23)
- 首次发布
- 实现完整的LR(1)语法分析功能
- 提供GUI界面和可视化功能
- 包含详细的文档和测试用例

=== 已知问题 ===

• 某些复杂文法可能显示冲突警告但仍能正常分析
• 大型自动机的可视化可能较慢
• 建议使用标准的文法格式以获得最佳效果

=== 联系方式 ===

如有问题或建议，请联系:
学生: 王海翔
学号: 2021060187
班级: 计科2203
"""
    
    with open(release_dir / "发布说明.txt", "w", encoding="utf-8") as f:
        f.write(release_content)

def clean_build_files():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已删除 {dir_name}")
    
    import glob
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            os.remove(file_path)
            print(f"✅ 已删除 {file_path}")

def main():
    """主函数"""
    print("LR(1)语法分析器构建脚本")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return False
    
    # 检查主程序文件
    if not os.path.exists("lr1_main.py"):
        print("❌ 找不到主程序文件 lr1_main.py")
        return False
    
    try:
        # 构建可执行文件
        if not build_executable():
            return False
        
        # 创建发布包
        if not create_release_package():
            return False
        
        print("\n" + "=" * 50)
        print("🎉 构建完成！")
        print("可执行文件位置: dist/LR1语法分析器.exe")
        print("发布包位置: 发布包/")
        print("=" * 50)
        
        # 询问是否清理构建文件
        response = input("\n是否清理构建文件? (y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            clean_build_files()
        
        return True
        
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
