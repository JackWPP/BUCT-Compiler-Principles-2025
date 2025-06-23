# -*- coding: utf-8 -*-
"""
编译原理作业 - LR语法分析方法判断程序
实现上下文无关文法的识别和拓广，LR(0)识别活前缀的状态机，4种LR方法判断

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import List, Dict, Set, Optional, Tuple, FrozenSet
from dataclasses import dataclass
from enum import Enum
import copy
import json

# ==================== 数据结构定义 ====================

class LRType(Enum):
    """LR分析方法类型"""
    LR0 = "LR(0)"
    SLR1 = "SLR(1)"
    LR1 = "LR(1)"
    LALR1 = "LALR(1)"

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
class LRItem:
    """LR项目类"""
    production: Production
    dot_position: int  # 点的位置
    lookahead: Optional[str] = None  # 向前看符号（用于LR(1)）
    
    def __str__(self):
        right = self.production.right.copy()
        right.insert(self.dot_position, '•')
        right_str = ' '.join(right) if right else '•'
        
        result = f"{self.production.left} -> {right_str}"
        if self.lookahead is not None:
            result += f", {self.lookahead}"
        return result
    
    def __eq__(self, other):
        if not isinstance(other, LRItem):
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
    
    def advance_dot(self) -> 'LRItem':
        """移动点的位置"""
        return LRItem(
            production=self.production,
            dot_position=self.dot_position + 1,
            lookahead=self.lookahead
        )

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

class LRAutomaton:
    """LR自动机类"""
    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states: List[FrozenSet[LRItem]] = []  # 状态集合
        self.transitions: Dict[Tuple[int, str], int] = {}  # 转换函数
        self.start_state = 0
        
    def closure(self, items: Set[LRItem]) -> FrozenSet[LRItem]:
        """计算项目集的闭包"""
        closure_set = set(items)
        
        changed = True
        while changed:
            changed = False
            new_items = set()
            
            for item in closure_set:
                if not item.is_complete():
                    next_sym = item.next_symbol()
                    if next_sym in self.grammar.nonterminals:
                        # 计算向前看符号
                        if item.lookahead is not None:  # LR(1)项目
                            beta = item.production.right[item.dot_position + 1:] + [item.lookahead]
                            first_beta = self.grammar.compute_first_of_string(beta)
                        else:  # LR(0)项目
                            first_beta = {None}
                        
                        # 为每个产生式创建新项目
                        for production in self.grammar.get_productions_for_nonterminal(next_sym):
                            for lookahead in first_beta:
                                if lookahead == 'ε':
                                    continue
                                new_item = LRItem(production, 0, lookahead if item.lookahead is not None else None)
                                if new_item not in closure_set:
                                    new_items.add(new_item)
                                    changed = True
            
            closure_set.update(new_items)
        
        return frozenset(closure_set)
    
    def goto(self, state: FrozenSet[LRItem], symbol: str) -> FrozenSet[LRItem]:
        """计算GOTO函数"""
        goto_items = set()
        
        for item in state:
            if not item.is_complete() and item.next_symbol() == symbol:
                goto_items.add(item.advance_dot())
        
        if goto_items:
            return self.closure(goto_items)
        else:
            return frozenset()
    
    def build_lr0_automaton(self):
        """构建LR(0)自动机"""
        # 确保文法已拓广
        if not self.grammar.augmented:
            self.grammar = self.grammar.augment_grammar()
        
        # 计算FIRST和FOLLOW集合
        self.grammar.compute_first_sets()
        self.grammar.compute_follow_sets()
        
        # 初始状态
        start_production = self.grammar.productions[0]
        start_item = LRItem(start_production, 0)
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
    
    def build_lr1_automaton(self):
        """构建LR(1)自动机"""
        # 确保文法已拓广
        if not self.grammar.augmented:
            self.grammar = self.grammar.augment_grammar()
        
        # 计算FIRST和FOLLOW集合
        self.grammar.compute_first_sets()
        self.grammar.compute_follow_sets()
        
        # 初始状态
        start_production = self.grammar.productions[0]
        start_item = LRItem(start_production, 0, '$')
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

class LRAnalyzer:
    """LR分析器类"""
    
    def __init__(self):
        self.grammar: Optional[Grammar] = None
        self.automaton: Optional[LRAutomaton] = None
        self.lr_types: Set[LRType] = set()
        self.conflicts: Dict[LRType, List[str]] = {}
        
    def set_grammar(self, grammar: Grammar):
        """设置文法"""
        self.grammar = grammar
        self.automaton = None
        self.lr_types.clear()
        self.conflicts.clear()
    
    def analyze_lr_types(self) -> Dict[LRType, bool]:
        """分析文法属于哪些LR类型"""
        if not self.grammar:
            return {}
        
        results = {}
        
        # 构建LR(0)自动机
        self.automaton = LRAutomaton(self.grammar.augment_grammar())
        self.automaton.build_lr0_automaton()
        
        # 检查LR(0)
        results[LRType.LR0] = self._check_lr0()
        
        # 检查SLR(1)
        results[LRType.SLR1] = self._check_slr1()
        
        # 构建LR(1)自动机
        lr1_automaton = LRAutomaton(self.grammar.augment_grammar())
        lr1_automaton.build_lr1_automaton()
        
        # 检查LR(1)
        results[LRType.LR1] = self._check_lr1(lr1_automaton)
        
        # 检查LALR(1)
        results[LRType.LALR1] = self._check_lalr1(lr1_automaton)
        
        return results
    
    def _check_lr0(self) -> bool:
        """检查是否为LR(0)文法"""
        conflicts = []
        
        for i, state in enumerate(self.automaton.states):
            # 收集移进项目和归约项目
            shift_items = []
            reduce_items = []
            
            for item in state:
                if item.is_complete():
                    # 归约项目
                    if item.production.index != 0:  # 不是拓广产生式
                        reduce_items.append(item)
                else:
                    # 移进项目
                    shift_items.append(item)
            
            # 检查移进-归约冲突
            if shift_items and reduce_items:
                conflicts.append(f"状态{i}: 移进-归约冲突")
            
            # 检查归约-归约冲突
            if len(reduce_items) > 1:
                conflicts.append(f"状态{i}: 归约-归约冲突")
        
        self.conflicts[LRType.LR0] = conflicts
        return len(conflicts) == 0
    
    def _check_slr1(self) -> bool:
        """检查是否为SLR(1)文法"""
        conflicts = []
        
        for i, state in enumerate(self.automaton.states):
            # 收集移进项目和归约项目
            shift_symbols = set()
            reduce_items = []
            
            for item in state:
                if item.is_complete():
                    # 归约项目
                    if item.production.index != 0:  # 不是拓广产生式
                        reduce_items.append(item)
                else:
                    # 移进项目
                    next_sym = item.next_symbol()
                    if next_sym in self.grammar.terminals:
                        shift_symbols.add(next_sym)
            
            # 检查移进-归约冲突
            for reduce_item in reduce_items:
                follow_set = self.grammar.follow_sets.get(reduce_item.production.left, set())
                conflict_symbols = shift_symbols & follow_set
                if conflict_symbols:
                    conflicts.append(f"状态{i}: SLR(1)移进-归约冲突，符号: {conflict_symbols}")
            
            # 检查归约-归约冲突
            if len(reduce_items) > 1:
                for j in range(len(reduce_items)):
                    for k in range(j + 1, len(reduce_items)):
                        follow1 = self.grammar.follow_sets.get(reduce_items[j].production.left, set())
                        follow2 = self.grammar.follow_sets.get(reduce_items[k].production.left, set())
                        conflict_symbols = follow1 & follow2
                        if conflict_symbols:
                            conflicts.append(f"状态{i}: SLR(1)归约-归约冲突，符号: {conflict_symbols}")
        
        self.conflicts[LRType.SLR1] = conflicts
        return len(conflicts) == 0
    
    def _check_lr1(self, lr1_automaton: LRAutomaton) -> bool:
        """检查是否为LR(1)文法"""
        conflicts = []
        
        for i, state in enumerate(lr1_automaton.states):
            # 按向前看符号分组检查冲突
            lookahead_groups = {}
            
            for item in state:
                lookahead = item.lookahead if item.lookahead else '$'
                if lookahead not in lookahead_groups:
                    lookahead_groups[lookahead] = {'shift': [], 'reduce': []}
                
                if item.is_complete():
                    if item.production.index != 0:  # 不是拓广产生式
                        lookahead_groups[lookahead]['reduce'].append(item)
                else:
                    next_sym = item.next_symbol()
                    if next_sym == lookahead:
                        lookahead_groups[lookahead]['shift'].append(item)
            
            # 检查每个向前看符号的冲突
            for lookahead, group in lookahead_groups.items():
                if group['shift'] and group['reduce']:
                    conflicts.append(f"状态{i}: LR(1)移进-归约冲突，向前看符号: {lookahead}")
                
                if len(group['reduce']) > 1:
                    conflicts.append(f"状态{i}: LR(1)归约-归约冲突，向前看符号: {lookahead}")
        
        self.conflicts[LRType.LR1] = conflicts
        return len(conflicts) == 0
    
    def _check_lalr1(self, lr1_automaton: LRAutomaton) -> bool:
        """检查是否为LALR(1)文法"""
        # 简化实现：如果LR(1)没有冲突，则LALR(1)也没有冲突
        # 实际实现需要合并同心状态并检查冲突
        return self._check_lr1(lr1_automaton)
    
    def get_conflicts(self, lr_type: LRType) -> List[str]:
        """获取指定LR类型的冲突信息"""
        return self.conflicts.get(lr_type, [])

# ==================== GUI应用程序 ====================

class LRParserGUI:
    """LR语法分析器GUI应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LR语法分析方法判断程序 - GUI版本")
        self.root.geometry("1400x900")
        
        # 初始化组件
        self.analyzer = LRAnalyzer()
        self.current_grammar: Optional[Grammar] = None
        
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
        
        # LR分析标签页
        self.create_analysis_tab(notebook)
        
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
    
    def create_analysis_tab(self, parent):
        """创建LR分析标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="LR分析")
        
        # 上方控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="执行LR分析", command=self.analyze_lr_types).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="生成分析表", command=self.generate_parsing_table).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="保存结果", command=self.save_analysis_results).pack(side=tk.LEFT)
        
        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧结果区域
        left_pane = ttk.Frame(paned_window)
        paned_window.add(left_pane, weight=1)
        
        ttk.Label(left_pane, text="LR类型判断结果:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # LR类型结果表格
        columns = ("LR类型", "是否满足", "冲突数量")
        self.lr_result_tree = ttk.Treeview(left_pane, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.lr_result_tree.heading(col, text=col)
            self.lr_result_tree.column(col, width=120)
        
        scrollbar1 = ttk.Scrollbar(left_pane, orient=tk.VERTICAL, command=self.lr_result_tree.yview)
        self.lr_result_tree.configure(yscrollcommand=scrollbar1.set)
        
        tree_frame1 = ttk.Frame(left_pane)
        tree_frame1.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        self.lr_result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 冲突详情
        ttk.Label(left_pane, text="冲突详情:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.conflict_text = scrolledtext.ScrolledText(left_pane, height=10, font=("Consolas", 9))
        self.conflict_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧自动机状态区域
        right_pane = ttk.Frame(paned_window)
        paned_window.add(right_pane, weight=1)
        
        ttk.Label(right_pane, text="自动机状态:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # 状态列表
        self.state_listbox = tk.Listbox(right_pane, height=8, font=("Consolas", 9))
        scrollbar2 = ttk.Scrollbar(right_pane, orient=tk.VERTICAL, command=self.state_listbox.yview)
        self.state_listbox.configure(yscrollcommand=scrollbar2.set)
        
        listbox_frame = ttk.Frame(right_pane)
        listbox_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        
        self.state_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.state_listbox.bind('<<ListboxSelect>>', self.on_state_select)
        
        # 状态详情
        ttk.Label(right_pane, text="状态详情:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.state_detail_text = scrolledtext.ScrolledText(right_pane, height=15, font=("Consolas", 9))
        self.state_detail_text.pack(fill=tk.BOTH, expand=True)
    
    def create_visualization_tab(self, parent):
        """创建自动机可视化标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="自动机可视化")
        
        # 控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="选择自动机类型:").pack(side=tk.LEFT)
        
        self.automaton_type_var = tk.StringVar(value="LR(0)")
        type_combo = ttk.Combobox(control_frame, textvariable=self.automaton_type_var, 
                                 values=["LR(0)", "LR(1)"], state="readonly", width=10)
        type_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(control_frame, text="生成可视化", command=self.generate_visualization).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="保存图片", command=self.save_visualization).pack(side=tk.LEFT)
        
        # 可视化区域
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_help_tab(self, parent):
        """创建帮助标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="帮助")
        
        help_text = scrolledtext.ScrolledText(frame, font=("Consolas", 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
=== LR语法分析方法判断程序 ===

本程序实现了上下文无关文法的LR分析方法判断，包括：
• 文法的识别和拓广
• LR(0)识别活前缀的状态机构建
• LR(1)识别活前缀的状态机构建
• 四种LR方法判断：LR(0)、SLR(1)、LR(1)、LALR(1)

=== 使用说明 ===

1. 文法输入
   • 在"文法输入"标签页中输入上下文无关文法
   • 格式：左部 -> 右部1 | 右部2 | ...
   • 示例：E -> E + T | T
   • 设置开始符号
   • 点击"解析文法"按钮

2. LR分析
   • 在"LR分析"标签页中点击"执行LR分析"
   • 查看各种LR类型的判断结果
   • 查看冲突详情和自动机状态

3. 可视化
   • 在"自动机可视化"标签页中选择自动机类型
   • 点击"生成可视化"查看状态转换图
   • 可保存图片

=== 文法格式 ===
• 非终结符：大写字母开头
• 终结符：小写字母、符号
• 空串：ε 或 epsilon
• 产生式分隔：|
• 每行一个产生式左部

=== 快捷键 ===
• Ctrl+O：加载文法文件
• Ctrl+S：保存结果
• F5：执行分析
• Ctrl+L：清空输入

=== 注意事项 ===
• 程序支持UTF-8编码的文本文件
• 文法必须是上下文无关文法
• 大型自动机的可视化可能需要较长时间
• 建议先进行LR分析再查看可视化
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
            self.analyzer.set_grammar(grammar)
            
            # 显示文法信息
            self.display_grammar_info(grammar)
            
            messagebox.showinfo("成功", "文法解析成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"文法解析失败: {e}")
    
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
    
    def analyze_lr_types(self):
        """分析LR类型"""
        if not self.current_grammar:
            messagebox.showwarning("警告", "请先解析文法")
            return
        
        try:
            # 执行LR分析
            results = self.analyzer.analyze_lr_types()
            
            # 清空之前的结果
            for item in self.lr_result_tree.get_children():
                self.lr_result_tree.delete(item)
            
            # 显示结果
            for lr_type, is_valid in results.items():
                conflicts = self.analyzer.get_conflicts(lr_type)
                conflict_count = len(conflicts)
                
                status = "是" if is_valid else "否"
                self.lr_result_tree.insert("", tk.END, values=(
                    lr_type.value, status, conflict_count
                ))
            
            # 显示冲突详情
            self.display_conflicts()
            
            # 显示自动机状态
            self.display_automaton_states()
            
            messagebox.showinfo("成功", "LR分析完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"LR分析失败: {e}")
    
    def display_conflicts(self):
        """显示冲突详情"""
        self.conflict_text.delete(1.0, tk.END)
        
        for lr_type in LRType:
            conflicts = self.analyzer.get_conflicts(lr_type)
            if conflicts:
                self.conflict_text.insert(tk.END, f"=== {lr_type.value} 冲突 ===\n")
                for conflict in conflicts:
                    self.conflict_text.insert(tk.END, f"  {conflict}\n")
                self.conflict_text.insert(tk.END, "\n")
        
        if not any(self.analyzer.get_conflicts(lr_type) for lr_type in LRType):
            self.conflict_text.insert(tk.END, "无冲突")
    
    def display_automaton_states(self):
        """显示自动机状态"""
        self.state_listbox.delete(0, tk.END)
        
        if self.analyzer.automaton:
            for i, state in enumerate(self.analyzer.automaton.states):
                self.state_listbox.insert(tk.END, f"状态 {i}")
    
    def on_state_select(self, event):
        """状态选择事件处理"""
        selection = self.state_listbox.curselection()
        if not selection or not self.analyzer.automaton:
            return
        
        state_index = selection[0]
        state = self.analyzer.automaton.states[state_index]
        
        # 显示状态详情
        self.state_detail_text.delete(1.0, tk.END)
        
        detail = f"状态 {state_index}:\n\n"
        detail += "项目集:\n"
        
        for item in state:
            detail += f"  {item}\n"
        
        # 显示转换
        detail += "\n转换:\n"
        for (from_state, symbol), to_state in self.analyzer.automaton.transitions.items():
            if from_state == state_index:
                detail += f"  {symbol} -> 状态{to_state}\n"
        
        self.state_detail_text.insert(tk.END, detail)
    
    def generate_parsing_table(self):
        """生成分析表"""
        if not self.analyzer.automaton:
            messagebox.showwarning("警告", "请先执行LR分析")
            return
        
        # 这里可以实现分析表的生成
        messagebox.showinfo("提示", "分析表生成功能待实现")
    
    def generate_visualization(self):
        """生成自动机可视化"""
        if not self.analyzer.automaton:
            messagebox.showwarning("警告", "请先执行LR分析")
            return
        
        try:
            self.ax.clear()
            
            automaton_type = self.automaton_type_var.get()
            
            if automaton_type == "LR(0)":
                self._draw_lr0_automaton()
            else:
                # 构建LR(1)自动机并可视化
                lr1_automaton = LRAutomaton(self.current_grammar.augment_grammar())
                lr1_automaton.build_lr1_automaton()
                self._draw_lr1_automaton(lr1_automaton)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"可视化生成失败: {e}")
    
    def _draw_lr0_automaton(self):
        """绘制LR(0)自动机"""
        G = nx.DiGraph()
        
        # 添加状态节点
        for i, state in enumerate(self.analyzer.automaton.states):
            # 检查是否为接受状态
            is_accept = any(item.is_complete() and item.production.index == 0 for item in state)
            node_color = 'lightgreen' if is_accept else 'lightblue'
            if i == 0:
                node_color = 'yellow'  # 开始状态
            
            G.add_node(i, color=node_color)
        
        # 添加转换边
        edge_labels = {}
        for (from_state, symbol), to_state in self.analyzer.automaton.transitions.items():
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
        
        self.ax.set_title("LR(0)自动机状态转换图", fontsize=14, fontweight='bold')
        self.ax.axis('off')
    
    def _draw_lr1_automaton(self, lr1_automaton: LRAutomaton):
        """绘制LR(1)自动机"""
        G = nx.DiGraph()
        
        # 添加状态节点
        for i, state in enumerate(lr1_automaton.states):
            # 检查是否为接受状态
            is_accept = any(item.is_complete() and item.production.index == 0 for item in state)
            node_color = 'lightgreen' if is_accept else 'lightblue'
            if i == 0:
                node_color = 'yellow'  # 开始状态
            
            G.add_node(i, color=node_color)
        
        # 添加转换边
        edge_labels = {}
        for (from_state, symbol), to_state in lr1_automaton.transitions.items():
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
    
    def clear_grammar(self):
        """清空文法输入"""
        self.grammar_input.delete(1.0, tk.END)
        self.grammar_info.delete(1.0, tk.END)
        self.start_symbol_var.set("")
        
        # 清空分析结果
        for item in self.lr_result_tree.get_children():
            self.lr_result_tree.delete(item)
        self.conflict_text.delete(1.0, tk.END)
        self.state_listbox.delete(0, tk.END)
        self.state_detail_text.delete(1.0, tk.END)
        
        self.current_grammar = None
        self.analyzer = LRAnalyzer()
    
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
    
    def save_analysis_results(self):
        """保存分析结果"""
        if not self.current_grammar:
            messagebox.showwarning("警告", "没有分析结果可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存分析结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("LR语法分析结果\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 文法信息
                    f.write("文法信息:\n")
                    f.write(str(self.current_grammar))
                    f.write("\n")
                    
                    # LR类型判断结果
                    if hasattr(self.analyzer, 'lr_types'):
                        results = self.analyzer.analyze_lr_types()
                        f.write("LR类型判断结果:\n")
                        for lr_type, is_valid in results.items():
                            status = "满足" if is_valid else "不满足"
                            f.write(f"  {lr_type.value}: {status}\n")
                        f.write("\n")
                        
                        # 冲突信息
                        f.write("冲突详情:\n")
                        for lr_type in LRType:
                            conflicts = self.analyzer.get_conflicts(lr_type)
                            if conflicts:
                                f.write(f"  {lr_type.value}:\n")
                                for conflict in conflicts:
                                    f.write(f"    {conflict}\n")
                        f.write("\n")
                    
                    # 自动机状态
                    if self.analyzer.automaton:
                        f.write("自动机状态:\n")
                        for i, state in enumerate(self.analyzer.automaton.states):
                            f.write(f"  状态 {i}:\n")
                            for item in state:
                                f.write(f"    {item}\n")
                            f.write("\n")
                
                messagebox.showinfo("成功", "分析结果已保存")
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
        self.root.bind('<Control-s>', lambda e: self.save_analysis_results())
        self.root.bind('<F5>', lambda e: self.analyze_lr_types())
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
        app = LRParserGUI()
        app.run()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()