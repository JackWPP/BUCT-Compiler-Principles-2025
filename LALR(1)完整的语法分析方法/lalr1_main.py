# -*- coding: utf-8 -*-
"""
编译原理作业 - LALR(1)完整的语法分析方法
实现上下文无关文法的识别和拓广，LR(1)识别活前缀的状态机，LALR(1)判断；
LALR(1)识别活前缀的状态机，LALR(1)分析表，LR分析过程

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import List, Dict, Set, Optional, Tuple, FrozenSet, Union
from dataclasses import dataclass
from enum import Enum
import copy
import json

# ==================== 数据结构定义 ====================

class ActionType(Enum):
    """LALR(1)分析表动作类型"""
    SHIFT = "移进"      # 移进动作
    REDUCE = "归约"     # 归约动作
    ACCEPT = "接受"     # 接受动作
    ERROR = "错误"      # 错误动作

@dataclass
class Action:
    """LALR(1)分析表动作类"""
    action_type: ActionType
    value: Optional[int] = None  # 移进状态号或归约产生式号
    
    def __str__(self):
        if self.action_type == ActionType.SHIFT:
            return f"s{self.value}"
        elif self.action_type == ActionType.REDUCE:
            return f"r{self.value}"
        elif self.action_type == ActionType.ACCEPT:
            return "acc"
        else:
            return "error"

@dataclass
class Production:
    """产生式类"""
    left: str  # 左部非终结符
    right: List[str]  # 右部符号列表
    index: int  # 产生式编号
    
    def __str__(self):
        right_str = ' '.join(self.right) if self.right else 'ε'
        return f"{self.left} -> {right_str}"
    
    def __eq__(self, other):
        if not isinstance(other, Production):
            return False
        return self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash((self.left, tuple(self.right)))

@dataclass
class LR1Item:
    """LR(1)项目类 - 包含向前看符号"""
    production: Production
    dot_position: int  # 点的位置
    lookahead: str  # 向前看符号（LR(1)必须有）
    
    def __str__(self):
        right = self.production.right.copy()
        right.insert(self.dot_position, '•')
        right_str = ' '.join(right) if right else '•'
        
        result = f"{self.production.left} -> {right_str}, {self.lookahead}"
        return result
    
    def __eq__(self, other):
        if not isinstance(other, LR1Item):
            return False
        return (self.production == other.production and 
                self.dot_position == other.dot_position and
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        return hash((self.production, self.dot_position, self.lookahead))
    
    def is_complete(self) -> bool:
        """判断项目是否完整（点在最右边）"""
        return self.dot_position >= len(self.production.right)
    
    def next_symbol(self) -> Optional[str]:
        """获取点后面的符号"""
        if self.is_complete():
            return None
        return self.production.right[self.dot_position]
    
    def advance_dot(self) -> 'LR1Item':
        """移动点的位置"""
        return LR1Item(
            production=self.production,
            dot_position=self.dot_position + 1,
            lookahead=self.lookahead
        )
    
    def get_core(self) -> Tuple:
        """获取项目的核心（不包含向前看符号）"""
        return (self.production, self.dot_position)

@dataclass
class LALR1Item:
    """LALR(1)项目类 - 核心相同的LR(1)项目合并后的结果"""
    production: Production
    dot_position: int  # 点的位置
    lookaheads: Set[str]  # 向前看符号集合（LALR(1)特有）
    
    def __str__(self):
        right = self.production.right.copy()
        right.insert(self.dot_position, '•')
        right_str = ' '.join(right) if right else '•'
        
        lookaheads_str = ', '.join(sorted(self.lookaheads))
        result = f"{self.production.left} -> {right_str}, {{{lookaheads_str}}}"
        return result
    
    def __eq__(self, other):
        if not isinstance(other, LALR1Item):
            return False
        return (self.production == other.production and 
                self.dot_position == other.dot_position and
                self.lookaheads == other.lookaheads)
    
    def __hash__(self):
        return hash((self.production, self.dot_position, frozenset(self.lookaheads)))
    
    def is_complete(self) -> bool:
        """判断项目是否完整（点在最右边）"""
        return self.dot_position >= len(self.production.right)
    
    def next_symbol(self) -> Optional[str]:
        """获取点后面的符号"""
        if self.is_complete():
            return None
        return self.production.right[self.dot_position]
    
    def advance_dot(self) -> 'LALR1Item':
        """移动点的位置"""
        return LALR1Item(
            production=self.production,
            dot_position=self.dot_position + 1,
            lookaheads=self.lookaheads.copy()
        )
    
    def get_core(self) -> Tuple:
        """获取项目的核心（不包含向前看符号）"""
        return (self.production, self.dot_position)

@dataclass
class ParseStep:
    """语法分析步骤类"""
    step: int                    # 步骤号
    stack: List[Union[str, int]] # 栈内容（状态和符号）
    input_buffer: str            # 输入缓冲区
    action: str                  # 执行的动作
    goto_state: Optional[int] = None  # GOTO状态（归约时使用）
    
    def __str__(self):
        stack_str = ' '.join(str(s) for s in self.stack)
        return f"{self.step:2d} | {stack_str:20s} | {self.input_buffer:15s} | {self.action}"

class Grammar:
    """上下文无关文法类"""
    
    def __init__(self):
        self.productions: List[Production] = []  # 产生式列表
        self.start_symbol: str = ""  # 开始符号
        self.terminals: Set[str] = set()  # 终结符集合
        self.nonterminals: Set[str] = set()  # 非终结符集合
        self.first_sets: Dict[str, Set[str]] = {}  # FIRST集合
        self.follow_sets: Dict[str, Set[str]] = {}  # FOLLOW集合
        self.augmented = False  # 是否已拓广
        
    def add_production(self, left: str, right: List[str]):
        """添加产生式"""
        production = Production(left, right, len(self.productions))
        self.productions.append(production)
        self.nonterminals.add(left)
        
        # 更新终结符和非终结符集合
        for symbol in right:
            if symbol.isupper() or symbol in ['ε', '$']:
                if symbol != 'ε':
                    self.nonterminals.add(symbol)
            else:
                self.terminals.add(symbol)
    
    def set_start_symbol(self, symbol: str):
        """设置开始符号"""
        self.start_symbol = symbol
        self.nonterminals.add(symbol)
    
    def augment_grammar(self) -> 'Grammar':
        """拓广文法"""
        if self.augmented:
            return self

        augmented = Grammar()

        # 创建新的开始符号
        new_start = self.start_symbol + "'"
        augmented.set_start_symbol(new_start)

        # 添加拓广产生式（索引为0）
        augmented.add_production(new_start, [self.start_symbol])

        # 复制原有产生式（索引从1开始）
        for prod in self.productions:
            augmented.add_production(prod.left, prod.right.copy())

        # 复制符号集合
        augmented.terminals = self.terminals.copy()
        augmented.nonterminals = self.nonterminals.copy()
        augmented.nonterminals.add(new_start)
        augmented.terminals.add('$')  # 添加结束符

        augmented.augmented = True
        return augmented
    
    def compute_first_sets(self):
        """计算FIRST集合"""
        self.first_sets = {}
        
        # 初始化
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}
        
        for nonterminal in self.nonterminals:
            self.first_sets[nonterminal] = set()
        
        # 迭代计算
        changed = True
        while changed:
            changed = False
            for production in self.productions:
                first_before = len(self.first_sets[production.left])
                
                if not production.right or production.right == ['ε']:
                    self.first_sets[production.left].add('ε')
                else:
                    for i, symbol in enumerate(production.right):
                        if symbol in self.terminals:
                            self.first_sets[production.left].add(symbol)
                            break
                        else:
                            # 非终结符
                            first_symbol = self.first_sets.get(symbol, set())
                            self.first_sets[production.left].update(first_symbol - {'ε'})
                            
                            if 'ε' not in first_symbol:
                                break
                            
                            # 如果是最后一个符号且包含ε
                            if i == len(production.right) - 1:
                                self.first_sets[production.left].add('ε')
                
                if len(self.first_sets[production.left]) > first_before:
                    changed = True
    
    def compute_follow_sets(self):
        """计算FOLLOW集合"""
        self.follow_sets = {}
        
        # 初始化
        for nonterminal in self.nonterminals:
            self.follow_sets[nonterminal] = set()
        
        # 开始符号的FOLLOW集合包含$
        if self.start_symbol:
            self.follow_sets[self.start_symbol].add('$')
        
        # 迭代计算
        changed = True
        while changed:
            changed = False
            for production in self.productions:
                for i, symbol in enumerate(production.right):
                    if symbol in self.nonterminals:
                        follow_before = len(self.follow_sets[symbol])
                        
                        # 计算β的FIRST集合
                        beta = production.right[i + 1:]
                        first_beta = self.compute_first_of_string(beta)
                        
                        self.follow_sets[symbol].update(first_beta - {'ε'})
                        
                        # 如果β能推导出ε，则将FOLLOW(A)加入FOLLOW(symbol)
                        if 'ε' in first_beta:
                            self.follow_sets[symbol].update(self.follow_sets[production.left])
                        
                        if len(self.follow_sets[symbol]) > follow_before:
                            changed = True
    
    def compute_first_of_string(self, symbols: List[str]) -> Set[str]:
        """计算符号串的FIRST集合"""
        if not symbols:
            return {'ε'}
        
        result = set()
        for symbol in symbols:
            if symbol in self.terminals:
                result.add(symbol)
                break
            else:
                first_symbol = self.first_sets.get(symbol, set())
                result.update(first_symbol - {'ε'})
                
                if 'ε' not in first_symbol:
                    break
        else:
            # 所有符号都能推导出ε
            result.add('ε')
        
        return result
    
    def get_productions_for_nonterminal(self, nonterminal: str) -> List[Production]:
        """获取指定非终结符的所有产生式"""
        return [p for p in self.productions if p.left == nonterminal]
    
    def __str__(self):
        result = f"开始符号: {self.start_symbol}\n"
        result += "产生式:\n"
        for i, prod in enumerate(self.productions):
            result += f"  {i}: {prod}\n"
        return result

# ==================== LR(1)自动机类 ====================

class LR1Automaton:
    """LR(1)自动机类 - 用于构建LALR(1)的基础"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states: List[FrozenSet[LR1Item]] = []  # 状态集合
        self.transitions: Dict[Tuple[int, str], int] = {}  # 转换函数
        self.start_state = 0

    def closure(self, items: Set[LR1Item]) -> FrozenSet[LR1Item]:
        """计算LR(1)项目集的闭包"""
        closure_set = set(items)

        changed = True
        while changed:
            changed = False
            new_items = set()

            for item in closure_set:
                if not item.is_complete():
                    next_sym = item.next_symbol()
                    if next_sym in self.grammar.nonterminals:
                        # 计算向前看符号：FIRST(βa)，其中β是点后面的符号串，a是当前项目的向前看符号
                        beta = item.production.right[item.dot_position + 1:] + [item.lookahead]
                        first_beta = self.grammar.compute_first_of_string(beta)

                        # 为每个产生式和每个向前看符号创建新项目
                        for production in self.grammar.get_productions_for_nonterminal(next_sym):
                            for lookahead in first_beta:
                                if lookahead == 'ε':
                                    continue
                                new_item = LR1Item(production, 0, lookahead)
                                if new_item not in closure_set:
                                    new_items.add(new_item)
                                    changed = True

            closure_set.update(new_items)

        return frozenset(closure_set)

    def goto(self, state: FrozenSet[LR1Item], symbol: str) -> FrozenSet[LR1Item]:
        """计算GOTO函数"""
        goto_items = set()

        for item in state:
            if not item.is_complete() and item.next_symbol() == symbol:
                goto_items.add(item.advance_dot())

        if goto_items:
            return self.closure(goto_items)
        else:
            return frozenset()

    def build_lr1_automaton(self):
        """构建LR(1)自动机"""
        # 确保文法已拓广
        if not self.grammar.augmented:
            self.grammar = self.grammar.augment_grammar()

        # 计算FIRST和FOLLOW集合
        self.grammar.compute_first_sets()
        self.grammar.compute_follow_sets()

        # 初始状态：包含拓广产生式的项目，向前看符号为$
        start_production = self.grammar.productions[0]
        start_item = LR1Item(start_production, 0, '$')
        start_state = self.closure({start_item})

        self.states = [start_state]
        worklist = [0]

        while worklist:
            state_index = worklist.pop(0)
            current_state = self.states[state_index]

            # 收集所有可能的转换符号
            symbols = set()
            for item in current_state:
                if not item.is_complete():
                    symbols.add(item.next_symbol())

            # 为每个符号计算GOTO
            for symbol in symbols:
                goto_state = self.goto(current_state, symbol)
                if goto_state:
                    # 检查是否已存在相同状态
                    target_index = None
                    for i, existing_state in enumerate(self.states):
                        if existing_state == goto_state:
                            target_index = i
                            break

                    if target_index is None:
                        # 新状态
                        target_index = len(self.states)
                        self.states.append(goto_state)
                        worklist.append(target_index)

                    # 添加转换
                    self.transitions[(state_index, symbol)] = target_index

    def get_state_cores(self) -> Dict[Tuple, List[int]]:
        """获取状态核心映射 - 用于LALR(1)合并"""
        core_to_states = {}

        for state_index, state in enumerate(self.states):
            # 计算状态的核心（所有项目的核心集合）
            core = frozenset(item.get_core() for item in state)

            if core not in core_to_states:
                core_to_states[core] = []
            core_to_states[core].append(state_index)

        return core_to_states

# ==================== LALR(1)自动机类 ====================

class LALR1Automaton:
    """LALR(1)自动机类 - 基于LR(1)状态合并"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.lr1_automaton = LR1Automaton(grammar)
        self.states: List[FrozenSet[LALR1Item]] = []  # LALR(1)状态集合
        self.transitions: Dict[Tuple[int, str], int] = {}  # 转换函数
        self.state_mapping: Dict[int, int] = {}  # LR(1)状态到LALR(1)状态的映射
        self.start_state = 0

    def build_lalr1_automaton(self):
        """构建LALR(1)自动机"""
        # 首先构建LR(1)自动机
        self.lr1_automaton.build_lr1_automaton()

        # 更新文法为拓广后的文法
        self.grammar = self.lr1_automaton.grammar

        # 获取状态核心映射
        core_to_lr1_states = self.lr1_automaton.get_state_cores()

        # 合并具有相同核心的状态
        self._merge_states_with_same_core(core_to_lr1_states)

        # 构建LALR(1)转换函数
        self._build_lalr1_transitions()

    def _merge_states_with_same_core(self, core_to_lr1_states: Dict[Tuple, List[int]]):
        """合并具有相同核心的LR(1)状态"""
        self.states = []
        self.state_mapping = {}

        lalr1_state_index = 0

        for core, lr1_state_indices in core_to_lr1_states.items():
            # 合并具有相同核心的所有LR(1)状态
            merged_items = {}  # 核心 -> LALR1Item

            for lr1_state_index in lr1_state_indices:
                lr1_state = self.lr1_automaton.states[lr1_state_index]

                for lr1_item in lr1_state:
                    item_core = lr1_item.get_core()

                    if item_core not in merged_items:
                        # 创建新的LALR(1)项目
                        merged_items[item_core] = LALR1Item(
                            production=lr1_item.production,
                            dot_position=lr1_item.dot_position,
                            lookaheads={lr1_item.lookahead}
                        )
                    else:
                        # 合并向前看符号
                        merged_items[item_core].lookaheads.add(lr1_item.lookahead)

                # 建立映射关系
                self.state_mapping[lr1_state_index] = lalr1_state_index

            # 创建LALR(1)状态
            lalr1_state = frozenset(merged_items.values())
            self.states.append(lalr1_state)
            lalr1_state_index += 1

    def _build_lalr1_transitions(self):
        """构建LALR(1)转换函数"""
        self.transitions = {}

        for (from_lr1_state, symbol), to_lr1_state in self.lr1_automaton.transitions.items():
            from_lalr1_state = self.state_mapping[from_lr1_state]
            to_lalr1_state = self.state_mapping[to_lr1_state]

            # 添加LALR(1)转换
            self.transitions[(from_lalr1_state, symbol)] = to_lalr1_state

# ==================== LALR(1)分析表类 ====================

class LALR1ParsingTable:
    """LALR(1)分析表类"""

    def __init__(self, grammar: Grammar, automaton: LALR1Automaton):
        self.grammar = grammar
        self.automaton = automaton
        self.action_table: Dict[Tuple[int, str], Action] = {}  # ACTION表
        self.goto_table: Dict[Tuple[int, str], int] = {}      # GOTO表
        self.conflicts: List[str] = []  # 冲突记录

    def build_parsing_table(self):
        """构建LALR(1)分析表"""
        self.action_table.clear()
        self.goto_table.clear()
        self.conflicts.clear()

        # 遍历所有状态
        for state_index, state in enumerate(self.automaton.states):
            # 处理移进动作
            self._add_shift_actions(state_index, state)

            # 处理归约动作
            self._add_reduce_actions(state_index, state)

            # 处理GOTO动作
            self._add_goto_actions(state_index)

        # 添加接受动作
        self._add_accept_action()

    def _add_shift_actions(self, state_index: int, state: FrozenSet[LALR1Item]):
        """添加移进动作"""
        for item in state:
            if not item.is_complete():
                next_sym = item.next_symbol()
                if next_sym in self.grammar.terminals:
                    # 查找转换目标状态
                    target_state = self.automaton.transitions.get((state_index, next_sym))
                    if target_state is not None:
                        action_key = (state_index, next_sym)
                        new_action = Action(ActionType.SHIFT, target_state)

                        # 检查冲突
                        if action_key in self.action_table:
                            existing_action = self.action_table[action_key]
                            self.conflicts.append(
                                f"状态{state_index}，符号'{next_sym}': "
                                f"移进-{existing_action.action_type.value}冲突"
                            )
                        else:
                            self.action_table[action_key] = new_action

    def _add_reduce_actions(self, state_index: int, state: FrozenSet[LALR1Item]):
        """添加归约动作 - LALR(1)使用项目的向前看符号集合"""
        for item in state:
            if item.is_complete() and item.production.index != 0:  # 不是拓广产生式
                # LALR(1)：在项目的所有向前看符号上添加归约动作
                for lookahead in item.lookaheads:
                    action_key = (state_index, lookahead)
                    new_action = Action(ActionType.REDUCE, item.production.index)

                    # 检查冲突
                    if action_key in self.action_table:
                        existing_action = self.action_table[action_key]
                        if existing_action.action_type == ActionType.SHIFT:
                            self.conflicts.append(
                                f"状态{state_index}，符号'{lookahead}': 移进-归约冲突"
                            )
                        elif existing_action.action_type == ActionType.REDUCE:
                            self.conflicts.append(
                                f"状态{state_index}，符号'{lookahead}': 归约-归约冲突"
                            )
                    else:
                        self.action_table[action_key] = new_action

    def _add_goto_actions(self, state_index: int):
        """添加GOTO动作"""
        for (from_state, symbol), to_state in self.automaton.transitions.items():
            if from_state == state_index and symbol in self.grammar.nonterminals:
                self.goto_table[(state_index, symbol)] = to_state

    def _add_accept_action(self):
        """添加接受动作"""
        # 查找包含拓广产生式完整项目的状态
        for state_index, state in enumerate(self.automaton.states):
            for item in state:
                if (item.is_complete() and
                    item.production.index == 0 and  # 拓广产生式
                    '$' in item.lookaheads):
                    action_key = (state_index, '$')
                    self.action_table[action_key] = Action(ActionType.ACCEPT)
                    break

    def get_action(self, state: int, symbol: str) -> Action:
        """获取ACTION表中的动作"""
        return self.action_table.get((state, symbol), Action(ActionType.ERROR))

    def get_goto(self, state: int, symbol: str) -> Optional[int]:
        """获取GOTO表中的状态"""
        return self.goto_table.get((state, symbol))

    def has_conflicts(self) -> bool:
        """检查是否有冲突"""
        return len(self.conflicts) > 0

    def get_conflicts(self) -> List[str]:
        """获取冲突列表"""
        return self.conflicts.copy()

    def print_table(self) -> str:
        """打印分析表"""
        result = "LALR(1)分析表:\n"
        result += "=" * 80 + "\n"

        # 收集所有终结符和非终结符
        terminals = sorted(self.grammar.terminals)
        nonterminals = sorted(self.grammar.nonterminals)

        # 确保$符号在终结符列表中
        if '$' not in terminals:
            terminals.append('$')

        # 移除开始符号（拓广后的）
        if self.grammar.start_symbol in nonterminals:
            nonterminals.remove(self.grammar.start_symbol)

        # 表头
        header = "状态".ljust(6)
        for terminal in terminals:
            header += terminal.ljust(8)
        header += "|"
        for nonterminal in nonterminals:
            header += nonterminal.ljust(8)
        result += header + "\n"
        result += "-" * len(header) + "\n"

        # 表内容
        for state_index in range(len(self.automaton.states)):
            row = f"{state_index}".ljust(6)

            # ACTION部分
            for terminal in terminals:
                action = self.get_action(state_index, terminal)
                action_str = str(action) if action.action_type != ActionType.ERROR else ""
                row += action_str.ljust(8)

            row += "|"

            # GOTO部分
            for nonterminal in nonterminals:
                goto_state = self.get_goto(state_index, nonterminal)
                if goto_state is not None:
                    row += str(goto_state).ljust(8)
                else:
                    row += "".ljust(8)

            result += row + "\n"

        return result

# ==================== LALR(1)语法分析器类 ====================

class LALR1Parser:
    """LALR(1)语法分析器类"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.automaton = LALR1Automaton(grammar)
        self.parsing_table = LALR1ParsingTable(grammar, self.automaton)
        self.built = False

    def build_parser(self):
        """构建分析器"""
        # 构建LALR(1)自动机
        self.automaton.build_lalr1_automaton()

        # 更新文法为拓广后的文法
        self.grammar = self.automaton.grammar

        # 构建分析表
        self.parsing_table.build_parsing_table()

        self.built = True

    def parse(self, input_string: str) -> Tuple[bool, List[ParseStep], str]:
        """解析输入串"""
        if not self.built:
            self.build_parser()

        # 词法分析
        tokens = self._tokenize(input_string)
        tokens.append('$')  # 添加结束符

        # 初始化栈和输入缓冲区
        stack = [0]  # 状态栈，初始状态为0
        input_buffer = tokens.copy()
        steps = []
        step_count = 0

        while True:
            step_count += 1
            current_state = stack[-1]
            current_symbol = input_buffer[0] if input_buffer else '$'

            # 记录当前步骤
            step = ParseStep(
                step=step_count,
                stack=stack.copy(),
                input_buffer=' '.join(input_buffer),
                action=""
            )

            # 查表获取动作
            action = self.parsing_table.get_action(current_state, current_symbol)

            if action.action_type == ActionType.SHIFT:
                # 移进动作
                step.action = f"移进到状态{action.value}"
                steps.append(step)

                stack.append(current_symbol)
                stack.append(action.value)
                input_buffer.pop(0)

            elif action.action_type == ActionType.REDUCE:
                # 归约动作
                production = self.grammar.productions[action.value]
                step.action = f"用产生式{action.value}归约: {production}"

                # 弹出栈中的符号和状态
                pop_count = len(production.right) * 2 if production.right != ['ε'] else 0
                for _ in range(pop_count):
                    if stack:
                        stack.pop()

                # 压入左部非终结符
                if stack:
                    goto_state = self.parsing_table.get_goto(stack[-1], production.left)
                    if goto_state is not None:
                        stack.append(production.left)
                        stack.append(goto_state)
                        step.goto_state = goto_state
                    else:
                        step.action += " (GOTO错误)"
                        steps.append(step)
                        return False, steps, f"GOTO错误：状态{stack[-1]}，符号{production.left}"
                else:
                    step.action += " (栈为空错误)"
                    steps.append(step)
                    return False, steps, "栈为空错误"

                steps.append(step)

            elif action.action_type == ActionType.ACCEPT:
                # 接受动作
                step.action = "接受"
                steps.append(step)
                return True, steps, "分析成功"

            else:
                # 错误动作
                step.action = f"错误：状态{current_state}，符号{current_symbol}"
                steps.append(step)
                return False, steps, f"语法错误：状态{current_state}，符号{current_symbol}"

    def _tokenize(self, input_string: str) -> List[str]:
        """简单的词法分析器"""
        tokens = []
        i = 0
        while i < len(input_string):
            char = input_string[i]
            if char.isspace():
                i += 1
                continue
            elif char.isalpha():
                # 标识符
                token = ""
                while i < len(input_string) and (input_string[i].isalnum() or input_string[i] == '_'):
                    token += input_string[i]
                    i += 1
                tokens.append('id' if token not in self.grammar.terminals else token)
            elif char in '+-*/()':
                tokens.append(char)
                i += 1
            else:
                i += 1
        return tokens

# ==================== 文法解析器类 ====================

class GrammarParser:
    """文法解析器类 - 解析文本格式的文法"""

    @staticmethod
    def parse_grammar_from_text(text: str) -> Grammar:
        """从文本解析文法"""
        grammar = Grammar()
        lines = text.strip().split('\n')

        # 过滤空行和注释行
        lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

        if not lines:
            raise ValueError("文法为空")

        # 解析产生式
        first_production = True
        for line in lines:
            if '->' not in line:
                continue

            # 分割左部和右部
            parts = line.split('->')
            if len(parts) != 2:
                continue

            left = parts[0].strip()
            right_part = parts[1].strip()

            # 设置开始符号（第一个产生式的左部）
            if first_production:
                grammar.set_start_symbol(left)
                first_production = False

            # 处理多个产生式（用|分隔）
            alternatives = right_part.split('|')
            for alt in alternatives:
                alt = alt.strip()
                if alt == 'ε' or alt == 'epsilon':
                    right_symbols = ['ε']
                else:
                    # 简单的符号分割（按空格）
                    right_symbols = alt.split()

                grammar.add_production(left, right_symbols)

        if not grammar.productions:
            raise ValueError("没有找到有效的产生式")

        return grammar

    @staticmethod
    def parse_grammar_from_file(filename: str) -> Grammar:
        """从文件解析文法"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            return GrammarParser.parse_grammar_from_text(text)
        except FileNotFoundError:
            raise ValueError(f"文件不存在: {filename}")
        except Exception as e:
            raise ValueError(f"读取文件错误: {e}")

# ==================== 工具函数 ====================

def create_sample_grammar() -> Grammar:
    """创建示例文法（算术表达式）"""
    grammar = Grammar()
    grammar.set_start_symbol('E')

    # E -> E + T | T
    grammar.add_production('E', ['E', '+', 'T'])
    grammar.add_production('E', ['T'])

    # T -> T * F | F
    grammar.add_production('T', ['T', '*', 'F'])
    grammar.add_production('T', ['F'])

    # F -> ( E ) | id
    grammar.add_production('F', ['(', 'E', ')'])
    grammar.add_production('F', ['id'])

    return grammar

def test_lalr1_parser():
    """测试LALR(1)分析器"""
    print("=== LALR(1)语法分析器测试 ===\n")

    # 创建示例文法
    grammar = create_sample_grammar()
    print("原始文法:")
    print(grammar)

    # 创建分析器
    parser = LALR1Parser(grammar)
    parser.build_parser()

    print(f"\n拓广后的文法:")
    print(parser.grammar)

    print(f"\nFIRST集合:")
    for symbol, first_set in parser.grammar.first_sets.items():
        if first_set:  # 只显示非空集合
            print(f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}")

    print(f"\nFOLLOW集合:")
    for symbol, follow_set in parser.grammar.follow_sets.items():
        if symbol != parser.grammar.start_symbol and follow_set:  # 不显示拓广开始符号，只显示非空集合
            print(f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}")

    print(f"\nLR(1)状态数: {len(parser.automaton.lr1_automaton.states)}")
    print(f"LALR(1)状态数: {len(parser.automaton.states)}")

    # 检查冲突
    if parser.parsing_table.has_conflicts():
        print(f"\n发现冲突:")
        for conflict in parser.parsing_table.get_conflicts():
            print(f"  {conflict}")
    else:
        print(f"\n无冲突，LALR(1)文法")

    # 打印分析表
    print(f"\n分析表:")
    print(parser.parsing_table.print_table())

    # 测试分析过程
    test_strings = ["id + id * id", "( id + id ) * id", "id"]

    for test_string in test_strings:
        print(f"\n分析输入串: {test_string}")
        success, steps, message = parser.parse(test_string)

        print(f"结果: {message}")
        if success:
            print("分析步骤:")
            for step in steps[-5:]:  # 只显示最后5步
                print(f"  {step}")
        else:
            print("最后几步:")
            for step in steps[-3:]:  # 显示最后3步
                print(f"  {step}")
        print("-" * 50)

# ==================== GUI界面类 ====================

class LALR1ParserGUI:
    """LALR(1)语法分析器GUI界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LALR(1)完整的语法分析方法")
        self.root.geometry("1200x800")

        # 数据
        self.grammar = None
        self.parser = None

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个标签页
        self.create_grammar_tab()
        self.create_parsing_table_tab()
        self.create_parsing_process_tab()
        self.create_automaton_tab()
        self.create_help_tab()

    def create_grammar_tab(self):
        """创建文法输入标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="文法输入")

        # 左侧：文法输入区域
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 文法输入标签
        ttk.Label(left_frame, text="文法输入（每行一个产生式，用 -> 分隔左右部，用 | 分隔多个候选）:").pack(anchor=tk.W)

        # 文法输入文本框
        self.grammar_text = scrolledtext.ScrolledText(left_frame, height=15, width=50)
        self.grammar_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 默认文法
        default_grammar = """# LALR(1)语法分析器示例文法
# 经典算术表达式文法

E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
        self.grammar_text.insert(tk.END, default_grammar)

        # 按钮框架
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="解析文法", command=self.parse_grammar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="构建分析器", command=self.build_parser).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载文件", command=self.load_grammar_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存文法", command=self.save_grammar).pack(side=tk.LEFT, padx=5)

        # 右侧：文法信息显示
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 文法信息标签
        ttk.Label(right_frame, text="文法信息:").pack(anchor=tk.W)

        # 文法信息显示
        self.grammar_info = scrolledtext.ScrolledText(right_frame, height=20, width=50)
        self.grammar_info.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_parsing_table_tab(self):
        """创建分析表标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="LALR(1)分析表")

        # 控制按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="生成分析表", command=self.generate_parsing_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="检查冲突", command=self.check_conflicts).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存分析表", command=self.save_parsing_table).pack(side=tk.LEFT, padx=5)

        # 分析表显示
        self.parsing_table_text = scrolledtext.ScrolledText(frame, height=25, font=('Courier', 10))
        self.parsing_table_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 冲突信息显示
        ttk.Label(frame, text="冲突信息:").pack(anchor=tk.W, padx=5)
        self.conflicts_text = scrolledtext.ScrolledText(frame, height=5)
        self.conflicts_text.pack(fill=tk.X, padx=5, pady=5)

    def create_parsing_process_tab(self):
        """创建语法分析过程标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="语法分析过程")

        # 输入控制区域
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="输入串:").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(input_frame, width=30)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.insert(0, "id + id * id")

        ttk.Button(input_frame, text="开始分析", command=self.start_parsing).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="清空结果", command=self.clear_parsing_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="保存分析过程", command=self.save_parsing_process).pack(side=tk.LEFT, padx=5)

        # 分析过程显示区域
        process_frame = ttk.Frame(frame)
        process_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧：分析步骤
        left_frame = ttk.Frame(process_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(left_frame, text="分析步骤:").pack(anchor=tk.W)
        self.steps_text = scrolledtext.ScrolledText(left_frame, height=20, font=('Courier', 10))
        self.steps_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 右侧：分析结果
        right_frame = ttk.Frame(process_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(right_frame, text="分析结果:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(right_frame, height=20)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_automaton_tab(self):
        """创建自动机可视化标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="自动机可视化")

        # 控制按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="生成可视化", command=self.generate_automaton_visualization).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存图片", command=self.save_visualization).pack(side=tk.LEFT, padx=5)

        # 状态选择
        ttk.Label(button_frame, text="选择状态:").pack(side=tk.LEFT, padx=10)
        self.state_var = tk.StringVar()
        self.state_combo = ttk.Combobox(button_frame, textvariable=self.state_var, width=10)
        self.state_combo.pack(side=tk.LEFT, padx=5)
        self.state_combo.bind('<<ComboboxSelected>>', self.on_state_selected)

        # 可视化区域
        viz_frame = ttk.Frame(frame)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧：自动机图形
        left_frame = ttk.Frame(viz_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 这里将放置matplotlib图形
        self.automaton_canvas_frame = left_frame

        # 右侧：状态详情
        right_frame = ttk.Frame(viz_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(right_frame, text="状态详情:").pack(anchor=tk.W)
        self.state_details_text = scrolledtext.ScrolledText(right_frame, height=25, width=40)
        self.state_details_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_help_tab(self):
        """创建帮助标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="帮助")

        help_text = scrolledtext.ScrolledText(frame, height=30, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_content = """LALR(1)完整的语法分析方法 - 使用说明

1. 文法输入
   - 在"文法输入"标签页中输入上下文无关文法
   - 格式：左部 -> 右部1 | 右部2 | ...
   - 示例：E -> E + T | T
   - 支持ε产生式，用ε或epsilon表示
   - 支持注释行，以#开头

2. 构建分析器
   - 点击"解析文法"按钮解析输入的文法
   - 点击"构建分析器"按钮构建LALR(1)分析器
   - 右侧会显示文法信息、FIRST集合、FOLLOW集合等

3. 查看分析表
   - 在"LALR(1)分析表"标签页中查看生成的分析表
   - 点击"生成分析表"按钮生成分析表
   - 点击"检查冲突"按钮检查是否有移进-归约或归约-归约冲突

4. 语法分析
   - 在"语法分析过程"标签页中进行语法分析
   - 输入要分析的字符串
   - 点击"开始分析"按钮开始分析
   - 左侧显示详细的分析步骤，右侧显示分析结果

5. 自动机可视化
   - 在"自动机可视化"标签页中查看LALR(1)自动机
   - 点击"生成可视化"按钮生成状态转换图
   - 选择状态可以查看该状态的详细信息

算法原理：
LALR(1)分析方法是LR(1)分析方法的简化版本，通过合并具有相同核心的LR(1)状态来减少状态数量。

核心步骤：
1. 构建LR(1)项目集族
2. 识别具有相同核心的状态
3. 合并这些状态的向前看符号
4. 构建LALR(1)分析表
5. 进行语法分析

特点：
- 状态数比LR(1)少，比SLR(1)多
- 分析能力介于SLR(1)和LR(1)之间
- 实用性强，被广泛应用于编译器构造

作者：王海翔
学号：2021060187
班级：计科2203
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

    # ==================== 事件处理方法 ====================

    def parse_grammar(self):
        """解析文法"""
        try:
            grammar_text = self.grammar_text.get(1.0, tk.END)
            self.grammar = GrammarParser.parse_grammar_from_text(grammar_text)

            # 显示文法信息
            info = f"文法解析成功！\n\n"
            info += f"开始符号: {self.grammar.start_symbol}\n\n"
            info += "产生式:\n"
            for i, prod in enumerate(self.grammar.productions):
                info += f"  {i}: {prod}\n"

            info += f"\n终结符: {{{', '.join(sorted(self.grammar.terminals))}}}\n"
            info += f"非终结符: {{{', '.join(sorted(self.grammar.nonterminals))}}}\n"

            self.grammar_info.delete(1.0, tk.END)
            self.grammar_info.insert(tk.END, info)

            messagebox.showinfo("成功", "文法解析成功！")

        except Exception as e:
            messagebox.showerror("错误", f"文法解析失败：{str(e)}")

    def build_parser(self):
        """构建分析器"""
        if not self.grammar:
            messagebox.showerror("错误", "请先解析文法！")
            return

        try:
            self.parser = LALR1Parser(self.grammar)
            self.parser.build_parser()

            # 显示详细信息
            info = f"LALR(1)分析器构建成功！\n\n"
            info += f"拓广后的文法:\n"
            info += f"开始符号: {self.parser.grammar.start_symbol}\n\n"
            info += "产生式:\n"
            for i, prod in enumerate(self.parser.grammar.productions):
                info += f"  {i}: {prod}\n"

            info += f"\nFIRST集合:\n"
            for symbol, first_set in self.parser.grammar.first_sets.items():
                if first_set:
                    info += f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}\n"

            info += f"\nFOLLOW集合:\n"
            for symbol, follow_set in self.parser.grammar.follow_sets.items():
                if symbol != self.parser.grammar.start_symbol and follow_set:
                    info += f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}\n"

            info += f"\nLR(1)状态数: {len(self.parser.automaton.lr1_automaton.states)}\n"
            info += f"LALR(1)状态数: {len(self.parser.automaton.states)}\n"

            if self.parser.parsing_table.has_conflicts():
                info += f"\n发现冲突:\n"
                for conflict in self.parser.parsing_table.get_conflicts():
                    info += f"  {conflict}\n"
            else:
                info += f"\n无冲突，LALR(1)文法\n"

            self.grammar_info.delete(1.0, tk.END)
            self.grammar_info.insert(tk.END, info)

            # 更新状态选择框
            state_count = len(self.parser.automaton.states)
            self.state_combo['values'] = [str(i) for i in range(state_count)]

            messagebox.showinfo("成功", "LALR(1)分析器构建成功！")

        except Exception as e:
            messagebox.showerror("错误", f"分析器构建失败：{str(e)}")

    def load_grammar_file(self):
        """加载文法文件"""
        try:
            filename = filedialog.askopenfilename(
                title="选择文法文件",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.grammar_text.delete(1.0, tk.END)
                self.grammar_text.insert(tk.END, content)
                messagebox.showinfo("成功", "文法文件加载成功！")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败：{str(e)}")

    def save_grammar(self):
        """保存文法"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存文法",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                content = self.grammar_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", "文法保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败：{str(e)}")

    def generate_parsing_table(self):
        """生成分析表"""
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器！")
            return

        try:
            table_str = self.parser.parsing_table.print_table()
            self.parsing_table_text.delete(1.0, tk.END)
            self.parsing_table_text.insert(tk.END, table_str)

            # 显示冲突信息
            if self.parser.parsing_table.has_conflicts():
                conflicts = "\n".join(self.parser.parsing_table.get_conflicts())
                self.conflicts_text.delete(1.0, tk.END)
                self.conflicts_text.insert(tk.END, conflicts)
            else:
                self.conflicts_text.delete(1.0, tk.END)
                self.conflicts_text.insert(tk.END, "无冲突")

            messagebox.showinfo("成功", "分析表生成成功！")

        except Exception as e:
            messagebox.showerror("错误", f"生成分析表失败：{str(e)}")

    def check_conflicts(self):
        """检查冲突"""
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器！")
            return

        if self.parser.parsing_table.has_conflicts():
            conflicts = "\n".join(self.parser.parsing_table.get_conflicts())
            self.conflicts_text.delete(1.0, tk.END)
            self.conflicts_text.insert(tk.END, conflicts)
            messagebox.showwarning("冲突", f"发现{len(self.parser.parsing_table.get_conflicts())}个冲突")
        else:
            self.conflicts_text.delete(1.0, tk.END)
            self.conflicts_text.insert(tk.END, "无冲突")
            messagebox.showinfo("无冲突", "该文法是LALR(1)文法，无冲突！")

    def save_parsing_table(self):
        """保存分析表"""
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器！")
            return

        try:
            filename = filedialog.asksaveasfilename(
                title="保存分析表",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                table_str = self.parser.parsing_table.print_table()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(table_str)
                messagebox.showinfo("成功", "分析表保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存分析表失败：{str(e)}")

    def start_parsing(self):
        """开始语法分析"""
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器！")
            return

        try:
            input_string = self.input_entry.get().strip()
            if not input_string:
                messagebox.showerror("错误", "请输入要分析的字符串！")
                return

            success, steps, message = self.parser.parse(input_string)

            # 显示分析步骤
            steps_str = "分析步骤:\n"
            steps_str += "步骤 | 栈内容                | 输入缓冲区      | 动作\n"
            steps_str += "-" * 60 + "\n"
            for step in steps:
                steps_str += str(step) + "\n"

            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(tk.END, steps_str)

            # 显示分析结果
            result_str = f"输入串: {input_string}\n"
            result_str += f"分析结果: {message}\n"
            result_str += f"状态: {'成功' if success else '失败'}\n\n"

            if success:
                result_str += "分析成功！该输入串符合文法。\n"
            else:
                result_str += "分析失败！该输入串不符合文法。\n"

            result_str += f"\n总步骤数: {len(steps)}\n"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_str)

            if success:
                messagebox.showinfo("分析成功", "语法分析成功！")
            else:
                messagebox.showerror("分析失败", f"语法分析失败：{message}")

        except Exception as e:
            messagebox.showerror("错误", f"分析过程出错：{str(e)}")

    def clear_parsing_result(self):
        """清空分析结果"""
        self.steps_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def save_parsing_process(self):
        """保存分析过程"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存分析过程",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                steps_content = self.steps_text.get(1.0, tk.END)
                result_content = self.result_text.get(1.0, tk.END)

                content = "LALR(1)语法分析过程\n"
                content += "=" * 50 + "\n\n"
                content += result_content + "\n"
                content += "=" * 50 + "\n\n"
                content += steps_content

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", "分析过程保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存分析过程失败：{str(e)}")

    def generate_automaton_visualization(self):
        """生成自动机可视化"""
        if not self.parser:
            messagebox.showerror("错误", "请先构建分析器！")
            return

        try:
            # 清除之前的图形
            for widget in self.automaton_canvas_frame.winfo_children():
                widget.destroy()

            # 创建图形
            fig, ax = plt.subplots(figsize=(12, 8))

            # 创建有向图
            G = nx.DiGraph()

            # 添加节点
            for i in range(len(self.parser.automaton.states)):
                G.add_node(i)

            # 添加边
            edge_labels = {}
            for (from_state, symbol), to_state in self.parser.automaton.transitions.items():
                if G.has_edge(from_state, to_state):
                    # 如果已有边，添加符号到标签
                    edge_labels[(from_state, to_state)] += f", {symbol}"
                else:
                    G.add_edge(from_state, to_state)
                    edge_labels[(from_state, to_state)] = symbol

            # 布局
            pos = nx.spring_layout(G, k=3, iterations=50)

            # 绘制节点
            nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                                 node_size=1000, ax=ax)

            # 绘制边
            nx.draw_networkx_edges(G, pos, edge_color='gray',
                                 arrows=True, arrowsize=20, ax=ax)

            # 绘制节点标签
            nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)

            # 绘制边标签
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)

            ax.set_title("LALR(1)自动机状态转换图")
            ax.axis('off')

            # 嵌入到tkinter
            canvas = FigureCanvasTkAgg(fig, self.automaton_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            messagebox.showinfo("成功", "自动机可视化生成成功！")

        except Exception as e:
            messagebox.showerror("错误", f"生成可视化失败：{str(e)}")

    def on_state_selected(self, event):
        """状态选择事件"""
        if not self.parser:
            return

        try:
            state_index = int(self.state_var.get())
            if 0 <= state_index < len(self.parser.automaton.states):
                state = self.parser.automaton.states[state_index]

                details = f"状态 {state_index} 详情:\n"
                details += "=" * 30 + "\n\n"
                details += "项目集:\n"
                for item in state:
                    details += f"  {item}\n"

                details += f"\n转换:\n"
                for (from_state, symbol), to_state in self.parser.automaton.transitions.items():
                    if from_state == state_index:
                        details += f"  {symbol} -> 状态{to_state}\n"

                self.state_details_text.delete(1.0, tk.END)
                self.state_details_text.insert(tk.END, details)

        except ValueError:
            pass
        except Exception as e:
            messagebox.showerror("错误", f"显示状态详情失败：{str(e)}")

    def save_visualization(self):
        """保存可视化图片"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存图片",
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
            )
            if filename:
                # 这里需要获取当前的matplotlib图形并保存
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", "图片保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存图片失败：{str(e)}")

if __name__ == "__main__":
    # 可以选择运行测试或GUI
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_lalr1_parser()
    else:
        # 运行GUI
        app = LALR1ParserGUI()
        app.root.mainloop()
