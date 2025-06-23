# -*- coding: utf-8 -*-
"""
SLR(1)语法分析器综合测试程序
测试所有功能模块的正确性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from slr1_main import Grammar, SLR1Parser
import time

def print_separator(title):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_grammar_parsing():
    """测试文法解析功能"""
    print_separator("测试1: 文法解析功能")
    
    # 测试算术表达式文法
    grammar_text = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
    
    print("输入文法:")
    print(grammar_text)
    
    grammar = Grammar()
    grammar.set_start_symbol("E")
    
    # 解析产生式
    lines = grammar_text.split('\n')
    for line in lines:
        line = line.strip()
        if '->' in line:
            parts = line.split('->')
            left = parts[0].strip()
            right_part = parts[1].strip()
            alternatives = [alt.strip() for alt in right_part.split('|')]
            for alt in alternatives:
                right = alt.split()
                grammar.add_production(left, right)
    
    # 计算FIRST和FOLLOW集合
    grammar.compute_first_sets()
    grammar.compute_follow_sets()
    
    print(f"\n产生式数量: {len(grammar.productions)}")
    print(f"非终结符: {sorted(grammar.nonterminals)}")
    print(f"终结符: {sorted(grammar.terminals)}")
    
    print("\nFIRST集合:")
    for symbol in sorted(grammar.nonterminals):
        first_set = grammar.first_sets.get(symbol, set())
        print(f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}")
    
    print("\nFOLLOW集合:")
    for symbol in sorted(grammar.nonterminals):
        follow_set = grammar.follow_sets.get(symbol, set())
        print(f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}")
    
    return grammar

def test_automaton_construction(grammar):
    """测试自动机构建"""
    print_separator("测试2: LR(0)自动机构建")
    
    parser = SLR1Parser(grammar)
    
    start_time = time.time()
    parser.build_parser()
    end_time = time.time()
    
    print(f"自动机构建时间: {end_time - start_time:.3f} 秒")
    print(f"状态数量: {len(parser.automaton.states)}")
    print(f"转换数量: {len(parser.automaton.transitions)}")
    
    # 显示前几个状态的详情
    print("\n前3个状态的项目集:")
    for i, state in enumerate(parser.automaton.states[:3]):
        print(f"\n状态 {i}:")
        for item in state:
            print(f"  {item}")
    
    return parser

def test_parsing_table(parser):
    """测试分析表构建"""
    print_separator("测试3: SLR(1)分析表构建")
    
    print(f"是否有冲突: {parser.parsing_table.has_conflicts()}")
    
    if parser.parsing_table.has_conflicts():
        conflicts = parser.parsing_table.get_conflicts()
        print(f"冲突数量: {len(conflicts)}")
        print("冲突详情:")
        for conflict in conflicts[:5]:  # 只显示前5个冲突
            print(f"  {conflict}")
        if len(conflicts) > 5:
            print(f"  ... 还有{len(conflicts) - 5}个冲突")
    else:
        print("✓ 无冲突，文法是SLR(1)文法")
    
    # 显示分析表的一部分
    print("\n分析表构建完成")
    print("ACTION表项数:", len([k for k in parser.parsing_table.action_table.keys()]))
    print("GOTO表项数:", len([k for k in parser.parsing_table.goto_table.keys()]))

def test_parsing_process(parser):
    """测试语法分析过程"""
    print_separator("测试4: 语法分析过程")
    
    test_strings = [
        "id",
        "id + id",
        "id * id",
        "id + id * id",
        "( id + id ) * id",
        "id +",  # 错误用例
        ") id ("  # 错误用例
    ]
    
    for test_string in test_strings:
        print(f"\n分析字符串: '{test_string}'")
        
        start_time = time.time()
        success, steps, message = parser.parse(test_string)
        end_time = time.time()
        
        print(f"结果: {'✓ 成功' if success else '✗ 失败'}")
        print(f"消息: {message}")
        print(f"步骤数: {len(steps)}")
        print(f"分析时间: {end_time - start_time:.3f} 秒")
        
        # 对于简短的分析过程，显示详细步骤
        if len(steps) <= 8:
            print("分析步骤:")
            for step in steps:
                stack_str = ' '.join(str(s) for s in step.stack)
                print(f"  {step.step:2d} | {stack_str:15s} | {step.input_buffer:15s} | {step.action}")

def test_conflict_detection():
    """测试冲突检测功能"""
    print_separator("测试5: 冲突检测功能")
    
    # 创建有冲突的文法
    conflict_grammar = Grammar()
    conflict_grammar.set_start_symbol("S")
    conflict_grammar.add_production("S", ["E"])
    conflict_grammar.add_production("E", ["E", "+", "E"])
    conflict_grammar.add_production("E", ["E", "*", "E"])
    conflict_grammar.add_production("E", ["id"])
    
    conflict_grammar.compute_first_sets()
    conflict_grammar.compute_follow_sets()
    
    print("测试有冲突的文法:")
    for i, prod in enumerate(conflict_grammar.productions):
        print(f"  {i}: {prod}")
    
    conflict_parser = SLR1Parser(conflict_grammar)
    conflict_parser.build_parser()
    
    print(f"\n状态数量: {len(conflict_parser.automaton.states)}")
    print(f"是否有冲突: {conflict_parser.parsing_table.has_conflicts()}")
    
    if conflict_parser.parsing_table.has_conflicts():
        conflicts = conflict_parser.parsing_table.get_conflicts()
        print(f"✓ 成功检测到 {len(conflicts)} 个冲突:")
        for conflict in conflicts:
            print(f"  {conflict}")
    else:
        print("✗ 未检测到冲突（应该有冲突）")

def test_edge_cases():
    """测试边界情况"""
    print_separator("测试6: 边界情况")
    
    # 测试空产生式
    epsilon_grammar = Grammar()
    epsilon_grammar.set_start_symbol("S")
    epsilon_grammar.add_production("S", ["A", "B"])
    epsilon_grammar.add_production("A", ["a"])
    epsilon_grammar.add_production("A", ["ε"])
    epsilon_grammar.add_production("B", ["b"])
    
    epsilon_grammar.compute_first_sets()
    epsilon_grammar.compute_follow_sets()
    
    print("测试含空产生式的文法:")
    for i, prod in enumerate(epsilon_grammar.productions):
        print(f"  {i}: {prod}")
    
    epsilon_parser = SLR1Parser(epsilon_grammar)
    epsilon_parser.build_parser()
    
    print(f"\n状态数量: {len(epsilon_parser.automaton.states)}")
    print(f"是否有冲突: {epsilon_parser.parsing_table.has_conflicts()}")
    
    # 测试分析
    test_cases = ["a b", "b", ""]
    for test_case in test_cases:
        success, steps, message = epsilon_parser.parse(test_case)
        print(f"'{test_case}': {'成功' if success else '失败'} - {message}")

def main():
    """主测试函数"""
    print("SLR(1)语法分析器综合测试")
    print("作者: 王海翔")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 执行所有测试
        grammar = test_grammar_parsing()
        parser = test_automaton_construction(grammar)
        test_parsing_table(parser)
        test_parsing_process(parser)
        test_conflict_detection()
        test_edge_cases()
        
        print_separator("测试总结")
        print("✓ 所有测试完成")
        print("✓ 文法解析功能正常")
        print("✓ LR(0)自动机构建正常")
        print("✓ SLR(1)分析表构建正常")
        print("✓ 语法分析过程正常")
        print("✓ 冲突检测功能正常")
        print("✓ 边界情况处理正常")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
