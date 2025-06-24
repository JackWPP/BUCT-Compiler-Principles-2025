#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析程序
编译原理作业 - 题目6.2 L属性文法语义分析程序

作者: 王海翔
学号: 2021060187
班级: 计科2203
完成时间: 2025年6月

本程序实现了L属性文法的语义分析功能，包括：
• L属性文法的定义和解析
• 语义规则的定义和执行
• 属性值的计算和传递
• 符号表的管理和维护
• 语义分析过程的可视化展示
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import os
from collections import defaultdict, deque


# ==================== 核心数据结构定义 ====================

class 属性类型(Enum):
    """属性类型枚举"""
    综合属性 = "综合属性"  # 自下而上传递
    继承属性 = "继承属性"  # 自上而下传递


class 符号类型(Enum):
    """文法符号类型枚举"""
    终结符 = "终结符"
    非终结符 = "非终结符"


@dataclass
class 属性定义:
    """属性定义类"""
    名称: str                    # 属性名称
    类型: 属性类型               # 属性类型（综合/继承）
    数据类型: str = "字符串"     # 数据类型（字符串、整数、浮点数等）
    默认值: Any = None           # 默认值
    描述: str = ""               # 属性描述


@dataclass
class 文法符号:
    """文法符号类"""
    名称: str                    # 符号名称
    类型: 符号类型               # 符号类型（终结符/非终结符）
    属性列表: List[属性定义] = field(default_factory=list)  # 符号的属性列表

    def 添加属性(self, 属性: 属性定义):
        """添加属性到符号"""
        self.属性列表.append(属性)

    def 获取属性(self, 属性名: str) -> Optional[属性定义]:
        """根据名称获取属性"""
        for 属性 in self.属性列表:
            if 属性.名称 == 属性名:
                return 属性
        return None


@dataclass
class 产生式:
    """产生式类"""
    左部: str                    # 产生式左部（非终结符）
    右部: List[str]              # 产生式右部（符号序列）
    语义规则: List[str] = field(default_factory=list)  # 语义规则列表
    编号: int = 0                # 产生式编号

    def __str__(self):
        右部字符串 = " ".join(self.右部) if self.右部 else "ε"
        return f"{self.左部} -> {右部字符串}"


@dataclass
class 语义规则:
    """语义规则类"""
    目标属性: str                # 目标属性（左部）
    表达式: str                  # 计算表达式（右部）
    依赖属性: List[str] = field(default_factory=list)  # 依赖的属性列表
    动作类型: str = "赋值"       # 动作类型（赋值、函数调用等）

    def __str__(self):
        return f"{self.目标属性} := {self.表达式}"


@dataclass
class 符号表项:
    """符号表项类"""
    名称: str                    # 标识符名称
    类型: str = ""               # 标识符类型
    值: Any = None               # 标识符值
    作用域: str = "全局"         # 作用域
    行号: int = 0                # 定义行号
    其他信息: Dict[str, Any] = field(default_factory=dict)  # 其他信息


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

    def 添加符号(self, 符号: 符号表项):
        """添加符号到符号表"""
        完整名称 = f"{self.当前作用域()}.{符号.名称}"
        符号.作用域 = self.当前作用域()
        self.表项[完整名称] = 符号

    def 查找符号(self, 名称: str) -> Optional[符号表项]:
        """查找符号"""
        # 先在当前作用域查找
        for 作用域 in reversed(self.作用域栈):
            完整名称 = f"{作用域}.{名称}"
            if 完整名称 in self.表项:
                return self.表项[完整名称]
        return None

    def 更新符号(self, 名称: str, **kwargs):
        """更新符号信息"""
        符号 = self.查找符号(名称)
        if 符号:
            for key, value in kwargs.items():
                if hasattr(符号, key):
                    setattr(符号, key, value)
                else:
                    符号.其他信息[key] = value


@dataclass
class 分析步骤:
    """语义分析步骤记录"""
    步骤号: int                  # 步骤编号
    动作: str                    # 执行的动作
    当前产生式: Optional[产生式] = None  # 当前使用的产生式
    属性计算: List[str] = field(default_factory=list)  # 属性计算过程
    符号表状态: Dict[str, Any] = field(default_factory=dict)  # 符号表状态快照
    错误信息: str = ""           # 错误信息

    def __str__(self):
        return f"步骤{self.步骤号}: {self.动作}"


# ==================== L属性文法类 ====================

class L属性文法:
    """L属性文法类"""

    def __init__(self):
        self.文法符号: Dict[str, 文法符号] = {}      # 文法符号表
        self.产生式列表: List[产生式] = []            # 产生式列表
        self.语义规则表: Dict[int, List[语义规则]] = {}  # 语义规则表（按产生式编号索引）
        self.开始符号: str = ""                      # 开始符号
        self.终结符集合: Set[str] = set()            # 终结符集合
        self.非终结符集合: Set[str] = set()          # 非终结符集合

    def 添加文法符号(self, 符号: 文法符号):
        """添加文法符号"""
        self.文法符号[符号.名称] = 符号
        if 符号.类型 == 符号类型.终结符:
            self.终结符集合.add(符号.名称)
        else:
            self.非终结符集合.add(符号.名称)

    def 添加产生式(self, 产生式: 产生式):
        """添加产生式"""
        产生式.编号 = len(self.产生式列表)
        self.产生式列表.append(产生式)

        # 自动添加符号到文法符号表
        if 产生式.左部 not in self.文法符号:
            左部符号 = 文法符号(产生式.左部, 符号类型.非终结符)
            self.添加文法符号(左部符号)

        for 符号名 in 产生式.右部:
            if 符号名 not in self.文法符号 and 符号名 != "ε":
                # 根据符号名判断是否为终结符（简单规则：小写或特殊字符为终结符）
                if 符号名.islower() or not 符号名.isalpha():
                    符号 = 文法符号(符号名, 符号类型.终结符)
                else:
                    符号 = 文法符号(符号名, 符号类型.非终结符)
                self.添加文法符号(符号)

    def 添加语义规则(self, 产生式编号: int, 规则: 语义规则):
        """为产生式添加语义规则"""
        if 产生式编号 not in self.语义规则表:
            self.语义规则表[产生式编号] = []
        self.语义规则表[产生式编号].append(规则)

    def 获取产生式语义规则(self, 产生式编号: int) -> List[语义规则]:
        """获取产生式的语义规则"""
        return self.语义规则表.get(产生式编号, [])

    def 验证L属性特性(self) -> Tuple[bool, List[str]]:
        """验证文法是否满足L属性特性"""
        错误列表 = []

        for 产生式 in self.产生式列表:
            语义规则列表 = self.获取产生式语义规则(产生式.编号)

            for 规则 in 语义规则列表:
                # 检查继承属性的依赖关系
                if self._是继承属性(规则.目标属性, 产生式):
                    if not self._检查继承属性依赖(规则, 产生式):
                        错误列表.append(f"产生式{产生式.编号}的语义规则违反L属性特性: {规则}")

        return len(错误列表) == 0, 错误列表

    def _是继承属性(self, 属性名: str, 产生式: 产生式) -> bool:
        """判断属性是否为继承属性"""
        # 解析属性名（格式：符号.属性）
        if '.' not in 属性名:
            return False

        符号名, 属性 = 属性名.split('.', 1)

        # 如果符号在产生式右部，且属性类型为继承属性，则为继承属性
        if 符号名 in 产生式.右部:
            符号 = self.文法符号.get(符号名)
            if 符号:
                属性定义 = 符号.获取属性(属性)
                return 属性定义 and 属性定义.类型 == 属性类型.继承属性

        return False

    def _检查继承属性依赖(self, 规则: 语义规则, 产生式: 产生式) -> bool:
        """检查继承属性的依赖关系是否满足L属性特性"""
        # L属性特性：继承属性只能依赖于左边符号的属性和父节点的继承属性
        符号名 = 规则.目标属性.split('.')[0]
        符号位置 = -1

        # 找到符号在产生式右部的位置
        for i, 右部符号 in enumerate(产生式.右部):
            if 右部符号 == 符号名:
                符号位置 = i
                break

        if 符号位置 == -1:
            return False

        # 检查依赖属性
        for 依赖属性 in 规则.依赖属性:
            if '.' not in 依赖属性:
                continue

            依赖符号名 = 依赖属性.split('.')[0]

            # 如果依赖符号在当前符号右边，则违反L属性特性
            if 依赖符号名 in 产生式.右部:
                依赖位置 = 产生式.右部.index(依赖符号名)
                if 依赖位置 > 符号位置:
                    return False

        return True


# ==================== 文法解析器类 ====================

class L属性文法解析器:
    """L属性文法解析器类"""

    def __init__(self):
        self.当前文法: Optional[L属性文法] = None

    def 解析文法文件(self, 文件内容: str) -> Tuple[bool, L属性文法, List[str]]:
        """解析L属性文法文件"""
        错误列表 = []
        文法 = L属性文法()

        try:
            行列表 = 文件内容.strip().split('\n')
            当前模式 = None  # 当前解析模式：'文法'、'属性'、'语义规则'
            当前产生式编号 = -1

            for 行号, 行内容 in enumerate(行列表, 1):
                行内容 = 行内容.strip()

                # 跳过空行和注释
                if not 行内容 or 行内容.startswith('#') or 行内容.startswith('//'):
                    continue

                # 解析模式标记
                if 行内容.startswith('[') and 行内容.endswith(']'):
                    当前模式 = 行内容[1:-1].strip()
                    continue

                # 根据当前模式解析内容
                if 当前模式 == '文法' or 当前模式 is None:
                    成功, 错误 = self._解析产生式(行内容, 文法, 行号)
                    if not 成功:
                        错误列表.append(f"第{行号}行: {错误}")
                    else:
                        当前产生式编号 = len(文法.产生式列表) - 1

                elif 当前模式 == '属性定义':
                    成功, 错误 = self._解析属性定义(行内容, 文法, 行号)
                    if not 成功:
                        错误列表.append(f"第{行号}行: {错误}")

                elif 当前模式 == '语义规则':
                    成功, 错误 = self._解析语义规则(行内容, 文法, 行号)
                    if not 成功:
                        错误列表.append(f"第{行号}行: {错误}")

            # 设置开始符号
            if 文法.产生式列表:
                文法.开始符号 = 文法.产生式列表[0].左部

            # 验证L属性特性
            是L属性, L属性错误 = 文法.验证L属性特性()
            if not 是L属性:
                错误列表.extend(L属性错误)

            self.当前文法 = 文法
            return len(错误列表) == 0, 文法, 错误列表

        except Exception as e:
            错误列表.append(f"解析过程中发生异常: {str(e)}")
            return False, 文法, 错误列表

    def _解析产生式(self, 行内容: str, 文法: L属性文法, 行号: int) -> Tuple[bool, str]:
        """解析产生式"""
        try:
            # 产生式格式：A -> B C | D E
            if '->' not in 行内容:
                return False, "产生式格式错误，缺少'->'符号"

            左部, 右部字符串 = 行内容.split('->', 1)
            左部 = 左部.strip()

            if not 左部:
                return False, "产生式左部不能为空"

            # 处理多个候选式（用|分隔）
            候选式列表 = [候选式.strip() for 候选式 in 右部字符串.split('|')]

            for 候选式 in 候选式列表:
                if not 候选式:
                    右部 = ["ε"]
                else:
                    右部 = 候选式.split()

                产生式对象 = 产生式(左部, 右部)
                文法.添加产生式(产生式对象)

            return True, ""

        except Exception as e:
            return False, f"解析产生式时发生错误: {str(e)}"

    def _解析属性定义(self, 行内容: str, 文法: L属性文法, 行号: int) -> Tuple[bool, str]:
        """解析属性定义"""
        try:
            # 属性定义格式：符号.属性名 : 属性类型 [数据类型] [默认值] [描述]
            if ':' not in 行内容:
                return False, "属性定义格式错误，缺少':'符号"

            属性部分, 定义部分 = 行内容.split(':', 1)
            属性部分 = 属性部分.strip()
            定义部分 = 定义部分.strip()

            if '.' not in 属性部分:
                return False, "属性定义格式错误，缺少'.'符号"

            符号名, 属性名 = 属性部分.split('.', 1)
            符号名 = 符号名.strip()
            属性名 = 属性名.strip()

            # 解析定义部分
            定义项 = 定义部分.split()
            if not 定义项:
                return False, "属性定义不能为空"

            属性类型名 = 定义项[0]
            数据类型 = 定义项[1] if len(定义项) > 1 else "字符串"
            默认值 = 定义项[2] if len(定义项) > 2 else None
            描述 = " ".join(定义项[3:]) if len(定义项) > 3 else ""

            # 创建属性定义
            if 属性类型名 == "综合" or 属性类型名 == "综合属性":
                类型 = 属性类型.综合属性
            elif 属性类型名 == "继承" or 属性类型名 == "继承属性":
                类型 = 属性类型.继承属性
            else:
                return False, f"未知的属性类型: {属性类型名}"

            属性定义对象 = 属性定义(属性名, 类型, 数据类型, 默认值, 描述)

            # 添加到对应的文法符号
            if 符号名 not in 文法.文法符号:
                # 根据符号名判断类型
                if 符号名.islower() or not 符号名.isalpha():
                    符号 = 文法符号(符号名, 符号类型.终结符)
                else:
                    符号 = 文法符号(符号名, 符号类型.非终结符)
                文法.添加文法符号(符号)

            文法.文法符号[符号名].添加属性(属性定义对象)
            return True, ""

        except Exception as e:
            return False, f"解析属性定义时发生错误: {str(e)}"

    def _解析语义规则(self, 行内容: str, 文法: L属性文法, 行号: int) -> Tuple[bool, str]:
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

            # 尝试从注释中提取产生式编号
            产生式编号 = self._提取产生式编号(行内容, 文法)
            if 产生式编号 >= 0:
                文法.添加语义规则(产生式编号, 语义规则对象)
            else:
                # 如果没有明确指定，添加到所有可能的产生式
                self._智能分配语义规则(语义规则对象, 文法)

            return True, ""

        except Exception as e:
            return False, f"解析语义规则时发生错误: {str(e)}"

    def _提取产生式编号(self, 行内容: str, 文法: L属性文法) -> int:
        """从注释中提取产生式编号"""
        # 查找形如"产生式0:"、"产生式 0:"的模式
        import re
        match = re.search(r'产生式\s*(\d+)', 行内容)
        if match:
            编号 = int(match.group(1))
            if 0 <= 编号 < len(文法.产生式列表):
                return 编号
        return -1

    def _智能分配语义规则(self, 规则: 语义规则, 文法: L属性文法):
        """智能分配语义规则到合适的产生式"""
        # 根据目标属性的符号名找到对应的产生式
        if '.' in 规则.目标属性:
            符号名 = 规则.目标属性.split('.')[0]

            # 查找左部为该符号的产生式
            for i, 产生式 in enumerate(文法.产生式列表):
                if 产生式.左部 == 符号名:
                    文法.添加语义规则(i, 规则)
                    return

        # 如果找不到合适的产生式，添加到第一个产生式
        if 文法.产生式列表:
            文法.添加语义规则(0, 规则)


# ==================== 语义分析引擎类 ====================

class 语义分析引擎:
    """L属性文法语义分析引擎"""

    def __init__(self, 文法: L属性文法):
        self.文法 = 文法
        self.符号表 = 符号表()
        self.分析步骤列表: List[分析步骤] = []
        self.属性值表: Dict[str, Any] = {}  # 存储属性值
        self.当前步骤号 = 0

    def 执行语义分析(self, 输入串: str, 语法分析结果: List[int]) -> Tuple[bool, List[分析步骤], str]:
        """
        执行语义分析
        输入串: 要分析的输入串
        语法分析结果: 语法分析器返回的产生式序列
        返回: (是否成功, 分析步骤列表, 错误信息)
        """
        try:
            self.分析步骤列表.clear()
            self.属性值表.clear()
            self.符号表 = 符号表()
            self.当前步骤号 = 0

            # 记录开始分析
            self._记录步骤("开始语义分析", f"输入串: {输入串}")

            # 初始化终结符的综合属性（由词法分析器提供）
            词法单元列表 = self._词法分析(输入串)
            self._初始化终结符属性(词法单元列表)

            # 按照语法分析结果执行语义动作
            for 产生式编号 in 语法分析结果:
                if 产生式编号 < len(self.文法.产生式列表):
                    产生式 = self.文法.产生式列表[产生式编号]
                    成功, 错误 = self._执行产生式语义动作(产生式)
                    if not 成功:
                        return False, self.分析步骤列表, 错误

            self._记录步骤("语义分析完成", "所有语义动作执行完毕")
            return True, self.分析步骤列表, ""

        except Exception as e:
            错误信息 = f"语义分析过程中发生异常: {str(e)}"
            self._记录步骤("分析异常", 错误信息)
            return False, self.分析步骤列表, 错误信息

    def _词法分析(self, 输入串: str) -> List[Tuple[str, str]]:
        """简单的词法分析"""
        词法单元列表 = []
        单词列表 = 输入串.split()

        for 单词 in 单词列表:
            # 简单的词法分析规则
            if 单词.isdigit():
                词法单元列表.append(("数字", 单词))
            elif 单词.isalpha() or (单词.isalnum() and any(c.isalpha() for c in 单词)):
                if 单词 in ['int', 'float', 'char', 'string']:
                    词法单元列表.append(("类型", 单词))
                else:
                    词法单元列表.append(("标识符", 单词))
            elif 单词 in ['+', '-', '*', '/', '=', '(', ')', ';', ',']:
                词法单元列表.append(("操作符", 单词))
            else:
                词法单元列表.append(("其他", 单词))

        return 词法单元列表

    def _初始化终结符属性(self, 词法单元列表: List[Tuple[str, str]]):
        """初始化终结符的综合属性"""
        for i, (类型, 值) in enumerate(词法单元列表):
            属性键 = f"终结符_{i}.值"
            self.属性值表[属性键] = 值
            属性键 = f"终结符_{i}.类型"
            self.属性值表[属性键] = 类型

    def _执行产生式语义动作(self, 产生式: 产生式) -> Tuple[bool, str]:
        """执行产生式的语义动作"""
        try:
            语义规则列表 = self.文法.获取产生式语义规则(产生式.编号)

            if not 语义规则列表:
                self._记录步骤(f"应用产生式{产生式.编号}", f"{产生式} (无语义规则)")
                return True, ""

            属性计算过程 = []

            for 规则 in 语义规则列表:
                成功, 结果, 错误 = self._执行语义规则(规则, 产生式)
                if not 成功:
                    return False, 错误

                属性计算过程.append(f"{规则.目标属性} := {结果}")

            # 记录分析步骤
            步骤 = 分析步骤(
                步骤号=self.当前步骤号,
                动作=f"应用产生式{产生式.编号}",
                当前产生式=产生式,
                属性计算=属性计算过程,
                符号表状态=self._获取符号表快照()
            )
            self.分析步骤列表.append(步骤)
            self.当前步骤号 += 1

            return True, ""

        except Exception as e:
            return False, f"执行产生式{产生式.编号}的语义动作时发生错误: {str(e)}"

    def _执行语义规则(self, 规则: 语义规则, 产生式: 产生式) -> Tuple[bool, Any, str]:
        """执行单个语义规则"""
        try:
            # 计算表达式（不预先检查依赖，在计算时动态处理）
            结果 = self._计算表达式(规则.表达式, 产生式)

            # 存储结果
            self.属性值表[规则.目标属性] = 结果

            # 如果是符号表操作，执行相应操作
            if "addtype(" in 规则.表达式:
                self._执行符号表操作(规则.表达式, 结果)

            return True, 结果, ""

        except Exception as e:
            return False, None, f"执行语义规则时发生错误: {str(e)}"

    def _计算表达式(self, 表达式: str, 产生式: 产生式) -> Any:
        """计算语义表达式"""
        # 处理直接的字符串常量
        if 表达式.startswith('"') and 表达式.endswith('"'):
            return 表达式.strip('"')

        # 处理特殊函数调用
        if "addtype(" in 表达式:
            return self._处理addtype函数调用(表达式)
        elif 表达式.startswith("newtemp("):
            return self._处理newtemp函数()

        # 替换表达式中的属性引用
        计算表达式 = 表达式
        属性引用列表 = re.findall(r'\b\w+\.\w+\b', 表达式)

        for 属性引用 in 属性引用列表:
            # 尝试获取属性值，如果不存在则使用默认值或推断值
            值 = self._获取或推断属性值(属性引用, 产生式)
            if isinstance(值, str):
                计算表达式 = 计算表达式.replace(属性引用, f'"{值}"')
            else:
                计算表达式 = 计算表达式.replace(属性引用, str(值))

        # 处理算术表达式
        if "+" in 计算表达式 or "-" in 计算表达式 or "*" in 计算表达式:
            try:
                return eval(计算表达式)
            except:
                return 计算表达式
        else:
            return 计算表达式.strip('"')

    def _获取或推断属性值(self, 属性引用: str, 产生式: 产生式) -> Any:
        """获取或推断属性值"""
        # 如果属性值已存在，直接返回
        if 属性引用 in self.属性值表:
            return self.属性值表[属性引用]

        # 尝试推断属性值
        符号名, 属性名 = 属性引用.split('.')

        # 对于类型属性，根据终结符推断
        if 属性名 == 'type' and 符号名 == 'T':
            # 查找输入串中的类型关键字
            for 键, 值 in self.属性值表.items():
                if '终结符' in 键 and 值 in ['int', 'float', 'char', 'string']:
                    return 值
            return "int"  # 默认类型

        # 对于标识符名称，从终结符中获取
        if 属性名 == 'name' and 符号名 == 'id':
            # 查找标识符终结符
            for 键, 值 in self.属性值表.items():
                if '终结符' in 键 and isinstance(值, str) and 值.isalpha():
                    if 值 not in ['int', 'float', 'char', 'string', ',']:
                        return 值
            return "unknown"  # 默认标识符名

        # 其他情况返回空字符串
        return ""

    def _处理addtype函数调用(self, 表达式: str) -> str:
        """处理addtype函数调用"""
        try:
            # 查找addtype函数调用
            start = 表达式.find("addtype(")
            if start == -1:
                return "未找到addtype函数调用"

            # 提取参数部分
            参数开始 = start + 8  # "addtype("的长度
            参数结束 = 表达式.find(")", 参数开始)
            if 参数结束 == -1:
                return "addtype函数格式错误"

            参数部分 = 表达式[参数开始:参数结束]
            参数列表 = [参数.strip() for 参数 in 参数部分.split(',')]

            if len(参数列表) >= 2:
                # 解析参数，可能包含属性引用
                标识符名参数 = 参数列表[0]
                类型名参数 = 参数列表[1]

                # 解析标识符名
                if '.' in 标识符名参数:
                    # 属性引用，需要获取实际值
                    标识符名 = self._获取或推断属性值(标识符名参数, None)
                else:
                    标识符名 = 标识符名参数.strip('"')

                # 解析类型名
                if '.' in 类型名参数:
                    # 属性引用，需要获取实际值
                    类型名 = self._获取或推断属性值(类型名参数, None)
                else:
                    类型名 = 类型名参数.strip('"')

                # 添加到符号表
                符号项 = 符号表项(标识符名, 类型名)
                self.符号表.添加符号(符号项)

                return f"已将 {标识符名}:{类型名} 添加到符号表"

            return "addtype函数参数不足"

        except Exception as e:
            return f"处理addtype函数时发生错误: {str(e)}"

    def _处理newtemp函数(self) -> str:
        """处理newtemp函数调用"""
        # 生成临时变量名
        临时变量名 = f"t{len([k for k in self.属性值表.keys() if k.startswith('temp_')])}"
        return 临时变量名

    def _执行符号表操作(self, 表达式: str, 结果: Any):
        """执行符号表相关操作"""
        # 这里可以扩展更多符号表操作
        pass

    def _记录步骤(self, 动作: str, 描述: str = ""):
        """记录分析步骤"""
        步骤 = 分析步骤(
            步骤号=self.当前步骤号,
            动作=动作,
            符号表状态=self._获取符号表快照()
        )
        if 描述:
            步骤.错误信息 = 描述

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


# ==================== GUI界面类 ====================

class L属性文法分析器GUI:
    """L属性文法语义分析器GUI界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("L属性文法语义分析程序 - 编译原理作业")
        self.root.geometry("1400x900")

        # 数据
        self.当前文法: Optional[L属性文法] = None
        self.解析器 = L属性文法解析器()
        self.分析引擎: Optional[语义分析引擎] = None

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
        self.创建符号表标签页()
        self.创建帮助标签页()

    def 创建文法输入标签页(self):
        """创建文法输入标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="L属性文法输入")

        # 上方控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="加载文法文件", command=self.加载文法文件).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="保存文法文件", command=self.保存文法文件).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="解析文法", command=self.解析文法).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="验证L属性", command=self.验证L属性).pack(side=tk.LEFT)

        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧文法输入区域
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)

        ttk.Label(left_frame, text="L属性文法定义:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 文法输入文本框
        self.文法输入框 = scrolledtext.ScrolledText(left_frame, height=25, font=("Consolas", 10))
        self.文法输入框.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 设置默认示例
        示例文法 = """# L属性文法示例：简单的声明语句
# 格式说明：
# [文法] - 产生式定义
# [属性定义] - 符号属性定义
# [语义规则] - 语义动作定义

[文法]
D -> T L
T -> int | float | char
L -> L , id | id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承的类型信息"
id.name : 综合 字符串 "" "标识符名称"

[语义规则]
# 产生式0: D -> T L 的语义规则
L.in := T.type

# 产生式1: T -> int 的语义规则
T.type := "int"

# 产生式2: T -> float 的语义规则
T.type := "float"

# 产生式3: T -> char 的语义规则
T.type := "char"

# 产生式4: L -> L1 , id 的语义规则
L1.in := L.in
id.entry := addtype(id.name, L.in)

# 产生式5: L -> id 的语义规则
id.entry := addtype(id.name, L.in)
"""
        self.文法输入框.insert(tk.END, 示例文法)

        # 右侧解析结果区域
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        ttk.Label(right_frame, text="解析结果:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 解析结果文本框
        self.解析结果框 = scrolledtext.ScrolledText(right_frame, height=25, font=("Consolas", 10))
        self.解析结果框.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def 创建语义分析标签页(self):
        """创建语义分析标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="语义分析过程")

        # 上方控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="输入串:").pack(side=tk.LEFT)
        self.输入串输入框 = ttk.Entry(control_frame, width=30, font=("Consolas", 10))
        self.输入串输入框.pack(side=tk.LEFT, padx=(5, 10))
        self.输入串输入框.insert(0, "int a , b , c")

        ttk.Button(control_frame, text="开始语义分析", command=self.开始语义分析).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="清空结果", command=self.清空分析结果).pack(side=tk.LEFT)

        # 创建分割窗口
        paned_window = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 上方分析步骤区域
        top_frame = ttk.Frame(paned_window)
        paned_window.add(top_frame, weight=2)

        ttk.Label(top_frame, text="语义分析步骤:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 分析步骤表格
        columns = ("步骤", "动作", "产生式", "属性计算")
        self.分析步骤表格 = ttk.Treeview(top_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.分析步骤表格.heading(col, text=col)
            self.分析步骤表格.column(col, width=200)

        # 添加滚动条
        步骤滚动条 = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=self.分析步骤表格.yview)
        self.分析步骤表格.configure(yscrollcommand=步骤滚动条.set)

        self.分析步骤表格.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
        步骤滚动条.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))

        # 下方详细信息区域
        bottom_frame = ttk.Frame(paned_window)
        paned_window.add(bottom_frame, weight=1)

        ttk.Label(bottom_frame, text="详细信息:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.详细信息框 = scrolledtext.ScrolledText(bottom_frame, height=8, font=("Consolas", 10))
        self.详细信息框.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 绑定选择事件
        self.分析步骤表格.bind("<<TreeviewSelect>>", self.显示步骤详情)

    def 创建符号表标签页(self):
        """创建符号表标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="符号表管理")

        # 上方控制区域
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="刷新符号表", command=self.刷新符号表).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="清空符号表", command=self.清空符号表).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="导出符号表", command=self.导出符号表).pack(side=tk.LEFT)

        # 符号表表格
        ttk.Label(frame, text="符号表内容:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        columns = ("名称", "类型", "值", "作用域", "其他信息")
        self.符号表表格 = ttk.Treeview(frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.符号表表格.heading(col, text=col)
            self.符号表表格.column(col, width=150)

        # 添加滚动条
        符号表滚动条 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.符号表表格.yview)
        self.符号表表格.configure(yscrollcommand=符号表滚动条.set)

        self.符号表表格.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
        符号表滚动条.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))

    def 创建帮助标签页(self):
        """创建帮助标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="使用帮助")

        帮助内容 = """
L属性文法语义分析程序 - 使用说明

=== 程序功能 ===

本程序实现了L属性文法的语义分析功能，包括：
• L属性文法的定义和解析
• 语义规则的定义和执行
• 属性值的计算和传递
• 符号表的管理和维护
• 语义分析过程的可视化展示

=== 使用步骤 ===

1. 文法定义
   • 在"L属性文法输入"标签页中定义文法
   • 文法格式包含三个部分：[文法]、[属性定义]、[语义规则]
   • 点击"解析文法"按钮解析文法定义
   • 点击"验证L属性"按钮验证文法是否满足L属性特性

2. 语义分析
   • 在"语义分析过程"标签页中输入要分析的字符串
   • 点击"开始语义分析"执行语义分析
   • 查看详细的分析步骤和属性计算过程
   • 选择分析步骤可查看详细信息

3. 符号表管理
   • 在"符号表管理"标签页中查看符号表内容
   • 可以刷新、清空或导出符号表

=== 文法格式说明 ===

[文法]
产生式格式：左部 -> 右部1 | 右部2 | ...
示例：
D -> T L
T -> int | float | char
L -> L , id | id

[属性定义]
格式：符号.属性名 : 属性类型 数据类型 默认值 描述
属性类型：综合 或 继承
示例：
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承的类型信息"

[语义规则]
格式：目标属性 := 表达式
示例：
L.in := T.type
addtype(id.name, L.in)

=== L属性文法特性 ===

L属性文法是一类特殊的属性文法，满足以下条件：
• 对于产生式 A -> X1 X2 ... Xn 中的每个符号 Xi
• Xi 的继承属性只能依赖于：
  - Xi 左边符号 X1, X2, ..., Xi-1 的属性
  - A 的继承属性
• 不能依赖于 Xi 右边符号的属性

=== 技术特点 ===

• 采用Python语言开发，界面友好
• 支持中文注释和错误提示
• 提供完整的语义分析过程可视化
• 集成符号表管理功能
• 支持文法文件的加载和保存

=== 作者信息 ===

作者：王海翔
学号：2021060187
班级：计科2203
课程：编译原理
完成时间：2025年6月
        """

        帮助文本框 = scrolledtext.ScrolledText(frame, font=("Consolas", 10))
        帮助文本框.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        帮助文本框.insert(tk.END, 帮助内容)
        帮助文本框.config(state=tk.DISABLED)

    # ==================== 事件处理方法 ====================

    def 加载文法文件(self):
        """加载文法文件"""
        try:
            文件路径 = filedialog.askopenfilename(
                title="选择L属性文法文件",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                with open(文件路径, 'r', encoding='utf-8') as f:
                    文件内容 = f.read()

                self.文法输入框.delete(1.0, tk.END)
                self.文法输入框.insert(tk.END, 文件内容)

                messagebox.showinfo("成功", f"已加载文法文件: {os.path.basename(文件路径)}")

        except Exception as e:
            messagebox.showerror("错误", f"加载文法文件失败: {str(e)}")

    def 保存文法文件(self):
        """保存文法文件"""
        try:
            文件路径 = filedialog.asksaveasfilename(
                title="保存L属性文法文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if 文件路径:
                文法内容 = self.文法输入框.get(1.0, tk.END)

                with open(文件路径, 'w', encoding='utf-8') as f:
                    f.write(文法内容)

                messagebox.showinfo("成功", f"已保存文法文件: {os.path.basename(文件路径)}")

        except Exception as e:
            messagebox.showerror("错误", f"保存文法文件失败: {str(e)}")

    def 解析文法(self):
        """解析文法"""
        try:
            文法内容 = self.文法输入框.get(1.0, tk.END).strip()

            if not 文法内容:
                messagebox.showwarning("警告", "请先输入L属性文法定义")
                return

            成功, 文法, 错误列表 = self.解析器.解析文法文件(文法内容)

            # 显示解析结果
            self.解析结果框.delete(1.0, tk.END)

            if 成功:
                self.当前文法 = 文法
                self.分析引擎 = 语义分析引擎(文法)

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

                messagebox.showinfo("成功", "L属性文法解析成功！")

            else:
                结果文本 = "=== 文法解析失败 ===\n\n"
                结果文本 += "错误列表:\n"
                for 错误 in 错误列表:
                    结果文本 += f"• {错误}\n"

                messagebox.showerror("错误", f"文法解析失败，共发现 {len(错误列表)} 个错误")

            self.解析结果框.insert(tk.END, 结果文本)

        except Exception as e:
            messagebox.showerror("错误", f"解析文法时发生异常: {str(e)}")

    def 验证L属性(self):
        """验证L属性特性"""
        if not self.当前文法:
            messagebox.showwarning("警告", "请先解析文法")
            return

        try:
            是L属性, 错误列表 = self.当前文法.验证L属性特性()

            if 是L属性:
                messagebox.showinfo("验证结果", "该文法满足L属性特性！")
            else:
                错误信息 = "该文法不满足L属性特性：\n\n"
                for 错误 in 错误列表:
                    错误信息 += f"• {错误}\n"
                messagebox.showerror("验证结果", 错误信息)

        except Exception as e:
            messagebox.showerror("错误", f"验证L属性特性时发生异常: {str(e)}")

    def 开始语义分析(self):
        """开始语义分析"""
        if not self.当前文法:
            messagebox.showwarning("警告", "请先解析文法")
            return

        if not self.分析引擎:
            messagebox.showwarning("警告", "语义分析引擎未初始化")
            return

        try:
            输入串 = self.输入串输入框.get().strip()

            if not 输入串:
                messagebox.showwarning("警告", "请输入要分析的字符串")
                return

            # 简单的语法分析（这里使用模拟的产生式序列）
            语法分析结果 = self._模拟语法分析(输入串)

            # 执行语义分析
            成功, 分析步骤列表, 错误信息 = self.分析引擎.执行语义分析(输入串, 语法分析结果)

            # 清空之前的结果
            for item in self.分析步骤表格.get_children():
                self.分析步骤表格.delete(item)

            self.详细信息框.delete(1.0, tk.END)

            if 成功:
                # 显示分析步骤
                for 步骤 in 分析步骤列表:
                    产生式信息 = str(步骤.当前产生式) if 步骤.当前产生式 else ""
                    属性计算信息 = "; ".join(步骤.属性计算) if 步骤.属性计算 else ""

                    self.分析步骤表格.insert("", tk.END, values=(
                        步骤.步骤号,
                        步骤.动作,
                        产生式信息,
                        属性计算信息
                    ))

                # 更新符号表
                self.刷新符号表()

                messagebox.showinfo("成功", "语义分析完成！")

            else:
                self.详细信息框.insert(tk.END, f"语义分析失败：{错误信息}")
                messagebox.showerror("错误", f"语义分析失败：{错误信息}")

        except Exception as e:
            messagebox.showerror("错误", f"语义分析过程中发生异常: {str(e)}")

    def _模拟语法分析(self, 输入串: str) -> List[int]:
        """模拟语法分析过程，返回产生式序列"""
        # 这里实现一个简单的语法分析模拟
        # 按照自顶向下的顺序生成产生式序列

        单词列表 = 输入串.split()
        产生式序列 = []

        # 根据输入串的模式确定产生式序列
        if len(单词列表) >= 2 and 单词列表[0] in ['int', 'float', 'char']:
            # 类型声明模式：int a, b, c

            # 首先应用 D -> T L
            产生式序列.append(0)  # D -> T L

            # 然后应用 T -> 具体类型
            if 单词列表[0] == 'int':
                产生式序列.append(1)  # T -> int
            elif 单词列表[0] == 'float':
                产生式序列.append(2)  # T -> float
            elif 单词列表[0] == 'char':
                产生式序列.append(3)  # T -> char

            # 处理标识符列表 L
            标识符列表 = [w for w in 单词列表[1:] if w not in [',', ';']]
            标识符数量 = len(标识符列表)

            if 标识符数量 > 1:
                # 多个标识符：L -> L , id
                # 需要从左到右递归展开
                for i in range(标识符数量 - 1):
                    产生式序列.append(4)  # L -> L , id
                产生式序列.append(5)  # L -> id (最后一个)
            else:
                # 单个标识符：L -> id
                产生式序列.append(5)  # L -> id

        return 产生式序列

    def 清空分析结果(self):
        """清空分析结果"""
        for item in self.分析步骤表格.get_children():
            self.分析步骤表格.delete(item)

        self.详细信息框.delete(1.0, tk.END)

        if self.分析引擎:
            self.分析引擎.分析步骤列表.clear()
            self.分析引擎.属性值表.clear()

    def 显示步骤详情(self, event):
        """显示选中步骤的详细信息"""
        选中项 = self.分析步骤表格.selection()

        if not 选中项:
            return

        try:
            项目 = self.分析步骤表格.item(选中项[0])
            步骤号 = int(项目['values'][0])

            if self.分析引擎 and 步骤号 < len(self.分析引擎.分析步骤列表):
                步骤 = self.分析引擎.分析步骤列表[步骤号]

                详细信息 = f"=== 步骤 {步骤.步骤号} 详细信息 ===\n\n"
                详细信息 += f"动作: {步骤.动作}\n"

                if 步骤.当前产生式:
                    详细信息 += f"产生式: {步骤.当前产生式}\n"

                if 步骤.属性计算:
                    详细信息 += f"\n属性计算:\n"
                    for 计算 in 步骤.属性计算:
                        详细信息 += f"  {计算}\n"

                if 步骤.符号表状态:
                    详细信息 += f"\n符号表状态:\n"
                    for 键, 值 in 步骤.符号表状态.items():
                        详细信息 += f"  {键}: {值}\n"

                if 步骤.错误信息:
                    详细信息 += f"\n备注: {步骤.错误信息}\n"

                self.详细信息框.delete(1.0, tk.END)
                self.详细信息框.insert(tk.END, 详细信息)

        except Exception as e:
            self.详细信息框.delete(1.0, tk.END)
            self.详细信息框.insert(tk.END, f"显示步骤详情时发生错误: {str(e)}")

    def 刷新符号表(self):
        """刷新符号表显示"""
        # 清空现有内容
        for item in self.符号表表格.get_children():
            self.符号表表格.delete(item)

        if not self.分析引擎:
            return

        try:
            # 显示符号表内容
            for 键, 符号项 in self.分析引擎.符号表.表项.items():
                其他信息 = json.dumps(符号项.其他信息, ensure_ascii=False) if 符号项.其他信息 else ""

                self.符号表表格.insert("", tk.END, values=(
                    符号项.名称,
                    符号项.类型,
                    str(符号项.值) if 符号项.值 is not None else "",
                    符号项.作用域,
                    其他信息
                ))

        except Exception as e:
            messagebox.showerror("错误", f"刷新符号表时发生错误: {str(e)}")

    def 清空符号表(self):
        """清空符号表"""
        if self.分析引擎:
            self.分析引擎.符号表 = 符号表()
            self.刷新符号表()

    def 导出符号表(self):
        """导出符号表"""
        if not self.分析引擎 or not self.分析引擎.符号表.表项:
            messagebox.showwarning("警告", "符号表为空")
            return

        try:
            文件路径 = filedialog.asksaveasfilename(
                title="导出符号表",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")]
            )

            if 文件路径:
                符号表数据 = {}
                for 键, 符号项 in self.分析引擎.符号表.表项.items():
                    符号表数据[键] = {
                        "名称": 符号项.名称,
                        "类型": 符号项.类型,
                        "值": 符号项.值,
                        "作用域": 符号项.作用域,
                        "行号": 符号项.行号,
                        "其他信息": 符号项.其他信息
                    }

                if 文件路径.endswith('.json'):
                    with open(文件路径, 'w', encoding='utf-8') as f:
                        json.dump(符号表数据, f, ensure_ascii=False, indent=2)
                else:
                    with open(文件路径, 'w', encoding='utf-8') as f:
                        f.write("=== 符号表导出 ===\n\n")
                        for 键, 数据 in 符号表数据.items():
                            f.write(f"{键}:\n")
                            for k, v in 数据.items():
                                f.write(f"  {k}: {v}\n")
                            f.write("\n")

                messagebox.showinfo("成功", f"符号表已导出到: {os.path.basename(文件路径)}")

        except Exception as e:
            messagebox.showerror("错误", f"导出符号表失败: {str(e)}")

    def 运行(self):
        """运行GUI应用程序"""
        self.root.mainloop()


# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    try:
        # 创建并运行GUI应用程序
        app = L属性文法分析器GUI()
        app.运行()

    except Exception as e:
        print(f"程序运行时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()