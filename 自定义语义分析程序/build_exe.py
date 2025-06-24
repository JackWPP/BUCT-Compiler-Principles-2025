#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义语义分析程序打包脚本

使用PyInstaller将程序打包为可执行文件

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def 检查环境():
    """检查打包环境"""
    print("检查打包环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 错误: 未安装PyInstaller")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查主程序文件
    if not os.path.exists("custom_semantic_analyzer.py"):
        print("❌ 错误: 找不到主程序文件 custom_semantic_analyzer.py")
        return False
    
    print("✓ 环境检查通过")
    return True

def 清理旧文件():
    """清理之前的打包文件"""
    print("清理旧的打包文件...")
    
    清理目录 = ["build", "dist", "__pycache__"]
    清理文件 = ["*.spec"]
    
    for 目录 in 清理目录:
        if os.path.exists(目录):
            shutil.rmtree(目录)
            print(f"✓ 删除目录: {目录}")
    
    # 删除spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✓ 删除文件: {spec_file}")

def 创建图标文件():
    """创建程序图标（如果不存在）"""
    图标文件 = "icon.ico"
    
    if not os.path.exists(图标文件):
        print("创建默认图标文件...")
        # 这里可以添加创建默认图标的代码
        # 暂时跳过图标创建
        print("⚠️ 警告: 未找到图标文件，将使用默认图标")
        return None
    
    return 图标文件

def 执行打包():
    """执行PyInstaller打包"""
    print("开始打包程序...")
    
    # 打包参数
    打包命令 = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 打包为单个文件
        "--windowed",                   # Windows下隐藏控制台窗口
        "--name=自定义语义分析程序",      # 可执行文件名称
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不询问确认
    ]
    
    # 添加图标（如果存在）
    图标文件 = 创建图标文件()
    if 图标文件:
        打包命令.extend(["--icon", 图标文件])
    
    # 添加隐藏导入（如果需要）
    隐藏导入 = [
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.filedialog",
        "tkinter.messagebox"
    ]
    
    for 模块 in 隐藏导入:
        打包命令.extend(["--hidden-import", 模块])
    
    # 添加主程序文件
    打包命令.append("custom_semantic_analyzer.py")
    
    print(f"执行命令: {' '.join(打包命令)}")
    
    try:
        # 执行打包命令
        result = subprocess.run(打包命令, check=True, capture_output=True, text=True)
        print("✓ 打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def 创建发布包():
    """创建完整的发布包"""
    print("创建发布包...")
    
    发布目录 = "release"
    
    # 创建发布目录
    if os.path.exists(发布目录):
        shutil.rmtree(发布目录)
    os.makedirs(发布目录)
    
    # 复制可执行文件
    可执行文件 = "dist/自定义语义分析程序.exe"
    if os.path.exists(可执行文件):
        shutil.copy2(可执行文件, 发布目录)
        print(f"✓ 复制可执行文件: {可执行文件}")
    else:
        print(f"❌ 错误: 找不到可执行文件 {可执行文件}")
        return False
    
    # 复制文档文件
    文档文件列表 = [
        "README.md",
        "用户手册.md",
        "技术文档.md",
        "sample_grammars.txt",
        "requirements.txt"
    ]
    
    for 文件 in 文档文件列表:
        if os.path.exists(文件):
            shutil.copy2(文件, 发布目录)
            print(f"✓ 复制文档: {文件}")
        else:
            print(f"⚠️ 警告: 找不到文件 {文件}")
    
    # 创建示例目录
    示例目录 = os.path.join(发布目录, "examples")
    os.makedirs(示例目录, exist_ok=True)
    
    # 复制测试文件（可选）
    测试文件列表 = [
        "test_s_attribute.py",
        "test_l_attribute.py", 
        "test_dependency_graph.py",
        "comprehensive_test.py"
    ]
    
    for 文件 in 测试文件列表:
        if os.path.exists(文件):
            shutil.copy2(文件, 示例目录)
            print(f"✓ 复制测试文件: {文件}")
    
    print(f"✓ 发布包创建完成: {发布目录}")
    return True

def 验证打包结果():
    """验证打包结果"""
    print("验证打包结果...")
    
    可执行文件 = "release/自定义语义分析程序.exe"
    
    if not os.path.exists(可执行文件):
        print(f"❌ 错误: 找不到可执行文件 {可执行文件}")
        return False
    
    # 检查文件大小
    文件大小 = os.path.getsize(可执行文件)
    文件大小MB = 文件大小 / (1024 * 1024)
    print(f"✓ 可执行文件大小: {文件大小MB:.1f} MB")
    
    if 文件大小MB > 100:
        print("⚠️ 警告: 可执行文件较大，可能包含不必要的依赖")
    
    # 检查发布包内容
    发布目录 = "release"
    文件列表 = os.listdir(发布目录)
    print(f"✓ 发布包包含 {len(文件列表)} 个文件/目录:")
    for 文件 in sorted(文件列表):
        print(f"  - {文件}")
    
    return True

def 生成安装说明():
    """生成安装和使用说明"""
    安装说明 = """# 自定义语义分析程序 - 安装说明

## 系统要求
- Windows 7/8/10/11 (64位)
- 至少 100MB 可用磁盘空间

## 安装步骤
1. 下载发布包并解压到任意目录
2. 双击运行 `自定义语义分析程序.exe`
3. 程序将自动启动图形界面

## 使用说明
1. 参考 `用户手册.md` 了解详细使用方法
2. 查看 `sample_grammars.txt` 获取示例文法
3. 阅读 `技术文档.md` 了解技术细节

## 故障排除
- 如果程序无法启动，请检查系统是否支持
- 如果遇到错误，请查看用户手册的故障排除部分
- 技术支持：王海翔 (2021060187)

## 文件说明
- `自定义语义分析程序.exe`: 主程序文件
- `README.md`: 项目说明
- `用户手册.md`: 详细使用说明
- `技术文档.md`: 技术实现文档
- `sample_grammars.txt`: 示例文法集合
- `examples/`: 测试程序和示例

---
版本: v1.0.0
作者: 王海翔 (2021060187)
班级: 计科2203
"""
    
    with open("release/安装说明.txt", "w", encoding="utf-8") as f:
        f.write(安装说明)
    
    print("✓ 生成安装说明文件")

def main():
    """主函数"""
    print("自定义语义分析程序打包工具")
    print("=" * 50)
    
    try:
        # 检查环境
        if not 检查环境():
            return False
        
        # 清理旧文件
        清理旧文件()
        
        # 执行打包
        if not 执行打包():
            return False
        
        # 创建发布包
        if not 创建发布包():
            return False
        
        # 验证结果
        if not 验证打包结果():
            return False
        
        # 生成安装说明
        生成安装说明()
        
        print("\n" + "=" * 50)
        print("🎉 打包完成！")
        print("发布包位置: release/")
        print("可执行文件: release/自定义语义分析程序.exe")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 打包过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
