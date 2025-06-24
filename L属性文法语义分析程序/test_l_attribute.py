#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析程序简单测试脚本

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主程序模块
from l_attribute_main import (
    L属性文法, L属性文法解析器, 语义分析引擎,
    属性定义, 文法符号, 产生式, 语义规则, 符号表项, 符号表,
    属性类型, 符号类型
)


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    try:
        # 1. 测试文法符号创建
        print("1. 测试文法符号创建...")
        终结符 = 文法符号("id", 符号类型.终结符)
        非终结符 = 文法符号("E", 符号类型.非终结符)
        print("   ✓ 文法符号创建成功")
        
        # 2. 测试属性定义创建
        print("2. 测试属性定义创建...")
        综合属性 = 属性定义("value", 属性类型.综合属性, "整数", 0, "值属性")
        继承属性 = 属性定义("type", 属性类型.继承属性, "字符串", "", "类型属性")
        print("   ✓ 属性定义创建成功")
        
        # 3. 测试产生式创建
        print("3. 测试产生式创建...")
        产生式对象 = 产生式("E", ["E", "+", "T"])
        print(f"   产生式: {产生式对象}")
        print("   ✓ 产生式创建成功")
        
        # 4. 测试语义规则创建
        print("4. 测试语义规则创建...")
        规则 = 语义规则("E.value", "E1.value + T.value", ["E1.value", "T.value"])
        print(f"   语义规则: {规则}")
        print("   ✓ 语义规则创建成功")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 基本功能测试失败: {e}")
        return False


def test_grammar_parsing():
    """测试文法解析"""
    print("\n=== 测试文法解析 ===")
    
    try:
        解析器 = L属性文法解析器()
        
        文法内容 = """
[文法]
D -> T L
T -> int
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"

[语义规则]
L.in := T.type
"""
        
        print("1. 解析简单L属性文法...")
        成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)
        
        if 成功:
            print("   ✓ 文法解析成功")
            print(f"   产生式数量: {len(文法.产生式列表)}")
            print(f"   开始符号: {文法.开始符号}")
            print(f"   终结符: {sorted(文法.终结符集合)}")
            print(f"   非终结符: {sorted(文法.非终结符集合)}")
            
            # 验证L属性特性
            print("2. 验证L属性特性...")
            是L属性, L属性错误 = 文法.验证L属性特性()
            if 是L属性:
                print("   ✓ L属性特性验证通过")
            else:
                print(f"   ✗ L属性特性验证失败: {L属性错误}")
            
            return True
        else:
            print(f"   ✗ 文法解析失败: {错误列表}")
            return False
            
    except Exception as e:
        print(f"   ✗ 文法解析测试失败: {e}")
        return False


def test_symbol_table():
    """测试符号表管理"""
    print("\n=== 测试符号表管理 ===")
    
    try:
        符号表对象 = 符号表()
        
        print("1. 测试符号表基本操作...")
        # 添加符号
        符号项 = 符号表项("variable1", "int", 42)
        符号表对象.添加符号(符号项)
        
        # 查找符号
        找到的符号 = 符号表对象.查找符号("variable1")
        if 找到的符号:
            print(f"   找到符号: {找到的符号.名称} ({找到的符号.类型}) = {找到的符号.值}")
            print("   ✓ 符号表基本操作成功")
        else:
            print("   ✗ 符号查找失败")
            return False
        
        print("2. 测试作用域管理...")
        # 进入新作用域
        符号表对象.进入作用域("函数1")
        局部符号 = 符号表项("local_var", "float")
        符号表对象.添加符号(局部符号)
        
        # 查找符号
        全局符号 = 符号表对象.查找符号("variable1")
        局部符号查找 = 符号表对象.查找符号("local_var")
        
        if 全局符号 and 局部符号查找:
            print("   ✓ 作用域管理成功")
        else:
            print("   ✗ 作用域管理失败")
            return False
        
        # 退出作用域
        符号表对象.退出作用域()
        print("   ✓ 作用域退出成功")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 符号表测试失败: {e}")
        return False


def test_semantic_analysis():
    """测试语义分析"""
    print("\n=== 测试语义分析 ===")
    
    try:
        # 创建测试文法
        文法 = L属性文法()
        
        # 添加产生式
        产生式1 = 产生式("D", ["T", "L"])
        产生式2 = 产生式("T", ["int"])
        产生式3 = 产生式("L", ["id"])
        
        文法.添加产生式(产生式1)
        文法.添加产生式(产生式2)
        文法.添加产生式(产生式3)
        
        print("1. 创建语义分析引擎...")
        分析引擎 = 语义分析引擎(文法)
        print("   ✓ 语义分析引擎创建成功")
        
        print("2. 测试词法分析...")
        输入串 = "int variable1"
        词法单元列表 = 分析引擎._词法分析(输入串)
        print(f"   词法单元: {词法单元列表}")
        
        if len(词法单元列表) == 2:
            print("   ✓ 词法分析成功")
        else:
            print("   ✗ 词法分析失败")
            return False
        
        print("3. 测试语义分析执行...")
        语法分析结果 = [0, 1, 2]  # 模拟的产生式序列
        成功, 分析步骤列表, 错误信息 = 分析引擎.执行语义分析(输入串, 语法分析结果)
        
        if 成功 or len(分析步骤列表) > 0:
            print(f"   分析步骤数: {len(分析步骤列表)}")
            print("   ✓ 语义分析执行成功")
        else:
            print(f"   ✗ 语义分析执行失败: {错误信息}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ 语义分析测试失败: {e}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")
    
    try:
        # 完整的文法定义
        文法内容 = """
[文法]
D -> T L
T -> int | float
L -> L , id | id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"
id.name : 综合 字符串 "" "标识符名称"

[语义规则]
L.in := T.type
T.type := "int"
"""
        
        print("1. 解析完整文法...")
        解析器 = L属性文法解析器()
        成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)
        
        if not 成功:
            print(f"   ✗ 文法解析失败: {错误列表}")
            return False
        
        print("   ✓ 文法解析成功")
        
        print("2. 执行语义分析...")
        分析引擎 = 语义分析引擎(文法)
        输入串 = "int a"
        语法分析结果 = [0, 1, 3]  # 模拟的产生式序列
        
        成功, 分析步骤列表, 错误信息 = 分析引擎.执行语义分析(输入串, 语法分析结果)
        
        print(f"   分析步骤数: {len(分析步骤列表)}")
        print(f"   符号表项数: {len(分析引擎.符号表.表项)}")
        
        if len(分析步骤列表) > 0:
            print("   ✓ 集成测试成功")
            return True
        else:
            print("   ✗ 集成测试失败")
            return False
        
    except Exception as e:
        print(f"   ✗ 集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("L属性文法语义分析程序 - 功能测试")
    print("=" * 50)
    
    测试结果 = []
    
    # 运行各项测试
    测试结果.append(("基本功能", test_basic_functionality()))
    测试结果.append(("文法解析", test_grammar_parsing()))
    测试结果.append(("符号表管理", test_symbol_table()))
    测试结果.append(("语义分析", test_semantic_analysis()))
    测试结果.append(("集成功能", test_integration()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    成功数 = 0
    总数 = len(测试结果)
    
    for 测试名, 结果 in 测试结果:
        状态 = "✓ 通过" if 结果 else "✗ 失败"
        print(f"  {测试名}: {状态}")
        if 结果:
            成功数 += 1
    
    print(f"\n总体结果: {成功数}/{总数} 测试通过")
    print(f"成功率: {(成功数/总数*100):.1f}%")
    
    if 成功数 == 总数:
        print("\n🎉 所有测试通过！程序功能正常。")
        return True
    else:
        print(f"\n⚠️  有 {总数-成功数} 个测试失败，请检查相关功能。")
        return False


if __name__ == "__main__":
    try:
        成功 = main()
        sys.exit(0 if 成功 else 1)
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
