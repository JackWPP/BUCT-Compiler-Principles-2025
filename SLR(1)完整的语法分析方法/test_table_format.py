# -*- coding: utf-8 -*-
"""
测试分析表格式显示
验证修复后的分析表不再显示多余的"error"
"""

from slr1_main import Grammar, SLR1Parser

def test_table_format():
    """测试分析表格式"""
    print("测试SLR(1)分析表格式显示")
    print("=" * 50)
    
    # 创建经典算术表达式文法
    grammar = Grammar()
    grammar.set_start_symbol("E")
    grammar.add_production("E", ["E", "+", "T"])
    grammar.add_production("E", ["T"])
    grammar.add_production("T", ["T", "*", "F"])
    grammar.add_production("T", ["F"])
    grammar.add_production("F", ["(", "E", ")"])
    grammar.add_production("F", ["id"])
    
    # 计算FIRST和FOLLOW集合
    grammar.compute_first_sets()
    grammar.compute_follow_sets()
    
    # 构建SLR(1)分析器
    parser = SLR1Parser(grammar)
    parser.build_parser()
    
    # 显示分析表
    print("修复后的分析表:")
    print(parser.parsing_table.print_table())
    
    # 验证空白位置
    print("\n验证结果:")
    table_str = parser.parsing_table.print_table()
    
    if "error" in table_str.lower():
        print("❌ 分析表中仍然包含'error'字样")
        # 找出包含error的行
        lines = table_str.split('\n')
        for i, line in enumerate(lines):
            if "error" in line.lower():
                print(f"  第{i+1}行: {line}")
    else:
        print("✅ 分析表格式正确，空白位置不显示'error'")
    
    # 检查特定位置是否为空
    print("\n检查特定位置:")

    # 找一个确实应该为空的位置：接受状态的GOTO部分
    accept_state = None
    for state_index, state in enumerate(parser.automaton.states):
        for item in state:
            if (item.is_complete() and
                item.production.index == 0 and  # 拓广产生式
                item.production.left == parser.grammar.start_symbol):
                accept_state = state_index
                break
        if accept_state is not None:
            break

    if accept_state is not None:
        print(f"找到接受状态: {accept_state}")

        # 检查接受状态的GOTO部分（应该为空）
        goto_E = parser.parsing_table.get_goto(accept_state, "E")
        goto_F = parser.parsing_table.get_goto(accept_state, "F")
        goto_T = parser.parsing_table.get_goto(accept_state, "T")

        print(f"接受状态的GOTO(E): {goto_E} (应该为None)")
        print(f"接受状态的GOTO(F): {goto_F} (应该为None)")
        print(f"接受状态的GOTO(T): {goto_T} (应该为None)")

        # 检查接受状态的某些ACTION位置（除了$应该为空）
        action_lparen = parser.parsing_table.action_table.get((accept_state, "("))
        action_id = parser.parsing_table.action_table.get((accept_state, "id"))

        print(f"接受状态的ACTION('('): {action_lparen} (应该为None)")
        print(f"接受状态的ACTION('id'): {action_id} (应该为None)")

        if (goto_E is None and goto_F is None and goto_T is None and
            action_lparen is None and action_id is None):
            print("✅ 空白位置检查正确")
        else:
            print("❌ 空白位置检查有问题")
    else:
        print("未找到接受状态")

if __name__ == "__main__":
    test_table_format()
