# -*- coding: utf-8 -*-
"""
LALR(1)语法分析器综合测试程序

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os
from lalr1_main import *

def test_basic_grammar():
    """测试基本算术表达式文法"""
    print("=== 测试1: 基本算术表达式文法 ===")
    
    grammar = create_sample_grammar()
    parser = LALR1Parser(grammar)
    parser.build_parser()
    
    print(f"LR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
    print(f"LALR(1)状态数: {len(parser.automaton.states)}")
    print(f"状态压缩率: {(1 - len(parser.automaton.states) / len(parser.automaton.lr1_automaton.states)) * 100:.1f}%")
    
    # 测试输入串
    test_strings = [
        "id",
        "id + id",
        "id * id",
        "id + id * id",
        "( id + id ) * id",
        "id * ( id + id )",
        "( ( id ) )",
        "id + id + id",
        "id * id * id"
    ]
    
    success_count = 0
    for test_string in test_strings:
        success, steps, message = parser.parse(test_string)
        if success:
            success_count += 1
            print(f"✓ '{test_string}' - 成功")
        else:
            print(f"✗ '{test_string}' - 失败: {message}")
    
    print(f"成功率: {success_count}/{len(test_strings)} ({success_count/len(test_strings)*100:.1f}%)")
    
    # 测试错误输入
    error_strings = [
        "+ id",
        "id +",
        "( id",
        "id )",
        "id + * id",
        "( )",
        ""
    ]
    
    error_count = 0
    for test_string in error_strings:
        success, steps, message = parser.parse(test_string)
        if not success:
            error_count += 1
            print(f"✓ '{test_string}' - 正确拒绝")
        else:
            print(f"✗ '{test_string}' - 错误接受")
    
    print(f"错误检测率: {error_count}/{len(error_strings)} ({error_count/len(error_strings)*100:.1f}%)")
    print()

def test_simple_grammar():
    """测试简单文法"""
    print("=== 测试2: 简单文法 ===")
    
    grammar_text = """
S -> A a | b
A -> b d | ε
"""
    
    try:
        grammar = GrammarParser.parse_grammar_from_text(grammar_text)
        parser = LALR1Parser(grammar)
        parser.build_parser()
        
        print(f"LR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
        print(f"LALR(1)状态数: {len(parser.automaton.states)}")
        
        if parser.parsing_table.has_conflicts():
            print("发现冲突:")
            for conflict in parser.parsing_table.get_conflicts():
                print(f"  {conflict}")
        else:
            print("无冲突")
        
        # 测试输入串
        test_cases = [
            ("b d a", True),
            ("a", True),
            ("b", True),
            ("b d", False),
            ("d a", False),
            ("b a", False)
        ]
        
        for test_string, expected in test_cases:
            success, steps, message = parser.parse(test_string)
            if success == expected:
                print(f"✓ '{test_string}' - {'接受' if success else '拒绝'}")
            else:
                print(f"✗ '{test_string}' - 期望{'接受' if expected else '拒绝'}，实际{'接受' if success else '拒绝'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print()

def test_lalr_specific_grammar():
    """测试LALR(1)特有的文法"""
    print("=== 测试3: LALR(1)特有文法 ===")
    
    grammar_text = """
S -> A a | B b
A -> c
B -> c
"""
    
    try:
        grammar = GrammarParser.parse_grammar_from_text(grammar_text)
        parser = LALR1Parser(grammar)
        parser.build_parser()
        
        print(f"LR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
        print(f"LALR(1)状态数: {len(parser.automaton.states)}")
        
        if parser.parsing_table.has_conflicts():
            print("发现冲突:")
            for conflict in parser.parsing_table.get_conflicts():
                print(f"  {conflict}")
        else:
            print("无冲突")
        
        # 测试输入串
        test_cases = [
            ("c a", True),
            ("c b", True),
            ("c", False),
            ("a", False),
            ("b", False)
        ]
        
        for test_string, expected in test_cases:
            success, steps, message = parser.parse(test_string)
            if success == expected:
                print(f"✓ '{test_string}' - {'接受' if success else '拒绝'}")
            else:
                print(f"✗ '{test_string}' - 期望{'接受' if expected else '拒绝'}，实际{'接受' if success else '拒绝'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print()

def test_conflict_grammar():
    """测试可能产生冲突的文法"""
    print("=== 测试4: 冲突检测 ===")
    
    # 这个文法可能产生冲突
    grammar_text = """
S -> A B | A C
A -> a
B -> b
C -> c
"""
    
    try:
        grammar = GrammarParser.parse_grammar_from_text(grammar_text)
        parser = LALR1Parser(grammar)
        parser.build_parser()
        
        print(f"LR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
        print(f"LALR(1)状态数: {len(parser.automaton.states)}")
        
        if parser.parsing_table.has_conflicts():
            print("发现冲突:")
            for conflict in parser.parsing_table.get_conflicts():
                print(f"  {conflict}")
        else:
            print("无冲突")
        
        # 测试输入串
        test_cases = [
            ("a b", True),
            ("a c", True),
            ("a", False),
            ("b", False),
            ("c", False)
        ]
        
        for test_string, expected in test_cases:
            success, steps, message = parser.parse(test_string)
            if success == expected:
                print(f"✓ '{test_string}' - {'接受' if success else '拒绝'}")
            else:
                print(f"✗ '{test_string}' - 期望{'接受' if expected else '拒绝'}，实际{'接受' if success else '拒绝'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print()

def test_epsilon_grammar():
    """测试包含ε产生式的文法"""
    print("=== 测试5: ε产生式文法 ===")
    
    grammar_text = """
S -> A B
A -> a | ε
B -> b | ε
"""
    
    try:
        grammar = GrammarParser.parse_grammar_from_text(grammar_text)
        parser = LALR1Parser(grammar)
        parser.build_parser()
        
        print(f"LR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
        print(f"LALR(1)状态数: {len(parser.automaton.states)}")
        
        if parser.parsing_table.has_conflicts():
            print("发现冲突:")
            for conflict in parser.parsing_table.get_conflicts():
                print(f"  {conflict}")
        else:
            print("无冲突")
        
        # 测试输入串
        test_cases = [
            ("a b", True),
            ("a", True),
            ("b", True),
            ("", True),  # 空串
            ("a a", False),
            ("b b", False)
        ]
        
        for test_string, expected in test_cases:
            success, steps, message = parser.parse(test_string)
            if success == expected:
                print(f"✓ '{test_string if test_string else 'ε'}' - {'接受' if success else '拒绝'}")
            else:
                print(f"✗ '{test_string if test_string else 'ε'}' - 期望{'接受' if expected else '拒绝'}，实际{'接受' if success else '拒绝'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    print()

def test_grammar_parsing():
    """测试文法解析功能"""
    print("=== 测试6: 文法解析功能 ===")
    
    # 测试正确的文法
    correct_grammars = [
        "E -> E + T | T",
        "S -> a S b | ε",
        "A -> B C\nB -> b\nC -> c",
        "# 注释\nS -> A\nA -> a"
    ]
    
    for i, grammar_text in enumerate(correct_grammars):
        try:
            grammar = GrammarParser.parse_grammar_from_text(grammar_text)
            print(f"✓ 文法{i+1} - 解析成功")
        except Exception as e:
            print(f"✗ 文法{i+1} - 解析失败: {e}")
    
    # 测试错误的文法
    error_grammars = [
        "",  # 空文法
        "E ->",  # 缺少右部
        "-> T",  # 缺少左部
        "E T",  # 缺少箭头
    ]
    
    for i, grammar_text in enumerate(error_grammars):
        try:
            grammar = GrammarParser.parse_grammar_from_text(grammar_text)
            print(f"✗ 错误文法{i+1} - 应该失败但成功了")
        except Exception as e:
            print(f"✓ 错误文法{i+1} - 正确拒绝: {e}")
    
    print()

def run_all_tests():
    """运行所有测试"""
    print("LALR(1)语法分析器综合测试")
    print("=" * 50)
    print()
    
    test_basic_grammar()
    test_simple_grammar()
    test_lalr_specific_grammar()
    test_conflict_grammar()
    test_epsilon_grammar()
    test_grammar_parsing()
    
    print("=" * 50)
    print("所有测试完成！")

if __name__ == "__main__":
    run_all_tests()
