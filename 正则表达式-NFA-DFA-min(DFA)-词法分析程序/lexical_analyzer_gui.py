# -*- coding: utf-8 -*-
"""
编译原理作业 - 词法分析程序
实现正则表达式->NFA->DFA->min(DFA)->词法分析的完整过程

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""


import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import re
from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
import json

# ==================== 数据结构定义 ====================

class TokenType(Enum):
    """Token类型枚举"""
    # Pascal关键字
    PROGRAM = "PROGRAM"
    VAR = "VAR"
    BEGIN = "BEGIN"
    END = "END"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    FOR = "FOR"
    TO = "TO"
    REPEAT = "REPEAT"
    UNTIL = "UNTIL"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"
    
    # 数据类型
    INTEGER = "INTEGER"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    CHAR = "CHAR"
    STRING = "STRING"
    
    # 标识符和字面量
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"
    
    # 运算符
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    ASSIGN = "ASSIGN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # 分隔符
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT = "DOT"
    COLON = "COLON"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    
    # 特殊
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"
    EOF = "EOF"
    ERROR = "ERROR"

@dataclass
class Token:
    """Token数据类"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

class State:
    """自动机状态类"""
    def __init__(self, state_id: int, is_final: bool = False, token_type: Optional[TokenType] = None):
        self.id = state_id
        self.is_final = is_final
        self.token_type = token_type
        self.transitions: Dict[str, Set['State']] = {}
        self.epsilon_transitions: Set['State'] = set()
    
    def add_transition(self, symbol: str, target_state: 'State'):
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(target_state)
    
    def add_epsilon_transition(self, target_state: 'State'):
        self.epsilon_transitions.add(target_state)
    
    def get_transitions(self, symbol: str) -> Set['State']:
        return self.transitions.get(symbol, set())
    
    def __str__(self):
        return f"State({self.id}, final={self.is_final})"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, State) and self.id == other.id

class NFA:
    """非确定性有限自动机"""
    def __init__(self):
        self.states: Set[State] = set()
        self.start_state: Optional[State] = None
        self.final_states: Set[State] = set()
        self.alphabet: Set[str] = set()
    
    def add_state(self, state: State):
        self.states.add(state)
        if state.is_final:
            self.final_states.add(state)
    
    def set_start_state(self, state: State):
        self.start_state = state
        self.add_state(state)
    
    def add_transition(self, from_state: State, symbol: str, to_state: State):
        from_state.add_transition(symbol, to_state)
        self.alphabet.add(symbol)
        self.add_state(from_state)
        self.add_state(to_state)

class DFA:
    """确定性有限自动机"""
    def __init__(self):
        self.states: Set[frozenset] = set()
        self.start_state: Optional[frozenset] = None
        self.final_states: Set[frozenset] = set()
        self.transitions: Dict[Tuple[frozenset, str], frozenset] = {}
        self.alphabet: Set[str] = set()
        self.state_token_types: Dict[frozenset, TokenType] = {}

# ==================== 转换器类 ====================

class RegexToNFA:
    """正则表达式到NFA转换器 (Thompson构造法)"""
    
    def __init__(self):
        self.state_counter = 0
    
    def new_state(self, is_final=False, token_type=None):
        state = State(self.state_counter, is_final, token_type)
        self.state_counter += 1
        return state
    
    def convert(self, regex: str, token_type: TokenType) -> NFA:
        """将正则表达式转换为NFA"""
        self.state_counter = 0
        
        try:
            # 预处理：展开字符类和转义字符
            processed_regex = self._preprocess_regex(regex)
            
            # 添加连接操作符
            concat_regex = self._add_concat_operator(processed_regex)
            
            # 转换为后缀表达式
            postfix = self._to_postfix(concat_regex)
            
            # 构建NFA
            nfa = self._build_nfa(postfix)
            
            # 设置最终状态的token类型
            for final_state in nfa.final_states:
                final_state.token_type = token_type
            
            return nfa
        except Exception as e:
            # 如果转换失败，创建一个简单的字符匹配NFA
            print(f"正则表达式转换失败: {e}，使用简单匹配")
            return self._create_simple_nfa(regex, token_type)
    
    def _create_simple_nfa(self, regex: str, token_type: TokenType) -> NFA:
        """创建简单的字符串匹配NFA"""
        nfa = NFA()
        current = self.new_state()
        nfa.set_start_state(current)
        
        # 为每个字符创建状态转移
        for i, char in enumerate(regex):
            next_state = self.new_state(is_final=(i == len(regex) - 1), token_type=token_type if i == len(regex) - 1 else None)
            current.add_transition(char, next_state)
            nfa.add_state(next_state)
            nfa.alphabet.add(char)
            current = next_state
        
        return nfa
    
    def _preprocess_regex(self, regex: str) -> str:
        """预处理正则表达式"""
        result = []
        i = 0
        while i < len(regex):
            if regex[i] == '\\' and i + 1 < len(regex):
                # 处理转义字符
                next_char = regex[i + 1]
                if next_char == 'd':
                    result.append('[0-9]')
                elif next_char == 'w':
                    result.append('[a-zA-Z0-9_]')
                elif next_char == 's':
                    result.append('[ \t\n\r]')
                elif next_char in '+*?()[]{}|.^$\\':
                    result.append(next_char)
                else:
                    result.append(next_char)
                i += 2
            elif regex[i] == '[' and i + 1 < len(regex):
                # 处理字符类
                j = i + 1
                while j < len(regex) and regex[j] != ']':
                    j += 1
                if j < len(regex):
                    char_class = regex[i:j+1]
                    expanded = self._expand_char_class(char_class)
                    result.append(f'({expanded})')
                    i = j + 1
                else:
                    result.append(regex[i])
                    i += 1
            else:
                result.append(regex[i])
                i += 1
        
        return ''.join(result)
    
    def _expand_char_class(self, char_class: str) -> str:
        """展开字符类为选择表达式"""
        content = char_class[1:-1]  # 去掉方括号
        chars = []
        i = 0
        
        while i < len(content):
            if i + 2 < len(content) and content[i + 1] == '-':
                # 处理范围 a-z
                start = ord(content[i])
                end = ord(content[i + 2])
                for code in range(start, end + 1):
                    chars.append(chr(code))
                i += 3
            else:
                chars.append(content[i])
                i += 1
        
        return '|'.join(chars) if chars else ''
    
    def _add_concat_operator(self, regex: str) -> str:
        """添加连接操作符"""
        output = []
        for i in range(len(regex)):
            output.append(regex[i])
            if (i + 1 < len(regex) and 
                regex[i] not in '(|' and 
                regex[i + 1] not in ')|*+?'):
                output.append('.')
        return ''.join(output)
    
    def _to_postfix(self, regex: str) -> List[str]:
        """转换为后缀表达式"""
        precedence = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
        operators = {'|', '.', '*', '+', '?', '(', ')'}
        
        output = []
        operator_stack = []
        
        for token in regex:
            if token not in operators:
                output.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                operator_stack.pop()  # 弹出左括号
            else:
                while (operator_stack and operator_stack[-1] != '(' and 
                       precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
        
        while operator_stack:
            output.append(operator_stack.pop())
        
        return output
    
    def _build_nfa(self, postfix: List[str]) -> NFA:
        """根据后缀表达式构建NFA"""
        stack = []
        
        for token in postfix:
            if token == '|':
                if len(stack) < 2:
                    raise ValueError(f"联合操作需要两个操作数，当前栈大小: {len(stack)}")
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self._union_nfa(nfa1, nfa2))
            elif token == '.':
                if len(stack) < 2:
                    raise ValueError(f"连接操作需要两个操作数，当前栈大小: {len(stack)}")
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self._concat_nfa(nfa1, nfa2))
            elif token == '*':
                if len(stack) < 1:
                    raise ValueError(f"克莱尼星操作需要一个操作数，当前栈大小: {len(stack)}")
                nfa = stack.pop()
                stack.append(self._kleene_star_nfa(nfa))
            elif token == '+':
                if len(stack) < 1:
                    raise ValueError(f"加号操作需要一个操作数，当前栈大小: {len(stack)}")
                nfa = stack.pop()
                stack.append(self._plus_nfa(nfa))
            elif token == '?':
                if len(stack) < 1:
                    raise ValueError(f"问号操作需要一个操作数，当前栈大小: {len(stack)}")
                nfa = stack.pop()
                stack.append(self._question_nfa(nfa))
            else:
                # 处理字符或字符组
                if token.startswith('(') and token.endswith(')'):
                    # 处理字符类展开后的选择表达式
                    choices = token[1:-1].split('|')
                    if len(choices) > 1:
                        nfa_list = [self._basic_nfa(choice) for choice in choices]
                        result_nfa = nfa_list[0]
                        for i in range(1, len(nfa_list)):
                            result_nfa = self._union_nfa(result_nfa, nfa_list[i])
                        stack.append(result_nfa)
                    else:
                        stack.append(self._basic_nfa(choices[0]))
                else:
                    stack.append(self._basic_nfa(token))
        
        if len(stack) != 1:
            raise ValueError(f"表达式构建失败，最终栈大小应为1，实际为: {len(stack)}")
        
        return stack[0]
    
    def _create_empty_nfa(self) -> NFA:
        nfa = NFA()
        start = self.new_state()
        final = self.new_state(is_final=True)
        start.add_epsilon_transition(final)
        nfa.set_start_state(start)
        nfa.add_state(final)
        return nfa
    
    def _basic_nfa(self, symbol: str) -> NFA:
        """创建基本NFA"""
        nfa = NFA()
        start = self.new_state()
        end = self.new_state(is_final=True)
        
        nfa.set_start_state(start)
        nfa.add_state(end)
        start.add_transition(symbol, end)
        nfa.alphabet.add(symbol)
        
        return nfa
    
    def _concat_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """连接两个NFA"""
        result = NFA()
        
        # 复制所有状态
        state_map = {}
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                new_state = self.new_state()
                new_state.is_final = False  # 重置接受状态
                state_map[state] = new_state
                result.states.add(new_state)
        
        # 复制转移
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        state_map[state].add_transition(symbol, state_map[target])
                        result.alphabet.add(symbol)
                for target in state.epsilon_transitions:
                    state_map[state].add_epsilon_transition(state_map[target])
        
        # 设置开始状态
        result.set_start_state(state_map[nfa1.start_state])
        
        # 连接nfa1的接受状态到nfa2的开始状态
        for accept_state in nfa1.final_states:
            state_map[accept_state].add_epsilon_transition(state_map[nfa2.start_state])
        
        # 设置nfa2的接受状态为结果的接受状态
        for accept_state in nfa2.final_states:
            state_map[accept_state].is_final = True
            result.final_states.add(state_map[accept_state])
        
        return result
    
    def _union_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """联合两个NFA"""
        result = NFA()
        
        # 创建新的开始和结束状态
        new_start = self.new_state()
        new_end = self.new_state(is_final=True)
        
        result.set_start_state(new_start)
        result.add_state(new_end)
        
        # 复制所有状态
        state_map = {}
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                new_state = self.new_state()
                new_state.is_final = False
                state_map[state] = new_state
                result.states.add(new_state)
        
        # 复制转移
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        state_map[state].add_transition(symbol, state_map[target])
                        result.alphabet.add(symbol)
                for target in state.epsilon_transitions:
                    state_map[state].add_epsilon_transition(state_map[target])
        
        # 连接新开始状态到两个NFA的开始状态
        new_start.add_epsilon_transition(state_map[nfa1.start_state])
        new_start.add_epsilon_transition(state_map[nfa2.start_state])
        
        # 连接两个NFA的接受状态到新结束状态
        for accept_state in nfa1.final_states:
            state_map[accept_state].add_epsilon_transition(new_end)
        for accept_state in nfa2.final_states:
            state_map[accept_state].add_epsilon_transition(new_end)
        
        return result
    
    def _kleene_star_nfa(self, nfa: NFA) -> NFA:
        """克莱尼星操作"""
        result = NFA()
        
        # 创建新的开始和结束状态
        new_start = self.new_state()
        new_end = self.new_state(is_final=True)
        
        result.set_start_state(new_start)
        result.add_state(new_end)
        
        # 复制所有状态
        state_map = {}
        for state in nfa.states:
            new_state = self.new_state()
            new_state.is_final = False
            state_map[state] = new_state
            result.states.add(new_state)
        
        # 复制转移
        for state in nfa.states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    state_map[state].add_transition(symbol, state_map[target])
                    result.alphabet.add(symbol)
            for target in state.epsilon_transitions:
                state_map[state].add_epsilon_transition(state_map[target])
        
        # 添加ε转移
        new_start.add_epsilon_transition(state_map[nfa.start_state])  # 进入
        new_start.add_epsilon_transition(new_end)  # 跳过
        
        for accept_state in nfa.final_states:
            state_map[accept_state].add_epsilon_transition(new_end)  # 退出
            state_map[accept_state].add_epsilon_transition(state_map[nfa.start_state])  # 循环
        
        return result
    
    def _plus_nfa(self, nfa: NFA) -> NFA:
        """加号操作 (一次或多次)"""
        # A+ = AA*
        star_nfa = self._kleene_star_nfa(nfa)
        return self._concat_nfa(nfa, star_nfa)
    
    def _question_nfa(self, nfa: NFA) -> NFA:
        """问号操作 (零次或一次)"""
        result = NFA()
        
        # 创建新的开始和结束状态
        new_start = self.new_state()
        new_end = self.new_state(is_final=True)
        
        result.set_start_state(new_start)
        result.add_state(new_end)
        
        # 复制所有状态
        state_map = {}
        for state in nfa.states:
            new_state = self.new_state()
            new_state.is_final = False
            state_map[state] = new_state
            result.states.add(new_state)
        
        # 复制转移
        for state in nfa.states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    state_map[state].add_transition(symbol, state_map[target])
                    result.alphabet.add(symbol)
            for target in state.epsilon_transitions:
                state_map[state].add_epsilon_transition(state_map[target])
        
        # 添加ε转移
        new_start.add_epsilon_transition(state_map[nfa.start_state])  # 进入
        new_start.add_epsilon_transition(new_end)  # 跳过
        
        for accept_state in nfa.final_states:
            state_map[accept_state].add_epsilon_transition(new_end)  # 退出
        
        return result

class NFAToDFA:
    """NFA到DFA转换器"""
    
    def convert(self, nfa: NFA) -> DFA:
        """使用子集构造算法将NFA转换为DFA"""
        dfa = DFA()
        
        # 计算初始状态的ε闭包
        start_closure = self._epsilon_closure({nfa.start_state})
        dfa.start_state = frozenset(start_closure)
        dfa.states.add(dfa.start_state)
        
        # 检查是否为最终状态
        if any(state.is_final for state in start_closure):
            dfa.final_states.add(dfa.start_state)
            # 设置token类型
            for state in start_closure:
                if state.is_final and state.token_type:
                    dfa.state_token_types[dfa.start_state] = state.token_type
                    break
        
        # 工作队列
        unprocessed = [dfa.start_state]
        processed = set()
        
        while unprocessed:
            current_dfa_state = unprocessed.pop(0)
            if current_dfa_state in processed:
                continue
            processed.add(current_dfa_state)
            
            # 对每个输入符号
            for symbol in nfa.alphabet:
                # 计算转换
                next_states = set()
                for nfa_state in current_dfa_state:
                    next_states.update(nfa_state.get_transitions(symbol))
                
                if next_states:
                    # 计算ε闭包
                    next_closure = self._epsilon_closure(next_states)
                    next_dfa_state = frozenset(next_closure)
                    
                    # 添加状态和转换
                    if next_dfa_state not in dfa.states:
                        dfa.states.add(next_dfa_state)
                        unprocessed.append(next_dfa_state)
                        
                        # 检查是否为最终状态
                        if any(state.is_final for state in next_closure):
                            dfa.final_states.add(next_dfa_state)
                            # 设置token类型
                            for state in next_closure:
                                if state.is_final and state.token_type:
                                    dfa.state_token_types[next_dfa_state] = state.token_type
                                    break
                    
                    dfa.transitions[(current_dfa_state, symbol)] = next_dfa_state
                    dfa.alphabet.add(symbol)
        
        return dfa
    
    def _epsilon_closure(self, states: Set[State]) -> Set[State]:
        """计算状态集合的ε闭包"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            current = stack.pop()
            for epsilon_target in current.epsilon_transitions:
                if epsilon_target not in closure:
                    closure.add(epsilon_target)
                    stack.append(epsilon_target)
        
        return closure

class DFAMinimizer:
    """DFA最小化器"""
    
    def minimize(self, dfa: DFA) -> DFA:
        """使用分割算法最小化DFA"""
        if not dfa.states:
            return dfa
        
        # 初始分割：最终状态和非最终状态
        final_states = dfa.final_states
        non_final_states = dfa.states - final_states
        
        partitions = []
        if non_final_states:
            partitions.append(non_final_states)
        if final_states:
            partitions.append(final_states)
        
        # 迭代分割直到稳定
        changed = True
        while changed:
            changed = False
            new_partitions = []
            
            for partition in partitions:
                sub_partitions = self._split_partition(partition, partitions, dfa)
                if len(sub_partitions) > 1:
                    changed = True
                new_partitions.extend(sub_partitions)
            
            partitions = new_partitions
        
        # 构建最小化的DFA
        return self._build_minimized_dfa(dfa, partitions)
    
    def _split_partition(self, partition: Set[frozenset], all_partitions: List[Set[frozenset]], dfa: DFA) -> List[Set[frozenset]]:
        """分割分区"""
        if len(partition) <= 1:
            return [partition]
        
        # 按转换行为分组
        groups = {}
        
        for state in partition:
            signature = []
            for symbol in sorted(dfa.alphabet):
                target = dfa.transitions.get((state, symbol))
                if target:
                    # 找到目标状态所在的分区
                    target_partition_idx = -1
                    for i, p in enumerate(all_partitions):
                        if target in p:
                            target_partition_idx = i
                            break
                    signature.append(target_partition_idx)
                else:
                    signature.append(-1)
            
            signature_tuple = tuple(signature)
            if signature_tuple not in groups:
                groups[signature_tuple] = set()
            groups[signature_tuple].add(state)
        
        return list(groups.values())
    
    def _build_minimized_dfa(self, original_dfa: DFA, partitions: List[Set[frozenset]]) -> DFA:
        """根据分区构建最小化的DFA"""
        minimized_dfa = DFA()
        
        # 创建分区到新状态的映射
        partition_to_state = {}
        for i, partition in enumerate(partitions):
            # 创建新的状态标识符，使用字符串而不是frozenset
            new_state_id = f"q{i}"
            partition_to_state[frozenset(partition)] = frozenset({new_state_id})
        
        # 设置状态
        for partition in partitions:
            new_state = partition_to_state[frozenset(partition)]
            minimized_dfa.states.add(new_state)
            
            # 检查是否包含原始的开始状态
            if original_dfa.start_state in partition:
                minimized_dfa.start_state = new_state
            
            # 检查是否包含最终状态
            if any(state in original_dfa.final_states for state in partition):
                minimized_dfa.final_states.add(new_state)
                # 设置token类型
                for state in partition:
                    if state in original_dfa.state_token_types:
                        minimized_dfa.state_token_types[new_state] = original_dfa.state_token_types[state]
                        break
        
        # 设置转换
        for partition in partitions:
            current_state = partition_to_state[frozenset(partition)]
            representative = next(iter(partition))
            
            for symbol in original_dfa.alphabet:
                target = original_dfa.transitions.get((representative, symbol))
                if target:
                    # 找到目标状态所在的分区
                    for target_partition in partitions:
                        if target in target_partition:
                            target_state = partition_to_state[frozenset(target_partition)]
                            minimized_dfa.transitions[(current_state, symbol)] = target_state
                            minimized_dfa.alphabet.add(symbol)
                            break
        
        return minimized_dfa

# ==================== 词法分析器 ====================

class LexicalAnalyzer:
    """词法分析器"""
    
    def __init__(self):
        self.rules = []
        self.errors = []
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认词法规则"""
        # Pascal关键字
        keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'for': TokenType.FOR,
            'to': TokenType.TO,
            'repeat': TokenType.REPEAT,
            'until': TokenType.UNTIL,
            'function': TokenType.FUNCTION,
            'procedure': TokenType.PROCEDURE,
            'integer': TokenType.INTEGER,
            'real': TokenType.REAL,
            'boolean': TokenType.BOOLEAN,
            'char': TokenType.CHAR,
            'string': TokenType.STRING,
        }
        
        for keyword, token_type in keywords.items():
            self.add_rule(f'\\b{keyword}\\b', token_type, 10)
        
        # 注释
        self.add_rule(r'//.*', TokenType.COMMENT, 9)
        self.add_rule(r'/\*[\s\S]*?\*/', TokenType.COMMENT, 9)
        
        # 字符串和字符字面量
        self.add_rule(r"'([^'\\\\]|\\\\.)*'", TokenType.STRING_LITERAL, 8)
        self.add_rule(r"'([^'\\\\]|\\\\.)?'", TokenType.CHAR_LITERAL, 8)
        
        # 数字
        self.add_rule(r'\d+\.\d+', TokenType.NUMBER, 7)
        self.add_rule(r'\d+', TokenType.NUMBER, 7)
        
        # 运算符
        self.add_rule(r':=', TokenType.ASSIGN, 6)
        self.add_rule(r'<=', TokenType.LESS_EQUAL, 6)
        self.add_rule(r'>=', TokenType.GREATER_EQUAL, 6)
        self.add_rule(r'<>', TokenType.NOT_EQUAL, 6)
        self.add_rule(r'=', TokenType.EQUAL, 6)
        self.add_rule(r'<', TokenType.LESS_THAN, 6)
        self.add_rule(r'>', TokenType.GREATER_THAN, 6)
        self.add_rule(r'\+', TokenType.PLUS, 6)
        self.add_rule(r'-', TokenType.MINUS, 6)
        self.add_rule(r'\*', TokenType.MULTIPLY, 6)
        self.add_rule(r'/', TokenType.DIVIDE, 6)
        
        # 分隔符
        self.add_rule(r';', TokenType.SEMICOLON, 5)
        self.add_rule(r',', TokenType.COMMA, 5)
        self.add_rule(r'\.', TokenType.DOT, 5)
        self.add_rule(r':', TokenType.COLON, 5)
        self.add_rule(r'\(', TokenType.LEFT_PAREN, 5)
        self.add_rule(r'\)', TokenType.RIGHT_PAREN, 5)
        self.add_rule(r'\[', TokenType.LEFT_BRACKET, 5)
        self.add_rule(r'\]', TokenType.RIGHT_BRACKET, 5)
        
        # 标识符
        self.add_rule(r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER, 4)
        
        # 空白字符
        self.add_rule(r'\s+', TokenType.WHITESPACE, 1)
    
    def add_rule(self, pattern: str, token_type: TokenType, priority: int = 0):
        """添加词法规则"""
        try:
            rule = {
                'pattern': pattern,
                'token_type': token_type,
                'priority': priority,
                'regex': re.compile(pattern)
            }
            self.rules.append(rule)
            # 按优先级排序
            self.rules.sort(key=lambda x: x['priority'], reverse=True)
        except re.error as e:
            self.errors.append(f"无效的正则表达式 '{pattern}': {e}")
    
    def analyze(self, text: str) -> List[Token]:
        """执行词法分析"""
        tokens = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 1
            position = 0
            
            while position < len(line):
                matched = False
                
                for rule in self.rules:
                    match = rule['regex'].match(line, position)
                    if match:
                        value = match.group(0)
                        
                        # 跳过空白字符和注释
                        if rule['token_type'] not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                            token = Token(
                                type=rule['token_type'],
                                value=value,
                                line=line_num,
                                column=column
                            )
                            tokens.append(token)
                        
                        position = match.end()
                        column += len(value)
                        matched = True
                        break
                
                if not matched:
                    # 错误处理
                    error_char = line[position]
                    self.errors.append(f"未识别的字符 '{error_char}' 在 {line_num}:{column}")
                    tokens.append(Token(
                        type=TokenType.ERROR,
                        value=error_char,
                        line=line_num,
                        column=column
                    ))
                    position += 1
                    column += 1
        
        # 添加EOF token
        tokens.append(Token(
            type=TokenType.EOF,
            value='',
            line=len(lines),
            column=1
        ))
        
        return tokens
    
    def get_errors(self) -> List[str]:
        return self.errors
    
    def clear_errors(self):
        self.errors = []

# ==================== GUI应用程序 ====================

class LexicalAnalyzerGUI:
    """词法分析器GUI应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("词法分析程序 - GUI版本")
        self.root.geometry("1200x800")
        
        # 初始化组件
        self.analyzer = LexicalAnalyzer()
        self.regex_converter = RegexToNFA()
        self.nfa_converter = NFAToDFA()
        self.dfa_minimizer = DFAMinimizer()
        
        # 存储当前的自动机
        self.current_nfa = None
        self.current_dfa = None
        self.current_min_dfa = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 词法分析标签页
        self.create_lexical_tab(notebook)
        
        # 正则表达式转换标签页
        self.create_regex_tab(notebook)
        
        # 自动机可视化标签页
        self.create_visualization_tab(notebook)
        
        # 帮助标签页
        self.create_help_tab(notebook)
    
    def create_lexical_tab(self, parent):
        """创建词法分析标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="词法分析")
        
        # 左侧输入区域
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="输入代码:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.code_input = scrolledtext.ScrolledText(left_frame, height=15, font=("Consolas", 10))
        self.code_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 示例代码
        sample_code = """program Example;
var
    x, y: integer;
    result: real;
begin
    x := 10;
    y := 20;
    if x > y then
        result := x / y
    else
        result := y / x;
    writeln(result);
end."""
        self.code_input.insert(tk.END, sample_code)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="分析代码", command=self.analyze_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空", command=self.clear_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="加载文件", command=self.load_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存结果", command=self.save_results).pack(side=tk.LEFT)
        
        # 右侧结果区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(right_frame, text="分析结果:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # 创建结果表格
        columns = ("序号", "类型", "值", "行", "列")
        self.result_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 统计信息
        stats_frame = ttk.LabelFrame(right_frame, text="统计信息")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_text = tk.Text(stats_frame, height=6, font=("Consolas", 9))
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
    
    def create_regex_tab(self, parent):
        """创建正则表达式转换标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="正则表达式转换")
        
        # 输入区域
        input_frame = ttk.LabelFrame(frame, text="输入")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="正则表达式:").pack(anchor=tk.W, padx=5, pady=5)
        self.regex_input = ttk.Entry(input_frame, font=("Consolas", 12))
        self.regex_input.pack(fill=tk.X, padx=5, pady=5)
        self.regex_input.insert(0, "(a|b)*abb")
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="转换为NFA", command=self.convert_to_nfa).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="NFA转DFA", command=self.convert_to_dfa).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="DFA最小化", command=self.minimize_dfa).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="完整流程", command=self.full_conversion).pack(side=tk.LEFT)
        
        # 结果区域
        result_frame = ttk.LabelFrame(frame, text="转换结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.conversion_result = scrolledtext.ScrolledText(result_frame, height=20, font=("Consolas", 10))
        self.conversion_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_visualization_tab(self, parent):
        """创建自动机可视化标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="自动机可视化")
        
        # 控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="选择要可视化的自动机:").pack(side=tk.LEFT)
        
        self.viz_var = tk.StringVar(value="NFA")
        ttk.Radiobutton(control_frame, text="NFA", variable=self.viz_var, value="NFA").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(control_frame, text="DFA", variable=self.viz_var, value="DFA").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(control_frame, text="最小DFA", variable=self.viz_var, value="MIN_DFA").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="生成图形", command=self.visualize_automaton).pack(side=tk.LEFT, padx=20)
        ttk.Button(control_frame, text="保存图片", command=self.save_visualization).pack(side=tk.LEFT, padx=5)
        
        # 图形显示区域
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_help_tab(self, parent):
        """创建帮助标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="帮助")
        
        help_text = scrolledtext.ScrolledText(frame, font=("Arial", 11))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
词法分析程序 - GUI版本使用说明

=== 功能概述 ===
本程序提供了完整的词法分析功能，包括：
1. Pascal语言词法分析
2. 正则表达式到NFA转换
3. NFA到DFA转换
4. DFA最小化
5. 自动机可视化

=== 词法分析标签页 ===
• 在左侧文本框中输入Pascal代码
• 点击"分析代码"按钮执行词法分析
• 右侧表格显示识别的Token
• 底部显示统计信息
• 支持加载文件和保存结果

=== 正则表达式转换标签页 ===
• 输入正则表达式（支持基本操作符：|, *, +, ?）
• 可以分步执行转换或一次性完成全流程
• 结果显示每个步骤的详细信息

=== 自动机可视化标签页 ===
• 选择要可视化的自动机类型
• 点击"生成图形"查看状态转换图
• 支持保存图片到文件

=== 支持的Token类型 ===
• 关键字：program, var, begin, end, if, then, else, while, do, for, to, repeat, until, function, procedure
• 数据类型：integer, real, boolean, char, string
• 标识符：以字母或下划线开头的标识符
• 数字：整数和浮点数
• 字符串：单引号包围的字符串
• 运算符：+, -, *, /, :=, =, <>, <, >, <=, >=
• 分隔符：;, ,, ., :, (, ), [, ]
• 注释：// 单行注释，/* */ 多行注释

=== 正则表达式语法 ===
• 字符：直接输入字符
• 选择：使用 | 分隔选项，如 a|b
• 连接：直接连写，如 ab
• Kleene闭包：使用 *，如 a*
• 正闭包：使用 +，如 a+
• 可选：使用 ?，如 a?
• 分组：使用括号，如 (ab)*

=== 快捷键 ===
• Ctrl+O：加载文件
• Ctrl+S：保存结果
• F5：执行分析
• Ctrl+L：清空输入

=== 注意事项 ===
• 程序支持UTF-8编码的文本文件
• 正则表达式转换功能为简化实现，支持基本操作
• 可视化功能需要先执行相应的转换操作
• 大型自动机的可视化可能需要较长时间
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    # ==================== 事件处理方法 ====================
    
    def analyze_code(self):
        """分析代码"""
        code = self.code_input.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("警告", "请输入要分析的代码")
            return
        
        # 清空之前的结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.analyzer.clear_errors()
        
        # 执行词法分析
        tokens = self.analyzer.analyze(code)
        
        # 显示结果
        for i, token in enumerate(tokens, 1):
            if token.type != TokenType.EOF:
                self.result_tree.insert("", tk.END, values=(
                    i, token.type.value, token.value, token.line, token.column
                ))
        
        # 显示统计信息
        self.show_statistics(tokens)
        
        # 显示错误信息
        if self.analyzer.get_errors():
            error_msg = "\n".join(self.analyzer.get_errors())
            messagebox.showerror("词法错误", error_msg)
    
    def show_statistics(self, tokens):
        """显示统计信息"""
        self.stats_text.delete(1.0, tk.END)
        
        # 统计token类型
        token_counts = {}
        for token in tokens:
            if token.type != TokenType.EOF:
                if token.type in token_counts:
                    token_counts[token.type] += 1
                else:
                    token_counts[token.type] = 1
        
        stats = f"总Token数量: {len(tokens) - 1}\n\n"
        stats += "各类型统计:\n"
        
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            stats += f"  {token_type.value}: {count}\n"
        
        self.stats_text.insert(tk.END, stats)
    
    def clear_code(self):
        """清空代码输入"""
        self.code_input.delete(1.0, tk.END)
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.stats_text.delete(1.0, tk.END)
    
    def load_file(self):
        """加载文件"""
        filename = filedialog.askopenfilename(
            title="选择代码文件",
            filetypes=[("文本文件", "*.txt"), ("Pascal文件", "*.pas"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_input.delete(1.0, tk.END)
                self.code_input.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("错误", f"无法加载文件: {e}")
    
    def save_results(self):
        """保存分析结果"""
        filename = filedialog.asksavename(
            title="保存分析结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("词法分析结果\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 写入token信息
                    for item in self.result_tree.get_children():
                        values = self.result_tree.item(item, 'values')
                        f.write(f"{values[0]:3s}. {values[1]:<15} '{values[2]}' {values[3]}:{values[4]}\n")
                    
                    # 写入统计信息
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("统计信息\n")
                    f.write("=" * 50 + "\n")
                    f.write(self.stats_text.get(1.0, tk.END))
                
                messagebox.showinfo("成功", "结果已保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")
    
    def convert_to_nfa(self):
        """转换正则表达式为NFA"""
        regex = self.regex_input.get().strip()
        if not regex:
            messagebox.showwarning("警告", "请输入正则表达式")
            return
        
        try:
            self.current_nfa = self.regex_converter.convert(regex, TokenType.IDENTIFIER)
            
            result = f"正则表达式: {regex}\n"
            result += f"转换为NFA成功！\n\n"
            result += f"NFA信息:\n"
            result += f"  状态数量: {len(self.current_nfa.states)}\n"
            result += f"  字母表: {sorted(self.current_nfa.alphabet)}\n"
            result += f"  开始状态: {self.current_nfa.start_state.id}\n"
            result += f"  最终状态: {[s.id for s in self.current_nfa.final_states]}\n\n"
            
            # 显示状态转换
            result += "状态转换:\n"
            for state in self.current_nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result += f"  δ({state.id}, {symbol}) = {target.id}\n"
                
                if state.epsilon_transitions:
                    for target in state.epsilon_transitions:
                        result += f"  δ({state.id}, ε) = {target.id}\n"
            
            self.conversion_result.delete(1.0, tk.END)
            self.conversion_result.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {e}")
    
    def convert_to_dfa(self):
        """将NFA转换为DFA"""
        if not self.current_nfa:
            messagebox.showwarning("警告", "请先转换正则表达式为NFA")
            return
        
        try:
            self.current_dfa = self.nfa_converter.convert(self.current_nfa)
            
            result = self.conversion_result.get(1.0, tk.END)
            result += "\n" + "=" * 50 + "\n"
            result += "NFA转DFA成功！\n\n"
            result += f"DFA信息:\n"
            result += f"  状态数量: {len(self.current_dfa.states)}\n"
            result += f"  字母表: {sorted(self.current_dfa.alphabet)}\n"
            result += f"  开始状态: {{{', '.join(str(s.id) for s in self.current_dfa.start_state)}}}\n"
            result += f"  最终状态数量: {len(self.current_dfa.final_states)}\n"
            if self.current_dfa.final_states:
                final_state_ids = ['{' + ', '.join(str(s.id) for s in state) + '}' for state in self.current_dfa.final_states]
                result += f"  最终状态: {', '.join(final_state_ids)}\n"
            result += "\n"
            
            # 显示状态转换
            result += "状态转换:\n"
            for (from_state, symbol), to_state in self.current_dfa.transitions.items():
                from_ids = '{' + ', '.join(str(s) for s in from_state) + '}'
                to_ids = '{' + ', '.join(str(s) for s in to_state) + '}'
                result += f"  δ({from_ids}, {symbol}) = {to_ids}\n"
            
            self.conversion_result.delete(1.0, tk.END)
            self.conversion_result.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {e}")
    
    def minimize_dfa(self):
        """最小化DFA"""
        if not self.current_dfa:
            messagebox.showwarning("警告", "请先转换NFA为DFA")
            return
        
        try:
            self.current_min_dfa = self.dfa_minimizer.minimize(self.current_dfa)
            
            result = self.conversion_result.get(1.0, tk.END)
            result += "\n" + "=" * 50 + "\n"
            result += "DFA最小化成功！\n\n"
            result += f"最小DFA信息:\n"
            result += f"  状态数量: {len(self.current_min_dfa.states)}\n"
            result += f"  字母表: {sorted(self.current_min_dfa.alphabet)}\n"
            result += f"  开始状态: {{{', '.join(str(s) for s in self.current_min_dfa.start_state)}}}\n"
            result += f"  最终状态数量: {len(self.current_min_dfa.final_states)}\n"
            if self.current_min_dfa.final_states:
                final_state_ids = ['{' + ', '.join(str(s) for s in state) + '}' for state in self.current_min_dfa.final_states]
                result += f"  最终状态: {', '.join(final_state_ids)}\n"
            result += "\n"
            
            # 显示状态转换
            result += "状态转换:\n"
            for (from_state, symbol), to_state in self.current_min_dfa.transitions.items():
                from_ids = '{' + ', '.join(str(s) for s in from_state) + '}'
                to_ids = '{' + ', '.join(str(s) for s in to_state) + '}'
                result += f"  δ({from_ids}, {symbol}) = {to_ids}\n"
            
            # 显示优化效果
            original_states = len(self.current_dfa.states)
            minimized_states = len(self.current_min_dfa.states)
            reduction = original_states - minimized_states
            result += f"\n优化效果: 减少了 {reduction} 个状态 ({reduction/original_states*100:.1f}%)\n"
            
            self.conversion_result.delete(1.0, tk.END)
            self.conversion_result.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"最小化失败: {e}")
    
    def full_conversion(self):
        """执行完整转换流程"""
        self.convert_to_nfa()
        if self.current_nfa:
            self.convert_to_dfa()
            if self.current_dfa:
                self.minimize_dfa()
    
    def visualize_automaton(self):
        """可视化自动机"""
        viz_type = self.viz_var.get()
        
        if viz_type == "NFA" and not self.current_nfa:
            messagebox.showwarning("警告", "请先生成NFA")
            return
        elif viz_type == "DFA" and not self.current_dfa:
            messagebox.showwarning("警告", "请先生成DFA")
            return
        elif viz_type == "MIN_DFA" and not self.current_min_dfa:
            messagebox.showwarning("警告", "请先生成最小DFA")
            return
        
        try:
            self.ax.clear()
            
            if viz_type == "NFA":
                self._draw_nfa()
            elif viz_type == "DFA":
                self._draw_dfa(self.current_dfa, "DFA")
            elif viz_type == "MIN_DFA":
                self._draw_dfa(self.current_min_dfa, "最小DFA")
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"可视化失败: {e}")
    
    def _draw_nfa(self):
        """绘制NFA"""
        G = nx.DiGraph()
        
        # 添加节点
        for state in self.current_nfa.states:
            node_color = 'lightgreen' if state.is_final else 'lightblue'
            if state == self.current_nfa.start_state:
                node_color = 'yellow'
            G.add_node(state.id, color=node_color)
        
        # 添加边
        edge_labels = {}
        for state in self.current_nfa.states:
            # 普通转换
            for symbol, targets in state.transitions.items():
                for target in targets:
                    edge_key = (state.id, target.id)
                    if edge_key in edge_labels:
                        edge_labels[edge_key] += f", {symbol}"
                    else:
                        edge_labels[edge_key] = symbol
                        G.add_edge(state.id, target.id)
            
            # ε转换
            for target in state.epsilon_transitions:
                edge_key = (state.id, target.id)
                if edge_key in edge_labels:
                    edge_labels[edge_key] += ", ε"
                else:
                    edge_labels[edge_key] = "ε"
                    G.add_edge(state.id, target.id)
        
        # 绘制图形
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 绘制节点
        node_colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=self.ax)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=self.ax)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=self.ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=self.ax)
        
        self.ax.set_title("NFA状态转换图", fontsize=14, fontweight='bold')
        self.ax.axis('off')
    
    def _draw_dfa(self, dfa, title):
        """绘制DFA"""
        G = nx.DiGraph()
        
        # 为状态创建简化的标签
        state_labels = {}
        for i, state in enumerate(dfa.states):
            label = f"q{i}"
            state_labels[state] = label
            
            node_color = 'lightgreen' if state in dfa.final_states else 'lightblue'
            if state == dfa.start_state:
                node_color = 'yellow'
            G.add_node(label, color=node_color)
        
        # 添加边
        edge_labels = {}
        for (from_state, symbol), to_state in dfa.transitions.items():
            from_label = state_labels[from_state]
            to_label = state_labels[to_state]
            edge_key = (from_label, to_label)
            
            if edge_key in edge_labels:
                edge_labels[edge_key] += f", {symbol}"
            else:
                edge_labels[edge_key] = symbol
                G.add_edge(from_label, to_label)
        
        # 绘制图形
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 绘制节点
        node_colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=self.ax)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=self.ax)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=self.ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=self.ax)
        
        self.ax.set_title(f"{title}状态转换图", fontsize=14, fontweight='bold')
        self.ax.axis('off')
    
    def save_visualization(self):
        """保存可视化图片"""
        filename = filedialog.asksavename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", "图片已保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存图片: {e}")
    
    def run(self):
        """运行GUI应用程序"""
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # 绑定快捷键
        self.root.bind('<Control-o>', lambda e: self.load_file())
        self.root.bind('<Control-s>', lambda e: self.save_results())
        self.root.bind('<F5>', lambda e: self.analyze_code())
        self.root.bind('<Control-l>', lambda e: self.clear_code())
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 启动主循环
        self.root.mainloop()
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    try:
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建并运行GUI应用
        app = LexicalAnalyzerGUI()
        app.run()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()