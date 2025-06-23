#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动机模块

实现有限自动机相关的数据结构和算法：
- NFA (非确定性有限自动机)
- DFA (确定性有限自动机)
- 正则表达式到NFA转换 (Thompson构造法)
- NFA到DFA转换 (子集构造法)
- DFA最小化
"""

import graphviz
import io
from PIL import Image
from typing import List, Dict, Set, Tuple, Optional, Union
from .token import TokenType


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
    
    def __repr__(self):
        return f"State({self.id}, accept={self.is_accept})"
    
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
    
    def move(self, states: Set[State], symbol: str) -> Set[State]:
        """计算状态集合在输入符号下的转移"""
        result = set()
        for state in states:
            result.update(state.get_transitions(symbol))
        return result


class DFA:
    """确定性有限自动机"""
    
    def __init__(self):
        self.states: Dict[str, Set[State]] = {}  # DFA状态ID -> NFA状态集合
        self.start_state: Optional[str] = None
        self.accept_states: Set[str] = set()
        self.transitions: Dict[Tuple[str, str], str] = {}  # (状态, 符号) -> 目标状态
        self.alphabet: Set[str] = set()
        self.token_types: Dict[str, TokenType] = {}  # 状态 -> Token类型
    
    def add_state(self, state_id: str, nfa_states: Set[State]):
        """添加DFA状态"""
        self.states[state_id] = nfa_states
        
        # 检查是否为接受状态
        for nfa_state in nfa_states:
            if nfa_state.is_accept:
                self.accept_states.add(state_id)
                if nfa_state.token_type:
                    self.token_types[state_id] = nfa_state.token_type
                break
    
    def add_transition(self, from_state: str, symbol: str, to_state: str):
        """添加状态转移"""
        self.transitions[(from_state, symbol)] = to_state
        self.alphabet.add(symbol)
    
    def get_transition(self, state: str, symbol: str) -> Optional[str]:
        """获取状态转移"""
        return self.transitions.get((state, symbol))
    
    def simulate(self, input_string: str) -> Tuple[bool, Optional[TokenType]]:
        """模拟DFA运行"""
        if not self.start_state:
            return False, None
        
        current_state = self.start_state
        
        for symbol in input_string:
            next_state = self.get_transition(current_state, symbol)
            if next_state is None:
                return False, None
            current_state = next_state
        
        is_accept = current_state in self.accept_states
        token_type = self.token_types.get(current_state) if is_accept else None
        
        return is_accept, token_type


class RegexToNFA:
    """正则表达式到NFA转换器 (Thompson构造法)"""
    
    def __init__(self):
        self.state_counter = 0
    
    def convert(self, regex: str, token_type: Optional[TokenType] = None) -> NFA:
        """将正则表达式转换为NFA"""
        # 预处理：展开字符类和转义字符
        processed_regex = self._preprocess_regex(regex)
        
        # 添加连接操作符
        concat_regex = self._add_concat_operator(processed_regex)
        
        # 转换为后缀表达式
        postfix = self._to_postfix(concat_regex)
        
        # 构建NFA
        return self._build_nfa(postfix, token_type)
    
    def _preprocess_regex(self, regex: str) -> str:
        """预处理正则表达式"""
        result = []
        i = 0
        while i < len(regex):
            if regex[i] == '\\':
                # 处理转义字符
                if i + 1 < len(regex):
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
                else:
                    result.append(regex[i])
                    i += 1
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
    
    def _build_nfa(self, postfix: List[str], token_type: Optional[TokenType]) -> NFA:
        """根据后缀表达式构建NFA"""
        stack = []
        
        for token in postfix:
            if token == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self._union_nfa(nfa1, nfa2))
            elif token == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self._concat_nfa(nfa1, nfa2))
            elif token == '*':
                nfa = stack.pop()
                stack.append(self._kleene_star_nfa(nfa))
            elif token == '+':
                nfa = stack.pop()
                stack.append(self._plus_nfa(nfa))
            elif token == '?':
                nfa = stack.pop()
                stack.append(self._question_nfa(nfa))
            else:
                stack.append(self._basic_nfa(token))
        
        result = stack[0] if stack else NFA()
        
        # 设置接受状态的Token类型
        if token_type:
            for state in result.accept_states:
                state.token_type = token_type
        
        return result
    
    def _basic_nfa(self, symbol: str) -> NFA:
        """创建基本NFA"""
        nfa = NFA()
        start = nfa.create_state()
        end = nfa.create_state()
        
        nfa.set_start(start)
        nfa.add_accept(end)
        nfa.add_transition(start, symbol, end)
        
        return nfa
    
    def _concat_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """连接两个NFA"""
        result = NFA()
        result.state_counter = max(nfa1.state_counter, nfa2.state_counter)
        
        # 复制所有状态
        state_map = {}
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                new_state = State(state.id)
                new_state.is_accept = False  # 重置接受状态
                state_map[state] = new_state
                result.states.add(new_state)
        
        # 复制转移
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[state], symbol, state_map[target])
        
        # 设置开始状态
        result.set_start(state_map[nfa1.start_state])
        
        # 连接nfa1的接受状态到nfa2的开始状态
        for accept_state in nfa1.accept_states:
            result.add_transition(state_map[accept_state], 'ε', state_map[nfa2.start_state])
        
        # 设置nfa2的接受状态为结果的接受状态
        for accept_state in nfa2.accept_states:
            result.add_accept(state_map[accept_state], accept_state.token_type)
        
        return result
    
    def _union_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """联合两个NFA"""
        result = NFA()
        result.state_counter = max(nfa1.state_counter, nfa2.state_counter)
        
        # 创建新的开始和结束状态
        new_start = result.create_state()
        new_end = result.create_state()
        
        result.set_start(new_start)
        result.add_accept(new_end)
        
        # 复制所有状态
        state_map = {}
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                new_state = State(result.state_counter)
                result.state_counter += 1
                new_state.is_accept = False
                state_map[state] = new_state
                result.states.add(new_state)
        
        # 复制转移
        for nfa in [nfa1, nfa2]:
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[state], symbol, state_map[target])
        
        # 连接新开始状态到两个NFA的开始状态
        result.add_transition(new_start, 'ε', state_map[nfa1.start_state])
        result.add_transition(new_start, 'ε', state_map[nfa2.start_state])
        
        # 连接两个NFA的接受状态到新结束状态
        for accept_state in nfa1.accept_states:
            result.add_transition(state_map[accept_state], 'ε', new_end)
        for accept_state in nfa2.accept_states:
            result.add_transition(state_map[accept_state], 'ε', new_end)
        
        return result
    
    def _kleene_star_nfa(self, nfa: NFA) -> NFA:
        """克莱尼星操作"""
        result = NFA()
        result.state_counter = nfa.state_counter
        
        # 创建新的开始和结束状态
        new_start = result.create_state()
        new_end = result.create_state()
        
        result.set_start(new_start)
        result.add_accept(new_end)
        
        # 复制所有状态
        state_map = {}
        for state in nfa.states:
            new_state = State(result.state_counter)
            result.state_counter += 1
            new_state.is_accept = False
            state_map[state] = new_state
            result.states.add(new_state)
        
        # 复制转移
        for state in nfa.states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    result.add_transition(state_map[state], symbol, state_map[target])
        
        # 添加ε转移
        result.add_transition(new_start, 'ε', state_map[nfa.start_state])  # 进入
        result.add_transition(new_start, 'ε', new_end)  # 跳过
        
        for accept_state in nfa.accept_states:
            result.add_transition(state_map[accept_state], 'ε', new_end)  # 退出
            result.add_transition(state_map[accept_state], 'ε', state_map[nfa.start_state])  # 循环
        
        return result
    
    def _plus_nfa(self, nfa: NFA) -> NFA:
        """加号操作 (一次或多次)"""
        # A+ = AA*
        star_nfa = self._kleene_star_nfa(nfa)
        return self._concat_nfa(nfa, star_nfa)
    
    def _question_nfa(self, nfa: NFA) -> NFA:
        """问号操作 (零次或一次)"""
        result = NFA()
        result.state_counter = nfa.state_counter
        
        # 创建新的开始和结束状态
        new_start = result.create_state()
        new_end = result.create_state()
        
        result.set_start(new_start)
        result.add_accept(new_end)
        
        # 复制所有状态
        state_map = {}
        for state in nfa.states:
            new_state = State(result.state_counter)
            result.state_counter += 1
            new_state.is_accept = False
            state_map[state] = new_state
            result.states.add(new_state)
        
        # 复制转移
        for state in nfa.states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    result.add_transition(state_map[state], symbol, state_map[target])
        
        # 添加ε转移
        result.add_transition(new_start, 'ε', state_map[nfa.start_state])  # 进入
        result.add_transition(new_start, 'ε', new_end)  # 跳过
        
        for accept_state in nfa.accept_states:
            result.add_transition(state_map[accept_state], 'ε', new_end)  # 退出
        
        return result


class NFAToDFA:
    """NFA到DFA转换器 (子集构造法)"""
    
    def convert(self, nfa: NFA) -> DFA:
        """将NFA转换为DFA"""
        dfa = DFA()
        dfa.alphabet = nfa.alphabet.copy()
        
        # 计算初始状态的ε闭包
        start_closure = nfa.epsilon_closure({nfa.start_state})
        start_id = self._state_set_to_id(start_closure)
        
        dfa.start_state = start_id
        dfa.add_state(start_id, start_closure)
        
        # 工作队列
        unprocessed = [start_closure]
        processed = {start_id}
        
        while unprocessed:
            current_set = unprocessed.pop(0)
            current_id = self._state_set_to_id(current_set)
            
            for symbol in dfa.alphabet:
                # 计算move和ε闭包
                move_result = nfa.move(current_set, symbol)
                if move_result:
                    next_closure = nfa.epsilon_closure(move_result)
                    next_id = self._state_set_to_id(next_closure)
                    
                    # 添加转移
                    dfa.add_transition(current_id, symbol, next_id)
                    
                    # 如果是新状态，添加到DFA和工作队列
                    if next_id not in processed:
                        dfa.add_state(next_id, next_closure)
                        unprocessed.append(next_closure)
                        processed.add(next_id)
        
        return dfa
    
    def _state_set_to_id(self, state_set: Set[State]) -> str:
        """将状态集合转换为ID"""
        return '{' + ','.join(str(s.id) for s in sorted(state_set, key=lambda x: x.id)) + '}'


class DFAMinimizer:
    """DFA最小化器"""
    
    def minimize(self, dfa: DFA) -> DFA:
        """最小化DFA"""
        # 初始分割：接受状态和非接受状态
        accept_states = set(dfa.accept_states)
        non_accept_states = set(dfa.states.keys()) - accept_states
        
        partitions = []
        if non_accept_states:
            partitions.append(non_accept_states)
        if accept_states:
            partitions.append(accept_states)
        
        # 迭代细化分割
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
        
        # 构建最小化DFA
        return self._build_minimized_dfa(dfa, partitions)
    
    def _split_partition(self, partition: Set[str], all_partitions: List[Set[str]], dfa: DFA) -> List[Set[str]]:
        """分割分区"""
        if len(partition) <= 1:
            return [partition]
        
        # 选择分区中的第一个状态作为代表
        representative = next(iter(partition))
        groups = {representative: {representative}}
        
        for state in partition:
            if state == representative:
                continue
            
            # 检查是否与代表状态等价
            equivalent = True
            for symbol in dfa.alphabet:
                rep_target = dfa.get_transition(representative, symbol)
                state_target = dfa.get_transition(state, symbol)
                
                # 找到目标状态所在的分区
                rep_partition = self._find_partition(rep_target, all_partitions) if rep_target else None
                state_partition = self._find_partition(state_target, all_partitions) if state_target else None
                
                if rep_partition != state_partition:
                    equivalent = False
                    break
            
            if equivalent:
                groups[representative].add(state)
            else:
                # 创建新组
                groups[state] = {state}
        
        return list(groups.values())
    
    def _find_partition(self, state: str, partitions: List[Set[str]]) -> Optional[int]:
        """找到状态所在的分区索引"""
        for i, partition in enumerate(partitions):
            if state in partition:
                return i
        return None
    
    def _build_minimized_dfa(self, original_dfa: DFA, partitions: List[Set[str]]) -> DFA:
        """构建最小化DFA"""
        minimized = DFA()
        minimized.alphabet = original_dfa.alphabet.copy()
        
        # 创建分区到新状态ID的映射
        partition_to_id = {}
        for i, partition in enumerate(partitions):
            new_id = f"q{i}"
            partition_to_id[i] = new_id
            
            # 选择分区中的一个代表状态
            representative = next(iter(partition))
            minimized.add_state(new_id, original_dfa.states[representative])
            
            # 设置开始状态
            if original_dfa.start_state in partition:
                minimized.start_state = new_id
            
            # 设置接受状态和Token类型
            if any(state in original_dfa.accept_states for state in partition):
                minimized.accept_states.add(new_id)
                # 使用代表状态的Token类型
                if representative in original_dfa.token_types:
                    minimized.token_types[new_id] = original_dfa.token_types[representative]
        
        # 添加转移
        for i, partition in enumerate(partitions):
            representative = next(iter(partition))
            from_id = partition_to_id[i]
            
            for symbol in minimized.alphabet:
                target = original_dfa.get_transition(representative, symbol)
                if target:
                    target_partition = self._find_partition(target, partitions)
                    if target_partition is not None:
                        to_id = partition_to_id[target_partition]
                        minimized.add_transition(from_id, symbol, to_id)
        
        return minimized


def visualize_nfa(nfa: NFA, title: str = "NFA") -> Image.Image:
    """可视化NFA"""
    dot = graphviz.Digraph(comment=title)
    dot.attr(rankdir='LR')
    
    # 添加状态
    for state in nfa.states:
        shape = 'doublecircle' if state.is_accept else 'circle'
        label = f"{state.id}"
        if state.token_type:
            label += f"\n{state.token_type.value}"
        dot.node(str(state.id), label, shape=shape)
    
    # 添加转移
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                label = 'ε' if symbol == 'ε' else symbol
                dot.edge(str(state.id), str(target.id), label=label)
    
    # 标记开始状态
    if nfa.start_state:
        dot.node('start', '', shape='point')
        dot.edge('start', str(nfa.start_state.id))
    
    # 渲染为图片
    img_data = dot.pipe(format='png')
    return Image.open(io.BytesIO(img_data))


def visualize_dfa(dfa: DFA, title: str = "DFA") -> Image.Image:
    """可视化DFA"""
    dot = graphviz.Digraph(comment=title)
    dot.attr(rankdir='LR')
    
    # 添加状态
    for state_id in dfa.states:
        shape = 'doublecircle' if state_id in dfa.accept_states else 'circle'
        label = state_id
        if state_id in dfa.token_types:
            label += f"\n{dfa.token_types[state_id].value}"
        dot.node(state_id, label, shape=shape)
    
    # 添加转移
    for (from_state, symbol), to_state in dfa.transitions.items():
        dot.edge(from_state, to_state, label=symbol)
    
    # 标记开始状态
    if dfa.start_state:
        dot.node('start', '', shape='point')
        dot.edge('start', dfa.start_state)
    
    # 渲染为图片
    img_data = dot.pipe(format='png')
    return Image.open(io.BytesIO(img_data))