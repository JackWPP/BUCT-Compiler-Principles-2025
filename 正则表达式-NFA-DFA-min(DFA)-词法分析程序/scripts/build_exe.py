#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词法分析器GUI程序打包脚本
使用PyInstaller将Python程序打包成EXE可执行文件
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """构建EXE文件"""
    print("开始构建词法分析器GUI程序...")
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    main_script = current_dir / "lexical_analyzer_gui.py"
    
    if not main_script.exists():
        print(f"错误：找不到主程序文件 {main_script}")
        return False
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--name=词法分析器GUI",  # 设置程序名称
        "--icon=NONE",  # 暂时不设置图标
        "--add-data=lexical_rules.txt;.",  # 包含规则文件
        "--add-data=sample_input.txt;.",  # 包含示例输入文件
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问确认
        str(main_script)
    ]
    
    try:
        print("执行打包命令...")
        print(" ".join(cmd))
        
        # 执行打包命令
        result = subprocess.run(cmd, cwd=current_dir, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("\n✅ 打包成功！")
            
            # 查找生成的EXE文件
            dist_dir = current_dir / "dist"
            exe_files = list(dist_dir.glob("*.exe"))
            
            if exe_files:
                exe_file = exe_files[0]
                print(f"📁 EXE文件位置: {exe_file}")
                print(f"📊 文件大小: {exe_file.stat().st_size / (1024*1024):.1f} MB")
                
                # 创建启动脚本
                create_launcher(exe_file)
                
                print("\n🎉 构建完成！您可以直接运行生成的EXE文件。")
                return True
            else:
                print("❌ 未找到生成的EXE文件")
                return False
        else:
            print("❌ 打包失败！")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出现异常: {e}")
        return False

def create_launcher(exe_file):
    """创建启动脚本"""
    launcher_content = f'''@echo off
chcp 65001 > nul
echo 启动词法分析器GUI程序...
echo.
"{exe_file.name}"
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查！
    pause
)
'''
    
    launcher_path = exe_file.parent / "启动词法分析器.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"📝 已创建启动脚本: {launcher_path}")

def clean_build_files():
    """清理构建文件"""
    current_dir = Path(__file__).parent
    
    # 要清理的目录和文件
    cleanup_items = [
        current_dir / "build",
        current_dir / "__pycache__",
        current_dir / "词法分析器GUI.spec"
    ]
    
    for item in cleanup_items:
        if item.exists():
            if item.is_dir():
                import shutil
                shutil.rmtree(item)
                print(f"🗑️ 已删除目录: {item}")
            else:
                item.unlink()
                print(f"🗑️ 已删除文件: {item}")

if __name__ == "__main__":
    print("=" * 50)
    print("    词法分析器GUI程序打包工具")
    print("=" * 50)
    print()
    
    # 检查依赖
    try:
        import PyInstaller
        print(f"✅ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 未安装PyInstaller，请先运行: pip install pyinstaller")
        sys.exit(1)
    
    # 构建EXE
    success = build_exe()
    
    if success:
        print("\n是否清理构建临时文件？(y/n): ", end="")
        choice = input().lower().strip()
        if choice in ['y', 'yes', '是', '']:
            clean_build_files()
            print("✅ 清理完成")
    
    print("\n按任意键退出...")
    input()