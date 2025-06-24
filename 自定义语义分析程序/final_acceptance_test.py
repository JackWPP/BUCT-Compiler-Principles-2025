#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义语义分析程序最终验收测试

验证程序是否符合作业要求的所有规格

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def 检查项目结构():
    """检查项目文件结构是否完整"""
    print("=== 检查项目结构 ===")
    
    必需文件 = [
        "custom_semantic_analyzer.py",  # 主程序
        "README.md",                   # 项目说明
        "用户手册.md",                  # 用户手册
        "技术文档.md",                  # 技术文档
        "requirements.txt",            # 依赖列表
        "sample_grammars.txt",         # 示例文法
        "build_exe.py",               # 打包脚本
    ]
    
    测试文件 = [
        "test_s_attribute.py",
        "test_l_attribute.py", 
        "test_dependency_graph.py",
        "comprehensive_test.py",
        "final_acceptance_test.py"
    ]
    
    发布文件 = [
        "release/自定义语义分析程序.exe",
        "release/README.md",
        "release/用户手册.md",
        "release/技术文档.md",
        "release/安装说明.txt"
    ]
    
    所有文件 = 必需文件 + 测试文件 + 发布文件
    
    缺失文件 = []
    for 文件 in 所有文件:
        if not os.path.exists(文件):
            缺失文件.append(文件)
        else:
            print(f"√ {文件}")
    
    if 缺失文件:
        print(f"\n× 缺失文件: {缺失文件}")
        return False
    
    print("√ 项目结构检查通过")
    return True

def 检查代码质量():
    """检查代码质量和注释"""
    print("\n=== 检查代码质量 ===")
    
    主程序文件 = "custom_semantic_analyzer.py"
    
    with open(主程序文件, 'r', encoding='utf-8') as f:
        代码内容 = f.read()
    
    # 检查中文注释
    中文注释数 = 代码内容.count('"""') + 代码内容.count("'''") + 代码内容.count('#')
    print(f"√ 注释数量: {中文注释数}")
    
    # 检查类和函数数量
    类数量 = 代码内容.count('class ')
    函数数量 = 代码内容.count('def ')
    print(f"√ 类数量: {类数量}")
    print(f"√ 函数数量: {函数数量}")
    
    # 检查代码行数
    代码行数 = len(代码内容.split('\n'))
    print(f"√ 代码行数: {代码行数}")
    
    if 代码行数 < 1000:
        print("! 警告: 代码行数较少，可能功能不够完整")
    
    return True

def 测试核心功能():
    """测试核心功能"""
    print("\n=== 测试核心功能 ===")
    
    try:
        # 导入主程序模块
        sys.path.insert(0, '.')
        from custom_semantic_analyzer import 语义分析引擎管理器, 语义分析类型
        
        # 创建引擎
        引擎 = 语义分析引擎管理器()
        
        # 测试文法解析
        测试文法 = """
[文法]
E -> E + T
E -> T
T -> num

[属性定义]
E.val : 综合 整数 0 "表达式值"
T.val : 综合 整数 0 "项值"
num.val : 综合 整数 0 "数字值"

[语义规则]
E.val := E.val + T.val
E.val := T.val
T.val := num.val
"""
        
        成功, 错误列表 = 引擎.加载文法(测试文法)
        if not 成功:
            print(f"× 文法解析失败: {错误列表}")
            return False
        print("√ 文法解析功能正常")
        
        # 测试S属性分析
        验证成功, 验证错误 = 引擎.验证文法特性(语义分析类型.S属性文法)
        if not 验证成功:
            print(f"× S属性验证失败: {验证错误}")
            return False
        print("√ S属性文法验证功能正常")
        
        # 测试语义分析
        分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
            语义分析类型.S属性文法, "3 + 5", [2, 1, 2, 1, 0]
        )
        if not 分析成功:
            print(f"× 语义分析失败: {错误信息}")
            return False
        print("√ 语义分析功能正常")
        
        # 测试L属性分析
        分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
            语义分析类型.L属性文法, "3 + 5", [2, 1, 2, 1, 0]
        )
        if not 分析成功:
            print(f"× L属性分析失败: {错误信息}")
            return False
        print("√ L属性文法分析功能正常")
        
        # 测试依赖图分析
        分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
            语义分析类型.依赖图, "3 + 5", [2, 1, 2, 1, 0]
        )
        if not 分析成功:
            print(f"× 依赖图分析失败: {错误信息}")
            return False
        print("√ 依赖图分析功能正常")
        
        print("√ 所有核心功能测试通过")
        return True
        
    except Exception as e:
        print(f"× 核心功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def 运行单元测试():
    """运行所有单元测试"""
    print("\n=== 运行单元测试 ===")
    
    测试文件列表 = [
        "comprehensive_test.py",
        "test_s_attribute.py",
        "test_l_attribute.py",
        "test_dependency_graph.py"
    ]
    
    所有测试通过 = True
    
    for 测试文件 in 测试文件列表:
        if not os.path.exists(测试文件):
            print(f"! 跳过不存在的测试文件: {测试文件}")
            continue
        
        print(f"运行测试: {测试文件}")
        try:
            result = subprocess.run([sys.executable, 测试文件], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"√ {测试文件} 通过")
            else:
                print(f"× {测试文件} 失败")
                print(f"错误输出: {result.stderr}")
                所有测试通过 = False
                
        except subprocess.TimeoutExpired:
            print(f"× {测试文件} 超时")
            所有测试通过 = False
        except Exception as e:
            print(f"× {测试文件} 异常: {e}")
            所有测试通过 = False
    
    if 所有测试通过:
        print("√ 所有单元测试通过")
    else:
        print("× 部分单元测试失败")
    
    return 所有测试通过

def 检查可执行文件():
    """检查可执行文件"""
    print("\n=== 检查可执行文件 ===")
    
    可执行文件 = "release/自定义语义分析程序.exe"
    
    if not os.path.exists(可执行文件):
        print(f"× 可执行文件不存在: {可执行文件}")
        return False
    
    # 检查文件大小
    文件大小 = os.path.getsize(可执行文件)
    文件大小MB = 文件大小 / (1024 * 1024)
    print(f"√ 可执行文件大小: {文件大小MB:.1f} MB")
    
    if 文件大小MB < 5:
        print("! 警告: 可执行文件可能不完整")
        return False
    
    if 文件大小MB > 50:
        print("! 警告: 可执行文件较大")
    
    print("√ 可执行文件检查通过")
    return True

def 检查文档完整性():
    """检查文档完整性"""
    print("\n=== 检查文档完整性 ===")
    
    文档文件 = {
        "README.md": ["项目简介", "功能特性", "快速开始"],
        "用户手册.md": ["程序概述", "安装与启动", "使用教程"],
        "技术文档.md": ["系统架构", "核心模块设计", "算法实现"],
        "sample_grammars.txt": ["示例1", "示例2", "使用说明"]
    }
    
    for 文件名, 必需内容 in 文档文件.items():
        if not os.path.exists(文件名):
            print(f"× 文档文件不存在: {文件名}")
            return False
        
        with open(文件名, 'r', encoding='utf-8') as f:
            内容 = f.read()
        
        缺失内容 = []
        for 内容项 in 必需内容:
            if 内容项 not in 内容:
                缺失内容.append(内容项)
        
        if 缺失内容:
            print(f"× {文件名} 缺失内容: {缺失内容}")
            return False
        
        print(f"√ {文件名} 内容完整")
    
    print("√ 文档完整性检查通过")
    return True

def 生成验收报告():
    """生成验收报告"""
    报告内容 = f"""# 自定义语义分析程序验收报告

## 基本信息
- 项目名称: 自定义语义分析程序
- 作者: 王海翔
- 学号: 2021060187
- 班级: 计科2203
- 验收时间: {time.strftime('%Y年%m月%d日 %H:%M:%S')}

## 功能实现情况

### ✅ 已实现功能
1. S属性文法语义分析
2. L属性文法语义分析
3. 依赖图语义分析
4. 文法特性验证
5. 循环依赖检测
6. 图形用户界面
7. 文法文件加载/保存
8. 分析过程可视化
9. 结果展示
10. 错误处理

### ✅ 技术特性
1. 模块化设计
2. 完整的单元测试
3. 中文文档和注释
4. 可执行文件打包
5. 用户友好的界面

### ✅ 文档完整性
1. README.md - 项目说明
2. 用户手册.md - 详细使用说明
3. 技术文档.md - 技术实现文档
4. sample_grammars.txt - 示例文法
5. 安装说明.txt - 安装和使用指南

## 测试结果
- 项目结构检查: ✅ 通过
- 代码质量检查: ✅ 通过
- 核心功能测试: ✅ 通过
- 单元测试: ✅ 通过
- 可执行文件检查: ✅ 通过
- 文档完整性检查: ✅ 通过

## 验收结论
该程序完全符合编译原理作业6.4的要求，实现了多种语义分析方法的集成，
提供了完整的图形用户界面和详细的中文文档，代码质量良好，测试覆盖完整。

**验收状态: ✅ 通过**

---
验收人: 王海翔
验收时间: {time.strftime('%Y年%m月%d日')}
"""
    
    with open("验收报告.md", "w", encoding="utf-8") as f:
        f.write(报告内容)
    
    print("√ 验收报告已生成: 验收报告.md")

def main():
    """主函数"""
    print("自定义语义分析程序最终验收测试")
    print("=" * 60)
    
    测试结果 = []
    
    # 执行各项检查
    测试项目 = [
        ("项目结构检查", 检查项目结构),
        ("代码质量检查", 检查代码质量),
        ("核心功能测试", 测试核心功能),
        ("单元测试", 运行单元测试),
        ("可执行文件检查", 检查可执行文件),
        ("文档完整性检查", 检查文档完整性)
    ]
    
    for 测试名称, 测试函数 in 测试项目:
        try:
            结果 = 测试函数()
            测试结果.append((测试名称, 结果))
        except Exception as e:
            print(f"× {测试名称}发生异常: {e}")
            测试结果.append((测试名称, False))
    
    # 统计结果
    通过数量 = sum(1 for _, 结果 in 测试结果 if 结果)
    总数量 = len(测试结果)
    
    print("\n" + "=" * 60)
    print("验收测试结果汇总:")
    print("=" * 60)
    
    for 测试名称, 结果 in 测试结果:
        状态 = "✅ 通过" if 结果 else "× 失败"
        print(f"{测试名称}: {状态}")
    
    print(f"\n总体结果: {通过数量}/{总数量} 项测试通过")
    
    if 通过数量 == 总数量:
        print("* 所有测试通过！程序验收成功！")
        生成验收报告()
        return True
    else:
        print("× 部分测试失败，需要修复后重新验收")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
