#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFA到DFA转换器 - Good Enough Compiler
实现正则表达式到NFA，以及NFA到DFA的转换算法
包括Thompson构造法和子集构造法
"""

import graphviz
import io
from PIL import Image
from typing import List, Dict, Set, Tuple, Optional
from .lexical_analyzer import State, NFA, DFA, TokenType

class RegexToNFA:
    """正则表达式到NFA转换器"""
    
    def __init__(self):
        self.state_counter = 0
    
    def convert(self, regex: str, token_type: TokenType = None) -> NFA:
        """将正则表达式转换为NFA"""
        # 定义操作符优先级
        precedence = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
        operators = {'|', '.', '*', '+', '?', '(', ')'}
        
        def add_concat_operator(regex):
            """在需要的位置添加连接操作符('.')"""
            output = []
            for i in range(len(regex)):
                output.append(regex[i])
                if i+1 < len(regex) and regex[i] not in '(|' and regex[i+1] not in ')|*+?':
                    output.append('.')
            return ''.join(output)
        
        def to_postfix(regex):
            """使用调度场算法将中缀表达式转换为后缀表达式"""
            output = []
            operator_stack = []
            
            for token in regex:
                if token not in operators:  # 普通字符
                    output.append(token)
                elif token == '(':  # 左括号
                    operator_stack.append(token)
                elif token == ')':  # 右括号
                    while operator_stack and operator_stack[-1] != '(':
                        output.append(operator_stack.pop())
                    operator_stack.pop()  # 弹出左括号
                else:  # 其他操作符
                    while (operator_stack and operator_stack[-1] != '(' and 
                           precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                        output.append(operator_stack.pop())
                    operator_stack.append(token)
            
            # 将剩余操作符添加到输出
            while operator_stack:
                output.append(operator_stack.pop())
                
            return output
        
        def basic_nfa(symbol):
            """为单个符号创建基本NFA"""
            nfa = NFA()
            start = nfa.create_state()
            end = nfa.create_state()
            
            nfa.set_start(start)
            nfa.add_end(end, token_type)
            nfa.add_transition(start, symbol, end)
            
            return nfa
        
        def concat_nfa(nfa1, nfa2):
            """连接两个NFA"""
            result = NFA()
            
            # 复制nfa1的所有状态
            state_map1 = {}
            for state in nfa1.states:
                new_state = result.create_state()
                state_map1[state.id] = new_state
                if state == nfa1.start_state:
                    result.set_start(new_state)
            
            # 复制nfa1的转移
            for state in nfa1.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map1[state.id], symbol, state_map1[target.id])
            
            # 复制nfa2的所有状态
            state_map2 = {}
            for state in nfa2.states:
                new_state = result.create_state()
                state_map2[state.id] = new_state
            
            # 复制nfa2的转移
            for state in nfa2.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map2[state.id], symbol, state_map2[target.id])
            
            # 从nfa1的结束状态添加ε转移到nfa2的起始状态
            for end_state in nfa1.end_states:
                result.add_transition(state_map1[end_state.id], 'ε', state_map2[nfa2.start_state.id])
            
            # 设置nfa2的结束状态为result的结束状态
            for end_state in nfa2.end_states:
                result.add_end(state_map2[end_state.id], end_state.token_type)
            
            return result
        
        def union_nfa(nfa1, nfa2):
            """合并两个NFA (对应 | 操作)"""
            result = NFA()
            
            # 创建新的起始和结束状态
            start = result.create_state()
            end = result.create_state()
            result.set_start(start)
            result.add_end(end, token_type)
            
            # 复制nfa1
            state_map1 = {}
            for state in nfa1.states:
                new_state = result.create_state()
                state_map1[state.id] = new_state
            
            for state in nfa1.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map1[state.id], symbol, state_map1[target.id])
            
            # 复制nfa2
            state_map2 = {}
            for state in nfa2.states:
                new_state = result.create_state()
                state_map2[state.id] = new_state
            
            for state in nfa2.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map2[state.id], symbol, state_map2[target.id])
            
            # 添加ε转移
            result.add_transition(start, 'ε', state_map1[nfa1.start_state.id])
            result.add_transition(start, 'ε', state_map2[nfa2.start_state.id])
            
            for end_state in nfa1.end_states:
                result.add_transition(state_map1[end_state.id], 'ε', end)
            for end_state in nfa2.end_states:
                result.add_transition(state_map2[end_state.id], 'ε', end)
            
            return result
        
        def kleene_star_nfa(nfa):
            """克莱尼星操作 (对应 * 操作)"""
            result = NFA()
            
            # 创建新的起始和结束状态
            start = result.create_state()
            end = result.create_state()
            result.set_start(start)
            result.add_end(end, token_type)
            
            # 添加ε转移以跳过nfa (允许空字符串)
            result.add_transition(start, 'ε', end)
            
            # 复制原始nfa
            state_map = {}
            for state in nfa.states:
                new_state = result.create_state()
                state_map[state.id] = new_state
            
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[state.id], symbol, state_map[target.id])
            
            # 添加转移
            result.add_transition(start, 'ε', state_map[nfa.start_state.id])
            
            for end_state in nfa.end_states:
                result.add_transition(state_map[end_state.id], 'ε', end)
                # 添加回环
                result.add_transition(state_map[end_state.id], 'ε', state_map[nfa.start_state.id])
            
            return result
        
        def plus_nfa(nfa):
            """加号操作 (对应 + 操作，一个或多个)"""
            # a+ = aa*
            star_nfa = kleene_star_nfa(nfa)
            return concat_nfa(nfa, star_nfa)
        
        def question_nfa(nfa):
            """问号操作 (对应 ? 操作，零个或一个)"""
            result = NFA()
            
            # 创建新的起始和结束状态
            start = result.create_state()
            end = result.create_state()
            result.set_start(start)
            result.add_end(end, token_type)
            
            # 添加ε转移以跳过nfa (允许空字符串)
            result.add_transition(start, 'ε', end)
            
            # 复制原始nfa
            state_map = {}
            for state in nfa.states:
                new_state = result.create_state()
                state_map[state.id] = new_state
            
            for state in nfa.states:
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[state.id], symbol, state_map[target.id])
            
            # 添加转移
            result.add_transition(start, 'ε', state_map[nfa.start_state.id])
            
            for end_state in nfa.end_states:
                result.add_transition(state_map[end_state.id], 'ε', end)
            
            return result
        
        def build_nfa(postfix):
            """根据后缀表达式构建NFA"""
            stack = []
            
            for token in postfix:
                if token == '*':
                    if not stack:
                        raise ValueError("无效的表达式: * 操作符没有操作数")
                    nfa = stack.pop()
                    stack.append(kleene_star_nfa(nfa))
                elif token == '+':
                    if not stack:
                        raise ValueError("无效的表达式: + 操作符没有操作数")
                    nfa = stack.pop()
                    stack.append(plus_nfa(nfa))
                elif token == '?':
                    if not stack:
                        raise ValueError("无效的表达式: ? 操作符没有操作数")
                    nfa = stack.pop()
                    stack.append(question_nfa(nfa))
                elif token == '.':
                    if len(stack) < 2:
                        raise ValueError("无效的表达式: . 操作符需要两个操作数")
                    nfa2 = stack.pop()
                    nfa1 = stack.pop()
                    stack.append(concat_nfa(nfa1, nfa2))
                elif token == '|':
                    if len(stack) < 2:
                        raise ValueError("无效的表达式: | 操作符需要两个操作数")
                    nfa2 = stack.pop()
                    nfa1 = stack.pop()
                    stack.append(union_nfa(nfa1, nfa2))
                else:
                    stack.append(basic_nfa(token))
            
            if len(stack) != 1:
                raise ValueError("无效的表达式")
                
            return stack[0]
        
        # 处理正则表达式并构建NFA
        regex_with_concat = add_concat_operator(regex)
        postfix = to_postfix(regex_with_concat)
        return build_nfa(postfix)

class NFAToDFA:
    """NFA到DFA转换器（子集构造法）"""
    
    def __init__(self):
        self.state_counter = 0
    
    def epsilon_closure(self, states: Set[State]) -> Set[State]:
        """计算状态集合的ε闭包"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            for next_state in state.epsilon_moves:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure
    
    def move(self, states: Set[State], symbol: str) -> Set[State]:
        """计算状态集合在输入符号下的转移"""
        result = set()
        for state in states:
            if symbol in state.transitions:
                result.update(state.transitions[symbol])
        return result
    
    def convert(self, nfa: NFA) -> DFA:
        """将NFA转换为DFA"""
        dfa = DFA()
        dfa.alphabet = nfa.alphabet.copy()
        
        # 计算初始状态的ε闭包
        start_closure = self.epsilon_closure({nfa.start_state})
        start_state_id = self._state_set_to_id(start_closure)
        
        dfa.start_state = start_state_id
        dfa.states[start_state_id] = start_closure
        
        # 检查是否为接受状态
        for state in start_closure:
            if state.is_end:
                dfa.accept_states[start_state_id] = state.token_type
                break
        
        # 工作列表
        worklist = [start_closure]
        processed = {start_state_id}
        
        while worklist:
            current_states = worklist.pop(0)
            current_id = self._state_set_to_id(current_states)
            
            # 对每个输入符号
            for symbol in dfa.alphabet:
                # 计算转移
                next_states = self.move(current_states, symbol)
                if next_states:
                    next_closure = self.epsilon_closure(next_states)
                    next_id = self._state_set_to_id(next_closure)
                    
                    # 添加转移
                    dfa.transitions[(current_id, symbol)] = next_id
                    
                    # 如果是新状态，添加到DFA
                    if next_id not in processed:
                        dfa.states[next_id] = next_closure
                        processed.add(next_id)
                        worklist.append(next_closure)
                        
                        # 检查是否为接受状态
                        for state in next_closure:
                            if state.is_end:
                                dfa.accept_states[next_id] = state.token_type
                                break
        
        return dfa
    
    def _state_set_to_id(self, states: Set[State]) -> str:
        """将状态集合转换为唯一ID"""
        state_ids = sorted([state.id for state in states])
        return '{' + ','.join(map(str, state_ids)) + '}'

class DFAMinimizer:
    """DFA最小化器"""
    
    def minimize(self, dfa: DFA) -> DFA:
        """最小化DFA"""
        # 初始分割：接受状态和非接受状态
        accept_states = set(dfa.accept_states.keys())
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
                # 尝试分割当前分区
                sub_partitions = self._split_partition(partition, partitions, dfa)
                if len(sub_partitions) > 1:
                    changed = True
                new_partitions.extend(sub_partitions)
            
            partitions = new_partitions
        
        # 构建最小化的DFA
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
            
            # 检查状态是否与代表状态等价
            equivalent = True
            for symbol in dfa.alphabet:
                rep_next = dfa.transitions.get((representative, symbol))
                state_next = dfa.transitions.get((state, symbol))
                
                # 找到下一个状态所在的分区
                rep_partition = self._find_partition(rep_next, all_partitions) if rep_next else None
                state_partition = self._find_partition(state_next, all_partitions) if state_next else None
                
                if rep_partition != state_partition:
                    equivalent = False
                    break
            
            if equivalent:
                groups[representative].add(state)
            else:
                # 创建新组
                groups[state] = {state}
        
        return list(groups.values())
    
    def _find_partition(self, state: str, partitions: List[Set[str]]) -> Optional[Set[str]]:
        """找到状态所在的分区"""
        for partition in partitions:
            if state in partition:
                return partition
        return None
    
    def _build_minimized_dfa(self, original_dfa: DFA, partitions: List[Set[str]]) -> DFA:
        """根据分区构建最小化的DFA"""
        minimized_dfa = DFA()
        minimized_dfa.alphabet = original_dfa.alphabet.copy()
        
        # 为每个分区创建新状态
        partition_to_state = {}
        for i, partition in enumerate(partitions):
            new_state_id = f"q{i}"
            partition_to_state[frozenset(partition)] = new_state_id
            minimized_dfa.states[new_state_id] = partition
            
            # 检查是否为接受状态
            for state in partition:
                if state in original_dfa.accept_states:
                    minimized_dfa.accept_states[new_state_id] = original_dfa.accept_states[state]
                    break
            
            # 检查是否为起始状态
            if original_dfa.start_state in partition:
                minimized_dfa.start_state = new_state_id
        
        # 添加转移
        for partition in partitions:
            representative = next(iter(partition))
            from_state = partition_to_state[frozenset(partition)]
            
            for symbol in minimized_dfa.alphabet:
                next_state = original_dfa.transitions.get((representative, symbol))
                if next_state:
                    # 找到目标状态所在的分区
                    target_partition = None
                    for p in partitions:
                        if next_state in p:
                            target_partition = frozenset(p)
                            break
                    
                    if target_partition:
                        to_state = partition_to_state[target_partition]
                        minimized_dfa.transitions[(from_state, symbol)] = to_state
        
        return minimized_dfa

def visualize_nfa(nfa: NFA, title: str = "NFA") -> Image.Image:
    """可视化NFA"""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='10,6')
    dot.attr('node', fontname='Arial')
    dot.attr('edge', fontname='Arial')
    
    # 添加标题
    dot.attr(label=title, fontsize='16', fontname='Arial Bold')
    
    # 添加一个隐藏的起始节点
    dot.node('start', style='invisible')
    
    # 添加所有状态
    for state in nfa.states:
        if state in nfa.end_states:
            # 接受状态用双圆圈
            dot.node(f'q{state.id}', shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # 普通状态用单圆圈
            dot.node(f'q{state.id}', shape='circle', style='filled', fillcolor='lightblue')
    
    # 添加起始箭头
    if nfa.start_state:
        dot.edge('start', f'q{nfa.start_state.id}', label='')
    
    # 添加所有转移
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                dot.edge(f'q{state.id}', f'q{target.id}', label=symbol)
    
    # 渲染为PNG并转换为PIL图像
    try:
        png_data = dot.pipe()
        buf = io.BytesIO(png_data)
        img = Image.open(buf)
        return img
    except Exception as e:
        print(f"可视化错误: {e}")
        return None

def visualize_dfa(dfa: DFA, title: str = "DFA") -> Image.Image:
    """可视化DFA"""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='10,6')
    dot.attr('node', fontname='Arial')
    dot.attr('edge', fontname='Arial')
    
    # 添加标题
    dot.attr(label=title, fontsize='16', fontname='Arial Bold')
    
    # 添加一个隐藏的起始节点
    dot.node('start', style='invisible')
    
    # 添加所有状态
    for state_id in dfa.states:
        if state_id in dfa.accept_states:
            # 接受状态用双圆圈
            dot.node(state_id, shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # 普通状态用单圆圈
            dot.node(state_id, shape='circle', style='filled', fillcolor='lightblue')
    
    # 添加起始箭头
    if dfa.start_state:
        dot.edge('start', dfa.start_state, label='')
    
    # 添加所有转移
    for (from_state, symbol), to_state in dfa.transitions.items():
        dot.edge(from_state, to_state, label=symbol)
    
    # 渲染为PNG并转换为PIL图像
    try:
        png_data = dot.pipe()
        buf = io.BytesIO(png_data)
        img = Image.open(buf)
        return img
    except Exception as e:
        print(f"可视化错误: {e}")
        return None

# 测试函数
def test_nfa_dfa_conversion():
    """测试NFA到DFA转换"""
    print("=== NFA到DFA转换测试 ===")
    
    # 创建正则表达式到NFA转换器
    regex_converter = RegexToNFA()
    
    # 测试正则表达式
    test_regex = "a(b|c)*"
    print(f"正则表达式: {test_regex}")
    
    try:
        # 转换为NFA
        nfa = regex_converter.convert(test_regex, TokenType.IDENTIFIER)
        print(f"NFA状态数: {len(nfa.states)}")
        print(f"NFA字母表: {nfa.alphabet}")
        
        # 转换为DFA
        nfa_to_dfa = NFAToDFA()
        dfa = nfa_to_dfa.convert(nfa)
        print(f"DFA状态数: {len(dfa.states)}")
        
        # 最小化DFA
        minimizer = DFAMinimizer()
        min_dfa = minimizer.minimize(dfa)
        print(f"最小化DFA状态数: {len(min_dfa.states)}")
        
        print("转换成功！")
        
    except Exception as e:
        print(f"转换失败: {e}")

if __name__ == "__main__":
    test_nfa_dfa_conversion()