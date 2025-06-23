#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词法分析器Web界面 - Good Enough Compiler
使用Gradio创建用户友好的词法分析界面
"""

import gradio as gr
import pandas as pd
from typing import List, Tuple, Optional
import traceback

from .lexical_analyzer import LexicalAnalyzer, TokenType, Token
from .nfa_dfa_converter import RegexToNFA, NFAToDFA, DFAMinimizer, visualize_nfa, visualize_dfa

class LexicalAnalyzerGUI:
    """词法分析器图形界面"""
    
    def __init__(self):
        self.analyzer = LexicalAnalyzer()
        self.regex_converter = RegexToNFA()
        self.nfa_to_dfa = NFAToDFA()
        self.minimizer = DFAMinimizer()
        
        # 存储当前的NFA和DFA
        self.current_nfa = None
        self.current_dfa = None
        self.current_min_dfa = None
    
    def analyze_code(self, code: str) -> Tuple[str, str, str]:
        """分析代码并返回结果"""
        try:
            if not code.strip():
                return "请输入要分析的代码", "", ""
            
            # 执行词法分析
            tokens = self.analyzer.analyze(code)
            
            # 生成Token表格
            token_table = self.analyzer.get_tokens_table()
            
            # 转换为HTML表格
            html_table = self._create_html_table(token_table)
            
            # 生成分析结果摘要
            summary = self._generate_summary(tokens)
            
            # 获取错误信息
            errors = self.analyzer.get_errors()
            error_info = "\n".join(errors) if errors else "无错误"
            
            return summary, html_table, error_info
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            return error_msg, "", error_msg
    
    def regex_to_automata(self, regex: str) -> Tuple[Optional[object], Optional[object], Optional[object], str, str, str]:
        """将正则表达式转换为自动机"""
        try:
            if not regex.strip():
                return None, None, None, "请输入正则表达式", "", ""
            
            # 转换为NFA
            nfa = self.regex_converter.convert(regex, TokenType.IDENTIFIER)
            self.current_nfa = nfa
            
            # 转换为DFA
            dfa = self.nfa_to_dfa.convert(nfa)
            self.current_dfa = dfa
            
            # 最小化DFA
            min_dfa = self.minimizer.minimize(dfa)
            self.current_min_dfa = min_dfa
            
            # 可视化
            nfa_img = visualize_nfa(nfa, f"NFA for: {regex}")
            dfa_img = visualize_dfa(dfa, f"DFA for: {regex}")
            min_dfa_img = visualize_dfa(min_dfa, f"Minimized DFA for: {regex}")
            
            # 生成状态转移表
            nfa_table = self._generate_nfa_table(nfa)
            dfa_table = self._generate_dfa_table(dfa)
            min_dfa_table = self._generate_dfa_table(min_dfa)
            
            return nfa_img, dfa_img, min_dfa_img, nfa_table, dfa_table, min_dfa_table
            
        except Exception as e:
            error_msg = f"转换过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            return None, None, None, error_msg, error_msg, error_msg
    
    def load_rules_file(self, file) -> str:
        """加载词法规则文件"""
        try:
            if file is None:
                return "请选择规则文件"
            
            # 保存上传的文件
            with open("temp_rules.txt", "wb") as f:
                f.write(file)
            
            # 重新初始化分析器并加载规则
            self.analyzer = LexicalAnalyzer()
            success = self.analyzer.load_rules_from_file("temp_rules.txt")
            
            if success:
                return f"成功加载规则文件，共 {len(self.analyzer.rules)} 条规则"
            else:
                errors = "\n".join(self.analyzer.get_errors())
                return f"加载规则文件失败:\n{errors}"
                
        except Exception as e:
            return f"加载文件时发生错误: {str(e)}"
    
    def get_current_rules(self) -> str:
        """获取当前的词法规则"""
        try:
            rules_info = []
            rules_info.append("当前词法规则:")
            rules_info.append("=" * 50)
            
            for i, rule in enumerate(self.analyzer.rules, 1):
                rules_info.append(f"{i:2d}. {rule.token_type.value:15s} | {rule.pattern:30s} | 优先级: {rule.priority}")
            
            rules_info.append("\n关键字:")
            rules_info.append("-" * 30)
            for keyword, token_type in self.analyzer.keywords.items():
                rules_info.append(f"{keyword:15s} -> {token_type.value}")
            
            return "\n".join(rules_info)
            
        except Exception as e:
            return f"获取规则信息时发生错误: {str(e)}"
    
    def _create_html_table(self, table_data: List[List[str]]) -> str:
        """创建HTML表格"""
        if not table_data:
            return "<p>无数据</p>"
        
        html = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
        
        # 表头
        html += "<thead><tr style='background-color: #f0f0f0;'>"
        for header in table_data[0]:
            html += f"<th style='padding: 8px; text-align: left;'>{header}</th>"
        html += "</tr></thead>"
        
        # 数据行
        html += "<tbody>"
        for i, row in enumerate(table_data[1:], 1):
            row_style = "background-color: #f9f9f9;" if i % 2 == 0 else ""
            html += f"<tr style='{row_style}'>"
            for j, cell in enumerate(row):
                cell_style = "padding: 8px;"
                # 为错误Token添加红色背景
                if j == 1 and cell == "ERROR":
                    cell_style += " background-color: #ffcccc;"
                # 为关键字添加蓝色背景
                elif j == 1 and any(cell.endswith(kw) for kw in ["PROGRAM", "VAR", "BEGIN", "END", "IF", "WHILE"]):
                    cell_style += " background-color: #cce5ff;"
                html += f"<td style='{cell_style}'>{cell}</td>"
            html += "</tr>"
        html += "</tbody>"
        
        html += "</table>"
        return html
    
    def _generate_summary(self, tokens: List[Token]) -> str:
        """生成分析结果摘要"""
        summary = []
        summary.append("=== 词法分析结果摘要 ===")
        summary.append(f"总Token数量: {len(tokens)}")
        
        # 统计各类型Token数量
        token_counts = {}
        for token in tokens:
            if token.type in token_counts:
                token_counts[token.type] += 1
            else:
                token_counts[token.type] = 1
        
        summary.append("\nToken类型统计:")
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            if token_type != TokenType.EOF:
                summary.append(f"  {token_type.value}: {count}")
        
        # 检查错误
        error_count = token_counts.get(TokenType.ERROR, 0)
        if error_count > 0:
            summary.append(f"\n⚠️ 发现 {error_count} 个错误Token")
        else:
            summary.append("\n✅ 词法分析成功，无错误")
        
        return "\n".join(summary)
    
    def _generate_nfa_table(self, nfa) -> str:
        """生成NFA状态转移表"""
        try:
            table = []
            table.append("<h3>NFA状态转移表</h3>")
            table.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>")
            
            # 表头
            symbols = sorted(list(nfa.alphabet))
            headers = ["状态", "是否接受状态"] + symbols + ["ε"]
            table.append("<tr style='background-color: #f0f0f0;'>")
            for header in headers:
                table.append(f"<th>{header}</th>")
            table.append("</tr>")
            
            # 数据行
            for state in nfa.states:
                table.append("<tr>")
                
                # 状态ID
                table.append(f"<td>q{state.id}</td>")
                
                # 是否接受状态
                is_accept = "是" if state.is_end else "否"
                style = "background-color: lightgreen;" if state.is_end else ""
                table.append(f"<td style='{style}'>{is_accept}</td>")
                
                # 各符号的转移
                for symbol in symbols:
                    if symbol in state.transitions:
                        targets = ",".join([f"q{t.id}" for t in state.transitions[symbol]])
                        table.append(f"<td>{targets}</td>")
                    else:
                        table.append("<td>-</td>")
                
                # ε转移
                if 'ε' in state.transitions:
                    targets = ",".join([f"q{t.id}" for t in state.transitions['ε']])
                    table.append(f"<td>{targets}</td>")
                else:
                    table.append("<td>-</td>")
                
                table.append("</tr>")
            
            table.append("</table>")
            return "".join(table)
            
        except Exception as e:
            return f"生成NFA表格时发生错误: {str(e)}"
    
    def _generate_dfa_table(self, dfa) -> str:
        """生成DFA状态转移表"""
        try:
            table = []
            table.append("<h3>DFA状态转移表</h3>")
            table.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>")
            
            # 表头
            symbols = sorted(list(dfa.alphabet))
            headers = ["状态", "是否接受状态"] + symbols
            table.append("<tr style='background-color: #f0f0f0;'>")
            for header in headers:
                table.append(f"<th>{header}</th>")
            table.append("</tr>")
            
            # 数据行
            for state_id in sorted(dfa.states.keys()):
                table.append("<tr>")
                
                # 状态ID
                table.append(f"<td>{state_id}</td>")
                
                # 是否接受状态
                is_accept = "是" if state_id in dfa.accept_states else "否"
                style = "background-color: lightgreen;" if state_id in dfa.accept_states else ""
                table.append(f"<td style='{style}'>{is_accept}</td>")
                
                # 各符号的转移
                for symbol in symbols:
                    next_state = dfa.transitions.get((state_id, symbol))
                    if next_state:
                        table.append(f"<td>{next_state}</td>")
                    else:
                        table.append("<td>-</td>")
                
                table.append("</tr>")
            
            table.append("</table>")
            return "".join(table)
            
        except Exception as e:
            return f"生成DFA表格时发生错误: {str(e)}"

def create_interface():
    """创建Gradio界面"""
    gui = LexicalAnalyzerGUI()
    
    with gr.Blocks(title="Good Enough Compiler - 词法分析器", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # Good Enough Compiler - 词法分析器
        
        这是一个功能完整的词法分析器，支持：
        - 词法分析和Token生成
        - 正则表达式到NFA/DFA的转换
        - 自动机可视化
        - 自定义词法规则
        """)
        
        with gr.Tabs():
            # 词法分析标签页
            with gr.TabItem("词法分析"):
                gr.Markdown("## 代码词法分析")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        code_input = gr.Textbox(
                            label="输入代码",
                            placeholder="请输入要分析的代码...",
                            lines=10,
                            value="""program example;
var
    x, y: integer;
    result: real;
begin
    x := 10;
    y := 20;
    result := x + y * 2.5;
    if result > 50 then
        writeln('Large')
    else
        writeln('Small');
end."""
                        )
                        
                        analyze_btn = gr.Button("开始分析", variant="primary")
                    
                    with gr.Column(scale=2):
                        summary_output = gr.Textbox(
                            label="分析摘要",
                            lines=8,
                            interactive=False
                        )
                        
                        error_output = gr.Textbox(
                            label="错误信息",
                            lines=4,
                            interactive=False
                        )
                
                token_table = gr.HTML(label="Token表格")
                
                analyze_btn.click(
                    gui.analyze_code,
                    inputs=[code_input],
                    outputs=[summary_output, token_table, error_output]
                )
            
            # 正则表达式转换标签页
            with gr.TabItem("正则表达式转换"):
                gr.Markdown("## 正则表达式到自动机转换")
                
                with gr.Row():
                    regex_input = gr.Textbox(
                        label="正则表达式",
                        placeholder="例如: a(b|c)*",
                        value="a(b|c)*"
                    )
                    convert_btn = gr.Button("转换", variant="primary")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### NFA")
                        nfa_image = gr.Image(label="NFA图")
                        nfa_table = gr.HTML(label="NFA状态转移表")
                    
                    with gr.Column():
                        gr.Markdown("### DFA")
                        dfa_image = gr.Image(label="DFA图")
                        dfa_table = gr.HTML(label="DFA状态转移表")
                    
                    with gr.Column():
                        gr.Markdown("### 最小化DFA")
                        min_dfa_image = gr.Image(label="最小化DFA图")
                        min_dfa_table = gr.HTML(label="最小化DFA状态转移表")
                
                convert_btn.click(
                    gui.regex_to_automata,
                    inputs=[regex_input],
                    outputs=[nfa_image, dfa_image, min_dfa_image, nfa_table, dfa_table, min_dfa_table]
                )
            
            # 规则管理标签页
            with gr.TabItem("规则管理"):
                gr.Markdown("## 词法规则管理")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 加载规则文件")
                        rules_file = gr.File(
                            label="选择规则文件",
                            file_types=[".txt", ".rules"]
                        )
                        load_btn = gr.Button("加载规则")
                        load_result = gr.Textbox(
                            label="加载结果",
                            lines=3,
                            interactive=False
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 当前规则")
                        view_rules_btn = gr.Button("查看当前规则")
                        current_rules = gr.Textbox(
                            label="当前规则列表",
                            lines=15,
                            interactive=False
                        )
                
                load_btn.click(
                    gui.load_rules_file,
                    inputs=[rules_file],
                    outputs=[load_result]
                )
                
                view_rules_btn.click(
                    gui.get_current_rules,
                    outputs=[current_rules]
                )
                
                # 规则文件格式说明
                gr.Markdown("""
                ### 规则文件格式说明
                
                规则文件应为文本文件，每行一个规则，格式为：
                ```
                正则表达式    Token类型    优先级
                ```
                
                示例：
                ```
                \\d+          NUMBER      8
                [a-zA-Z_]\\w*  IDENTIFIER  5
                \\+           PLUS        6
                ```
                
                - 使用制表符分隔各字段
                - 以#开头的行为注释
                - 优先级数字越大越优先
                """)
        
        # 使用说明
        with gr.Accordion("使用说明", open=False):
            gr.Markdown("""
            ## 功能说明
            
            ### 1. 词法分析
            - 输入源代码，自动识别Token
            - 支持关键字、标识符、数字、运算符等
            - 显示详细的Token表格和错误信息
            
            ### 2. 正则表达式转换
            - 支持基本正则表达式语法：|（或）、*（零个或多个）、+（一个或多个）、?（零个或一个）
            - 自动生成NFA、DFA和最小化DFA
            - 提供可视化图形和状态转移表
            
            ### 3. 规则管理
            - 支持自定义词法规则
            - 可以从文件加载规则
            - 查看当前生效的规则
            
            ## 支持的Token类型
            
            - **关键字**: program, var, begin, end, if, then, else, while, do等
            - **数据类型**: integer, real, boolean, char, string
            - **运算符**: +, -, *, /, :=, =, <>, <, <=, >, >=, and, or, not
            - **分隔符**: ;, ,, ., :, (, ), [, ]
            - **字面量**: 数字、字符串、字符
            - **标识符**: 变量名、函数名等
            """)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )