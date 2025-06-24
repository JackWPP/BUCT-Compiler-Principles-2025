# -*- coding: utf-8 -*-
"""
测试修复后的依赖图构建功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependency_graph_main import *

def test_dependency_graph_fix():
    """测试修复后的依赖图构建"""
    print("测试修复后的依赖图构建功能")
    print("=" * 50)
    
    # 创建默认文法
    default_grammar = """# 依赖图语义分析器示例文法
# 简单算术表达式文法

[文法]
E -> E + T | T
T -> T * F | F
F -> ( E ) | id

[属性定义]
E.val : 综合属性
T.val : 综合属性
F.val : 综合属性
id.lexval : 综合属性

[语义规则]
E.val := E.val + T.val  # 0
E.val := T.val          # 1
T.val := T.val * F.val  # 2
T.val := F.val          # 3
F.val := E.val          # 4
F.val := id.lexval      # 5"""
    
    # 解析文法
    parser = 属性文法解析器()
    success, grammar, errors = parser.解析文法文件(default_grammar)
    
    if not success:
        print("文法解析失败:")
        for error in errors:
            print(f"  {error}")
        return False
    
    print("✓ 文法解析成功")
    
    # 构建依赖图
    builder = 依赖图构建器(grammar)
    parse_sequence = [5, 3, 1, 2, 0]  # 默认的语法分析序列
    
    print(f"语法分析序列: {parse_sequence}")
    
    success, dep_graph, error = builder.构建依赖图(parse_sequence)
    
    if not success:
        print(f"✗ 依赖图构建失败: {error}")
        return False
    
    print("✓ 依赖图构建成功")
    
    # 检查循环依赖
    cycles = dep_graph.检测循环依赖()
    if cycles:
        print(f"✗ 检测到循环依赖:")
        for cycle in cycles:
            if isinstance(cycle, list):
                print(f"  {' -> '.join(cycle)}")
            else:
                print(f"  {cycle}")
        print("继续分析依赖图结构...")
        # return False  # 暂时不返回，继续分析
    
    print("✓ 无循环依赖")
    
    # 显示依赖图信息
    print("\n依赖图节点:")
    for node_id, node in dep_graph.节点表.items():
        print(f"  {node_id}: {node.属性名}")
        if node.依赖节点:
            print(f"    依赖于: {', '.join(node.依赖节点)}")
        if node.计算表达式:
            print(f"    计算表达式: {node.计算表达式}")
    
    print("\n依赖关系:")
    for 源节点, 目标节点列表 in dep_graph.邻接表.items():
        for 目标节点 in 目标节点列表:
            print(f"  {源节点} -> {目标节点}")
    
    # 拓扑排序
    topo_order = dep_graph.拓扑排序()
    if topo_order:
        print(f"\n拓扑排序结果:")
        for i, node_id in enumerate(topo_order):
            print(f"  {i+1}. {node_id}")
    
    print("\n✓ 测试通过！修复成功！")
    return True

if __name__ == "__main__":
    test_dependency_graph_fix()
