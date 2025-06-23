#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LR语法分析器打包脚本
使用PyInstaller将Python程序打包为exe可执行文件

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['lr_parser_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sample_input.txt', '.'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'networkx',
        'numpy',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LR语法分析器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('lr_parser_gui.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 已创建PyInstaller规格文件: lr_parser_gui.spec")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "lr_parser_gui.spec"]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✓ exe文件构建成功！")
            
            # 检查生成的文件
            exe_path = Path("dist/LR语法分析器.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✓ 生成的exe文件: {exe_path}")
                print(f"✓ 文件大小: {size_mb:.1f} MB")
                return True
            else:
                print("✗ 未找到生成的exe文件")
                return False
        else:
            print("✗ exe文件构建失败")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("✗ 未找到pyinstaller命令，请确保PyInstaller已正确安装")
        return False
    except Exception as e:
        print(f"✗ 构建过程中出现错误: {e}")
        return False

def create_distribution():
    """创建发布包"""
    print("创建发布包...")
    
    dist_dir = Path("发布包")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # 复制exe文件
    exe_src = Path("dist/LR语法分析器.exe")
    if exe_src.exists():
        shutil.copy2(exe_src, dist_dir / "LR语法分析器.exe")
        print(f"✓ 已复制exe文件到: {dist_dir}")
    
    # 复制相关文件
    files_to_copy = [
        "README.md",
        "sample_input.txt",
        "test.md",
        "parsing_table_test.md"
    ]
    
    for file_name in files_to_copy:
        src_file = Path(file_name)
        if src_file.exists():
            shutil.copy2(src_file, dist_dir / file_name)
            print(f"✓ 已复制: {file_name}")
    
    # 创建使用说明
    usage_content = """
# LR语法分析器 - 使用说明

## 运行程序
双击 `LR语法分析器.exe` 即可运行程序。

## 功能说明
1. **文法输入**: 在"文法输入"标签页中输入上下文无关文法
2. **LR分析**: 执行LR类型判断，支持LR(0)、SLR(1)、LR(1)、LALR(1)
3. **分析表生成**: 生成各种LR方法的ACTION和GOTO分析表
4. **自动机可视化**: 查看LR(0)和LR(1)自动机状态转换图

## 测试文件
- `sample_input.txt`: 示例文法文件
- `test.md`: 详细测试用例
- `parsing_table_test.md`: 分析表功能测试文档

## 系统要求
- Windows 7/8/10/11
- 无需安装Python环境

## 注意事项
- 首次运行可能需要较长时间加载
- 大型文法的分析可能需要一些时间
- 建议在有足够内存的环境下运行

## 技术支持
如有问题，请参考README.md文档或联系开发者。
"""
    
    with open(dist_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print(f"✓ 发布包创建完成: {dist_dir.absolute()}")
    return True

def cleanup():
    """清理临时文件"""
    print("清理临时文件...")
    
    # 清理PyInstaller生成的临时文件
    temp_dirs = ["build", "__pycache__"]
    temp_files = ["lr_parser_gui.spec"]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"✓ 已删除临时目录: {temp_dir}")
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"✓ 已删除临时文件: {temp_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("LR语法分析器 - exe打包工具")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("lr_parser_gui.py"):
        print("✗ 错误: 未找到lr_parser_gui.py文件")
        print("请确保在正确的目录下运行此脚本")
        return False
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("✗ 无法安装PyInstaller，打包失败")
            return False
    
    try:
        # 创建规格文件
        create_spec_file()
        
        # 构建exe
        if not build_exe():
            return False
        
        # 创建发布包
        if not create_distribution():
            return False
        
        print("\n" + "=" * 60)
        print("✓ 打包完成！")
        print("✓ 可执行文件位置: 发布包/LR语法分析器.exe")
        print("✓ 发布包包含所有必要文件")
        print("=" * 60)
        
        # 询问是否清理临时文件
        response = input("\n是否清理临时文件？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            cleanup()
        
        return True
        
    except KeyboardInterrupt:
        print("\n✗ 用户中断操作")
        return False
    except Exception as e:
        print(f"\n✗ 打包过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n打包失败，请检查错误信息并重试")
        input("按回车键退出...")
        sys.exit(1)
    else:
        input("\n按回车键退出...")