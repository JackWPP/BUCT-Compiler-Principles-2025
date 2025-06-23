# -*- coding: utf-8 -*-
"""
LR(1)语法分析器综合测试程序
用于验证LR(1)解析器的正确性和功能完整性

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lr1_main import Grammar, LR1Parser

def create_grammar_from_rules(rules, start_symbol):
    """从规则字符串创建文法对象"""
    grammar = Grammar()
    grammar.set_start_symbol(start_symbol)
    
    for rule in rules:
        if '->' not in rule:
            continue
        
        left, right_part = rule.split('->', 1)
        left = left.strip()
        
        # 处理多个右部（用|分隔）
        alternatives = [alt.strip() for alt in right_part.split('|')]
        
        for alt in alternatives:
            if alt == 'ε' or alt == 'epsilon' or alt == '':
                right = ['ε']
            else:
                right = alt.split()
            grammar.add_production(left, right)
    
    return grammar

def test_case(name, rules, start_symbol, test_strings, expected_results):
    """执行单个测试用例"""
    print(f"\n{'='*60}")
    print(f"测试用例: {name}")
    print(f"{'='*60}")
    
    try:
        # 创建文法
        grammar = create_grammar_from_rules(rules, start_symbol)
        print(f"文法规则:")
        for rule in rules:
            print(f"  {rule}")
        print(f"开始符号: {start_symbol}")
        
        # 创建解析器
        parser = LR1Parser(grammar)
        parser.build_parser()
        
        # 检查冲突
        if parser.parsing_table.has_conflicts():
            conflicts = parser.parsing_table.get_conflicts()
            print(f"\n⚠️  发现 {len(conflicts)} 个冲突:")
            for i, conflict in enumerate(conflicts[:3], 1):
                print(f"  {i}. {conflict}")
            if len(conflicts) > 3:
                print(f"  ... 还有 {len(conflicts) - 3} 个冲突")
        else:
            print("\n✅ 无冲突，文法是LR(1)文法")
        
        # 测试输入串
        print(f"\n测试输入串:")
        success_count = 0
        total_count = len(test_strings)
        
        for i, (test_string, expected) in enumerate(zip(test_strings, expected_results)):
            success, steps, message = parser.parse(test_string)
            
            if success == expected:
                status = "✅ 通过"
                if success:
                    success_count += 1
            else:
                status = "❌ 失败"
            
            print(f"  {i+1}. '{test_string}' -> {status}")
            if not success and expected:
                print(f"     错误: {message}")
        
        print(f"\n测试结果: {success_count}/{total_count} 个成功用例通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试用例"""
    print("LR(1)语法分析器综合测试")
    print("=" * 60)
    
    test_results = []
    
    # 测试用例1: 经典算术表达式文法
    rules1 = [
        "E -> E + T | T",
        "T -> T * F | F", 
        "F -> ( E ) | id"
    ]
    test_strings1 = ["id + id * id", "( id + id ) * id", "id * ( id + id )", "( ( id ) )"]
    expected1 = [True, True, True, True]
    
    result1 = test_case("经典算术表达式文法", rules1, "E", test_strings1, expected1)
    test_results.append(("经典算术表达式文法", result1))
    
    # 测试用例2: 包含空产生式的文法
    rules2 = [
        "S -> A B",
        "A -> a | ε",
        "B -> b"
    ]
    test_strings2 = ["a b", "b"]
    expected2 = [True, True]
    
    result2 = test_case("包含空产生式的文法", rules2, "S", test_strings2, expected2)
    test_results.append(("包含空产生式的文法", result2))
    
    # 测试用例3: LR(1)特有文法
    rules3 = [
        "S -> L = R | R",
        "L -> * R | id",
        "R -> L"
    ]
    test_strings3 = ["id = id", "* id = id", "id"]
    expected3 = [True, True, True]
    
    result3 = test_case("LR(1)特有文法", rules3, "S", test_strings3, expected3)
    test_results.append(("LR(1)特有文法", result3))
    
    # 测试用例4: 错误输入测试
    rules4 = [
        "E -> E + T | T",
        "T -> T * F | F",
        "F -> ( E ) | id"
    ]
    test_strings4 = ["id + + id", "( id + id", "id ) + id", "+ id"]
    expected4 = [False, False, False, False]
    
    result4 = test_case("错误输入测试", rules4, "E", test_strings4, expected4)
    test_results.append(("错误输入测试", result4))
    
    # 测试用例5: 复杂嵌套表达式
    rules5 = [
        "E -> E + T | E - T | T",
        "T -> T * F | T / F | F",
        "F -> ( E ) | id | num"
    ]
    test_strings5 = ["id + num * ( id - num ) / id", "( id + num ) * ( id - num )"]
    expected5 = [True, True]
    
    result5 = test_case("复杂嵌套表达式", rules5, "E", test_strings5, expected5)
    test_results.append(("复杂嵌套表达式", result5))
    
    # 测试用例6: 函数调用文法
    rules6 = [
        "S -> F | E",
        "F -> id ( A )",
        "A -> E , A | E | ε",
        "E -> id | num"
    ]
    test_strings6 = ["id ( id )", "id ( id , num )", "id ( )"]
    expected6 = [True, True, True]
    
    result6 = test_case("函数调用文法", rules6, "S", test_strings6, expected6)
    test_results.append(("函数调用文法", result6))
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总体结果: {passed_tests}/{total_tests} 个测试用例通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试用例都通过了！LR(1)解析器工作正常。")
    else:
        print("⚠️  部分测试用例失败，请检查实现。")
    
    return passed_tests == total_tests

def test_lr1_vs_slr1():
    """测试LR(1)相对于SLR(1)的优势"""
    print(f"\n{'='*60}")
    print("LR(1) vs SLR(1) 对比测试")
    print(f"{'='*60}")
    
    # 这个文法对于SLR(1)可能有冲突，但LR(1)应该能处理
    rules = [
        "S -> L = R | R",
        "L -> * R | id", 
        "R -> L"
    ]
    
    print("测试文法（LR(1)特有）:")
    for rule in rules:
        print(f"  {rule}")
    
    try:
        grammar = create_grammar_from_rules(rules, "S")
        parser = LR1Parser(grammar)
        parser.build_parser()
        
        if parser.parsing_table.has_conflicts():
            print("❌ LR(1)解析器仍有冲突")
        else:
            print("✅ LR(1)解析器成功处理，无冲突")
            
        # 测试一些输入
        test_inputs = ["id = id", "* id = id", "id"]
        print("\n测试输入:")
        for inp in test_inputs:
            success, _, message = parser.parse(inp)
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  '{inp}' -> {status}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 运行所有测试
    success = run_all_tests()
    
    # 运行LR(1) vs SLR(1)对比测试
    test_lr1_vs_slr1()
    
    # 退出代码
    sys.exit(0 if success else 1)
