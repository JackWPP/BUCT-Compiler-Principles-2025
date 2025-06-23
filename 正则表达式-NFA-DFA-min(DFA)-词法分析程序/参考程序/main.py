#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Good Enough Compiler - 主程序入口
词法分析器系统的主要入口点
"""

import sys
import os
import argparse
from typing import Optional

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.lexical_analyzer import LexicalAnalyzer, TokenType
from scripts.nfa_dfa_converter import RegexToNFA, NFAToDFA, DFAMinimizer
from scripts.lexical_gui import create_interface

def run_gui():
    """启动图形界面"""
    print("启动词法分析器Web界面...")
    print("界面将在浏览器中打开，地址: http://localhost:7860")
    print("按 Ctrl+C 停止服务")
    
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )

def run_cli_analysis(code_file: str, rules_file: Optional[str] = None):
    """运行命令行词法分析"""
    try:
        # 读取代码文件
        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 创建词法分析器
        analyzer = LexicalAnalyzer()
        
        # 如果指定了规则文件，加载它
        if rules_file:
            success = analyzer.load_rules_from_file(rules_file)
            if not success:
                print("加载规则文件失败:")
                for error in analyzer.get_errors():
                    print(f"  {error}")
                return
            print(f"成功加载规则文件: {rules_file}")
        
        print(f"\n分析文件: {code_file}")
        print("=" * 50)
        
        # 执行词法分析
        tokens = analyzer.analyze(code)
        
        # 输出结果
        print("\n词法分析结果:")
        print("-" * 30)
        
        for i, token in enumerate(tokens, 1):
            if token.type != TokenType.EOF:
                print(f"{i:3d}. {token}")
        
        # 输出统计信息
        token_counts = {}
        for token in tokens:
            if token.type in token_counts:
                token_counts[token.type] += 1
            else:
                token_counts[token.type] = 1
        
        print("\n统计信息:")
        print("-" * 20)
        print(f"总Token数量: {len(tokens)}")
        
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            if token_type != TokenType.EOF:
                print(f"  {token_type.value}: {count}")
        
        # 输出错误信息
        if analyzer.has_errors():
            print("\n错误信息:")
            print("-" * 20)
            for error in analyzer.get_errors():
                print(f"  {error}")
        else:
            print("\n✅ 词法分析完成，无错误")
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{code_file}'")
    except Exception as e:
        print(f"错误: {e}")

def run_regex_test(regex: str):
    """测试正则表达式转换"""
    try:
        print(f"测试正则表达式: {regex}")
        print("=" * 50)
        
        # 创建转换器
        regex_converter = RegexToNFA()
        nfa_to_dfa = NFAToDFA()
        minimizer = DFAMinimizer()
        
        # 转换为NFA
        print("1. 转换为NFA...")
        nfa = regex_converter.convert(regex, TokenType.IDENTIFIER)
        print(f"   NFA状态数: {len(nfa.states)}")
        print(f"   字母表: {sorted(nfa.alphabet)}")
        
        # 转换为DFA
        print("\n2. 转换为DFA...")
        dfa = nfa_to_dfa.convert(nfa)
        print(f"   DFA状态数: {len(dfa.states)}")
        
        # 最小化DFA
        print("\n3. 最小化DFA...")
        min_dfa = minimizer.minimize(dfa)
        print(f"   最小化DFA状态数: {len(min_dfa.states)}")
        
        print("\n✅ 转换完成")
        
        # 显示DFA状态转移表
        print("\nDFA状态转移表:")
        print("-" * 40)
        symbols = sorted(list(dfa.alphabet))
        
        # 表头
        header = f"{'状态':<10} {'接受':<6}"
        for symbol in symbols:
            header += f" {symbol:<6}"
        print(header)
        print("-" * len(header))
        
        # 数据行
        for state_id in sorted(dfa.states.keys()):
            is_accept = "是" if state_id in dfa.accept_states else "否"
            row = f"{state_id:<10} {is_accept:<6}"
            
            for symbol in symbols:
                next_state = dfa.transitions.get((state_id, symbol), "-")
                row += f" {str(next_state):<6}"
            
            print(row)
    
    except Exception as e:
        print(f"错误: {e}")

def create_sample_files():
    """创建示例文件"""
    # 创建示例代码文件
    sample_code = """program example;
var
    x, y: integer;
    result: real;
    message: string;
begin
    x := 10;
    y := 20;
    result := x + y * 2.5;
    
    if result > 50 then
    begin
        message := 'Result is large';
        writeln(message);
    end
    else
    begin
        message := 'Result is small';
        writeln(message);
    end;
    
    { 这是一个注释 }
    while x > 0 do
    begin
        x := x - 1;
        writeln('x = ', x);
    end;
end.
"""
    
    with open("sample_code.pas", "w", encoding="utf-8") as f:
        f.write(sample_code)
    
    print("已创建示例文件:")
    print("  - sample_code.pas: 示例Pascal代码")
    print("  - lexical_rules.txt: 词法规则文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Good Enough Compiler - 词法分析器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py gui                           # 启动Web界面
  python main.py analyze sample_code.pas      # 分析代码文件
  python main.py regex "a(b|c)*"               # 测试正则表达式
  python main.py create-samples               # 创建示例文件
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # GUI命令
    gui_parser = subparsers.add_parser("gui", help="启动Web图形界面")
    
    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析代码文件")
    analyze_parser.add_argument("file", help="要分析的代码文件")
    analyze_parser.add_argument("-r", "--rules", help="词法规则文件")
    
    # 正则表达式测试命令
    regex_parser = subparsers.add_parser("regex", help="测试正则表达式转换")
    regex_parser.add_argument("pattern", help="正则表达式")
    
    # 创建示例文件命令
    sample_parser = subparsers.add_parser("create-samples", help="创建示例文件")
    
    args = parser.parse_args()
    
    if args.command == "gui":
        run_gui()
    elif args.command == "analyze":
        run_cli_analysis(args.file, args.rules)
    elif args.command == "regex":
        run_regex_test(args.pattern)
    elif args.command == "create-samples":
        create_sample_files()
    else:
        # 默认启动GUI
        print("未指定命令，启动Web界面...")
        print("使用 'python main.py --help' 查看所有可用命令")
        print()
        run_gui()

if __name__ == "__main__":
    main()