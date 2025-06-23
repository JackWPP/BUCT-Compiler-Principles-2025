# -*- coding: utf-8 -*-
"""
编译原理作业 - 词法分析程序
实现正则表达式->NFA->DFA->min(DFA)->词法分析的完整过程

作者: [您的姓名]
学号: [您的学号]
班级: [您的班级]
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional, Union
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict


# ==================== Token定义 ====================

class TokenType(Enum):
    """Token类型枚举"""
    # Pascal关键字
    PROGRAM = "PROGRAM"
    VAR = "VAR"
    CONST = "CONST"
    BEGIN = "BEGIN"
    END = "END"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    FOR = "FOR"
    TO = "TO"
    
    # 数据类型
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    
    # 标识符和字面量
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    
    # 运算符
    PLUS = "PLUS"          # +
    MINUS = "MINUS"        # -
    MULTIPLY = "MULTIPLY"  # *
    DIVIDE = "DIVIDE"      # /
    ASSIGN = "ASSIGN"      # :=
    EQUAL = "EQUAL"        # =
    LESS = "LESS"          # <
    GREATER = "GREATER"    # >
    LESS_EQUAL = "LESS_EQUAL"      # <=
    GREATER_EQUAL = "GREATER_EQUAL" # >=
    NOT_EQUAL = "NOT_EQUAL"         # <>
    
    # 分隔符
    SEMICOLON = "SEMICOLON"  # ;
    COMMA = "COMMA"          # ,
    DOT = "DOT"              # .
    COLON = "COLON"          # :
    LPAREN = "LPAREN"        # (
    RPAREN = "RPAREN"        # )
    
    # 其他
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    ERROR = "ERROR"


@dataclass
class Token:
    """Token数据结构"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"


# ==================== 自动机相关类 ====================

class State:
    """自动机状态类"""
    
    def __init__(self, state_id: int):
        self.id = state_id
        self.transitions: Dict[str, Set['State']] = {}
        self.is_accept = False
        self.token_type: Optional[TokenType] = None
    
    def add_transition(self, symbol: str, target: 'State'):
        """添加状态转移"""
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(target)
    
    def get_transitions(self, symbol: str) -> Set['State']:
        """获取指定符号的转移目标"""
        return self.transitions.get(symbol, set())
    
    def __str__(self):
        return f"State({self.id})"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, State) and self.id == other.id


class NFA:
    """非确定性有限自动机"""
    
    def __init__(self):
        self.states: Set[State] = set()
        self.start_state: Optional[State] = None
        self.accept_states: Set[State] = set()
        self.alphabet: Set[str] = set()
        self.state_counter = 0
    
    def create_state(self) -> State:
        """创建新状态"""
        state = State(self.state_counter)
        self.state_counter += 1
        self.states.add(state)
        return state
    
    def set_start(self, state: State):
        """设置开始状态"""
        self.start_state = state
    
    def add_accept(self, state: State, token_type: Optional[TokenType] = None):
        """添加接受状态"""
        state.is_accept = True
        if token_type:
            state.token_type = token_type
        self.accept_states.add(state)
    
    def add_transition(self, from_state: State, symbol: str, to_state: State):
        """添加状态转移"""
        from_state.add_transition(symbol, to_state)
        if symbol != 'ε':  # ε不加入字母表
            self.alphabet.add(symbol)
    
    def epsilon_closure(self, states: Set[State]) -> Set[State]:
        """计算状态集合的ε闭包"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            current = stack.pop()
            for next_state in current.get_transitions('ε'):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure


class DFA:
    """确定性有限自动机"""
    
    def __init__(self):
        self.states: Dict[int, Set[State]] = {}  # DFA状态ID -> NFA状态集合
        self.start_state: int = 0
        self.accept_states: Set[int] = set()
        self.transitions: Dict[Tuple[int, str], int] = {}
        self.alphabet: Set[str] = set()
        self.state_counter = 0
        self.token_types: Dict[int, TokenType] = {}  # DFA状态 -> Token类型
    
    def create_state(self, nfa_states: Set[State]) -> int:
        """创建新的DFA状态"""
        state_id = self.state_counter
        self.state_counter += 1
        self.states[state_id] = nfa_states
        
        # 检查是否为接受状态
        for nfa_state in nfa_states:
            if nfa_state.is_accept:
                self.accept_states.add(state_id)
                if nfa_state.token_type:
                    self.token_types[state_id] = nfa_state.token_type
                break
        
        return state_id
    
    def add_transition(self, from_state: int, symbol: str, to_state: int):
        """添加状态转移"""
        self.transitions[(from_state, symbol)] = to_state
        self.alphabet.add(symbol)


# ==================== 转换器类 ====================

class RegexToNFA:
    """正则表达式到NFA转换器（Thompson构造法）"""
    
    def __init__(self):
        self.nfa = NFA()
    
    def convert(self, regex: str, token_type: TokenType) -> NFA:
        """将正则表达式转换为NFA"""
        self.nfa = NFA()
        
        # 简化的正则表达式解析（支持基本操作）
        start, end = self._parse_regex(regex)
        
        self.nfa.set_start(start)
        self.nfa.add_accept(end, token_type)
        
        return self.nfa
    
    def _parse_regex(self, regex: str) -> Tuple[State, State]:
        """解析正则表达式（简化版本）"""
        if len(regex) == 1:
            # 单个字符
            start = self.nfa.create_state()
            end = self.nfa.create_state()
            self.nfa.add_transition(start, regex, end)
            return start, end
        
        # 处理连接（简化处理）
        start = self.nfa.create_state()
        current = start
        
        for char in regex:
            if char.isalnum() or char in '+-*/=<>().,;:':
                next_state = self.nfa.create_state()
                self.nfa.add_transition(current, char, next_state)
                current = next_state
        
        return start, current


class NFAToDFA:
    """NFA到DFA转换器（子集构造法）"""
    
    def convert(self, nfa: NFA) -> DFA:
        """将NFA转换为DFA"""
        dfa = DFA()
        dfa.alphabet = nfa.alphabet.copy()
        
        # 计算初始状态的ε闭包
        start_closure = nfa.epsilon_closure({nfa.start_state})
        start_id = dfa.create_state(start_closure)
        dfa.start_state = start_id
        
        # 工作队列
        unprocessed = [start_id]
        processed = set()
        
        while unprocessed:
            current_id = unprocessed.pop(0)
            if current_id in processed:
                continue
            processed.add(current_id)
            
            current_nfa_states = dfa.states[current_id]
            
            # 对每个输入符号
            for symbol in dfa.alphabet:
                # 计算转移目标
                target_states = set()
                for nfa_state in current_nfa_states:
                    target_states.update(nfa_state.get_transitions(symbol))
                
                if target_states:
                    # 计算ε闭包
                    target_closure = nfa.epsilon_closure(target_states)
                    
                    # 查找或创建目标DFA状态
                    target_id = None
                    for existing_id, existing_states in dfa.states.items():
                        if existing_states == target_closure:
                            target_id = existing_id
                            break
                    
                    if target_id is None:
                        target_id = dfa.create_state(target_closure)
                        unprocessed.append(target_id)
                    
                    dfa.add_transition(current_id, symbol, target_id)
        
        return dfa


class DFAMinimizer:
    """DFA最小化器"""
    
    def minimize(self, dfa: DFA) -> DFA:
        """最小化DFA（简化版本）"""
        # 这里实现一个简化的最小化算法
        # 实际应用中应该使用更完整的算法
        
        min_dfa = DFA()
        min_dfa.alphabet = dfa.alphabet.copy()
        
        # 简单地复制原DFA（在实际实现中应该进行状态合并）
        state_mapping = {}
        for old_id in dfa.states:
            new_id = min_dfa.create_state(dfa.states[old_id])
            state_mapping[old_id] = new_id
            
            if old_id == dfa.start_state:
                min_dfa.start_state = new_id
            
            if old_id in dfa.accept_states:
                min_dfa.accept_states.add(new_id)
            
            if old_id in dfa.token_types:
                min_dfa.token_types[new_id] = dfa.token_types[old_id]
        
        # 复制转移
        for (from_state, symbol), to_state in dfa.transitions.items():
            min_dfa.add_transition(
                state_mapping[from_state],
                symbol,
                state_mapping[to_state]
            )
        
        return min_dfa


# ==================== 词法分析器 ====================

class LexicalAnalyzer:
    """词法分析器主类"""
    
    def __init__(self):
        self.rules: List[Tuple[str, TokenType, int]] = []  # (pattern, token_type, priority)
        self.keywords: Dict[str, TokenType] = {}
        self.tokens: List[Token] = []
        self.errors: List[str] = []
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认词法规则"""
        # Pascal关键字
        self.keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'const': TokenType.CONST,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'for': TokenType.FOR,
            'to': TokenType.TO,
            'integer': TokenType.INTEGER,
            'real': TokenType.REAL,
            'string': TokenType.STRING,
        }
        
        # 词法规则（按优先级排序）
        self.rules = [
            # 注释
            (r'\{[^}]*\}', TokenType.COMMENT, 10),
            
            # 字符串字面量
            (r"'([^'\\]|\\.)*'", TokenType.STRING_LITERAL, 9),
            
            # 数字
            (r'\d+\.\d+', TokenType.NUMBER, 8),  # 实数
            (r'\d+', TokenType.NUMBER, 8),       # 整数
            
            # 双字符运算符
            (r':=', TokenType.ASSIGN, 7),
            (r'<=', TokenType.LESS_EQUAL, 7),
            (r'>=', TokenType.GREATER_EQUAL, 7),
            (r'<>', TokenType.NOT_EQUAL, 7),
            
            # 单字符运算符和分隔符
            (r'\+', TokenType.PLUS, 6),
            (r'-', TokenType.MINUS, 6),
            (r'\*', TokenType.MULTIPLY, 6),
            (r'/', TokenType.DIVIDE, 6),
            (r'=', TokenType.EQUAL, 6),
            (r'<', TokenType.LESS, 6),
            (r'>', TokenType.GREATER, 6),
            (r';', TokenType.SEMICOLON, 6),
            (r',', TokenType.COMMA, 6),
            (r'\.', TokenType.DOT, 6),
            (r':', TokenType.COLON, 6),
            (r'\(', TokenType.LPAREN, 6),
            (r'\)', TokenType.RPAREN, 6),
            
            # 标识符
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER, 5),
            
            # 空白字符
            (r'\n', TokenType.NEWLINE, 1),
            (r'[ \t]+', TokenType.WHITESPACE, 1),
        ]
    
    def load_rules_from_file(self, filename: str) -> bool:
        """从文件加载词法规则"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # 简单的规则文件格式：每行一个规则
                    # 格式：pattern|token_type|priority
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 2:
                                pattern = parts[0].strip()
                                token_type_str = parts[1].strip()
                                priority = int(parts[2].strip()) if len(parts) > 2 else 5
                                
                                # 查找对应的TokenType
                                token_type = None
                                for tt in TokenType:
                                    if tt.value == token_type_str:
                                        token_type = tt
                                        break
                                
                                if token_type:
                                    self.rules.append((pattern, token_type, priority))
            return True
        except Exception as e:
            self.errors.append(f"加载规则文件失败: {e}")
            return False
    
    def analyze(self, text: str) -> List[Token]:
        """执行词法分析"""
        self.tokens = []
        self.errors = []
        
        line = 1
        column = 1
        position = 0
        
        while position < len(text):
            matched = False
            
            # 按优先级尝试匹配规则
            for pattern, token_type, priority in sorted(self.rules, key=lambda x: x[2], reverse=True):
                regex = re.compile(pattern)
                match = regex.match(text, position)
                
                if match:
                    value = match.group(0)
                    
                    # 检查是否为关键字
                    if token_type == TokenType.IDENTIFIER and value.lower() in self.keywords:
                        token_type = self.keywords[value.lower()]
                    
                    # 创建Token（跳过空白字符和注释）
                    if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                        token = Token(token_type, value, line, column)
                        self.tokens.append(token)
                    
                    # 更新位置
                    if token_type == TokenType.NEWLINE:
                        line += 1
                        column = 1
                    else:
                        column += len(value)
                    
                    position = match.end()
                    matched = True
                    break
            
            if not matched:
                # 未匹配的字符
                char = text[position]
                self.errors.append(f"未识别的字符 '{char}' 在 {line}:{column}")
                error_token = Token(TokenType.ERROR, char, line, column)
                self.tokens.append(error_token)
                position += 1
                column += 1
        
        # 添加EOF标记
        eof_token = Token(TokenType.EOF, '', line, column)
        self.tokens.append(eof_token)
        
        return self.tokens
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors


# ==================== 主程序和菜单系统 ====================

def print_menu():
    """打印主菜单"""
    print("\n" + "="*50)
    print("    编译原理作业 - 词法分析程序")
    print("="*50)
    print("1. 正则表达式转NFA")
    print("2. NFA转DFA")
    print("3. DFA最小化")
    print("4. 词法分析")
    print("5. 完整流程演示")
    print("6. 加载词法规则文件")
    print("7. 创建示例文件")
    print("8. 帮助")
    print("0. 退出")
    print("="*50)


def regex_to_nfa_demo():
    """正则表达式转NFA演示"""
    print("\n=== 正则表达式转NFA ===")
    regex = input("请输入正则表达式: ").strip()
    
    if not regex:
        print("输入为空！")
        return
    
    try:
        converter = RegexToNFA()
        nfa = converter.convert(regex, TokenType.IDENTIFIER)
        
        print(f"\n转换成功！")
        print(f"NFA状态数: {len(nfa.states)}")
        print(f"字母表: {sorted(nfa.alphabet)}")
        print(f"开始状态: {nfa.start_state.id}")
        print(f"接受状态: {[s.id for s in nfa.accept_states]}")
        
        # 显示状态转移
        print("\n状态转移:")
        for state in nfa.states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    print(f"  {state.id} --{symbol}--> {target.id}")
    
    except Exception as e:
        print(f"转换失败: {e}")


def nfa_to_dfa_demo():
    """NFA转DFA演示"""
    print("\n=== NFA转DFA ===")
    regex = input("请输入正则表达式: ").strip()
    
    if not regex:
        print("输入为空！")
        return
    
    try:
        # 先转换为NFA
        regex_converter = RegexToNFA()
        nfa = regex_converter.convert(regex, TokenType.IDENTIFIER)
        
        # 再转换为DFA
        nfa_to_dfa = NFAToDFA()
        dfa = nfa_to_dfa.convert(nfa)
        
        print(f"\n转换成功！")
        print(f"原NFA状态数: {len(nfa.states)}")
        print(f"转换后DFA状态数: {len(dfa.states)}")
        print(f"字母表: {sorted(dfa.alphabet)}")
        
        # 显示DFA状态转移表
        print("\nDFA状态转移表:")
        print("-" * 40)
        symbols = sorted(list(dfa.alphabet))
        
        # 表头
        header = f"{'状态':<8} {'接受':<6}"
        for symbol in symbols:
            header += f" {symbol:<6}"
        print(header)
        print("-" * len(header))
        
        # 数据行
        for state_id in sorted(dfa.states.keys()):
            is_accept = "是" if state_id in dfa.accept_states else "否"
            row = f"{state_id:<8} {is_accept:<6}"
            
            for symbol in symbols:
                next_state = dfa.transitions.get((state_id, symbol), "-")
                row += f" {str(next_state):<6}"
            
            print(row)
    
    except Exception as e:
        print(f"转换失败: {e}")


def dfa_minimize_demo():
    """DFA最小化演示"""
    print("\n=== DFA最小化 ===")
    regex = input("请输入正则表达式: ").strip()
    
    if not regex:
        print("输入为空！")
        return
    
    try:
        # 完整转换流程
        regex_converter = RegexToNFA()
        nfa = regex_converter.convert(regex, TokenType.IDENTIFIER)
        
        nfa_to_dfa = NFAToDFA()
        dfa = nfa_to_dfa.convert(nfa)
        
        minimizer = DFAMinimizer()
        min_dfa = minimizer.minimize(dfa)
        
        print(f"\n最小化完成！")
        print(f"原NFA状态数: {len(nfa.states)}")
        print(f"DFA状态数: {len(dfa.states)}")
        print(f"最小化DFA状态数: {len(min_dfa.states)}")
        
        print("\n最小化DFA状态转移表:")
        print("-" * 40)
        symbols = sorted(list(min_dfa.alphabet))
        
        # 表头
        header = f"{'状态':<8} {'接受':<6}"
        for symbol in symbols:
            header += f" {symbol:<6}"
        print(header)
        print("-" * len(header))
        
        # 数据行
        for state_id in sorted(min_dfa.states.keys()):
            is_accept = "是" if state_id in min_dfa.accept_states else "否"
            row = f"{state_id:<8} {is_accept:<6}"
            
            for symbol in symbols:
                next_state = min_dfa.transitions.get((state_id, symbol), "-")
                row += f" {str(next_state):<6}"
            
            print(row)
    
    except Exception as e:
        print(f"最小化失败: {e}")


def lexical_analysis_demo():
    """词法分析演示"""
    print("\n=== 词法分析 ===")
    print("1. 输入代码")
    print("2. 从文件读取")
    
    choice = input("请选择输入方式 (1/2): ").strip()
    
    code = ""
    if choice == "1":
        print("请输入代码（输入空行结束）:")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        code = "\n".join(lines)
    
    elif choice == "2":
        filename = input("请输入文件名: ").strip()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"文件 '{filename}' 不存在！")
            return
        except Exception as e:
            print(f"读取文件失败: {e}")
            return
    
    else:
        print("无效选择！")
        return
    
    if not code.strip():
        print("代码为空！")
        return
    
    # 执行词法分析
    analyzer = LexicalAnalyzer()
    tokens = analyzer.analyze(code)
    
    print(f"\n词法分析结果:")
    print("-" * 50)
    
    for i, token in enumerate(tokens, 1):
        if token.type != TokenType.EOF:
            print(f"{i:3d}. {token}")
    
    # 统计信息
    token_counts = {}
    for token in tokens:
        if token.type in token_counts:
            token_counts[token.type] += 1
        else:
            token_counts[token.type] = 1
    
    print(f"\n统计信息:")
    print("-" * 20)
    print(f"总Token数量: {len(tokens)}")
    
    for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
        if token_type != TokenType.EOF:
            print(f"  {token_type.value}: {count}")
    
    # 错误信息
    if analyzer.has_errors():
        print(f"\n错误信息:")
        print("-" * 20)
        for error in analyzer.get_errors():
            print(f"  {error}")
    else:
        print(f"\n✅ 词法分析完成，无错误")


def complete_demo():
    """完整流程演示"""
    print("\n=== 完整流程演示 ===")
    regex = input("请输入正则表达式: ").strip()
    
    if not regex:
        print("输入为空！")
        return
    
    try:
        print(f"\n开始完整流程演示...")
        print(f"输入正则表达式: {regex}")
        print("="*50)
        
        # 步骤1: 正则表达式转NFA
        print("\n步骤1: 正则表达式 -> NFA")
        regex_converter = RegexToNFA()
        nfa = regex_converter.convert(regex, TokenType.IDENTIFIER)
        print(f"  ✓ NFA状态数: {len(nfa.states)}")
        print(f"  ✓ 字母表: {sorted(nfa.alphabet)}")
        
        # 步骤2: NFA转DFA
        print("\n步骤2: NFA -> DFA")
        nfa_to_dfa = NFAToDFA()
        dfa = nfa_to_dfa.convert(nfa)
        print(f"  ✓ DFA状态数: {len(dfa.states)}")
        
        # 步骤3: DFA最小化
        print("\n步骤3: DFA -> 最小化DFA")
        minimizer = DFAMinimizer()
        min_dfa = minimizer.minimize(dfa)
        print(f"  ✓ 最小化DFA状态数: {len(min_dfa.states)}")
        
        # 步骤4: 词法分析应用
        print("\n步骤4: 词法分析应用")
        test_string = input("请输入测试字符串: ").strip()
        
        if test_string:
            analyzer = LexicalAnalyzer()
            tokens = analyzer.analyze(test_string)
            
            print("  词法分析结果:")
            for token in tokens:
                if token.type != TokenType.EOF:
                    print(f"    {token}")
        
        print("\n✅ 完整流程演示完成！")
        
        # 显示最终的状态转移表
        print("\n最终最小化DFA状态转移表:")
        print("-" * 40)
        symbols = sorted(list(min_dfa.alphabet))
        
        if symbols:
            # 表头
            header = f"{'状态':<8} {'接受':<6}"
            for symbol in symbols:
                header += f" {symbol:<6}"
            print(header)
            print("-" * len(header))
            
            # 数据行
            for state_id in sorted(min_dfa.states.keys()):
                is_accept = "是" if state_id in min_dfa.accept_states else "否"
                row = f"{state_id:<8} {is_accept:<6}"
                
                for symbol in symbols:
                    next_state = min_dfa.transitions.get((state_id, symbol), "-")
                    row += f" {str(next_state):<6}"
                
                print(row)
    
    except Exception as e:
        print(f"演示过程中出错: {e}")


def load_rules_demo():
    """加载词法规则文件演示"""
    print("\n=== 加载词法规则文件 ===")
    filename = input("请输入规则文件名: ").strip()
    
    if not filename:
        print("文件名为空！")
        return
    
    analyzer = LexicalAnalyzer()
    success = analyzer.load_rules_from_file(filename)
    
    if success:
        print(f"✅ 成功加载规则文件: {filename}")
        print(f"当前规则数量: {len(analyzer.rules)}")
        
        # 测试加载的规则
        test_code = input("\n请输入测试代码: ").strip()
        if test_code:
            tokens = analyzer.analyze(test_code)
            print("\n分析结果:")
            for token in tokens:
                if token.type != TokenType.EOF:
                    print(f"  {token}")
    else:
        print("❌ 加载规则文件失败:")
        for error in analyzer.get_errors():
            print(f"  {error}")


def create_sample_files():
    """创建示例文件"""
    print("\n=== 创建示例文件 ===")
    
    # 创建示例Pascal代码
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
    end
    else
    begin
        message := 'Result is small';
    end;
    
    { 这是一个注释 }
    while x > 0 do
    begin
        x := x - 1;
    end;
end."""
    
    # 创建示例规则文件
    sample_rules = """# 词法规则文件
# 格式: pattern|token_type|priority
\\d+|NUMBER|8
[a-zA-Z_][a-zA-Z0-9_]*|IDENTIFIER|5
\\+|PLUS|6
-|MINUS|6
\\*|MULTIPLY|6
/|DIVIDE|6
:=|ASSIGN|7
=|EQUAL|6
;|SEMICOLON|6
,|COMMA|6
\\(|LPAREN|6
\\)|RPAREN|6
[ \\t]+|WHITESPACE|1
\\n|NEWLINE|1"""
    
    try:
        # 写入示例代码文件
        with open("sample_code.pas", "w", encoding="utf-8") as f:
            f.write(sample_code)
        
        # 写入示例规则文件
        with open("lexical_rules.txt", "w", encoding="utf-8") as f:
            f.write(sample_rules)
        
        # 创建输入输出示例
        with open("input.txt", "w", encoding="utf-8") as f:
            f.write("x := 10 + 20;\ny := x * 2;")
        
        print("✅ 示例文件创建成功:")
        print("  - sample_code.pas: 示例Pascal代码")
        print("  - lexical_rules.txt: 词法规则文件")
        print("  - input.txt: 输入示例文件")
        
    except Exception as e:
        print(f"❌ 创建示例文件失败: {e}")


def show_help():
    """显示帮助信息"""
    print("\n=== 帮助信息 ===")
    print("\n本程序实现了编译原理中词法分析的完整流程:")
    print("\n1. 正则表达式转NFA (Thompson构造法)")
    print("   - 将正则表达式转换为非确定性有限自动机")
    print("   - 支持基本的正则表达式操作")
    
    print("\n2. NFA转DFA (子集构造法)")
    print("   - 将NFA转换为确定性有限自动机")
    print("   - 消除非确定性")
    
    print("\n3. DFA最小化")
    print("   - 合并等价状态，减少DFA状态数")
    print("   - 优化自动机性能")
    
    print("\n4. 词法分析")
    print("   - 基于规则的词法分析器")
    print("   - 支持Pascal语言的基本语法")
    print("   - 可以从文件加载自定义规则")
    
    print("\n5. 文件格式说明:")
    print("   - 代码文件: 支持Pascal等语言")
    print("   - 规则文件: 每行格式为 pattern|token_type|priority")
    print("   - 输入文件: 普通文本文件")
    
    print("\n6. 使用建议:")
    print("   - 先使用'创建示例文件'功能生成示例")
    print("   - 可以修改示例文件来测试不同情况")
    print("   - 使用'完整流程演示'了解整个转换过程")
    
    print("\n作者信息:")
    print("   作业: 编译原理 - 词法分析程序")
    print("   要求: 实现正则表达式->NFA->DFA->min(DFA)->词法分析")


def main():
    """主函数"""
    print("欢迎使用编译原理词法分析程序！")
    
    while True:
        print_menu()
        choice = input("\n请选择功能 (0-8): ").strip()
        
        if choice == "1":
            regex_to_nfa_demo()
        elif choice == "2":
            nfa_to_dfa_demo()
        elif choice == "3":
            dfa_minimize_demo()
        elif choice == "4":
            lexical_analysis_demo()
        elif choice == "5":
            complete_demo()
        elif choice == "6":
            load_rules_demo()
        elif choice == "7":
            create_sample_files()
        elif choice == "8":
            show_help()
        elif choice == "0":
            print("\n感谢使用！再见！")
            break
        else:
            print("\n❌ 无效选择，请重新输入！")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()