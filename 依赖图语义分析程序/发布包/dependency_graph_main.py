# -*- coding: utf-8 -*-
"""
编译原理作业 - 依赖图语义分析程序
实现依赖图语义分析方法，包括依赖图构建、拓扑排序、属性计算等功能

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict, deque

# ==================== 数据结构定义 ====================

class 属性类型(Enum):
    """属性类型枚举"""
    综合属性 = "综合属性"    # 综合属性（由子节点计算得出）
    继承属性 = "继承属性"    # 继承属性（由父节点传递下来）

class 节点类型(Enum):
    """依赖图节点类型"""
    属性节点 = "属性节点"    # 表示一个属性实例
    虚拟节点 = "虚拟节点"    # 用于辅助计算的虚拟节点

@dataclass
class 属性定义:
    """属性定义类"""
    名称: str                    # 属性名称
    类型: 属性类型               # 属性类型（综合/继承）
    数据类型: str = "字符串"     # 数据类型
    默认值: Any = None           # 默认值
    描述: str = ""               # 属性描述

@dataclass
class 产生式:
    """产生式类"""
    左部: str                    # 产生式左部
    右部: List[str]              # 产生式右部
    编号: int = 0                # 产生式编号
    语义规则: List[str] = field(default_factory=list)  # 关联的语义规则

@dataclass
class 语义规则:
    """语义规则类"""
    目标属性: str                # 目标属性（如 E.val）
    表达式: str                  # 计算表达式
    依赖属性: List[str] = field(default_factory=list)  # 依赖的属性列表
    产生式编号: int = -1         # 关联的产生式编号
    动作类型: str = "赋值"       # 动作类型

@dataclass
class 依赖图节点:
    """依赖图节点类"""
    节点ID: str                  # 节点唯一标识
    属性名: str                  # 属性名称（如 E.val）
    节点类型: str = "属性节点"   # 节点类型
    属性值: Any = None           # 属性值
    已计算: bool = False         # 是否已计算
    计算表达式: str = ""         # 计算表达式
    依赖节点: List[str] = field(default_factory=list)  # 依赖的节点ID列表

@dataclass
class 分析步骤:
    """分析步骤记录类"""
    步骤号: int                  # 步骤编号
    操作类型: str                # 操作类型
    描述: str                    # 步骤描述
    节点信息: str = ""           # 相关节点信息
    计算结果: str = ""           # 计算结果

class 文法符号:
    """文法符号类"""
    
    def __init__(self, 名称: str, 是否终结符: bool = False):
        self.名称 = 名称
        self.是否终结符 = 是否终结符
        self.属性定义列表: List[属性定义] = []
    
    def 添加属性定义(self, 属性定义对象: 属性定义):
        """添加属性定义"""
        self.属性定义列表.append(属性定义对象)
    
    def 获取属性定义(self, 属性名: str) -> Optional[属性定义]:
        """获取指定属性的定义"""
        for 属性定义对象 in self.属性定义列表:
            if 属性定义对象.名称 == 属性名:
                return 属性定义对象
        return None

class 属性文法:
    """属性文法类"""
    
    def __init__(self):
        self.符号表: Dict[str, 文法符号] = {}
        self.产生式列表: List[产生式] = []
        self.语义规则表: Dict[int, List[语义规则]] = defaultdict(list)
        self.开始符号: str = ""
    
    def 添加符号(self, 符号名: str, 是否终结符: bool = False) -> 文法符号:
        """添加文法符号"""
        if 符号名 not in self.符号表:
            self.符号表[符号名] = 文法符号(符号名, 是否终结符)
        return self.符号表[符号名]
    
    def 添加产生式(self, 产生式对象: 产生式):
        """添加产生式"""
        产生式对象.编号 = len(self.产生式列表)
        self.产生式列表.append(产生式对象)
        
        # 自动添加符号到符号表
        self.添加符号(产生式对象.左部)
        for 符号 in 产生式对象.右部:
            if 符号 != "ε":  # 空产生式
                self.添加符号(符号)
    
    def 添加语义规则(self, 产生式编号: int, 语义规则对象: 语义规则):
        """为指定产生式添加语义规则"""
        语义规则对象.产生式编号 = 产生式编号
        self.语义规则表[产生式编号].append(语义规则对象)
    
    def 获取产生式(self, 编号: int) -> Optional[产生式]:
        """获取指定编号的产生式"""
        if 0 <= 编号 < len(self.产生式列表):
            return self.产生式列表[编号]
        return None
    
    def 获取语义规则(self, 产生式编号: int) -> List[语义规则]:
        """获取指定产生式的语义规则"""
        return self.语义规则表.get(产生式编号, [])

# ==================== 依赖图类 ====================

class 依赖图:
    """依赖图类 - 表示属性之间的依赖关系"""
    
    def __init__(self):
        self.节点表: Dict[str, 依赖图节点] = {}  # 节点ID -> 节点对象
        self.邻接表: Dict[str, List[str]] = defaultdict(list)  # 依赖关系：节点ID -> 依赖的节点ID列表
        self.反向邻接表: Dict[str, List[str]] = defaultdict(list)  # 反向依赖：节点ID -> 依赖它的节点ID列表
        self.计算顺序: List[str] = []  # 拓扑排序后的计算顺序
    
    def 添加节点(self, 节点: 依赖图节点):
        """添加节点到依赖图"""
        self.节点表[节点.节点ID] = 节点
    
    def 添加依赖边(self, 源节点ID: str, 目标节点ID: str):
        """添加依赖边：源节点依赖于目标节点"""
        if 目标节点ID not in self.邻接表[源节点ID]:
            self.邻接表[源节点ID].append(目标节点ID)
        if 源节点ID not in self.反向邻接表[目标节点ID]:
            self.反向邻接表[目标节点ID].append(源节点ID)
    
    def 检测循环依赖(self) -> Tuple[bool, List[str]]:
        """检测循环依赖"""
        颜色 = {}  # 0: 白色(未访问), 1: 灰色(正在访问), 2: 黑色(已完成)
        循环路径 = []
        
        def dfs(节点ID: str, 路径: List[str]) -> bool:
            if 节点ID in 颜色:
                if 颜色[节点ID] == 1:  # 发现循环
                    循环开始 = 路径.index(节点ID)
                    循环路径.extend(路径[循环开始:] + [节点ID])
                    return True
                elif 颜色[节点ID] == 2:  # 已完成的节点
                    return False
            
            颜色[节点ID] = 1  # 标记为正在访问
            路径.append(节点ID)
            
            for 依赖节点ID in self.邻接表[节点ID]:
                if dfs(依赖节点ID, 路径):
                    return True
            
            颜色[节点ID] = 2  # 标记为已完成
            路径.pop()
            return False
        
        for 节点ID in self.节点表:
            if 节点ID not in 颜色:
                if dfs(节点ID, []):
                    return True, 循环路径
        
        return False, []
    
    def 拓扑排序(self) -> Tuple[bool, List[str], str]:
        """拓扑排序，返回计算顺序"""
        # 先检测循环依赖
        有循环, 循环路径 = self.检测循环依赖()
        if 有循环:
            return False, [], f"检测到循环依赖: {' -> '.join(循环路径)}"
        
        # Kahn算法进行拓扑排序
        入度 = defaultdict(int)
        
        # 计算每个节点的入度
        for 节点ID in self.节点表:
            入度[节点ID] = len(self.邻接表[节点ID])
        
        # 找到所有入度为0的节点
        队列 = deque([节点ID for 节点ID in self.节点表 if 入度[节点ID] == 0])
        结果 = []
        
        while 队列:
            当前节点 = 队列.popleft()
            结果.append(当前节点)
            
            # 更新依赖当前节点的其他节点的入度
            for 依赖节点 in self.反向邻接表[当前节点]:
                入度[依赖节点] -= 1
                if 入度[依赖节点] == 0:
                    队列.append(依赖节点)
        
        if len(结果) != len(self.节点表):
            return False, [], "拓扑排序失败，可能存在循环依赖"
        
        self.计算顺序 = 结果
        return True, 结果, ""
    
    def 获取节点(self, 节点ID: str) -> Optional[依赖图节点]:
        """获取指定ID的节点"""
        return self.节点表.get(节点ID)
    
    def 获取所有节点(self) -> List[依赖图节点]:
        """获取所有节点"""
        return list(self.节点表.values())
    
    def 清空(self):
        """清空依赖图"""
        self.节点表.clear()
        self.邻接表.clear()
        self.反向邻接表.clear()
        self.计算顺序.clear()

# ==================== 文法解析器类 ====================

class 属性文法解析器:
    """属性文法解析器类"""
    
    def __init__(self):
        self.当前文法: Optional[属性文法] = None
    
    def 解析文法文件(self, 文件内容: str) -> Tuple[bool, 属性文法, List[str]]:
        """解析属性文法文件"""
        错误列表 = []
        文法 = 属性文法()
        
        try:
            行列表 = 文件内容.strip().split('\n')
            当前模式 = ""
            
            for 行号, 行内容 in enumerate(行列表, 1):
                行内容 = 行内容.strip()
                
                # 跳过空行和注释
                if not 行内容 or 行内容.startswith('#'):
                    continue
                
                # 识别模式标记
                if 行内容.startswith('[') and 行内容.endswith(']'):
                    当前模式 = 行内容[1:-1]
                    continue
                
                # 根据当前模式解析内容
                if 当前模式 == "文法":
                    成功, 错误 = self._解析产生式(行内容, 文法, 行号)
                elif 当前模式 == "属性定义":
                    成功, 错误 = self._解析属性定义(行内容, 文法, 行号)
                elif 当前模式 == "语义规则":
                    成功, 错误 = self._解析语义规则(行内容, 文法, 行号)
                else:
                    # 默认尝试解析为产生式
                    成功, 错误 = self._解析产生式(行内容, 文法, 行号)
                
                if not 成功:
                    错误列表.append(f"第{行号}行: {错误}")
            
            # 设置开始符号
            if 文法.产生式列表:
                文法.开始符号 = 文法.产生式列表[0].左部
            
            self.当前文法 = 文法
            return len(错误列表) == 0, 文法, 错误列表
            
        except Exception as e:
            错误列表.append(f"解析文法时发生异常: {str(e)}")
            return False, 文法, 错误列表
    
    def _解析产生式(self, 行内容: str, 文法: 属性文法, 行号: int) -> Tuple[bool, str]:
        """解析产生式"""
        try:
            if '->' not in 行内容:
                return False, "产生式格式错误，缺少'->'符号"
            
            左部, 右部 = 行内容.split('->', 1)
            左部 = 左部.strip()
            右部 = 右部.strip()
            
            if not 左部:
                return False, "产生式左部不能为空"
            
            # 处理多个候选（用|分隔）
            候选列表 = [候选.strip() for 候选 in 右部.split('|')]
            
            for 候选 in 候选列表:
                if not 候选:
                    候选 = "ε"  # 空产生式
                
                右部符号列表 = 候选.split() if 候选 != "ε" else ["ε"]
                产生式对象 = 产生式(左部, 右部符号列表)
                文法.添加产生式(产生式对象)
            
            return True, ""
            
        except Exception as e:
            return False, f"解析产生式时发生错误: {str(e)}"
    
    def _解析属性定义(self, 行内容: str, 文法: 属性文法, 行号: int) -> Tuple[bool, str]:
        """解析属性定义"""
        try:
            # 属性定义格式：符号名.属性名 : 属性类型 [数据类型] [默认值] [描述]
            部分 = 行内容.split(':')
            if len(部分) < 2:
                return False, "属性定义格式错误，缺少':'符号"
            
            属性全名 = 部分[0].strip()
            属性信息 = 部分[1].strip()
            
            if '.' not in 属性全名:
                return False, "属性名格式错误，应为'符号名.属性名'"
            
            符号名, 属性名 = 属性全名.split('.', 1)
            
            # 解析属性类型
            信息部分 = 属性信息.split()
            if not 信息部分:
                return False, "属性类型不能为空"
            
            属性类型名 = 信息部分[0]
            if 属性类型名 == "综合属性":
                属性类型对象 = 属性类型.综合属性
            elif 属性类型名 == "继承属性":
                属性类型对象 = 属性类型.继承属性
            else:
                return False, f"未知的属性类型: {属性类型名}"
            
            # 创建属性定义
            属性定义对象 = 属性定义(属性名, 属性类型对象)
            
            # 添加到对应符号
            符号对象 = 文法.添加符号(符号名)
            符号对象.添加属性定义(属性定义对象)
            
            return True, ""
            
        except Exception as e:
            return False, f"解析属性定义时发生错误: {str(e)}"
    
    def _解析语义规则(self, 行内容: str, 文法: 属性文法, 行号: int) -> Tuple[bool, str]:
        """解析语义规则"""
        try:
            # 语义规则格式：目标属性 := 表达式 [# 产生式编号]
            if ':=' not in 行内容:
                return False, "语义规则格式错误，缺少':='符号"
            
            目标属性, 表达式部分 = 行内容.split(':=', 1)
            目标属性 = 目标属性.strip()
            
            # 检查是否有产生式编号注释
            产生式编号 = -1
            if '#' in 表达式部分:
                表达式, 注释 = 表达式部分.split('#', 1)
                表达式 = 表达式.strip()
                注释 = 注释.strip()
                try:
                    产生式编号 = int(注释)
                except ValueError:
                    pass
            else:
                表达式 = 表达式部分.strip()
            
            if not 目标属性 or not 表达式:
                return False, "语义规则的目标属性和表达式都不能为空"
            
            # 提取依赖属性
            依赖属性 = re.findall(r'\b\w+\.\w+\b', 表达式)
            
            语义规则对象 = 语义规则(目标属性, 表达式, 依赖属性)
            
            # 如果指定了产生式编号，直接添加
            if 产生式编号 >= 0 and 产生式编号 < len(文法.产生式列表):
                文法.添加语义规则(产生式编号, 语义规则对象)
            else:
                # 否则尝试智能匹配
                self._智能分配语义规则(语义规则对象, 文法)
            
            return True, ""
            
        except Exception as e:
            return False, f"解析语义规则时发生错误: {str(e)}"
    
    def _智能分配语义规则(self, 语义规则对象: 语义规则, 文法: 属性文法):
        """智能分配语义规则到合适的产生式"""
        目标符号 = 语义规则对象.目标属性.split('.')[0]

        # 查找左部为目标符号的产生式
        for 产生式对象 in 文法.产生式列表:
            if 产生式对象.左部 == 目标符号:
                文法.添加语义规则(产生式对象.编号, 语义规则对象)
                break

# ==================== 依赖图构建器类 ====================

class 依赖图构建器:
    """依赖图构建器 - 根据属性文法和语法分析树构建依赖图"""

    def __init__(self, 文法: 属性文法):
        self.文法 = 文法
        self.依赖图对象 = 依赖图()
        self.节点计数器 = 0

    def 构建依赖图(self, 语法分析树: List[int]) -> Tuple[bool, 依赖图, str]:
        """
        根据语法分析树构建依赖图
        语法分析树: 产生式编号序列（自底向上归约顺序）
        """
        try:
            self.依赖图对象.清空()
            self.节点计数器 = 0

            # 模拟语法分析过程，构建属性实例
            属性实例表 = {}  # 符号实例ID -> 属性名 -> 节点ID
            符号栈 = []  # 存储符号实例信息

            # 为每个产生式应用创建属性节点和依赖关系
            for 产生式编号 in 语法分析树:
                产生式对象 = self.文法.获取产生式(产生式编号)
                if not 产生式对象:
                    continue

                # 创建产生式应用的属性节点
                成功, 错误 = self._处理产生式应用(产生式对象, 属性实例表, 符号栈)
                if not 成功:
                    return False, self.依赖图对象, 错误

            return True, self.依赖图对象, ""

        except Exception as e:
            return False, self.依赖图对象, f"构建依赖图时发生异常: {str(e)}"

    def _处理产生式应用(self, 产生式: 产生式, 属性实例表: Dict, 符号栈: List) -> Tuple[bool, str]:
        """处理单个产生式的应用"""
        try:
            # 为产生式左部和右部的每个符号创建属性节点
            符号实例列表 = []

            # 处理右部符号（从栈中弹出）
            右部符号实例 = []
            for i in range(len(产生式.右部)):
                if 符号栈:
                    右部符号实例.insert(0, 符号栈.pop())

            # 创建左部符号实例
            左部实例ID = f"{产生式.左部}_{self.节点计数器}"
            self.节点计数器 += 1

            # 为左部符号创建属性节点
            左部符号 = self.文法.符号表.get(产生式.左部)
            if 左部符号:
                for 属性定义对象 in 左部符号.属性定义列表:
                    节点ID = f"{左部实例ID}.{属性定义对象.名称}"
                    节点 = 依赖图节点(节点ID, f"{产生式.左部}.{属性定义对象.名称}")
                    self.依赖图对象.添加节点(节点)

                    if 左部实例ID not in 属性实例表:
                        属性实例表[左部实例ID] = {}
                    属性实例表[左部实例ID][属性定义对象.名称] = 节点ID

            # 为右部符号创建属性节点（如果还没有）
            右部实例ID列表 = []
            for i, 符号名 in enumerate(产生式.右部):
                if 符号名 == "ε":
                    continue

                if i < len(右部符号实例):
                    实例ID = 右部符号实例[i]
                else:
                    实例ID = f"{符号名}_{self.节点计数器}"
                    self.节点计数器 += 1

                右部实例ID列表.append(实例ID)

                符号对象 = self.文法.符号表.get(符号名)
                if 符号对象:
                    for 属性定义对象 in 符号对象.属性定义列表:
                        节点ID = f"{实例ID}.{属性定义对象.名称}"
                        if 节点ID not in self.依赖图对象.节点表:
                            节点 = 依赖图节点(节点ID, f"{符号名}.{属性定义对象.名称}")
                            self.依赖图对象.添加节点(节点)

                        if 实例ID not in 属性实例表:
                            属性实例表[实例ID] = {}
                        属性实例表[实例ID][属性定义对象.名称] = 节点ID

            # 处理语义规则，建立依赖关系
            语义规则列表 = self.文法.获取语义规则(产生式.编号)
            for 语义规则对象 in 语义规则列表:
                成功, 错误 = self._处理语义规则(语义规则对象, 产生式, 属性实例表, 左部实例ID, 右部实例ID列表)
                if not 成功:
                    return False, 错误

            # 将左部符号实例压入栈
            符号栈.append(左部实例ID)

            return True, ""

        except Exception as e:
            return False, f"处理产生式应用时发生错误: {str(e)}"

    def _处理语义规则(self, 语义规则对象: 语义规则, 产生式: 产生式,
                      属性实例表: Dict, 左部实例ID: str, 右部实例ID列表: List[str]) -> Tuple[bool, str]:
        """处理语义规则，建立依赖关系"""
        try:
            # 解析目标属性
            目标属性部分 = 语义规则对象.目标属性.split('.')
            if len(目标属性部分) != 2:
                return False, f"目标属性格式错误: {语义规则对象.目标属性}"

            目标符号名, 目标属性名 = 目标属性部分

            # 确定目标节点ID - 目标属性只能是左部符号的属性
            目标节点ID = None
            if 目标符号名 == 产生式.左部:
                # 左部符号的属性
                if 左部实例ID in 属性实例表 and 目标属性名 in 属性实例表[左部实例ID]:
                    目标节点ID = 属性实例表[左部实例ID][目标属性名]
            else:
                return False, f"语义规则的目标属性必须是左部符号的属性: {语义规则对象.目标属性}"

            if not 目标节点ID:
                return False, f"找不到目标属性节点: {语义规则对象.目标属性}"

            # 设置目标节点的计算表达式
            目标节点 = self.依赖图对象.获取节点(目标节点ID)
            if 目标节点:
                目标节点.计算表达式 = 语义规则对象.表达式

            # 处理依赖属性，建立依赖边
            # 需要跟踪已使用的右部符号位置，避免重复匹配同一个符号实例
            已使用位置 = set()

            for 依赖属性 in 语义规则对象.依赖属性:
                依赖属性部分 = 依赖属性.split('.')
                if len(依赖属性部分) != 2:
                    continue

                依赖符号名, 依赖属性名 = 依赖属性部分
                依赖节点ID = None

                # 右部符号的属性 - 按顺序匹配未使用的符号
                for i, 符号名 in enumerate(产生式.右部):
                    if 符号名 == 依赖符号名 and i not in 已使用位置 and i < len(右部实例ID列表):
                        实例ID = 右部实例ID列表[i]
                        if 实例ID in 属性实例表 and 依赖属性名 in 属性实例表[实例ID]:
                            依赖节点ID = 属性实例表[实例ID][依赖属性名]
                            已使用位置.add(i)  # 标记此位置已使用
                        break

                if 依赖节点ID:
                    # 检查是否会产生自循环
                    if 依赖节点ID == 目标节点ID:
                        return False, f"检测到自循环依赖: {目标节点ID} -> {依赖节点ID}"

                    # 添加依赖边：目标节点依赖于依赖节点
                    self.依赖图对象.添加依赖边(目标节点ID, 依赖节点ID)
                    if 目标节点:
                        目标节点.依赖节点.append(依赖节点ID)

            return True, ""

        except Exception as e:
            return False, f"处理语义规则时发生错误: {str(e)}"

# ==================== 语义分析引擎类 ====================

class 语义分析引擎:
    """语义分析引擎 - 基于依赖图执行语义分析"""

    def __init__(self, 文法: 属性文法):
        self.文法 = 文法
        self.依赖图对象: Optional[依赖图] = None
        self.分析步骤列表: List[分析步骤] = []
        self.当前步骤号 = 0

    def 执行语义分析(self, 依赖图对象: 依赖图, 输入串: str = "") -> Tuple[bool, List[分析步骤], str]:
        """执行基于依赖图的语义分析"""
        try:
            self.依赖图对象 = 依赖图对象
            self.分析步骤列表.clear()
            self.当前步骤号 = 0

            self._记录步骤("开始语义分析", f"输入串: {输入串}")

            # 执行拓扑排序
            成功, 计算顺序, 错误信息 = 依赖图对象.拓扑排序()
            if not 成功:
                self._记录步骤("拓扑排序失败", 错误信息)
                return False, self.分析步骤列表, 错误信息

            self._记录步骤("拓扑排序成功", f"计算顺序: {' -> '.join(计算顺序)}")

            # 初始化终结符属性（模拟词法分析结果）
            self._初始化终结符属性(输入串)

            # 按照拓扑排序的顺序计算属性值
            for 节点ID in 计算顺序:
                节点 = 依赖图对象.获取节点(节点ID)
                if 节点 and not 节点.已计算:
                    成功, 错误 = self._计算节点属性(节点)
                    if not 成功:
                        self._记录步骤("属性计算失败", f"节点 {节点ID}: {错误}")
                        return False, self.分析步骤列表, 错误

            self._记录步骤("语义分析完成", "所有属性计算完毕")
            return True, self.分析步骤列表, ""

        except Exception as e:
            错误信息 = f"语义分析过程中发生异常: {str(e)}"
            self._记录步骤("分析异常", 错误信息)
            return False, self.分析步骤列表, 错误信息

    def _记录步骤(self, 操作类型: str, 描述: str, 节点信息: str = "", 计算结果: str = ""):
        """记录分析步骤"""
        self.当前步骤号 += 1
        步骤 = 分析步骤(self.当前步骤号, 操作类型, 描述, 节点信息, 计算结果)
        self.分析步骤列表.append(步骤)

    def _初始化终结符属性(self, 输入串: str):
        """初始化终结符的属性值"""
        if not self.依赖图对象:
            return

        # 简单的词法分析：将输入串分解为标识符和操作符
        词法单元 = []
        当前单元 = ""

        for 字符 in 输入串:
            if 字符.isalnum() or 字符 == '_':
                当前单元 += 字符
            else:
                if 当前单元:
                    词法单元.append(当前单元)
                    当前单元 = ""
                if not 字符.isspace():
                    词法单元.append(字符)

        if 当前单元:
            词法单元.append(当前单元)

        # 为终结符节点设置属性值
        词法单元索引 = 0
        for 节点 in self.依赖图对象.获取所有节点():
            if '.' in 节点.属性名:
                符号名, 属性名 = 节点.属性名.split('.', 1)
                符号对象 = self.文法.符号表.get(符号名)

                if 符号对象 and 符号对象.是否终结符:
                    if 属性名 == "lexval" and 词法单元索引 < len(词法单元):
                        节点.属性值 = 词法单元[词法单元索引]
                        节点.已计算 = True
                        self._记录步骤("初始化终结符", f"设置 {节点.节点ID} = {节点.属性值}")
                        词法单元索引 += 1
                    elif 属性名 == "type":
                        # 简单的类型推断
                        if 词法单元索引 < len(词法单元):
                            单元 = 词法单元[词法单元索引]
                            if 单元.isdigit():
                                节点.属性值 = "int"
                            elif 单元.replace('.', '').isdigit():
                                节点.属性值 = "float"
                            else:
                                节点.属性值 = "id"
                            节点.已计算 = True
                            self._记录步骤("初始化终结符", f"设置 {节点.节点ID} = {节点.属性值}")

    def _计算节点属性(self, 节点: 依赖图节点) -> Tuple[bool, str]:
        """计算单个节点的属性值"""
        try:
            if 节点.已计算:
                return True, ""

            # 检查所有依赖节点是否已计算
            for 依赖节点ID in 节点.依赖节点:
                依赖节点 = self.依赖图对象.获取节点(依赖节点ID)
                if 依赖节点 and not 依赖节点.已计算:
                    return False, f"依赖节点 {依赖节点ID} 尚未计算"

            # 计算属性值
            if 节点.计算表达式:
                节点.属性值 = self._计算表达式(节点.计算表达式, 节点)
            else:
                # 如果没有计算表达式，使用默认值
                节点.属性值 = "未定义"

            节点.已计算 = True

            self._记录步骤("属性计算",
                         f"计算 {节点.节点ID}",
                         f"表达式: {节点.计算表达式}",
                         f"结果: {节点.属性值}")

            return True, ""

        except Exception as e:
            return False, f"计算节点属性时发生错误: {str(e)}"

    def _计算表达式(self, 表达式: str, 节点: 依赖图节点) -> Any:
        """计算语义表达式"""
        try:
            # 处理字符串常量
            if 表达式.startswith('"') and 表达式.endswith('"'):
                return 表达式.strip('"')

            # 替换表达式中的属性引用
            计算表达式 = 表达式
            属性引用列表 = re.findall(r'\b\w+\.\w+\b', 表达式)

            for 属性引用 in 属性引用列表:
                # 查找对应的依赖节点
                for 依赖节点ID in 节点.依赖节点:
                    依赖节点 = self.依赖图对象.获取节点(依赖节点ID)
                    if 依赖节点 and 依赖节点.属性名 == 属性引用:
                        值 = 依赖节点.属性值
                        if isinstance(值, str) and not 值.isdigit():
                            计算表达式 = 计算表达式.replace(属性引用, f'"{值}"')
                        else:
                            计算表达式 = 计算表达式.replace(属性引用, str(值))
                        break

            # 处理特殊函数
            if "newtemp()" in 计算表达式:
                temp_name = f"t{len([n for n in self.依赖图对象.获取所有节点() if 't' in str(n.属性值)])}"
                计算表达式 = 计算表达式.replace("newtemp()", f'"{temp_name}"')

            # 尝试计算表达式
            if any(op in 计算表达式 for op in ['+', '-', '*', '/', '(', ')']):
                try:
                    return eval(计算表达式)
                except:
                    return 计算表达式
            else:
                return 计算表达式.strip('"')

        except Exception as e:
            return f"计算错误: {str(e)}"

# ==================== GUI界面类 ====================

class 依赖图语义分析器GUI:
    """依赖图语义分析器GUI界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("依赖图语义分析程序")
        self.root.geometry("1200x800")

        # 数据
        self.文法 = None
        self.解析器 = 属性文法解析器()
        self.构建器 = None
        self.分析引擎 = None
        self.依赖图对象 = None

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个标签页
        self.create_grammar_tab()
        self.create_dependency_graph_tab()
        self.create_analysis_tab()
        self.create_visualization_tab()
        self.create_help_tab()

    def create_grammar_tab(self):
        """创建文法输入标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="属性文法输入")

        # 左侧：文法输入区域
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 文法输入标签
        ttk.Label(left_frame, text="属性文法输入（支持文法、属性定义、语义规则三个部分）:").pack(anchor=tk.W)

        # 文法输入文本框
        self.grammar_text = scrolledtext.ScrolledText(left_frame, height=20, width=60)
        self.grammar_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 默认文法
        default_grammar = """# 依赖图语义分析器示例文法
# 简单算术表达式文法

[文法]
E -> E + T | T
T -> T * F | F
F -> ( E ) | id

[属性定义]
E.val : 综合属性
T.val : 综合属性
F.val : 综合属性
id.lexval : 综合属性

[语义规则]
E.val := E.val + T.val  # 0
E.val := T.val          # 1
T.val := T.val * F.val  # 2
T.val := F.val          # 3
F.val := E.val          # 4
F.val := id.lexval      # 5"""
        self.grammar_text.insert(tk.END, default_grammar)

        # 按钮框架
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="解析文法", command=self.parse_grammar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载文件", command=self.load_grammar_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存文法", command=self.save_grammar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_grammar).pack(side=tk.LEFT, padx=5)

        # 右侧：文法信息显示
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 文法信息标签
        ttk.Label(right_frame, text="文法解析结果:").pack(anchor=tk.W)

        # 文法信息显示
        self.grammar_info = scrolledtext.ScrolledText(right_frame, height=25, width=50)
        self.grammar_info.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_dependency_graph_tab(self):
        """创建依赖图标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="依赖图构建")

        # 上部：输入区域
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        # 语法分析结果输入
        ttk.Label(top_frame, text="语法分析结果（产生式编号序列，用空格分隔）:").pack(anchor=tk.W)
        self.parse_result_entry = tk.Entry(top_frame, width=80)
        self.parse_result_entry.pack(fill=tk.X, pady=2)
        self.parse_result_entry.insert(0, "5 3 1 2 0")  # 默认示例

        # 按钮
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="构建依赖图", command=self.build_dependency_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="检测循环依赖", command=self.check_cycles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="拓扑排序", command=self.topological_sort).pack(side=tk.LEFT, padx=5)

        # 下部：结果显示
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 依赖图信息
        ttk.Label(bottom_frame, text="依赖图信息:").pack(anchor=tk.W)
        self.dependency_info = scrolledtext.ScrolledText(bottom_frame, height=20)
        self.dependency_info.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_analysis_tab(self):
        """创建语义分析标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="语义分析过程")

        # 上部：输入区域
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        # 输入串
        ttk.Label(top_frame, text="输入串:").pack(anchor=tk.W)
        self.input_string_entry = tk.Entry(top_frame, width=80)
        self.input_string_entry.pack(fill=tk.X, pady=2)
        self.input_string_entry.insert(0, "id + id * id")  # 默认示例

        # 按钮
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="执行语义分析", command=self.perform_semantic_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空结果", command=self.clear_analysis_result).pack(side=tk.LEFT, padx=5)

        # 下部：分析过程显示
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 分析步骤
        ttk.Label(bottom_frame, text="语义分析步骤:").pack(anchor=tk.W)
        self.analysis_steps = scrolledtext.ScrolledText(bottom_frame, height=20)
        self.analysis_steps.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_visualization_tab(self):
        """创建可视化标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="依赖图可视化")

        # 控制按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="显示依赖图", command=self.show_dependency_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存图片", command=self.save_graph_image).pack(side=tk.LEFT, padx=5)

        # 图形显示区域
        self.graph_frame = ttk.Frame(frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_help_tab(self):
        """创建帮助标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="帮助")

        help_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_content = """依赖图语义分析程序 - 使用帮助

1. 程序功能
   本程序实现了基于依赖图的语义分析方法，主要功能包括：
   - 属性文法解析
   - 依赖图构建
   - 循环依赖检测
   - 拓扑排序
   - 语义分析执行
   - 依赖图可视化

2. 使用步骤
   (1) 在"属性文法输入"标签页中输入属性文法
   (2) 点击"解析文法"按钮解析文法
   (3) 在"依赖图构建"标签页中输入语法分析结果
   (4) 点击"构建依赖图"按钮构建依赖图
   (5) 在"语义分析过程"标签页中执行语义分析
   (6) 在"依赖图可视化"标签页中查看依赖图

3. 文法格式
   属性文法包含三个部分：

   [文法]
   - 使用 -> 分隔左部和右部
   - 使用 | 分隔多个候选
   - 支持 ε 产生式

   [属性定义]
   - 格式：符号名.属性名 : 属性类型
   - 属性类型：综合属性 或 继承属性

   [语义规则]
   - 格式：目标属性 := 表达式 # 产生式编号
   - 支持属性引用和算术表达式

4. 依赖图理论
   依赖图是表示属性之间依赖关系的有向图：
   - 节点表示属性实例
   - 边表示依赖关系
   - 通过拓扑排序确定计算顺序
   - 检测循环依赖并报告错误

5. 示例
   文法：E -> E + T | T
   属性：E.val, T.val
   语义规则：E.val := E.val + T.val

   这表示左部E的val属性依赖于右部E和T的val属性。

6. 注意事项
   - 确保语义规则与产生式对应
   - 避免循环依赖
   - 终结符属性需要初始化
   - 语法分析结果应为产生式编号序列

7. 技术支持
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
            文法内容 = self.grammar_text.get(1.0, tk.END).strip()
            if not 文法内容:
                messagebox.showwarning("警告", "请输入文法内容")
                return

            成功, 文法, 错误列表 = self.解析器.解析文法文件(文法内容)

            if 成功:
                self.文法 = 文法
                self.构建器 = 依赖图构建器(文法)
                self.分析引擎 = 语义分析引擎(文法)

                # 显示文法信息
                self.display_grammar_info(文法)
                messagebox.showinfo("成功", "文法解析成功！")
            else:
                错误信息 = "\n".join(错误列表)
                self.grammar_info.delete(1.0, tk.END)
                self.grammar_info.insert(tk.END, f"文法解析失败：\n{错误信息}")
                messagebox.showerror("错误", f"文法解析失败：\n{错误信息}")

        except Exception as e:
            messagebox.showerror("错误", f"解析文法时发生异常：{str(e)}")

    def display_grammar_info(self, 文法: 属性文法):
        """显示文法信息"""
        self.grammar_info.delete(1.0, tk.END)

        info = "=== 文法解析结果 ===\n\n"

        # 显示产生式
        info += "产生式列表：\n"
        for i, 产生式对象 in enumerate(文法.产生式列表):
            右部 = " ".join(产生式对象.右部)
            info += f"{i}: {产生式对象.左部} -> {右部}\n"

        info += "\n符号表：\n"
        for 符号名, 符号对象 in 文法.符号表.items():
            info += f"{符号名} ({'终结符' if 符号对象.是否终结符 else '非终结符'})\n"
            for 属性定义对象 in 符号对象.属性定义列表:
                info += f"  - {属性定义对象.名称}: {属性定义对象.类型.value}\n"

        info += "\n语义规则：\n"
        for 产生式编号, 规则列表 in 文法.语义规则表.items():
            if 规则列表:
                info += f"产生式 {产生式编号}:\n"
                for 规则 in 规则列表:
                    info += f"  {规则.目标属性} := {规则.表达式}\n"

        self.grammar_info.insert(tk.END, info)

    def load_grammar_file(self):
        """加载文法文件"""
        try:
            文件路径 = filedialog.askopenfilename(
                title="选择文法文件",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                with open(文件路径, 'r', encoding='utf-8') as f:
                    文法内容 = f.read()

                self.grammar_text.delete(1.0, tk.END)
                self.grammar_text.insert(tk.END, 文法内容)
                messagebox.showinfo("成功", "文法文件加载成功！")

        except Exception as e:
            messagebox.showerror("错误", f"加载文法文件时发生错误：{str(e)}")

    def save_grammar(self):
        """保存文法"""
        try:
            文件路径 = filedialog.asksaveasfilename(
                title="保存文法文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                文法内容 = self.grammar_text.get(1.0, tk.END)
                with open(文件路径, 'w', encoding='utf-8') as f:
                    f.write(文法内容)
                messagebox.showinfo("成功", "文法文件保存成功！")

        except Exception as e:
            messagebox.showerror("错误", f"保存文法文件时发生错误：{str(e)}")

    def clear_grammar(self):
        """清空文法"""
        self.grammar_text.delete(1.0, tk.END)
        self.grammar_info.delete(1.0, tk.END)

    def build_dependency_graph(self):
        """构建依赖图"""
        try:
            if not self.文法:
                messagebox.showwarning("警告", "请先解析文法")
                return

            # 获取语法分析结果
            分析结果文本 = self.parse_result_entry.get().strip()
            if not 分析结果文本:
                messagebox.showwarning("警告", "请输入语法分析结果")
                return

            try:
                语法分析结果 = [int(x) for x in 分析结果文本.split()]
            except ValueError:
                messagebox.showerror("错误", "语法分析结果格式错误，应为数字序列")
                return

            # 构建依赖图
            成功, 依赖图对象, 错误信息 = self.构建器.构建依赖图(语法分析结果)

            if 成功:
                self.依赖图对象 = 依赖图对象
                self.display_dependency_graph_info(依赖图对象)
                messagebox.showinfo("成功", "依赖图构建成功！")
            else:
                self.dependency_info.delete(1.0, tk.END)
                self.dependency_info.insert(tk.END, f"依赖图构建失败：\n{错误信息}")
                messagebox.showerror("错误", f"依赖图构建失败：\n{错误信息}")

        except Exception as e:
            messagebox.showerror("错误", f"构建依赖图时发生异常：{str(e)}")

    def display_dependency_graph_info(self, 依赖图对象: 依赖图):
        """显示依赖图信息"""
        self.dependency_info.delete(1.0, tk.END)

        info = "=== 依赖图信息 ===\n\n"

        # 显示节点
        info += f"节点数量：{len(依赖图对象.节点表)}\n\n"
        info += "节点列表：\n"
        for 节点ID, 节点 in 依赖图对象.节点表.items():
            info += f"{节点ID}: {节点.属性名}\n"
            if 节点.计算表达式:
                info += f"  计算表达式: {节点.计算表达式}\n"
            if 节点.依赖节点:
                info += f"  依赖节点: {', '.join(节点.依赖节点)}\n"
            info += "\n"

        # 显示依赖关系
        info += "依赖关系：\n"
        for 源节点, 目标节点列表 in 依赖图对象.邻接表.items():
            if 目标节点列表:
                info += f"{源节点} 依赖于: {', '.join(目标节点列表)}\n"

        self.dependency_info.insert(tk.END, info)

    def check_cycles(self):
        """检测循环依赖"""
        try:
            if not self.依赖图对象:
                messagebox.showwarning("警告", "请先构建依赖图")
                return

            有循环, 循环路径 = self.依赖图对象.检测循环依赖()

            if 有循环:
                循环信息 = " -> ".join(循环路径)
                messagebox.showwarning("循环依赖", f"检测到循环依赖：\n{循环信息}")

                # 在依赖图信息中显示循环
                当前内容 = self.dependency_info.get(1.0, tk.END)
                self.dependency_info.delete(1.0, tk.END)
                self.dependency_info.insert(tk.END, 当前内容 + f"\n=== 循环依赖检测 ===\n检测到循环：{循环信息}\n")
            else:
                messagebox.showinfo("检测结果", "未检测到循环依赖")

                # 在依赖图信息中显示结果
                当前内容 = self.dependency_info.get(1.0, tk.END)
                self.dependency_info.delete(1.0, tk.END)
                self.dependency_info.insert(tk.END, 当前内容 + "\n=== 循环依赖检测 ===\n未检测到循环依赖\n")

        except Exception as e:
            messagebox.showerror("错误", f"检测循环依赖时发生异常：{str(e)}")

    def topological_sort(self):
        """拓扑排序"""
        try:
            if not self.依赖图对象:
                messagebox.showwarning("警告", "请先构建依赖图")
                return

            成功, 计算顺序, 错误信息 = self.依赖图对象.拓扑排序()

            if 成功:
                排序结果 = " -> ".join(计算顺序)
                messagebox.showinfo("拓扑排序", f"计算顺序：\n{排序结果}")

                # 在依赖图信息中显示排序结果
                当前内容 = self.dependency_info.get(1.0, tk.END)
                self.dependency_info.delete(1.0, tk.END)
                self.dependency_info.insert(tk.END, 当前内容 + f"\n=== 拓扑排序结果 ===\n计算顺序：{排序结果}\n")
            else:
                messagebox.showerror("错误", f"拓扑排序失败：\n{错误信息}")

        except Exception as e:
            messagebox.showerror("错误", f"拓扑排序时发生异常：{str(e)}")

    def perform_semantic_analysis(self):
        """执行语义分析"""
        try:
            if not self.依赖图对象:
                messagebox.showwarning("警告", "请先构建依赖图")
                return

            if not self.分析引擎:
                messagebox.showwarning("警告", "语义分析引擎未初始化")
                return

            输入串 = self.input_string_entry.get().strip()

            成功, 分析步骤列表, 错误信息 = self.分析引擎.执行语义分析(self.依赖图对象, 输入串)

            if 成功:
                self.display_analysis_steps(分析步骤列表)
                messagebox.showinfo("成功", "语义分析完成！")
            else:
                self.analysis_steps.delete(1.0, tk.END)
                self.analysis_steps.insert(tk.END, f"语义分析失败：\n{错误信息}")
                messagebox.showerror("错误", f"语义分析失败：\n{错误信息}")

        except Exception as e:
            messagebox.showerror("错误", f"执行语义分析时发生异常：{str(e)}")

    def display_analysis_steps(self, 分析步骤列表: List[分析步骤]):
        """显示分析步骤"""
        self.analysis_steps.delete(1.0, tk.END)

        info = "=== 语义分析步骤 ===\n\n"

        for 步骤 in 分析步骤列表:
            info += f"步骤 {步骤.步骤号}: {步骤.操作类型}\n"
            info += f"描述: {步骤.描述}\n"
            if 步骤.节点信息:
                info += f"节点: {步骤.节点信息}\n"
            if 步骤.计算结果:
                info += f"结果: {步骤.计算结果}\n"
            info += "-" * 50 + "\n"

        self.analysis_steps.insert(tk.END, info)

    def clear_analysis_result(self):
        """清空分析结果"""
        self.analysis_steps.delete(1.0, tk.END)

    def show_dependency_graph(self):
        """显示依赖图可视化"""
        try:
            if not self.依赖图对象:
                messagebox.showwarning("警告", "请先构建依赖图")
                return

            # 清空之前的图形
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            # 创建NetworkX图
            G = nx.DiGraph()

            # 添加节点
            for 节点ID, 节点 in self.依赖图对象.节点表.items():
                G.add_node(节点ID, label=节点.属性名)

            # 添加边
            for 源节点, 目标节点列表 in self.依赖图对象.邻接表.items():
                for 目标节点 in 目标节点列表:
                    G.add_edge(源节点, 目标节点)

            # 创建matplotlib图形
            fig, ax = plt.subplots(figsize=(10, 8))

            # 设置布局
            if len(G.nodes()) > 0:
                try:
                    pos = nx.spring_layout(G, k=2, iterations=50)
                except:
                    pos = nx.random_layout(G)

                # 绘制节点
                nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue',
                                     node_size=2000, alpha=0.7)

                # 绘制边
                nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray',
                                     arrows=True, arrowsize=20, alpha=0.6)

                # 绘制标签
                labels = {}
                for 节点ID in G.nodes():
                    节点 = self.依赖图对象.获取节点(节点ID)
                    if 节点:
                        # 简化标签显示
                        标签 = 节点.属性名.replace('.', '.\n')
                        labels[节点ID] = 标签

                nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8)

            ax.set_title("依赖图可视化", fontsize=14, fontweight='bold')
            ax.axis('off')

            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False

            # 嵌入到Tkinter中
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            messagebox.showinfo("成功", "依赖图可视化完成！")

        except Exception as e:
            messagebox.showerror("错误", f"显示依赖图时发生异常：{str(e)}")

    def save_graph_image(self):
        """保存图片"""
        try:
            if not self.依赖图对象:
                messagebox.showwarning("警告", "请先构建并显示依赖图")
                return

            文件路径 = filedialog.asksaveasfilename(
                title="保存依赖图图片",
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("所有文件", "*.*")]
            )

            if 文件路径:
                # 重新创建图形用于保存
                G = nx.DiGraph()

                for 节点ID, 节点 in self.依赖图对象.节点表.items():
                    G.add_node(节点ID, label=节点.属性名)

                for 源节点, 目标节点列表 in self.依赖图对象.邻接表.items():
                    for 目标节点 in 目标节点列表:
                        G.add_edge(源节点, 目标节点)

                plt.figure(figsize=(12, 10))

                if len(G.nodes()) > 0:
                    pos = nx.spring_layout(G, k=2, iterations=50)

                    nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                                         node_size=3000, alpha=0.7)
                    nx.draw_networkx_edges(G, pos, edge_color='gray',
                                         arrows=True, arrowsize=20, alpha=0.6)

                    labels = {}
                    for 节点ID in G.nodes():
                        节点 = self.依赖图对象.获取节点(节点ID)
                        if 节点:
                            labels[节点ID] = 节点.属性名

                    nx.draw_networkx_labels(G, pos, labels, font_size=10)

                plt.title("依赖图", fontsize=16, fontweight='bold')
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(文件路径, dpi=300, bbox_inches='tight')
                plt.close()

                messagebox.showinfo("成功", f"依赖图已保存到：{文件路径}")

        except Exception as e:
            messagebox.showerror("错误", f"保存图片时发生异常：{str(e)}")

    def run(self):
        """运行GUI程序"""
        self.root.mainloop()

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    try:
        # 创建并运行GUI应用
        app = 依赖图语义分析器GUI()
        app.run()
    except Exception as e:
        print(f"程序运行时发生异常：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
