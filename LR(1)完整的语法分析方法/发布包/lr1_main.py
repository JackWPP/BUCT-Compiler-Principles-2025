# -*- coding: utf-8 -*-
"""
编译原理作业 - LR(1)完整的语法分析方法
实现上下文无关文法的识别和拓广，LR(0)识别活前缀的状态机，LR(1)判断；
LR(1)识别活前缀的状态机，LR(1)分析表，LR分析过程

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
    """LR(1)分析表动作类型"""
    SHIFT = "移进"      # 移进动作
    REDUCE = "归约"     # 归约动作
    ACCEPT = "接受"     # 接受动作
    ERROR = "错误"      # 错误动作

@dataclass
class Action:
    """LR(1)分析表动作类"""
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
        
        # 添加拓广产生式
        augmented.add_production(new_start, [self.start_symbol])
        
        # 复制原有产生式
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
    """LR(1)自动机类"""

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

class LR1ParsingTable:
    """LR(1)分析表类"""

    def __init__(self, grammar: Grammar, automaton: LR1Automaton):
        self.grammar = grammar
        self.automaton = automaton
        self.action_table: Dict[Tuple[int, str], Action] = {}  # ACTION表
        self.goto_table: Dict[Tuple[int, str], int] = {}      # GOTO表
        self.conflicts: List[str] = []  # 冲突记录

    def build_parsing_table(self):
        """构建LR(1)分析表"""
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

    def _add_shift_actions(self, state_index: int, state: FrozenSet[LR1Item]):
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

    def _add_reduce_actions(self, state_index: int, state: FrozenSet[LR1Item]):
        """添加归约动作 - LR(1)使用项目的向前看符号而不是FOLLOW集合"""
        for item in state:
            if item.is_complete() and item.production.index != 0:  # 不是拓广产生式
                # LR(1)：只在项目的向前看符号上添加归约动作
                action_key = (state_index, item.lookahead)
                new_action = Action(ActionType.REDUCE, item.production.index)

                # 检查冲突
                if action_key in self.action_table:
                    existing_action = self.action_table[action_key]
                    if existing_action.action_type == ActionType.SHIFT:
                        self.conflicts.append(
                            f"状态{state_index}，符号'{item.lookahead}': 移进-归约冲突"
                        )
                    elif existing_action.action_type == ActionType.REDUCE:
                        self.conflicts.append(
                            f"状态{state_index}，符号'{item.lookahead}': 归约-归约冲突"
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
                    item.production.left == self.grammar.start_symbol and
                    item.lookahead == '$'):
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
        result = "LR(1)分析表:\n"
        result += "=" * 80 + "\n"

        # 收集所有终结符和非终结符
        terminals = sorted(self.grammar.terminals)
        nonterminals = sorted(self.grammar.nonterminals - {self.grammar.start_symbol})

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
            row = str(state_index).ljust(6)

            # ACTION部分
            for terminal in terminals:
                action_key = (state_index, terminal)
                if action_key in self.action_table:
                    action = self.action_table[action_key]
                    action_str = str(action)
                else:
                    action_str = ""  # 空白而不是error
                row += action_str.ljust(8)

            row += "|"

            # GOTO部分
            for nonterminal in nonterminals:
                goto_state = self.get_goto(state_index, nonterminal)
                goto_str = str(goto_state) if goto_state is not None else ""
                row += goto_str.ljust(8)

            result += row + "\n"

        return result

class LR1Parser:
    """LR(1)语法分析器类"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar.augment_grammar()
        self.automaton = LR1Automaton(self.grammar)
        self.parsing_table = LR1ParsingTable(self.grammar, self.automaton)
        self.parse_steps: List[ParseStep] = []  # 分析步骤记录

    def build_parser(self):
        """构建分析器"""
        # 构建LR(1)自动机
        self.automaton.build_lr1_automaton()

        # 构建LR(1)分析表
        self.parsing_table.build_parsing_table()

    def parse(self, input_string: str) -> Tuple[bool, List[ParseStep], str]:
        """
        解析输入串
        返回: (是否成功, 分析步骤, 错误信息)
        """
        self.parse_steps.clear()

        # 词法分析：将输入字符串分割为符号序列
        tokens = self._tokenize(input_string)

        # 初始化
        stack = [0]  # 状态栈，初始状态为0
        input_buffer = tokens + ['$']  # 输入缓冲区
        input_index = 0
        step_count = 0

        while True:
            step_count += 1
            current_state = stack[-1]
            current_symbol = input_buffer[input_index] if input_index < len(input_buffer) else '$'

            # 记录当前步骤
            remaining_input = ' '.join(input_buffer[input_index:])
            step = ParseStep(
                step=step_count,
                stack=stack.copy(),
                input_buffer=remaining_input,
                action=""
            )

            # 查找动作
            action = self.parsing_table.get_action(current_state, current_symbol)

            if action.action_type == ActionType.SHIFT:
                # 移进动作
                stack.append(action.value)
                input_index += 1
                step.action = f"移进到状态{action.value}"
                self.parse_steps.append(step)

            elif action.action_type == ActionType.REDUCE:
                # 归约动作
                production = self.grammar.productions[action.value]

                # 弹出栈顶的|右部|个状态（对于ε产生式不弹出）
                pop_count = len(production.right) if production.right != ['ε'] else 0
                for _ in range(pop_count):
                    if stack:
                        stack.pop()

                # 查找GOTO状态
                if stack:
                    goto_state = self.parsing_table.get_goto(stack[-1], production.left)
                    if goto_state is not None:
                        stack.append(goto_state)
                        step.action = f"用产生式{action.value}归约: {production}"
                        step.goto_state = goto_state
                        self.parse_steps.append(step)
                    else:
                        error_msg = f"GOTO表中未找到状态{stack[-1]}和符号{production.left}的转换"
                        return False, self.parse_steps, error_msg
                else:
                    error_msg = "栈为空，无法执行GOTO操作"
                    return False, self.parse_steps, error_msg

            elif action.action_type == ActionType.ACCEPT:
                # 接受动作
                step.action = "接受"
                self.parse_steps.append(step)
                return True, self.parse_steps, "分析成功"

            else:
                # 错误动作
                error_msg = f"在状态{current_state}遇到符号'{current_symbol}'时发生语法错误"
                step.action = f"错误: {error_msg}"
                self.parse_steps.append(step)
                return False, self.parse_steps, error_msg

    def _tokenize(self, input_string: str) -> List[str]:
        """
        简单的词法分析器，将输入字符串分割为符号序列
        """
        if not input_string.strip():
            return []

        # 简单的分词：按空格分割，同时处理括号
        tokens = []
        current_token = ""

        for char in input_string:
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            elif char in "()":
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens

# ==================== GUI应用程序 ====================

class LR1ParserGUI:
    """LR(1)语法分析器GUI应用程序"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LR(1)完整的语法分析方法 - GUI版本")
        self.root.geometry("1600x1000")

        # 初始化组件
        self.current_grammar: Optional[Grammar] = None
        self.current_parser: Optional[LR1Parser] = None

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 文法输入标签页
        self.create_grammar_tab(notebook)

        # LR(1)分析表标签页
        self.create_parsing_table_tab(notebook)

        # 语法分析过程标签页
        self.create_parsing_process_tab(notebook)

        # 自动机可视化标签页
        self.create_visualization_tab(notebook)

        # 帮助标签页
        self.create_help_tab(notebook)

    def create_grammar_tab(self, parent):
        """创建文法输入标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="文法输入")

        # 左侧输入区域
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="输入上下文无关文法:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 文法输入说明
        info_frame = ttk.LabelFrame(left_frame, text="输入格式说明")
        info_frame.pack(fill=tk.X, pady=(5, 10))

        info_text = tk.Text(info_frame, height=4, font=("Consolas", 9))
        info_text.pack(fill=tk.X, padx=5, pady=5)
        info_text.insert(tk.END, "格式: 左部 -> 右部\n")
        info_text.insert(tk.END, "示例: E -> E + T | T\n")
        info_text.insert(tk.END, "     T -> T * F | F\n")
        info_text.insert(tk.END, "     F -> ( E ) | id\n")
        info_text.config(state=tk.DISABLED)

        self.grammar_input = scrolledtext.ScrolledText(left_frame, height=15, font=("Consolas", 10))
        self.grammar_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 示例文法
        sample_grammar = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
        self.grammar_input.insert(tk.END, sample_grammar)

        # 开始符号输入
        start_frame = ttk.Frame(left_frame)
        start_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(start_frame, text="开始符号:").pack(side=tk.LEFT)
        self.start_symbol_var = tk.StringVar(value="E")
        start_entry = ttk.Entry(start_frame, textvariable=self.start_symbol_var, width=10)
        start_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="解析文法", command=self.parse_grammar).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="构建分析器", command=self.build_parser).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空", command=self.clear_grammar).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="加载文件", command=self.load_grammar_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存文法", command=self.save_grammar).pack(side=tk.LEFT)

        # 右侧文法信息区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="文法信息:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 文法信息显示
        self.grammar_info = scrolledtext.ScrolledText(right_frame, height=20, font=("Consolas", 9))
        self.grammar_info.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_parsing_table_tab(self, parent):
        """创建LR(1)分析表标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="LR(1)分析表")

        # 上方控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="生成分析表", command=self.generate_parsing_table).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="保存分析表", command=self.save_parsing_table).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="检查冲突", command=self.check_conflicts).pack(side=tk.LEFT)

        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 上方分析表区域
        table_frame = ttk.Frame(paned_window)
        paned_window.add(table_frame, weight=3)

        ttk.Label(table_frame, text="LR(1)分析表:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 分析表显示
        self.parsing_table_text = scrolledtext.ScrolledText(table_frame, font=("Consolas", 8))
        self.parsing_table_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 下方冲突信息区域
        conflict_frame = ttk.Frame(paned_window)
        paned_window.add(conflict_frame, weight=1)

        ttk.Label(conflict_frame, text="冲突信息:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        self.conflict_info = scrolledtext.ScrolledText(conflict_frame, height=8, font=("Consolas", 9))
        self.conflict_info.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_parsing_process_tab(self, parent):
        """创建语法分析过程标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="语法分析过程")

        # 上方输入区域
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="输入串:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        self.input_string_var = tk.StringVar(value="id + id * id")
        input_entry = ttk.Entry(input_frame, textvariable=self.input_string_var, width=30, font=("Consolas", 10))
        input_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(input_frame, text="开始分析", command=self.start_parsing).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="清空结果", command=self.clear_parsing_result).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="保存分析过程", command=self.save_parsing_process).pack(side=tk.LEFT)

        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧分析步骤区域
        steps_frame = ttk.Frame(paned_window)
        paned_window.add(steps_frame, weight=2)

        ttk.Label(steps_frame, text="分析步骤:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 分析步骤表格
        columns = ("步骤", "栈", "输入", "动作")
        self.steps_tree = ttk.Treeview(steps_frame, columns=columns, show="headings", height=15)

        # 设置列宽
        self.steps_tree.column("步骤", width=50)
        self.steps_tree.column("栈", width=150)
        self.steps_tree.column("输入", width=100)
        self.steps_tree.column("动作", width=200)

        for col in columns:
            self.steps_tree.heading(col, text=col)

        # 添加滚动条
        steps_scrollbar = ttk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=self.steps_tree.yview)
        self.steps_tree.configure(yscrollcommand=steps_scrollbar.set)

        steps_tree_frame = ttk.Frame(steps_frame)
        steps_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        self.steps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧结果信息区域
        result_frame = ttk.Frame(paned_window)
        paned_window.add(result_frame, weight=1)

        ttk.Label(result_frame, text="分析结果:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 结果状态
        self.result_status = ttk.Label(result_frame, text="未开始分析", font=("Arial", 11))
        self.result_status.pack(anchor=tk.W, pady=(5, 10))

        # 详细信息
        ttk.Label(result_frame, text="详细信息:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.result_detail = scrolledtext.ScrolledText(result_frame, height=20, font=("Consolas", 9))
        self.result_detail.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_visualization_tab(self, parent):
        """创建自动机可视化标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="自动机可视化")

        # 控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="生成LR(1)自动机", command=self.generate_automaton_visualization).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="保存图片", command=self.save_visualization).pack(side=tk.LEFT, padx=(0, 10))

        # 状态选择
        ttk.Label(control_frame, text="选择状态:").pack(side=tk.LEFT, padx=(20, 5))
        self.state_var = tk.StringVar()
        self.state_combo = ttk.Combobox(control_frame, textvariable=self.state_var,
                                       state="readonly", width=10)
        self.state_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.state_combo.bind('<<ComboboxSelected>>', self.on_state_selected)

        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧可视化区域
        viz_frame = ttk.Frame(paned_window)
        paned_window.add(viz_frame, weight=2)

        # 可视化区域
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 右侧状态详情区域
        detail_frame = ttk.Frame(paned_window)
        paned_window.add(detail_frame, weight=1)

        ttk.Label(detail_frame, text="状态详情:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.state_detail = scrolledtext.ScrolledText(detail_frame, font=("Consolas", 9))
        self.state_detail.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_help_tab(self, parent):
        """创建帮助标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="帮助")

        help_text = scrolledtext.ScrolledText(frame, font=("Consolas", 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_content = """
=== LR(1)完整的语法分析方法 ===

本程序实现了LR(1)完整的语法分析方法，包括：
• 上下文无关文法的识别和拓广
• LR(0)识别活前缀的状态机构建
• LR(1)判断；LR(1)识别活前缀的状态机
• LR(1)分析表的构建
• 完整的LR分析过程

=== 使用说明 ===

1. 文法输入
   • 在"文法输入"标签页中输入上下文无关文法
   • 格式：左部 -> 右部1 | 右部2 | ...
   • 示例：E -> E + T | T
   • 设置开始符号
   • 点击"解析文法"按钮解析文法
   • 点击"构建分析器"按钮构建LR(1)分析器

2. LR(1)分析表
   • 在"LR(1)分析表"标签页中查看生成的分析表
   • 点击"生成分析表"查看ACTION和GOTO表
   • 点击"检查冲突"查看是否存在移进-归约或归约-归约冲突
   • 可保存分析表到文件

3. 语法分析过程
   • 在"语法分析过程"标签页中输入要分析的字符串
   • 点击"开始分析"执行LR(1)语法分析
   • 查看详细的分析步骤，包括栈状态、输入缓冲区和执行的动作
   • 查看分析结果（成功/失败）和错误信息

4. 自动机可视化
   • 在"自动机可视化"标签页中查看LR(1)自动机的状态转换图
   • 点击"生成LR(1)自动机"生成可视化图形
   • 选择特定状态查看状态详情
   • 可保存图片

=== 文法格式 ===
• 非终结符：大写字母开头
• 终结符：小写字母、符号
• 空串：ε 或 epsilon
• 产生式分隔：|
• 每行一个产生式左部

=== LR(1)分析原理 ===
1. 文法拓广：添加新开始符号S' -> S
2. 构建LR(1)项目集族（状态机）
3. 构建LR(1)分析表：
   • ACTION表：移进、归约、接受、错误动作
   • GOTO表：非终结符的状态转换
4. 使用栈进行语法分析：
   • 移进：将输入符号和新状态压栈
   • 归约：弹栈并查找GOTO状态
   • 接受：分析成功
   • 错误：语法错误

=== LR(1)与SLR(1)的区别 ===
• LR(1)：每个项目都有精确的向前看符号
• SLR(1)：使用FOLLOW集合决定归约动作
• LR(1)比SLR(1)更强大，能处理更多的文法
• LR(1)产生的冲突更少，但状态数量可能更多

=== 冲突处理 ===
• 移进-归约冲突：使用向前看符号精确解决
• 归约-归约冲突：选择产生式编号较小的
• 如果存在冲突，文法不是LR(1)文法

=== 注意事项 ===
• 程序支持UTF-8编码的文本文件
• 文法必须是上下文无关文法
• 建议先检查文法是否为LR(1)文法
• 大型自动机的可视化可能需要较长时间

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

    # ==================== 事件处理方法 ====================

    def parse_grammar(self):
        """解析文法"""
        grammar_text = self.grammar_input.get(1.0, tk.END).strip()
        start_symbol = self.start_symbol_var.get().strip()

        if not grammar_text:
            messagebox.showwarning("警告", "请输入文法")
            return

        if not start_symbol:
            messagebox.showwarning("警告", "请输入开始符号")
            return

        try:
            # 创建新文法
            grammar = Grammar()
            grammar.set_start_symbol(start_symbol)

            # 解析产生式
            lines = grammar_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '->' not in line:
                    continue

                parts = line.split('->')
                if len(parts) != 2:
                    continue

                left = parts[0].strip()
                right_part = parts[1].strip()

                # 处理多个右部（用|分隔）
                alternatives = [alt.strip() for alt in right_part.split('|')]

                for alt in alternatives:
                    if alt == 'ε' or alt == 'epsilon' or alt == '':
                        right = ['ε']
                    else:
                        # 简单的符号分割（按空格）
                        right = alt.split()

                    grammar.add_production(left, right)

            if not grammar.productions:
                messagebox.showerror("错误", "未找到有效的产生式")
                return

            # 计算FIRST和FOLLOW集合
            grammar.compute_first_sets()
            grammar.compute_follow_sets()

            self.current_grammar = grammar

            # 显示文法信息
            self.display_grammar_info(grammar)

            messagebox.showinfo("成功", "文法解析成功")

        except Exception as e:
            messagebox.showerror("错误", f"文法解析失败: {e}")

    def build_parser(self):
        """构建LR(1)分析器"""
        if not self.current_grammar:
            messagebox.showwarning("警告", "请先解析文法")
            return

        try:
            # 创建LR(1)分析器
            self.current_parser = LR1Parser(self.current_grammar)
            self.current_parser.build_parser()

            # 检查是否有冲突
            if self.current_parser.parsing_table.has_conflicts():
                conflicts = self.current_parser.parsing_table.get_conflicts()
                conflict_msg = "构建成功，但存在冲突:\n" + "\n".join(conflicts[:5])
                if len(conflicts) > 5:
                    conflict_msg += f"\n... 还有{len(conflicts) - 5}个冲突"
                messagebox.showwarning("警告", conflict_msg)
            else:
                messagebox.showinfo("成功", "LR(1)分析器构建成功，无冲突")

            # 更新状态选择框
            self.update_state_combo()

        except Exception as e:
            messagebox.showerror("错误", f"分析器构建失败: {e}")

    def display_grammar_info(self, grammar: Grammar):
        """显示文法信息"""
        self.grammar_info.delete(1.0, tk.END)

        info = f"开始符号: {grammar.start_symbol}\n\n"

        info += "产生式:\n"
        for i, prod in enumerate(grammar.productions):
            info += f"  {i}: {prod}\n"

        info += f"\n非终结符: {', '.join(sorted(grammar.nonterminals))}\n"
        info += f"终结符: {', '.join(sorted(grammar.terminals))}\n\n"

        info += "FIRST集合:\n"
        for symbol in sorted(grammar.nonterminals):
            first_set = grammar.first_sets.get(symbol, set())
            info += f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}\n"

        info += "\nFOLLOW集合:\n"
        for symbol in sorted(grammar.nonterminals):
            follow_set = grammar.follow_sets.get(symbol, set())
            info += f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}\n"

        self.grammar_info.insert(tk.END, info)

    def generate_parsing_table(self):
        """生成分析表"""
        if not self.current_parser:
            messagebox.showwarning("警告", "请先构建分析器")
            return

        try:
            # 显示分析表
            table_str = self.current_parser.parsing_table.print_table()
            self.parsing_table_text.delete(1.0, tk.END)
            self.parsing_table_text.insert(tk.END, table_str)

            messagebox.showinfo("成功", "分析表生成完成")

        except Exception as e:
            messagebox.showerror("错误", f"分析表生成失败: {e}")

    def check_conflicts(self):
        """检查冲突"""
        if not self.current_parser:
            messagebox.showwarning("警告", "请先构建分析器")
            return

        conflicts = self.current_parser.parsing_table.get_conflicts()

        self.conflict_info.delete(1.0, tk.END)

        if conflicts:
            self.conflict_info.insert(tk.END, f"发现 {len(conflicts)} 个冲突:\n\n")
            for i, conflict in enumerate(conflicts, 1):
                self.conflict_info.insert(tk.END, f"{i}. {conflict}\n")
        else:
            self.conflict_info.insert(tk.END, "无冲突，文法是LR(1)文法")

    def start_parsing(self):
        """开始语法分析"""
        if not self.current_parser:
            messagebox.showwarning("警告", "请先构建分析器")
            return

        input_string = self.input_string_var.get().strip()
        if not input_string:
            messagebox.showwarning("警告", "请输入要分析的字符串")
            return

        try:
            # 执行语法分析
            success, steps, message = self.current_parser.parse(input_string)

            # 清空之前的结果
            for item in self.steps_tree.get_children():
                self.steps_tree.delete(item)

            # 显示分析步骤
            for step in steps:
                stack_str = ' '.join(str(s) for s in step.stack)
                self.steps_tree.insert("", tk.END, values=(
                    step.step, stack_str, step.input_buffer, step.action
                ))

            # 显示结果状态
            if success:
                self.result_status.config(text="✓ 分析成功", foreground="green")
            else:
                self.result_status.config(text="✗ 分析失败", foreground="red")

            # 显示详细信息
            self.result_detail.delete(1.0, tk.END)
            self.result_detail.insert(tk.END, f"输入串: {input_string}\n")
            self.result_detail.insert(tk.END, f"结果: {message}\n\n")

            if success:
                self.result_detail.insert(tk.END, "分析成功！输入串符合文法。\n\n")
            else:
                self.result_detail.insert(tk.END, f"分析失败: {message}\n\n")

            self.result_detail.insert(tk.END, f"总步骤数: {len(steps)}\n")

            if not success and steps:
                last_step = steps[-1]
                self.result_detail.insert(tk.END, f"错误位置: 步骤 {last_step.step}\n")
                self.result_detail.insert(tk.END, f"错误状态: {last_step.stack[-1] if last_step.stack else '空栈'}\n")

        except Exception as e:
            messagebox.showerror("错误", f"语法分析失败: {e}")

    def clear_parsing_result(self):
        """清空分析结果"""
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)

        self.result_status.config(text="未开始分析", foreground="black")
        self.result_detail.delete(1.0, tk.END)

    def generate_automaton_visualization(self):
        """生成自动机可视化"""
        if not self.current_parser:
            messagebox.showwarning("警告", "请先构建分析器")
            return

        try:
            self.ax.clear()
            self._draw_lr1_automaton()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("错误", f"可视化生成失败: {e}")

    def _draw_lr1_automaton(self):
        """绘制LR(1)自动机"""
        G = nx.DiGraph()

        # 添加状态节点
        for i, state in enumerate(self.current_parser.automaton.states):
            # 检查是否为接受状态
            is_accept = any(item.is_complete() and item.production.index == 0 for item in state)
            node_color = 'lightgreen' if is_accept else 'lightblue'
            if i == 0:
                node_color = 'yellow'  # 开始状态

            G.add_node(i, color=node_color)

        # 添加转换边
        edge_labels = {}
        for (from_state, symbol), to_state in self.current_parser.automaton.transitions.items():
            edge_key = (from_state, to_state)
            if edge_key in edge_labels:
                edge_labels[edge_key] += f", {symbol}"
            else:
                edge_labels[edge_key] = symbol
                G.add_edge(from_state, to_state)

        # 绘制图形
        pos = nx.spring_layout(G, k=3, iterations=50)

        # 绘制节点
        node_colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, ax=self.ax)

        # 绘制边
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=self.ax)

        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=self.ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=self.ax)

        self.ax.set_title("LR(1)自动机状态转换图", fontsize=14, fontweight='bold')
        self.ax.axis('off')

    def update_state_combo(self):
        """更新状态选择框"""
        if self.current_parser:
            state_count = len(self.current_parser.automaton.states)
            state_values = [f"状态{i}" for i in range(state_count)]
            self.state_combo['values'] = state_values

    def on_state_selected(self, event):
        """状态选择事件处理"""
        if not self.current_parser:
            return

        selection = self.state_var.get()
        if not selection:
            return

        try:
            state_index = int(selection.replace("状态", ""))
            state = self.current_parser.automaton.states[state_index]

            # 显示状态详情
            self.state_detail.delete(1.0, tk.END)

            detail = f"状态 {state_index}:\n\n"
            detail += "项目集:\n"

            for item in state:
                detail += f"  {item}\n"

            # 显示转换
            detail += "\n转换:\n"
            for (from_state, symbol), to_state in self.current_parser.automaton.transitions.items():
                if from_state == state_index:
                    detail += f"  {symbol} -> 状态{to_state}\n"

            self.state_detail.insert(tk.END, detail)

        except (ValueError, IndexError):
            pass

    def clear_grammar(self):
        """清空文法输入"""
        self.grammar_input.delete(1.0, tk.END)
        self.grammar_info.delete(1.0, tk.END)
        self.start_symbol_var.set("")

        # 清空其他结果
        self.parsing_table_text.delete(1.0, tk.END)
        self.conflict_info.delete(1.0, tk.END)
        self.clear_parsing_result()
        self.state_detail.delete(1.0, tk.END)

        self.current_grammar = None
        self.current_parser = None
        self.state_combo['values'] = []

    def load_grammar_file(self):
        """加载文法文件"""
        filename = filedialog.askopenfilename(
            title="选择文法文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.grammar_input.delete(1.0, tk.END)
                self.grammar_input.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("错误", f"无法加载文件: {e}")

    def save_grammar(self):
        """保存文法"""
        filename = filedialog.asksaveasfilename(
            title="保存文法",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            try:
                content = self.grammar_input.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", "文法已保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")

    def save_parsing_table(self):
        """保存分析表"""
        if not self.current_parser:
            messagebox.showwarning("警告", "没有分析表可保存")
            return

        filename = filedialog.asksaveasfilename(
            title="保存分析表",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            try:
                table_content = self.current_parser.parsing_table.print_table()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("LR(1)分析表\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(table_content)

                    # 添加冲突信息
                    conflicts = self.current_parser.parsing_table.get_conflicts()
                    if conflicts:
                        f.write("\n\n冲突信息:\n")
                        f.write("-" * 30 + "\n")
                        for i, conflict in enumerate(conflicts, 1):
                            f.write(f"{i}. {conflict}\n")
                    else:
                        f.write("\n\n无冲突，文法是LR(1)文法\n")

                messagebox.showinfo("成功", "分析表已保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")

    def save_parsing_process(self):
        """保存分析过程"""
        if not self.current_parser or not hasattr(self.current_parser, 'parse_steps'):
            messagebox.showwarning("警告", "没有分析过程可保存")
            return

        filename = filedialog.asksaveasfilename(
            title="保存分析过程",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("LR(1)语法分析过程\n")
                    f.write("=" * 50 + "\n\n")

                    input_string = self.input_string_var.get()
                    f.write(f"输入串: {input_string}\n\n")

                    f.write("分析步骤:\n")
                    f.write("-" * 80 + "\n")
                    f.write("步骤 | 栈                   | 输入            | 动作\n")
                    f.write("-" * 80 + "\n")

                    for step in self.current_parser.parse_steps:
                        f.write(str(step) + "\n")

                messagebox.showinfo("成功", "分析过程已保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {e}")

    def save_visualization(self):
        """保存可视化图片"""
        filename = filedialog.asksaveasfilename(
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
        self.root.bind('<Control-o>', lambda e: self.load_grammar_file())
        self.root.bind('<Control-s>', lambda e: self.save_parsing_process())
        self.root.bind('<F5>', lambda e: self.start_parsing())
        self.root.bind('<Control-l>', lambda e: self.clear_grammar())

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
        app = LR1ParserGUI()
        app.run()

    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
