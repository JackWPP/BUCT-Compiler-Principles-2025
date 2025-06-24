# -*- coding: utf-8 -*-
"""
依赖图语义分析程序测试脚本

测试核心功能的正确性

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependency_graph_main import *

def test_grammar_parsing():
    """测试文法解析功能"""
    print("=== 测试文法解析功能 ===")
    
    解析器 = 属性文法解析器()
    
    # 测试文法内容
    文法内容 = """# 测试文法
[文法]
E -> T
T -> F
F -> id

[属性定义]
E.val : 综合属性
T.val : 综合属性
F.val : 综合属性
id.lexval : 综合属性

[语义规则]
E.val := T.val          # 0
T.val := F.val          # 1
F.val := id.lexval      # 2
"""
    
    成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)
    
    if 成功:
        print("✓ 文法解析成功")
        print(f"  产生式数量: {len(文法.产生式列表)}")
        print(f"  符号数量: {len(文法.符号表)}")
        print(f"  语义规则数量: {sum(len(规则列表) for 规则列表 in 文法.语义规则表.values())}")
        return 文法
    else:
        print("✗ 文法解析失败")
        for 错误 in 错误列表:
            print(f"  错误: {错误}")
        return None

def test_dependency_graph_construction(文法):
    """测试依赖图构建功能"""
    print("\n=== 测试依赖图构建功能 ===")
    
    if not 文法:
        print("✗ 文法为空，跳过测试")
        return None
    
    构建器 = 依赖图构建器(文法)

    # 测试语法分析结果：id (对应产生式序列: 2 1 0)
    语法分析结果 = [2, 1, 0]
    
    成功, 依赖图对象, 错误信息 = 构建器.构建依赖图(语法分析结果)
    
    if 成功:
        print("✓ 依赖图构建成功")
        print(f"  节点数量: {len(依赖图对象.节点表)}")
        print(f"  依赖关系数量: {sum(len(目标列表) for 目标列表 in 依赖图对象.邻接表.values())}")
        
        # 显示节点信息
        print("  节点列表:")
        for 节点ID, 节点 in 依赖图对象.节点表.items():
            print(f"    {节点ID}: {节点.属性名}")
        
        return 依赖图对象
    else:
        print("✗ 依赖图构建失败")
        print(f"  错误: {错误信息}")
        return None

def test_cycle_detection(依赖图对象):
    """测试循环依赖检测功能"""
    print("\n=== 测试循环依赖检测功能 ===")
    
    if not 依赖图对象:
        print("✗ 依赖图为空，跳过测试")
        return
    
    有循环, 循环路径 = 依赖图对象.检测循环依赖()
    
    if 有循环:
        print("✗ 检测到循环依赖")
        print(f"  循环路径: {' -> '.join(循环路径)}")
    else:
        print("✓ 未检测到循环依赖")

def test_topological_sort(依赖图对象):
    """测试拓扑排序功能"""
    print("\n=== 测试拓扑排序功能 ===")
    
    if not 依赖图对象:
        print("✗ 依赖图为空，跳过测试")
        return None
    
    成功, 计算顺序, 错误信息 = 依赖图对象.拓扑排序()
    
    if 成功:
        print("✓ 拓扑排序成功")
        print(f"  计算顺序: {' -> '.join(计算顺序)}")
        return 计算顺序
    else:
        print("✗ 拓扑排序失败")
        print(f"  错误: {错误信息}")
        return None

def test_semantic_analysis(文法, 依赖图对象):
    """测试语义分析功能"""
    print("\n=== 测试语义分析功能 ===")
    
    if not 文法 or not 依赖图对象:
        print("✗ 文法或依赖图为空，跳过测试")
        return
    
    分析引擎 = 语义分析引擎(文法)
    输入串 = "id"
    
    成功, 分析步骤列表, 错误信息 = 分析引擎.执行语义分析(依赖图对象, 输入串)
    
    if 成功:
        print("✓ 语义分析成功")
        print(f"  分析步骤数量: {len(分析步骤列表)}")
        print("  主要步骤:")
        for 步骤 in 分析步骤列表[:5]:  # 显示前5个步骤
            print(f"    步骤{步骤.步骤号}: {步骤.操作类型} - {步骤.描述}")
        if len(分析步骤列表) > 5:
            print(f"    ... 还有 {len(分析步骤列表) - 5} 个步骤")
    else:
        print("✗ 语义分析失败")
        print(f"  错误: {错误信息}")

def test_error_handling():
    """测试错误处理功能"""
    print("\n=== 测试错误处理功能 ===")
    
    解析器 = 属性文法解析器()
    
    # 测试错误的文法格式
    错误文法 = """
[文法]
E -> E +  # 缺少右部
T -> 
F -> id

[属性定义]
E.val 综合属性  # 缺少冒号

[语义规则]
E.val = E.val + T.val  # 错误的赋值符号
"""
    
    成功, 文法, 错误列表 = 解析器.解析文法文件(错误文法)
    
    if not 成功:
        print("✓ 错误检测正常")
        print(f"  检测到 {len(错误列表)} 个错误")
        for i, 错误 in enumerate(错误列表[:3]):  # 显示前3个错误
            print(f"    错误{i+1}: {错误}")
    else:
        print("✗ 错误检测异常，应该检测到错误")

def run_all_tests():
    """运行所有测试"""
    print("依赖图语义分析程序 - 功能测试")
    print("=" * 50)
    
    try:
        # 测试文法解析
        文法 = test_grammar_parsing()
        
        # 测试依赖图构建
        依赖图对象 = test_dependency_graph_construction(文法)
        
        # 测试循环依赖检测
        test_cycle_detection(依赖图对象)
        
        # 测试拓扑排序
        计算顺序 = test_topological_sort(依赖图对象)
        
        # 测试语义分析
        test_semantic_analysis(文法, 依赖图对象)
        
        # 测试错误处理
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
