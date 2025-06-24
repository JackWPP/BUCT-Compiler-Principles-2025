#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义语义分析程序综合测试

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import unittest
import sys
import os
from custom_semantic_analyzer import *

class Test基础数据结构(unittest.TestCase):
    """测试基础数据结构"""
    
    def test_属性定义创建(self):
        """测试属性定义的创建"""
        属性 = 属性定义("val", 属性类型.综合, 数据类型.整数, 0, "值属性")
        self.assertEqual(属性.名称, "val")
        self.assertEqual(属性.类型, 属性类型.综合)
        self.assertEqual(属性.数据类型, 数据类型.整数)
        self.assertEqual(属性.默认值, 0)
        self.assertEqual(属性.描述, "值属性")
    
    def test_文法符号创建(self):
        """测试文法符号的创建"""
        符号 = 文法符号("E", False)
        属性 = 属性定义("val", 属性类型.综合, 数据类型.整数)
        符号.添加属性(属性)
        
        self.assertEqual(符号.名称, "E")
        self.assertFalse(符号.是否终结符)
        self.assertEqual(len(符号.属性列表), 1)
        self.assertEqual(符号.获取属性("val"), 属性)
    
    def test_产生式创建(self):
        """测试产生式的创建"""
        产生式对象 = 产生式(0, "E", ["E", "+", "T"])
        self.assertEqual(产生式对象.编号, 0)
        self.assertEqual(产生式对象.左部, "E")
        self.assertEqual(产生式对象.右部, ["E", "+", "T"])
        self.assertEqual(str(产生式对象), "E -> E + T")
    
    def test_语义规则创建(self):
        """测试语义规则的创建"""
        规则 = 语义规则("E.val", "E.val + T.val", ["E.val", "T.val"])
        self.assertEqual(规则.目标属性, "E.val")
        self.assertEqual(规则.表达式, "E.val + T.val")
        self.assertIn("E.val", 规则.依赖属性)
        self.assertIn("T.val", 规则.依赖属性)
    
    def test_符号表操作(self):
        """测试符号表操作"""
        符号表对象 = 符号表()
        符号项对象 = 符号表项("x", "int", 10)
        
        符号表对象.插入符号(符号项对象)
        查找结果 = 符号表对象.查找符号("x")
        
        self.assertIsNotNone(查找结果)
        self.assertEqual(查找结果.名称, "x")
        self.assertEqual(查找结果.类型, "int")
        self.assertEqual(查找结果.值, 10)

class Test文法解析器(unittest.TestCase):
    """测试文法解析器"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.解析器 = 文法解析器()
    
    def test_解析简单文法(self):
        """测试解析简单文法"""
        文法内容 = """
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
"""
        
        成功, 文法, 错误列表 = self.解析器.解析文法文件(文法内容)
        
        self.assertTrue(成功, f"文法解析失败: {错误列表}")
        self.assertEqual(文法.开始符号, "E")
        self.assertIn("E", 文法.非终结符集合)
        self.assertIn("T", 文法.非终结符集合)
        self.assertIn("num", 文法.终结符集合)
        self.assertIn("+", 文法.终结符集合)
        self.assertEqual(len(文法.产生式列表), 3)
    
    def test_解析错误文法(self):
        """测试解析错误文法"""
        错误文法 = """
[文法]
E -> E +  # 缺少右部符号
T -> 

[属性定义]
E.val 综合 整数  # 缺少冒号

[语义规则]
E.val = T.val  # 应该使用 :=
"""
        
        成功, 文法, 错误列表 = self.解析器.解析文法文件(错误文法)
        
        self.assertFalse(成功)
        self.assertGreater(len(错误列表), 0)

class TestS属性文法分析器(unittest.TestCase):
    """测试S属性文法分析器"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.引擎 = 语义分析引擎管理器()
        
        # 加载测试文法
        文法内容 = """
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
"""
        
        成功, 错误列表 = self.引擎.加载文法(文法内容)
        self.assertTrue(成功, f"文法加载失败: {错误列表}")
    
    def test_S属性特性验证(self):
        """测试S属性特性验证"""
        验证成功, 验证错误 = self.引擎.验证文法特性(语义分析类型.S属性文法)
        self.assertTrue(验证成功, f"S属性验证失败: {验证错误}")
    
    def test_S属性语义分析(self):
        """测试S属性语义分析"""
        输入串 = "3 + 5"
        语法分析结果 = [2, 1, 2, 1, 0]  # 产生式编号序列
        
        分析成功, 分析步骤, 错误信息 = self.引擎.执行语义分析(
            语义分析类型.S属性文法, 输入串, 语法分析结果
        )
        
        self.assertTrue(分析成功, f"S属性语义分析失败: {错误信息}")
        self.assertGreater(len(分析步骤), 0)

class TestL属性文法分析器(unittest.TestCase):
    """测试L属性文法分析器"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.引擎 = 语义分析引擎管理器()
        
        # 加载测试文法
        文法内容 = """
[文法]
D -> T L
T -> int
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"
id.name : 综合 字符串 "" "标识符名称"

[语义规则]
L.in := T.type
T.type := "int"
L.in := L.in
"""
        
        成功, 错误列表 = self.引擎.加载文法(文法内容)
        self.assertTrue(成功, f"文法加载失败: {错误列表}")
    
    def test_L属性语义分析(self):
        """测试L属性语义分析"""
        输入串 = "int x"
        语法分析结果 = [1, 2, 0]  # 产生式编号序列
        
        分析成功, 分析步骤, 错误信息 = self.引擎.执行语义分析(
            语义分析类型.L属性文法, 输入串, 语法分析结果
        )
        
        self.assertTrue(分析成功, f"L属性语义分析失败: {错误信息}")
        self.assertGreater(len(分析步骤), 0)

class Test依赖图分析器(unittest.TestCase):
    """测试依赖图分析器"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.引擎 = 语义分析引擎管理器()
        
        # 加载测试文法
        文法内容 = """
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
"""
        
        成功, 错误列表 = self.引擎.加载文法(文法内容)
        self.assertTrue(成功, f"文法加载失败: {错误列表}")
    
    def test_依赖图语义分析(self):
        """测试依赖图语义分析"""
        输入串 = "3 + 5"
        语法分析结果 = [2, 1, 2, 1, 0]  # 产生式编号序列
        
        分析成功, 分析步骤, 错误信息 = self.引擎.执行语义分析(
            语义分析类型.依赖图, 输入串, 语法分析结果
        )
        
        self.assertTrue(分析成功, f"依赖图语义分析失败: {错误信息}")
        self.assertGreater(len(分析步骤), 0)
    
    def test_循环依赖检测(self):
        """测试循环依赖检测"""
        # 创建包含循环依赖的文法
        循环文法 = """
[文法]
A -> B
B -> C
C -> A

[属性定义]
A.s : 综合 字符串 "" "属性A"
B.s : 综合 字符串 "" "属性B"
C.s : 综合 字符串 "" "属性C"

[语义规则]
A.s := B.s
B.s := C.s
C.s := A.s
"""
        
        引擎 = 语义分析引擎管理器()
        成功, 错误列表 = 引擎.加载文法(循环文法)
        
        if 成功:
            输入串 = "test"
            语法分析结果 = [2, 1, 0]
            
            分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
                语义分析类型.依赖图, 输入串, 语法分析结果
            )
            
            # 应该检测到循环依赖
            self.assertFalse(分析成功)
            self.assertIn("循环依赖", 错误信息)

def 运行所有测试():
    """运行所有测试用例"""
    print("自定义语义分析程序 - 综合测试")
    print("=" * 50)
    
    # 创建测试套件
    测试套件 = unittest.TestSuite()
    
    # 添加测试类
    测试类列表 = [
        Test基础数据结构,
        Test文法解析器,
        TestS属性文法分析器,
        TestL属性文法分析器,
        Test依赖图分析器
    ]
    
    for 测试类 in 测试类列表:
        测试套件.addTest(unittest.TestLoader().loadTestsFromTestCase(测试类))
    
    # 运行测试
    运行器 = unittest.TextTestRunner(verbosity=2)
    结果 = 运行器.run(测试套件)
    
    # 显示测试结果统计
    print("\n" + "=" * 50)
    print("测试结果统计:")
    print(f"总测试数: {结果.testsRun}")
    print(f"成功: {结果.testsRun - len(结果.failures) - len(结果.errors)}")
    print(f"失败: {len(结果.failures)}")
    print(f"错误: {len(结果.errors)}")
    
    if 结果.failures:
        print("\n失败的测试:")
        for 测试, 错误 in 结果.failures:
            print(f"  {测试}: {错误}")
    
    if 结果.errors:
        print("\n错误的测试:")
        for 测试, 错误 in 结果.errors:
            print(f"  {测试}: {错误}")
    
    成功率 = (结果.testsRun - len(结果.failures) - len(结果.errors)) / 结果.testsRun * 100
    print(f"\n总体成功率: {成功率:.1f}%")
    
    return 结果.wasSuccessful()

if __name__ == "__main__":
    成功 = 运行所有测试()
    sys.exit(0 if 成功 else 1)
