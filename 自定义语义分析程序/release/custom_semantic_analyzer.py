#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义语义分析程序
编译原理作业 - 题目6.4

实现多种语义分析方法的集成程序，包括：
- S属性文法语义分析
- L属性文法语义分析  
- 依赖图语义分析

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import os
from collections import defaultdict, deque
import copy

# ==================== 基础数据结构 ====================

class 属性类型(Enum):
    """属性类型枚举"""
    综合 = "综合"
    继承 = "继承"

class 数据类型(Enum):
    """数据类型枚举"""
    整数 = "整数"
    浮点数 = "浮点数"
    字符串 = "字符串"
    布尔值 = "布尔值"
    列表 = "列表"
    字典 = "字典"

@dataclass
class 属性定义:
    """属性定义类"""
    名称: str
    类型: 属性类型
    数据类型: 数据类型
    默认值: Any = None
    描述: str = ""

@dataclass
class 文法符号:
    """文法符号类"""
    名称: str
    是否终结符: bool
    属性列表: List[属性定义] = field(default_factory=list)
    
    def 添加属性(self, 属性: 属性定义):
        """添加属性定义"""
        self.属性列表.append(属性)
    
    def 获取属性(self, 属性名: str) -> Optional[属性定义]:
        """获取指定名称的属性"""
        for 属性 in self.属性列表:
            if 属性.名称 == 属性名:
                return 属性
        return None

@dataclass
class 产生式:
    """产生式类"""
    编号: int
    左部: str
    右部: List[str]
    
    def __str__(self):
        return f"{self.左部} -> {' '.join(self.右部)}"

@dataclass
class 语义规则:
    """语义规则类"""
    目标属性: str  # 格式：符号.属性
    表达式: str
    依赖属性: List[str] = field(default_factory=list)  # 格式：符号.属性
    
    def __str__(self):
        return f"{self.目标属性} := {self.表达式}"

@dataclass
class 符号表项:
    """符号表项类"""
    名称: str
    类型: str
    值: Any = None
    作用域: str = "全局"
    行号: int = 0
    
class 符号表:
    """符号表类"""
    
    def __init__(self):
        self.表项: Dict[str, 符号表项] = {}
        self.作用域栈: List[str] = ["全局"]
    
    def 进入作用域(self, 作用域名: str):
        """进入新作用域"""
        self.作用域栈.append(作用域名)
    
    def 退出作用域(self):
        """退出当前作用域"""
        if len(self.作用域栈) > 1:
            self.作用域栈.pop()
    
    def 当前作用域(self) -> str:
        """获取当前作用域"""
        return self.作用域栈[-1]
    
    def 插入符号(self, 符号项: 符号表项):
        """插入符号"""
        键 = f"{self.当前作用域()}.{符号项.名称}"
        self.表项[键] = 符号项
    
    def 查找符号(self, 名称: str) -> Optional[符号表项]:
        """查找符号"""
        # 从当前作用域向上查找
        for 作用域 in reversed(self.作用域栈):
            键 = f"{作用域}.{名称}"
            if 键 in self.表项:
                return self.表项[键]
        return None
    
    def 更新符号值(self, 名称: str, 值: Any) -> bool:
        """更新符号值"""
        符号项 = self.查找符号(名称)
        if 符号项:
            符号项.值 = 值
            return True
        return False

@dataclass
class 分析步骤:
    """分析步骤记录类"""
    步骤号: int
    动作: str
    描述: str = ""
    当前产生式: Optional[产生式] = None
    属性计算: List[str] = field(default_factory=list)
    符号表状态: Dict[str, Any] = field(default_factory=dict)
    错误信息: str = ""

class 通用属性文法:
    """通用属性文法类"""
    
    def __init__(self):
        self.开始符号: str = ""
        self.终结符集合: Set[str] = set()
        self.非终结符集合: Set[str] = set()
        self.产生式列表: List[产生式] = []
        self.文法符号: Dict[str, 文法符号] = {}
        self.语义规则表: Dict[int, List[语义规则]] = defaultdict(list)
    
    def 添加符号(self, 符号: 文法符号):
        """添加文法符号"""
        self.文法符号[符号.名称] = 符号
        if 符号.是否终结符:
            self.终结符集合.add(符号.名称)
        else:
            self.非终结符集合.add(符号.名称)
    
    def 添加产生式(self, 产生式对象: 产生式):
        """添加产生式"""
        self.产生式列表.append(产生式对象)
        # 自动添加符号到集合
        if 产生式对象.左部 not in self.文法符号:
            self.添加符号(文法符号(产生式对象.左部, False))
        
        for 符号 in 产生式对象.右部:
            if 符号 not in self.文法符号:
                # 默认假设大写字母开头的是非终结符
                是否终结符 = not (符号[0].isupper() if 符号 else True)
                self.添加符号(文法符号(符号, 是否终结符))
    
    def 添加语义规则(self, 产生式编号: int, 规则: 语义规则):
        """添加语义规则"""
        self.语义规则表[产生式编号].append(规则)
    
    def 获取产生式(self, 编号: int) -> Optional[产生式]:
        """获取产生式"""
        if 0 <= 编号 < len(self.产生式列表):
            return self.产生式列表[编号]
        return None
    
    def 获取产生式语义规则(self, 编号: int) -> List[语义规则]:
        """获取产生式的语义规则"""
        return self.语义规则表.get(编号, [])

class 语义分析类型(Enum):
    """语义分析类型枚举"""
    S属性文法 = "S属性文法"
    L属性文法 = "L属性文法"
    依赖图 = "依赖图"

@dataclass
class 语义分析配置:
    """语义分析配置类"""
    分析类型: 语义分析类型
    文法: 通用属性文法
    输入串: str = ""
    语法分析结果: List[int] = field(default_factory=list)
    启用调试: bool = True
    最大步骤数: int = 1000

# ==================== 文法解析器 ====================

class 文法解析器:
    """通用文法解析器"""
    
    def __init__(self):
        self.错误列表: List[str] = []
    
    def 解析文法文件(self, 文法内容: str) -> Tuple[bool, Optional[通用属性文法], List[str]]:
        """解析文法文件内容"""
        try:
            self.错误列表.clear()
            文法 = 通用属性文法()
            
            # 按行分割并处理
            行列表 = [行.strip() for 行 in 文法内容.split('\n') if 行.strip()]
            
            当前节 = ""
            产生式编号 = 0
            
            for 行号, 行内容 in enumerate(行列表, 1):
                # 跳过注释
                if 行内容.startswith('#') or 行内容.startswith('//'):
                    continue
                
                # 检查节标记
                if 行内容.startswith('[') and 行内容.endswith(']'):
                    当前节 = 行内容[1:-1].strip()
                    continue
                
                # 根据当前节处理内容
                if 当前节 == "文法" or 当前节 == "产生式":
                    成功, 错误 = self._解析产生式(行内容, 文法, 产生式编号)
                    if 成功:
                        产生式编号 += 1
                    else:
                        self.错误列表.append(f"行{行号}: {错误}")
                
                elif 当前节 == "属性定义":
                    成功, 错误 = self._解析属性定义(行内容, 文法, 行号)
                    if not 成功:
                        self.错误列表.append(f"行{行号}: {错误}")
                
                elif 当前节 == "语义规则":
                    成功, 错误 = self._解析语义规则(行内容, 文法, 行号)
                    if not 成功:
                        self.错误列表.append(f"行{行号}: {错误}")
            
            # 设置开始符号
            if 文法.产生式列表:
                文法.开始符号 = 文法.产生式列表[0].左部
            
            return len(self.错误列表) == 0, 文法, self.错误列表
            
        except Exception as e:
            self.错误列表.append(f"解析文法时发生异常: {str(e)}")
            return False, None, self.错误列表

    def _解析产生式(self, 行内容: str, 文法: 通用属性文法, 编号: int) -> Tuple[bool, str]:
        """解析产生式"""
        try:
            if '->' not in 行内容:
                return False, "产生式格式错误，缺少'->'符号"

            左部, 右部 = 行内容.split('->', 1)
            左部 = 左部.strip()
            右部 = 右部.strip()

            if not 左部:
                return False, "产生式左部不能为空"

            # 解析右部符号
            if 右部 == "ε" or 右部 == "epsilon":
                右部符号列表 = []
            else:
                右部符号列表 = [符号.strip() for 符号 in 右部.split() if 符号.strip()]

            产生式对象 = 产生式(编号, 左部, 右部符号列表)
            文法.添加产生式(产生式对象)

            return True, ""

        except Exception as e:
            return False, f"解析产生式时发生错误: {str(e)}"

    def _解析属性定义(self, 行内容: str, 文法: 通用属性文法, 行号: int) -> Tuple[bool, str]:
        """解析属性定义"""
        try:
            # 属性定义格式：符号.属性名 : 属性类型 数据类型 默认值 "描述"
            parts = 行内容.split(':')
            if len(parts) != 2:
                return False, "属性定义格式错误，缺少':'分隔符"

            符号属性部分 = parts[0].strip()
            属性信息部分 = parts[1].strip()

            # 解析符号.属性名
            if '.' not in 符号属性部分:
                return False, "属性定义格式错误，缺少'.'分隔符"

            符号名, 属性名 = 符号属性部分.split('.', 1)
            符号名 = 符号名.strip()
            属性名 = 属性名.strip()

            # 解析属性信息
            属性信息列表 = 属性信息部分.split()
            if len(属性信息列表) < 2:
                return False, "属性定义信息不完整"

            属性类型名 = 属性信息列表[0]
            数据类型名 = 属性信息列表[1]

            # 转换枚举类型
            try:
                属性类型对象 = 属性类型(属性类型名)
                数据类型对象 = 数据类型(数据类型名)
            except ValueError:
                return False, f"未知的属性类型或数据类型: {属性类型名}, {数据类型名}"

            # 解析默认值和描述
            默认值 = None
            描述 = ""

            if len(属性信息列表) > 2:
                默认值 = 属性信息列表[2]
                if 默认值 == '""' or 默认值 == "''":
                    默认值 = ""

            # 提取描述（引号内的内容）
            描述匹配 = re.search(r'"([^"]*)"', 属性信息部分)
            if 描述匹配:
                描述 = 描述匹配.group(1)

            # 创建属性定义
            属性定义对象 = 属性定义(属性名, 属性类型对象, 数据类型对象, 默认值, 描述)

            # 添加到文法符号
            if 符号名 not in 文法.文法符号:
                # 根据命名约定判断是否为终结符
                是否终结符 = not 符号名[0].isupper() if 符号名 else True
                文法.添加符号(文法符号(符号名, 是否终结符))

            文法.文法符号[符号名].添加属性(属性定义对象)

            return True, ""

        except Exception as e:
            return False, f"解析属性定义时发生错误: {str(e)}"

    def _解析语义规则(self, 行内容: str, 文法: 通用属性文法, 行号: int) -> Tuple[bool, str]:
        """解析语义规则"""
        try:
            # 语义规则格式：目标属性 := 表达式
            if ':=' not in 行内容:
                return False, "语义规则格式错误，缺少':='符号"

            目标属性, 表达式 = 行内容.split(':=', 1)
            目标属性 = 目标属性.strip()
            表达式 = 表达式.strip()

            if not 目标属性 or not 表达式:
                return False, "语义规则的目标属性和表达式都不能为空"

            # 提取依赖属性（简单的正则表达式匹配）
            依赖属性 = re.findall(r'\b\w+\.\w+\b', 表达式)

            语义规则对象 = 语义规则(目标属性, 表达式, 依赖属性)

            # 尝试从注释中提取产生式编号，或智能分配
            产生式编号 = self._提取产生式编号(行内容, 文法)
            if 产生式编号 >= 0:
                文法.添加语义规则(产生式编号, 语义规则对象)
            else:
                # 如果没有明确指定，添加到所有可能的产生式
                self._智能分配语义规则(语义规则对象, 文法)

            return True, ""

        except Exception as e:
            return False, f"解析语义规则时发生错误: {str(e)}"

    def _提取产生式编号(self, 行内容: str, 文法: 通用属性文法) -> int:
        """从注释中提取产生式编号"""
        # 查找注释中的产生式编号，格式如：# 产生式0
        匹配 = re.search(r'#.*产生式(\d+)', 行内容)
        if 匹配:
            return int(匹配.group(1))
        return -1

    def _智能分配语义规则(self, 规则: 语义规则, 文法: 通用属性文法):
        """智能分配语义规则到合适的产生式"""
        # 简单策略：根据目标属性的符号名匹配产生式左部
        目标符号 = 规则.目标属性.split('.')[0] if '.' in 规则.目标属性 else ""

        for i, 产生式对象 in enumerate(文法.产生式列表):
            if 产生式对象.左部 == 目标符号:
                文法.添加语义规则(i, 规则)
                break

# ==================== S属性文法语义分析器 ====================

class S属性文法分析器:
    """S属性文法语义分析器"""

    def __init__(self, 文法: 通用属性文法):
        self.文法 = 文法
        self.属性值表: Dict[str, Any] = {}
        self.符号表 = 符号表()
        self.分析步骤列表: List[分析步骤] = []
        self.当前步骤号 = 0

    def 验证S属性特性(self) -> Tuple[bool, List[str]]:
        """验证文法是否满足S属性特性"""
        错误列表 = []

        for 产生式编号, 规则列表 in self.文法.语义规则表.items():
            产生式对象 = self.文法.获取产生式(产生式编号)
            if not 产生式对象:
                continue

            for 规则 in 规则列表:
                # 检查目标属性是否为左部符号的综合属性
                if '.' in 规则.目标属性:
                    符号名, 属性名 = 规则.目标属性.split('.', 1)

                    if 符号名 != 产生式对象.左部:
                        错误列表.append(f"产生式{产生式编号}: 目标属性{规则.目标属性}不是左部符号的属性")
                        continue

                    # 检查是否为综合属性
                    符号对象 = self.文法.文法符号.get(符号名)
                    if 符号对象:
                        属性对象 = 符号对象.获取属性(属性名)
                        if 属性对象 and 属性对象.类型 != 属性类型.综合:
                            错误列表.append(f"产生式{产生式编号}: 属性{规则.目标属性}不是综合属性")

                # 检查依赖属性是否只来自右部符号
                for 依赖属性 in 规则.依赖属性:
                    if '.' in 依赖属性:
                        依赖符号名 = 依赖属性.split('.')[0]
                        if 依赖符号名 not in 产生式对象.右部 and 依赖符号名 != 产生式对象.左部:
                            错误列表.append(f"产生式{产生式编号}: 依赖属性{依赖属性}不来自产生式符号")

        return len(错误列表) == 0, 错误列表

    def 执行语义分析(self, 输入串: str, 语法分析结果: List[int]) -> Tuple[bool, List[分析步骤], str]:
        """执行S属性文法语义分析"""
        try:
            self.分析步骤列表.clear()
            self.属性值表.clear()
            self.符号表 = 符号表()
            self.当前步骤号 = 0

            self._记录步骤("开始S属性文法语义分析", f"输入串: {输入串}")

            # 初始化终结符属性
            词法单元列表 = self._词法分析(输入串)
            self._初始化终结符属性(词法单元列表)

            # 按照语法分析结果（自底向上归约顺序）执行语义动作
            for 产生式编号 in 语法分析结果:
                产生式对象 = self.文法.获取产生式(产生式编号)
                if 产生式对象:
                    成功, 错误 = self._执行产生式语义动作(产生式对象)
                    if not 成功:
                        return False, self.分析步骤列表, 错误

            self._记录步骤("S属性文法语义分析完成", "所有语义动作执行完毕")
            return True, self.分析步骤列表, ""

        except Exception as e:
            错误信息 = f"S属性文法语义分析过程中发生异常: {str(e)}"
            self._记录步骤("分析异常", 错误信息)
            return False, self.分析步骤列表, 错误信息

    def _词法分析(self, 输入串: str) -> List[Dict[str, Any]]:
        """简单的词法分析"""
        词法单元列表 = []
        tokens = 输入串.split()

        for token in tokens:
            if token.isdigit():
                词法单元列表.append({"类型": "数字", "值": int(token), "文本": token})
            elif token.replace('.', '').isdigit():
                词法单元列表.append({"类型": "浮点数", "值": float(token), "文本": token})
            elif token.isalpha():
                词法单元列表.append({"类型": "标识符", "值": token, "文本": token})
            else:
                词法单元列表.append({"类型": "操作符", "值": token, "文本": token})

        return 词法单元列表

    def _初始化终结符属性(self, 词法单元列表: List[Dict[str, Any]]):
        """初始化终结符的综合属性"""
        for i, 词法单元 in enumerate(词法单元列表):
            符号名 = 词法单元["文本"]

            # 为终结符创建属性值
            if 符号名 in self.文法.终结符集合:
                符号对象 = self.文法.文法符号.get(符号名)
                if 符号对象:
                    for 属性对象 in 符号对象.属性列表:
                        if 属性对象.类型 == 属性类型.综合:
                            属性键 = f"{符号名}_{i}.{属性对象.名称}"
                            if 属性对象.名称 == "值":
                                self.属性值表[属性键] = 词法单元["值"]
                            elif 属性对象.名称 == "类型":
                                self.属性值表[属性键] = 词法单元["类型"]
                            else:
                                self.属性值表[属性键] = 属性对象.默认值

    def _执行产生式语义动作(self, 产生式对象: 产生式) -> Tuple[bool, str]:
        """执行产生式的语义动作"""
        try:
            语义规则列表 = self.文法.获取产生式语义规则(产生式对象.编号)

            if not 语义规则列表:
                self._记录步骤(f"应用产生式{产生式对象.编号}", f"{产生式对象} (无语义规则)")
                return True, ""

            属性计算过程 = []

            for 规则 in 语义规则列表:
                成功, 结果, 错误 = self._执行语义规则(规则, 产生式对象)
                if not 成功:
                    return False, 错误

                属性计算过程.append(f"{规则.目标属性} := {结果}")

            # 记录分析步骤
            步骤 = 分析步骤(
                步骤号=self.当前步骤号,
                动作=f"应用产生式{产生式对象.编号}",
                描述=str(产生式对象),
                当前产生式=产生式对象,
                属性计算=属性计算过程,
                符号表状态=self._获取符号表快照()
            )
            self.分析步骤列表.append(步骤)
            self.当前步骤号 += 1

            return True, ""

        except Exception as e:
            return False, f"执行产生式{产生式对象.编号}的语义动作时发生错误: {str(e)}"

    def _执行语义规则(self, 规则: 语义规则, 产生式对象: 产生式) -> Tuple[bool, Any, str]:
        """执行单个语义规则"""
        try:
            # 简单的表达式求值（这里可以扩展为更复杂的表达式解析器）
            表达式 = 规则.表达式

            # 替换属性引用为实际值
            for 依赖属性 in 规则.依赖属性:
                if 依赖属性 in self.属性值表:
                    值 = self.属性值表[依赖属性]
                    表达式 = 表达式.replace(依赖属性, str(值))

            # 执行表达式（简单情况）
            if 表达式.isdigit():
                结果 = int(表达式)
            elif 表达式.replace('.', '').isdigit():
                结果 = float(表达式)
            elif 表达式.startswith('"') and 表达式.endswith('"'):
                结果 = 表达式[1:-1]
            else:
                # 尝试作为Python表达式求值（注意安全性）
                try:
                    结果 = eval(表达式, {"__builtins__": {}}, self.属性值表)
                except:
                    结果 = 表达式

            # 保存结果
            self.属性值表[规则.目标属性] = 结果

            return True, 结果, ""

        except Exception as e:
            return False, None, f"执行语义规则时发生错误: {str(e)}"

    def _记录步骤(self, 动作: str, 描述: str):
        """记录分析步骤"""
        步骤 = 分析步骤(
            步骤号=self.当前步骤号,
            动作=动作,
            描述=描述,
            符号表状态=self._获取符号表快照()
        )
        self.分析步骤列表.append(步骤)
        self.当前步骤号 += 1

    def _获取符号表快照(self) -> Dict[str, Any]:
        """获取符号表状态快照"""
        快照 = {}
        for 键, 符号项 in self.符号表.表项.items():
            快照[键] = {
                "名称": 符号项.名称,
                "类型": 符号项.类型,
                "值": 符号项.值,
                "作用域": 符号项.作用域
            }
        return 快照

# ==================== L属性文法语义分析器 ====================

class L属性文法分析器:
    """L属性文法语义分析器"""

    def __init__(self, 文法: 通用属性文法):
        self.文法 = 文法
        self.属性值表: Dict[str, Any] = {}
        self.符号表 = 符号表()
        self.分析步骤列表: List[分析步骤] = []
        self.当前步骤号 = 0

    def 验证L属性特性(self) -> Tuple[bool, List[str]]:
        """验证文法是否满足L属性特性"""
        错误列表 = []

        for 产生式对象 in self.文法.产生式列表:
            语义规则列表 = self.文法.获取产生式语义规则(产生式对象.编号)

            for 规则 in 语义规则列表:
                # 检查继承属性的依赖关系
                if self._是继承属性(规则.目标属性, 产生式对象):
                    if not self._检查继承属性依赖(规则, 产生式对象):
                        错误列表.append(f"产生式{产生式对象.编号}的语义规则违反L属性特性: {规则}")

        return len(错误列表) == 0, 错误列表

    def _是继承属性(self, 属性名: str, 产生式对象: 产生式) -> bool:
        """判断属性是否为继承属性"""
        if '.' not in 属性名:
            return False

        符号名, 属性 = 属性名.split('.', 1)

        # 如果符号在产生式右部，且属性类型为继承属性，则为继承属性
        if 符号名 in 产生式对象.右部:
            符号对象 = self.文法.文法符号.get(符号名)
            if 符号对象:
                属性定义对象 = 符号对象.获取属性(属性)
                return 属性定义对象 and 属性定义对象.类型 == 属性类型.继承

        return False

    def _检查继承属性依赖(self, 规则: 语义规则, 产生式对象: 产生式) -> bool:
        """检查继承属性的依赖关系是否满足L属性特性"""
        # 获取目标属性的符号在产生式右部的位置
        目标符号 = 规则.目标属性.split('.')[0] if '.' in 规则.目标属性 else ""

        # 找到目标符号在产生式右部的所有位置（可能有重复符号）
        目标位置列表 = []
        for i, 符号 in enumerate(产生式对象.右部):
            if 符号 == 目标符号:
                目标位置列表.append(i)

        if not 目标位置列表:
            return False  # 目标符号不在产生式右部

        # 对每个可能的目标位置检查依赖关系
        for 目标位置 in 目标位置列表:
            位置有效 = True

            # 检查每个依赖属性
            for 依赖属性 in 规则.依赖属性:
                if '.' not in 依赖属性:
                    continue

                依赖符号 = 依赖属性.split('.')[0]
                依赖有效 = False

                # 依赖属性可以来自：
                # 1. 产生式左部的继承属性
                if 依赖符号 == 产生式对象.左部:
                    依赖有效 = True

                # 2. 目标符号左边的符号的属性
                elif 依赖符号 in 产生式对象.右部:
                    for i, 符号 in enumerate(产生式对象.右部):
                        if 符号 == 依赖符号 and i < 目标位置:
                            依赖有效 = True
                            break

                if not 依赖有效:
                    位置有效 = False
                    break

            if 位置有效:
                return True

        return False

    def 执行语义分析(self, 输入串: str, 语法分析结果: List[int]) -> Tuple[bool, List[分析步骤], str]:
        """执行L属性文法语义分析"""
        try:
            self.分析步骤列表.clear()
            self.属性值表.clear()
            self.符号表 = 符号表()
            self.当前步骤号 = 0

            self._记录步骤("开始L属性文法语义分析", f"输入串: {输入串}")

            # 初始化终结符属性
            词法单元列表 = self._词法分析(输入串)
            self._初始化终结符属性(词法单元列表)

            # 按照语法分析结果执行语义动作
            for 产生式编号 in 语法分析结果:
                产生式对象 = self.文法.获取产生式(产生式编号)
                if 产生式对象:
                    成功, 错误 = self._执行产生式语义动作(产生式对象)
                    if not 成功:
                        return False, self.分析步骤列表, 错误

            self._记录步骤("L属性文法语义分析完成", "所有语义动作执行完毕")
            return True, self.分析步骤列表, ""

        except Exception as e:
            错误信息 = f"L属性文法语义分析过程中发生异常: {str(e)}"
            self._记录步骤("分析异常", 错误信息)
            return False, self.分析步骤列表, 错误信息

    def _词法分析(self, 输入串: str) -> List[Dict[str, Any]]:
        """简单的词法分析"""
        词法单元列表 = []
        tokens = 输入串.split()

        for token in tokens:
            if token.isdigit():
                词法单元列表.append({"类型": "数字", "值": int(token), "文本": token})
            elif token.replace('.', '').isdigit():
                词法单元列表.append({"类型": "浮点数", "值": float(token), "文本": token})
            elif token.isalpha():
                词法单元列表.append({"类型": "标识符", "值": token, "文本": token})
            else:
                词法单元列表.append({"类型": "操作符", "值": token, "文本": token})

        return 词法单元列表

    def _初始化终结符属性(self, 词法单元列表: List[Dict[str, Any]]):
        """初始化终结符的综合属性"""
        for i, 词法单元 in enumerate(词法单元列表):
            符号名 = 词法单元["文本"]

            # 为终结符创建属性值
            if 符号名 in self.文法.终结符集合:
                符号对象 = self.文法.文法符号.get(符号名)
                if 符号对象:
                    for 属性对象 in 符号对象.属性列表:
                        if 属性对象.类型 == 属性类型.综合:
                            属性键 = f"{符号名}_{i}.{属性对象.名称}"
                            if 属性对象.名称 == "值" or 属性对象.名称 == "val":
                                self.属性值表[属性键] = 词法单元["值"]
                            elif 属性对象.名称 == "类型" or 属性对象.名称 == "type":
                                self.属性值表[属性键] = 词法单元["类型"]
                            else:
                                self.属性值表[属性键] = 属性对象.默认值

    def _执行产生式语义动作(self, 产生式对象: 产生式) -> Tuple[bool, str]:
        """执行产生式的语义动作"""
        try:
            语义规则列表 = self.文法.获取产生式语义规则(产生式对象.编号)

            if not 语义规则列表:
                self._记录步骤(f"应用产生式{产生式对象.编号}", f"{产生式对象} (无语义规则)")
                return True, ""

            属性计算过程 = []

            # 按照L属性特性的要求，先计算继承属性，再计算综合属性
            for 规则 in 语义规则列表:
                成功, 结果, 错误 = self._执行语义规则(规则, 产生式对象)
                if not 成功:
                    return False, 错误

                属性计算过程.append(f"{规则.目标属性} := {结果}")

            # 记录分析步骤
            步骤 = 分析步骤(
                步骤号=self.当前步骤号,
                动作=f"应用产生式{产生式对象.编号}",
                描述=str(产生式对象),
                当前产生式=产生式对象,
                属性计算=属性计算过程,
                符号表状态=self._获取符号表快照()
            )
            self.分析步骤列表.append(步骤)
            self.当前步骤号 += 1

            return True, ""

        except Exception as e:
            return False, f"执行产生式{产生式对象.编号}的语义动作时发生错误: {str(e)}"

    def _执行语义规则(self, 规则: 语义规则, 产生式对象: 产生式) -> Tuple[bool, Any, str]:
        """执行单个语义规则"""
        try:
            表达式 = 规则.表达式

            # 处理特殊函数调用
            if 表达式.startswith('addtype('):
                return self._处理addtype函数(表达式)
            elif 表达式.startswith('newtemp('):
                return self._处理newtemp函数(表达式)

            # 替换属性引用为实际值
            for 依赖属性 in 规则.依赖属性:
                if 依赖属性 in self.属性值表:
                    值 = self.属性值表[依赖属性]
                    表达式 = 表达式.replace(依赖属性, str(值))

            # 执行表达式
            if 表达式.isdigit():
                结果 = int(表达式)
            elif 表达式.replace('.', '').isdigit():
                结果 = float(表达式)
            elif 表达式.startswith('"') and 表达式.endswith('"'):
                结果 = 表达式[1:-1]
            else:
                # 尝试作为Python表达式求值
                try:
                    结果 = eval(表达式, {"__builtins__": {}}, self.属性值表)
                except:
                    结果 = 表达式

            # 保存结果
            self.属性值表[规则.目标属性] = 结果

            return True, 结果, ""

        except Exception as e:
            return False, None, f"执行语义规则时发生错误: {str(e)}"

    def _处理addtype函数(self, 表达式: str) -> Tuple[bool, str, str]:
        """处理addtype函数调用"""
        try:
            # 解析addtype(name, type)
            import re
            匹配 = re.match(r'addtype\(([^,]+),\s*([^)]+)\)', 表达式)
            if 匹配:
                名称 = 匹配.group(1).strip()
                类型 = 匹配.group(2).strip()

                # 从属性值表中获取实际值
                if 名称 in self.属性值表:
                    名称 = self.属性值表[名称]
                if 类型 in self.属性值表:
                    类型 = self.属性值表[类型]

                # 添加到符号表
                符号项对象 = 符号表项(str(名称), str(类型))
                self.符号表.插入符号(符号项对象)

                return True, f"addtype({名称}, {类型})", ""
            else:
                return False, None, f"addtype函数格式错误: {表达式}"

        except Exception as e:
            return False, None, f"处理addtype函数时发生错误: {str(e)}"

    def _处理newtemp函数(self, 表达式: str) -> Tuple[bool, str, str]:
        """处理newtemp函数调用"""
        try:
            # 生成临时变量名
            临时变量名 = f"t{len(self.属性值表)}"
            return True, 临时变量名, ""
        except Exception as e:
            return False, None, f"处理newtemp函数时发生错误: {str(e)}"

    def _记录步骤(self, 动作: str, 描述: str):
        """记录分析步骤"""
        步骤 = 分析步骤(
            步骤号=self.当前步骤号,
            动作=动作,
            描述=描述,
            符号表状态=self._获取符号表快照()
        )
        self.分析步骤列表.append(步骤)
        self.当前步骤号 += 1

    def _获取符号表快照(self) -> Dict[str, Any]:
        """获取符号表状态快照"""
        快照 = {}
        for 键, 符号项 in self.符号表.表项.items():
            快照[键] = {
                "名称": 符号项.名称,
                "类型": 符号项.类型,
                "值": 符号项.值,
                "作用域": 符号项.作用域
            }
        return 快照

# ==================== 依赖图语义分析器 ====================

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

    def 清空(self):
        """清空依赖图"""
        self.节点表.clear()
        self.邻接表.clear()
        self.反向邻接表.clear()
        self.计算顺序.clear()

    def 检测循环依赖(self) -> Tuple[bool, List[str]]:
        """检测循环依赖，使用DFS + 三色标记法"""
        # 三色标记：0-白色(未访问)，1-灰色(正在访问)，2-黑色(已完成)
        颜色 = {节点ID: 0 for 节点ID in self.节点表}
        路径 = []

        def dfs(节点ID: str) -> bool:
            if 颜色[节点ID] == 1:  # 灰色节点，发现循环
                循环开始 = 路径.index(节点ID)
                return True

            if 颜色[节点ID] == 2:  # 黑色节点，已访问完成
                return False

            # 标记为灰色
            颜色[节点ID] = 1
            路径.append(节点ID)

            # 访问所有邻接节点
            for 邻接节点 in self.邻接表[节点ID]:
                if dfs(邻接节点):
                    return True

            # 标记为黑色
            颜色[节点ID] = 2
            路径.pop()
            return False

        # 对所有白色节点进行DFS
        for 节点ID in self.节点表:
            if 颜色[节点ID] == 0:
                if dfs(节点ID):
                    return True, 路径

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

    def 获取节点数量(self) -> int:
        """获取节点数量"""
        return len(self.节点表)

    def 获取边数量(self) -> int:
        """获取边数量"""
        return sum(len(邻接列表) for 邻接列表 in self.邻接表.values())

class 依赖图构建器:
    """依赖图构建器 - 根据属性文法和语法分析树构建依赖图"""

    def __init__(self, 文法: 通用属性文法):
        self.文法 = 文法
        self.依赖图对象 = 依赖图()
        self.节点计数器 = 0

    def 构建依赖图(self, 语法分析树: List[int]) -> Tuple[bool, 依赖图, str]:
        """根据语法分析树构建依赖图"""
        try:
            self.依赖图对象.清空()
            self.节点计数器 = 0
            节点映射 = {}  # 属性名 -> 节点ID

            # 第一阶段：为每个语义规则创建节点
            for 产生式编号 in 语法分析树:
                产生式对象 = self.文法.获取产生式(产生式编号)
                if not 产生式对象:
                    continue

                语义规则列表 = self.文法.获取产生式语义规则(产生式编号)
                for 规则 in 语义规则列表:
                    # 为目标属性创建节点（如果不存在）
                    if 规则.目标属性 not in 节点映射:
                        节点ID = f"node_{self.节点计数器}"
                        self.节点计数器 += 1

                        节点 = 依赖图节点(
                            节点ID=节点ID,
                            属性名=规则.目标属性,
                            计算表达式=规则.表达式
                        )

                        self.依赖图对象.添加节点(节点)
                        节点映射[规则.目标属性] = 节点ID

            # 第二阶段：建立依赖关系
            for 产生式编号 in 语法分析树:
                产生式对象 = self.文法.获取产生式(产生式编号)
                if not 产生式对象:
                    continue

                语义规则列表 = self.文法.获取产生式语义规则(产生式编号)
                for 规则 in 语义规则列表:
                    目标节点ID = 节点映射.get(规则.目标属性)
                    if not 目标节点ID:
                        continue

                    # 添加依赖边
                    for 依赖属性 in 规则.依赖属性:
                        依赖节点ID = 节点映射.get(依赖属性)
                        if 依赖节点ID and 依赖节点ID != 目标节点ID:
                            self.依赖图对象.添加依赖边(目标节点ID, 依赖节点ID)
                            # 更新节点的依赖列表
                            目标节点 = self.依赖图对象.获取节点(目标节点ID)
                            if 目标节点 and 依赖节点ID not in 目标节点.依赖节点:
                                目标节点.依赖节点.append(依赖节点ID)

            return True, self.依赖图对象, ""

        except Exception as e:
            return False, self.依赖图对象, f"构建依赖图时发生异常: {str(e)}"

    def _查找属性节点(self, 属性名: str) -> Optional[str]:
        """查找属性对应的节点ID"""
        for 节点ID, 节点 in self.依赖图对象.节点表.items():
            if 节点.属性名 == 属性名:
                return 节点ID
        return None

class 依赖图语义分析器:
    """依赖图语义分析器"""

    def __init__(self, 文法: 通用属性文法):
        self.文法 = 文法
        self.构建器 = 依赖图构建器(文法)
        self.分析步骤列表: List[分析步骤] = []
        self.当前步骤号 = 0
        self.依赖图对象: Optional[依赖图] = None

    def 执行语义分析(self, 输入串: str, 语法分析结果: List[int]) -> Tuple[bool, List[分析步骤], str]:
        """执行基于依赖图的语义分析"""
        try:
            self.分析步骤列表.clear()
            self.当前步骤号 = 0

            self._记录步骤("开始依赖图语义分析", f"输入串: {输入串}")

            # 构建依赖图
            成功, 依赖图对象, 错误信息 = self.构建器.构建依赖图(语法分析结果)
            if not 成功:
                self._记录步骤("依赖图构建失败", 错误信息)
                return False, self.分析步骤列表, 错误信息

            self.依赖图对象 = 依赖图对象
            self._记录步骤("依赖图构建成功", f"节点数: {依赖图对象.获取节点数量()}, 边数: {依赖图对象.获取边数量()}")

            # 执行拓扑排序
            成功, 计算顺序, 错误信息 = 依赖图对象.拓扑排序()
            if not 成功:
                self._记录步骤("拓扑排序失败", 错误信息)
                return False, self.分析步骤列表, 错误信息

            self._记录步骤("拓扑排序成功", f"计算顺序: {' -> '.join(计算顺序)}")

            # 初始化终结符属性
            self._初始化终结符属性(输入串)

            # 按照拓扑排序的顺序计算属性值
            for 节点ID in 计算顺序:
                节点 = 依赖图对象.获取节点(节点ID)
                if 节点 and not 节点.已计算:
                    成功, 错误 = self._计算节点属性(节点)
                    if not 成功:
                        self._记录步骤("属性计算失败", f"节点 {节点ID}: {错误}")
                        return False, self.分析步骤列表, 错误

            self._记录步骤("依赖图语义分析完成", "所有属性计算完毕")
            return True, self.分析步骤列表, ""

        except Exception as e:
            错误信息 = f"依赖图语义分析过程中发生异常: {str(e)}"
            self._记录步骤("分析异常", 错误信息)
            return False, self.分析步骤列表, 错误信息

    def _初始化终结符属性(self, 输入串: str):
        """初始化终结符属性"""
        词法单元列表 = self._词法分析(输入串)

        for i, 词法单元 in enumerate(词法单元列表):
            符号名 = 词法单元["文本"]

            if 符号名 in self.文法.终结符集合:
                符号对象 = self.文法.文法符号.get(符号名)
                if 符号对象:
                    for 属性对象 in 符号对象.属性列表:
                        if 属性对象.类型 == 属性类型.综合:
                            属性名 = f"{符号名}_{i}.{属性对象.名称}"

                            # 查找对应的节点并设置值
                            if self.依赖图对象:
                                for 节点 in self.依赖图对象.获取所有节点():
                                    if 节点.属性名 == 属性名:
                                        if 属性对象.名称 == "值" or 属性对象.名称 == "val":
                                            节点.属性值 = 词法单元["值"]
                                        elif 属性对象.名称 == "类型" or 属性对象.名称 == "type":
                                            节点.属性值 = 词法单元["类型"]
                                        else:
                                            节点.属性值 = 属性对象.默认值
                                        节点.已计算 = True

    def _词法分析(self, 输入串: str) -> List[Dict[str, Any]]:
        """简单的词法分析"""
        词法单元列表 = []
        tokens = 输入串.split()

        for token in tokens:
            if token.isdigit():
                词法单元列表.append({"类型": "数字", "值": int(token), "文本": token})
            elif token.replace('.', '').isdigit():
                词法单元列表.append({"类型": "浮点数", "值": float(token), "文本": token})
            elif token.isalpha():
                词法单元列表.append({"类型": "标识符", "值": token, "文本": token})
            else:
                词法单元列表.append({"类型": "操作符", "值": token, "文本": token})

        return 词法单元列表

    def _计算节点属性(self, 节点: 依赖图节点) -> Tuple[bool, str]:
        """计算单个节点的属性值"""
        try:
            if 节点.已计算:
                return True, ""

            # 检查所有依赖节点是否已计算
            for 依赖节点ID in 节点.依赖节点:
                if self.依赖图对象:
                    依赖节点 = self.依赖图对象.获取节点(依赖节点ID)
                    if 依赖节点 and not 依赖节点.已计算:
                        return False, f"依赖节点 {依赖节点ID} 尚未计算"

            # 计算属性值
            if 节点.计算表达式:
                节点.属性值 = self._计算表达式(节点.计算表达式)
            else:
                节点.属性值 = "未定义"

            节点.已计算 = True

            self._记录步骤("属性计算", f"计算 {节点.节点ID}: {节点.属性名} = {节点.属性值}")

            return True, ""

        except Exception as e:
            return False, f"计算节点属性时发生错误: {str(e)}"

    def _计算表达式(self, 表达式: str) -> Any:
        """计算表达式的值"""
        try:
            # 简单的表达式计算
            if 表达式.isdigit():
                return int(表达式)
            elif 表达式.replace('.', '').isdigit():
                return float(表达式)
            elif 表达式.startswith('"') and 表达式.endswith('"'):
                return 表达式[1:-1]
            else:
                # 尝试作为Python表达式求值
                try:
                    return eval(表达式, {"__builtins__": {}})
                except:
                    return 表达式
        except Exception:
            return 表达式

    def _记录步骤(self, 动作: str, 描述: str):
        """记录分析步骤"""
        步骤 = 分析步骤(
            步骤号=self.当前步骤号,
            动作=动作,
            描述=描述
        )
        self.分析步骤列表.append(步骤)
        self.当前步骤号 += 1

# ==================== 语义分析引擎管理器 ====================

class 语义分析引擎管理器:
    """统一管理多种语义分析方法的引擎"""

    def __init__(self):
        self.当前文法: Optional[通用属性文法] = None
        self.S属性分析器: Optional[S属性文法分析器] = None
        self.L属性分析器: Optional[L属性文法分析器] = None
        self.依赖图分析器: Optional[依赖图语义分析器] = None
        self.文法解析器 = 文法解析器()

    def 加载文法(self, 文法内容: str) -> Tuple[bool, List[str]]:
        """加载和解析文法"""
        成功, 文法, 错误列表 = self.文法解析器.解析文法文件(文法内容)

        if 成功:
            self.当前文法 = 文法
            # 初始化各种分析器
            self.S属性分析器 = S属性文法分析器(文法)
            self.L属性分析器 = L属性文法分析器(文法)
            self.依赖图分析器 = 依赖图语义分析器(文法)

        return 成功, 错误列表

    def 执行语义分析(self, 分析类型: 语义分析类型, 输入串: str,
                     语法分析结果: List[int]) -> Tuple[bool, List[分析步骤], str]:
        """执行指定类型的语义分析"""
        if not self.当前文法:
            return False, [], "未加载文法"

        if 分析类型 == 语义分析类型.S属性文法:
            if not self.S属性分析器:
                return False, [], "S属性文法分析器未初始化"
            return self.S属性分析器.执行语义分析(输入串, 语法分析结果)

        elif 分析类型 == 语义分析类型.L属性文法:
            if not self.L属性分析器:
                return False, [], "L属性文法分析器未初始化"
            return self.L属性分析器.执行语义分析(输入串, 语法分析结果)

        elif 分析类型 == 语义分析类型.依赖图:
            if not self.依赖图分析器:
                return False, [], "依赖图分析器未初始化"
            return self.依赖图分析器.执行语义分析(输入串, 语法分析结果)

        else:
            return False, [], f"不支持的分析类型: {分析类型}"

    def 验证文法特性(self, 分析类型: 语义分析类型) -> Tuple[bool, List[str]]:
        """验证文法是否满足指定分析类型的特性"""
        if not self.当前文法:
            return False, ["未加载文法"]

        if 分析类型 == 语义分析类型.S属性文法:
            if not self.S属性分析器:
                return False, ["S属性文法分析器未初始化"]
            return self.S属性分析器.验证S属性特性()

        elif 分析类型 == 语义分析类型.L属性文法:
            if not self.L属性分析器:
                return False, ["L属性文法分析器未初始化"]
            return self.L属性分析器.验证L属性特性()

        elif 分析类型 == 语义分析类型.依赖图:
            # 依赖图方法通常不需要特殊验证
            return True, []

        else:
            return False, [f"不支持的分析类型: {分析类型}"]

# ==================== GUI界面类 ====================

class 自定义语义分析器GUI:
    """自定义语义分析器GUI界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自定义语义分析程序 - 编译原理作业")
        self.root.geometry("1400x900")

        # 数据
        self.引擎 = 语义分析引擎管理器()
        self.当前分析类型 = 语义分析类型.S属性文法

        # 创建界面
        self.创建界面组件()

    def 创建界面组件(self):
        """创建界面组件"""
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个标签页
        self.创建文法输入标签页()
        self.创建语义分析标签页()
        self.创建分析结果标签页()
        self.创建帮助标签页()

    def 创建文法输入标签页(self):
        """创建文法输入标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="文法输入")

        # 左侧：文法输入区域
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="属性文法定义:", font=("微软雅黑", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # 文法输入框
        self.文法输入框 = scrolledtext.ScrolledText(left_frame, height=20, font=("Consolas", 10))
        self.文法输入框.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 设置默认文法
        默认文法 = """[文法]
E -> E + T
E -> T
T -> T * F
T -> F
F -> ( E )
F -> num

[属性定义]
E.val : 综合 整数 0 "表达式值"
T.val : 综合 整数 0 "项值"
F.val : 综合 整数 0 "因子值"
num.val : 综合 整数 0 "数字值"

[语义规则]
E.val := E.val + T.val
E.val := T.val
T.val := T.val * F.val
T.val := F.val
F.val := E.val
F.val := num.val"""

        self.文法输入框.insert(tk.END, 默认文法)

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(button_frame, text="解析文法", command=self.解析文法).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空", command=self.清空文法).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="加载文件", command=self.加载文法文件).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存文件", command=self.保存文法文件).pack(side=tk.LEFT)

        # 右侧：解析结果区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="解析结果:", font=("微软雅黑", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # 解析结果框
        self.解析结果框 = scrolledtext.ScrolledText(right_frame, height=20, font=("Consolas", 10))
        self.解析结果框.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 验证按钮区域
        verify_frame = ttk.Frame(right_frame)
        verify_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(verify_frame, text="验证S属性特性", command=lambda: self.验证文法特性(语义分析类型.S属性文法)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(verify_frame, text="验证L属性特性", command=lambda: self.验证文法特性(语义分析类型.L属性文法)).pack(side=tk.LEFT, padx=(0, 5))

    def 创建语义分析标签页(self):
        """创建语义分析标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="语义分析")

        # 上部：分析配置区域
        config_frame = ttk.LabelFrame(frame, text="分析配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 分析类型选择
        type_frame = ttk.Frame(config_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(type_frame, text="分析类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.分析类型变量 = tk.StringVar(value="S属性文法")
        分析类型选项 = ["S属性文法", "L属性文法", "依赖图"]

        for 类型 in 分析类型选项:
            ttk.Radiobutton(type_frame, text=类型, variable=self.分析类型变量,
                          value=类型, command=self.更新分析类型).pack(side=tk.LEFT, padx=(0, 20))

        # 输入配置
        input_frame = ttk.Frame(config_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="输入串:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.输入串输入框 = ttk.Entry(input_frame, width=30, font=("Consolas", 10))
        self.输入串输入框.pack(side=tk.LEFT, padx=(0, 20))
        self.输入串输入框.insert(0, "3 + 2 * 4")

        ttk.Label(input_frame, text="语法分析结果:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.语法分析结果输入框 = ttk.Entry(input_frame, width=40, font=("Consolas", 10))
        self.语法分析结果输入框.pack(side=tk.LEFT, padx=(0, 20))
        self.语法分析结果输入框.insert(0, "5 3 5 3 2 1 5 3 1 0")

        # 分析按钮
        ttk.Button(input_frame, text="开始语义分析", command=self.执行语义分析).pack(side=tk.LEFT, padx=(20, 0))

        # 下部：分析过程显示区域
        process_frame = ttk.LabelFrame(frame, text="分析过程", padding=10)
        process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # 分析步骤显示
        self.分析过程框 = scrolledtext.ScrolledText(process_frame, height=15, font=("Consolas", 9))
        self.分析过程框.pack(fill=tk.BOTH, expand=True)

    def 创建分析结果标签页(self):
        """创建分析结果标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="分析结果")

        # 创建左右分栏
        left_frame = ttk.LabelFrame(frame, text="属性值表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)

        right_frame = ttk.LabelFrame(frame, text="符号表", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # 属性值表
        self.属性值表框 = scrolledtext.ScrolledText(left_frame, height=20, font=("Consolas", 10))
        self.属性值表框.pack(fill=tk.BOTH, expand=True)

        # 符号表
        self.符号表框 = scrolledtext.ScrolledText(right_frame, height=20, font=("Consolas", 10))
        self.符号表框.pack(fill=tk.BOTH, expand=True)

    def 创建帮助标签页(self):
        """创建帮助标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="使用帮助")

        # 帮助内容
        help_frame = ttk.Frame(frame)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_text = scrolledtext.ScrolledText(help_frame, height=25, font=("微软雅黑", 10))
        help_text.pack(fill=tk.BOTH, expand=True)

        帮助内容 = """自定义语义分析程序 - 使用帮助

=== 程序简介 ===
本程序实现了多种语义分析方法的集成，包括：
• S属性文法语义分析
• L属性文法语义分析
• 依赖图语义分析

=== 使用步骤 ===

1. 文法输入
   • 在"文法输入"标签页中定义属性文法
   • 文法格式包含三个部分：[文法]、[属性定义]、[语义规则]
   • 点击"解析文法"按钮解析文法定义
   • 可以验证文法是否满足S属性或L属性特性

2. 语义分析
   • 在"语义分析"标签页中选择分析类型
   • 输入要分析的字符串和语法分析结果
   • 点击"开始语义分析"执行分析过程
   • 分析过程会详细显示每个步骤

3. 查看结果
   • 在"分析结果"标签页中查看属性值表和符号表
   • 可以看到所有属性的计算结果

=== 文法格式说明 ===

[文法]
E -> E + T
E -> T
T -> num

[属性定义]
E.val : 综合 整数 0 "表达式值"
T.val : 综合 整数 0 "项值"
num.val : 综合 整数 0 "数字值"

[语义规则]
E.val := E.val + T.val
E.val := T.val
T.val := num.val

=== 分析类型说明 ===

• S属性文法：只包含综合属性的文法
• L属性文法：包含综合属性和继承属性，满足L属性特性
• 依赖图：通过构建属性依赖图进行语义分析

=== 技术信息 ===
作者：王海翔
学号：2021060187
班级：计科2203
版本：v1.0.0
"""

        help_text.insert(tk.END, 帮助内容)
        help_text.config(state=tk.DISABLED)

    def 解析文法(self):
        """解析文法"""
        try:
            文法内容 = self.文法输入框.get(1.0, tk.END).strip()
            if not 文法内容:
                messagebox.showwarning("警告", "请输入文法定义")
                return

            成功, 错误列表 = self.引擎.加载文法(文法内容)

            # 显示解析结果
            self.解析结果框.delete(1.0, tk.END)

            if 成功:
                文法 = self.引擎.当前文法
                结果文本 = "=== 文法解析成功 ===\n\n"
                结果文本 += f"开始符号: {文法.开始符号}\n"
                结果文本 += f"终结符: {', '.join(sorted(文法.终结符集合))}\n"
                结果文本 += f"非终结符: {', '.join(sorted(文法.非终结符集合))}\n\n"

                结果文本 += "=== 产生式列表 ===\n"
                for i, 产生式 in enumerate(文法.产生式列表):
                    结果文本 += f"{i}: {产生式}\n"

                结果文本 += "\n=== 属性定义 ===\n"
                for 符号名, 符号 in 文法.文法符号.items():
                    if 符号.属性列表:
                        结果文本 += f"{符号名}:\n"
                        for 属性 in 符号.属性列表:
                            结果文本 += f"  {属性.名称} ({属性.类型.value})\n"

                结果文本 += "\n=== 语义规则 ===\n"
                for 产生式编号, 规则列表 in 文法.语义规则表.items():
                    if 规则列表:
                        结果文本 += f"产生式{产生式编号}:\n"
                        for 规则 in 规则列表:
                            结果文本 += f"  {规则}\n"

                messagebox.showinfo("成功", "文法解析成功！")
            else:
                结果文本 = "=== 文法解析失败 ===\n\n"
                结果文本 += "错误列表:\n"
                for 错误 in 错误列表:
                    结果文本 += f"• {错误}\n"

                messagebox.showerror("错误", f"文法解析失败，共发现 {len(错误列表)} 个错误")

            self.解析结果框.insert(tk.END, 结果文本)

        except Exception as e:
            messagebox.showerror("错误", f"解析文法时发生异常: {str(e)}")

    def 清空文法(self):
        """清空文法输入"""
        self.文法输入框.delete(1.0, tk.END)
        self.解析结果框.delete(1.0, tk.END)

    def 加载文法文件(self):
        """加载文法文件"""
        try:
            文件路径 = filedialog.askopenfilename(
                title="选择文法文件",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                with open(文件路径, 'r', encoding='utf-8') as f:
                    文法内容 = f.read()

                self.文法输入框.delete(1.0, tk.END)
                self.文法输入框.insert(tk.END, 文法内容)

                messagebox.showinfo("成功", "文法文件加载成功！")

        except Exception as e:
            messagebox.showerror("错误", f"加载文法文件时发生错误: {str(e)}")

    def 保存文法文件(self):
        """保存文法文件"""
        try:
            文件路径 = filedialog.asksaveasfilename(
                title="保存文法文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                文法内容 = self.文法输入框.get(1.0, tk.END)

                with open(文件路径, 'w', encoding='utf-8') as f:
                    f.write(文法内容)

                messagebox.showinfo("成功", "文法文件保存成功！")

        except Exception as e:
            messagebox.showerror("错误", f"保存文法文件时发生错误: {str(e)}")

    def 验证文法特性(self, 分析类型: 语义分析类型):
        """验证文法特性"""
        try:
            if not self.引擎.当前文法:
                messagebox.showwarning("警告", "请先解析文法")
                return

            验证成功, 验证错误 = self.引擎.验证文法特性(分析类型)

            if 验证成功:
                messagebox.showinfo("验证结果", f"该文法满足{分析类型.value}特性！")
            else:
                错误信息 = f"该文法不满足{分析类型.value}特性：\n\n"
                for 错误 in 验证错误:
                    错误信息 += f"• {错误}\n"
                messagebox.showerror("验证结果", 错误信息)

        except Exception as e:
            messagebox.showerror("错误", f"验证文法特性时发生异常: {str(e)}")

    def 更新分析类型(self):
        """更新分析类型"""
        类型映射 = {
            "S属性文法": 语义分析类型.S属性文法,
            "L属性文法": 语义分析类型.L属性文法,
            "依赖图": 语义分析类型.依赖图
        }

        选择的类型 = self.分析类型变量.get()
        self.当前分析类型 = 类型映射.get(选择的类型, 语义分析类型.S属性文法)

    def 执行语义分析(self):
        """执行语义分析"""
        try:
            if not self.引擎.当前文法:
                messagebox.showwarning("警告", "请先解析文法")
                return

            # 获取输入参数
            输入串 = self.输入串输入框.get().strip()
            语法分析结果文本 = self.语法分析结果输入框.get().strip()

            if not 输入串:
                messagebox.showwarning("警告", "请输入要分析的字符串")
                return

            if not 语法分析结果文本:
                messagebox.showwarning("警告", "请输入语法分析结果")
                return

            try:
                语法分析结果 = [int(x) for x in 语法分析结果文本.split()]
            except ValueError:
                messagebox.showerror("错误", "语法分析结果格式错误，应为数字序列")
                return

            # 执行语义分析
            分析成功, 分析步骤, 错误信息 = self.引擎.执行语义分析(
                self.当前分析类型, 输入串, 语法分析结果
            )

            # 显示分析过程
            self.分析过程框.delete(1.0, tk.END)

            if 分析成功:
                过程文本 = f"=== {self.当前分析类型.value}语义分析过程 ===\n\n"
                过程文本 += f"输入串: {输入串}\n"
                过程文本 += f"语法分析结果: {语法分析结果文本}\n\n"

                for 步骤 in 分析步骤:
                    过程文本 += f"步骤{步骤.步骤号}: {步骤.动作}\n"
                    if 步骤.描述:
                        过程文本 += f"  {步骤.描述}\n"
                    if hasattr(步骤, '属性计算') and 步骤.属性计算:
                        for 计算 in 步骤.属性计算:
                            过程文本 += f"  {计算}\n"
                    过程文本 += "\n"

                self.显示分析结果(分析步骤)
                messagebox.showinfo("成功", "语义分析完成！")
            else:
                过程文本 = f"=== {self.当前分析类型.value}语义分析失败 ===\n\n"
                过程文本 += f"错误信息: {错误信息}\n\n"

                if 分析步骤:
                    过程文本 += "已完成的步骤:\n"
                    for 步骤 in 分析步骤:
                        过程文本 += f"步骤{步骤.步骤号}: {步骤.动作}\n"
                        if 步骤.描述:
                            过程文本 += f"  {步骤.描述}\n"
                        过程文本 += "\n"

                messagebox.showerror("错误", f"语义分析失败：\n{错误信息}")

            self.分析过程框.insert(tk.END, 过程文本)

        except Exception as e:
            messagebox.showerror("错误", f"执行语义分析时发生异常: {str(e)}")

    def 显示分析结果(self, 分析步骤: List[分析步骤]):
        """显示分析结果"""
        try:
            # 清空结果显示区域
            self.属性值表框.delete(1.0, tk.END)
            self.符号表框.delete(1.0, tk.END)

            # 收集属性值和符号表信息
            属性值信息 = {}
            符号表信息 = {}

            for 步骤 in 分析步骤:
                if hasattr(步骤, '属性计算') and 步骤.属性计算:
                    for 计算 in 步骤.属性计算:
                        if ':=' in 计算:
                            属性名, 属性值 = 计算.split(':=', 1)
                            属性值信息[属性名.strip()] = 属性值.strip()

                if hasattr(步骤, '符号表状态') and 步骤.符号表状态:
                    符号表信息.update(步骤.符号表状态)

            # 显示属性值表
            属性值文本 = "=== 属性值表 ===\n\n"
            if 属性值信息:
                for 属性名, 属性值 in 属性值信息.items():
                    属性值文本 += f"{属性名} = {属性值}\n"
            else:
                属性值文本 += "无属性值信息\n"

            self.属性值表框.insert(tk.END, 属性值文本)

            # 显示符号表
            符号表文本 = "=== 符号表 ===\n\n"
            if 符号表信息:
                for 键, 符号项 in 符号表信息.items():
                    if isinstance(符号项, dict):
                        符号表文本 += f"{键}:\n"
                        符号表文本 += f"  名称: {符号项.get('名称', 'N/A')}\n"
                        符号表文本 += f"  类型: {符号项.get('类型', 'N/A')}\n"
                        符号表文本 += f"  值: {符号项.get('值', 'N/A')}\n"
                        符号表文本 += f"  作用域: {符号项.get('作用域', 'N/A')}\n\n"
            else:
                符号表文本 += "无符号表信息\n"

            self.符号表框.insert(tk.END, 符号表文本)

        except Exception as e:
            print(f"显示分析结果时发生错误: {e}")

    def 运行(self):
        """运行GUI应用"""
        self.root.mainloop()

if __name__ == "__main__":
    # 启动GUI界面
    try:
        app = 自定义语义分析器GUI()
        app.root.mainloop()
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        import traceback
        traceback.print_exc()
