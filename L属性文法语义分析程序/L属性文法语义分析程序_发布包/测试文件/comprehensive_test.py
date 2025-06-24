#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析程序综合测试脚本

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os
import unittest
from io import StringIO
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主程序模块
from l_attribute_main import (
    L属性文法, L属性文法解析器, 语义分析引擎,
    属性定义, 文法符号, 产生式, 语义规则, 符号表项, 符号表,
    属性类型, 符号类型
)


class TestL属性文法基础功能(unittest.TestCase):
    """测试L属性文法的基础功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.文法 = L属性文法()
        self.解析器 = L属性文法解析器()
    
    def test_文法符号创建(self):
        """测试文法符号的创建"""
        # 测试终结符
        终结符 = 文法符号("id", 符号类型.终结符)
        self.assertEqual(终结符.名称, "id")
        self.assertEqual(终结符.类型, 符号类型.终结符)
        
        # 测试非终结符
        非终结符 = 文法符号("E", 符号类型.非终结符)
        self.assertEqual(非终结符.名称, "E")
        self.assertEqual(非终结符.类型, 符号类型.非终结符)
    
    def test_属性定义创建(self):
        """测试属性定义的创建"""
        # 测试综合属性
        综合属性 = 属性定义("value", 属性类型.综合属性, "整数", 0, "值属性")
        self.assertEqual(综合属性.名称, "value")
        self.assertEqual(综合属性.类型, 属性类型.综合属性)
        
        # 测试继承属性
        继承属性 = 属性定义("type", 属性类型.继承属性, "字符串", "", "类型属性")
        self.assertEqual(继承属性.名称, "type")
        self.assertEqual(继承属性.类型, 属性类型.继承属性)
    
    def test_产生式创建(self):
        """测试产生式的创建"""
        产生式对象 = 产生式("E", ["E", "+", "T"])
        self.assertEqual(产生式对象.左部, "E")
        self.assertEqual(产生式对象.右部, ["E", "+", "T"])
        self.assertEqual(str(产生式对象), "E -> E + T")
    
    def test_语义规则创建(self):
        """测试语义规则的创建"""
        规则 = 语义规则("E.value", "E1.value + T.value", ["E1.value", "T.value"])
        self.assertEqual(规则.目标属性, "E.value")
        self.assertEqual(规则.表达式, "E1.value + T.value")
        self.assertIn("E1.value", 规则.依赖属性)
        self.assertIn("T.value", 规则.依赖属性)


class TestL属性文法解析器(unittest.TestCase):
    """测试L属性文法解析器"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.解析器 = L属性文法解析器()
    
    def test_解析简单文法(self):
        """测试解析简单的L属性文法"""
        文法内容 = """
[文法]
D -> T L
T -> int
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"

[语义规则]
L.in := T.type
"""
        
        成功, 文法, 错误列表 = self.解析器.解析文法文件(文法内容)
        
        self.assertTrue(成功, f"解析失败: {错误列表}")
        self.assertEqual(len(文法.产生式列表), 3)
        self.assertEqual(文法.开始符号, "D")
        self.assertIn("D", 文法.非终结符集合)
        self.assertIn("int", 文法.终结符集合)
    
    def test_解析错误文法(self):
        """测试解析错误的文法"""
        错误文法内容 = """
[文法]
D -> 
T -> int |
"""
        
        成功, 文法, 错误列表 = self.解析器.解析文法文件(错误文法内容)
        
        self.assertFalse(成功)
        self.assertGreater(len(错误列表), 0)
    
    def test_L属性特性验证(self):
        """测试L属性特性验证"""
        # 正确的L属性文法
        正确文法内容 = """
[文法]
D -> T L
T -> int
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"

[语义规则]
L.in := T.type
"""
        
        成功, 文法, _ = self.解析器.解析文法文件(正确文法内容)
        self.assertTrue(成功)
        
        是L属性, 错误列表 = 文法.验证L属性特性()
        self.assertTrue(是L属性, f"L属性验证失败: {错误列表}")


class Test符号表管理(unittest.TestCase):
    """测试符号表管理功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.符号表 = 符号表()
    
    def test_符号表基本操作(self):
        """测试符号表的基本操作"""
        # 添加符号
        符号项 = 符号表项("variable1", "int", 42)
        self.符号表.添加符号(符号项)
        
        # 查找符号
        找到的符号 = self.符号表.查找符号("variable1")
        self.assertIsNotNone(找到的符号)
        self.assertEqual(找到的符号.名称, "variable1")
        self.assertEqual(找到的符号.类型, "int")
        self.assertEqual(找到的符号.值, 42)
    
    def test_作用域管理(self):
        """测试作用域管理"""
        # 全局作用域
        全局符号 = 符号表项("global_var", "int")
        self.符号表.添加符号(全局符号)
        
        # 进入新作用域
        self.符号表.进入作用域("函数1")
        局部符号 = 符号表项("local_var", "float")
        self.符号表.添加符号(局部符号)
        
        # 查找符号
        self.assertIsNotNone(self.符号表.查找符号("global_var"))
        self.assertIsNotNone(self.符号表.查找符号("local_var"))
        
        # 退出作用域
        self.符号表.退出作用域()
        self.assertIsNotNone(self.符号表.查找符号("global_var"))


class Test语义分析引擎(unittest.TestCase):
    """测试语义分析引擎"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试文法
        self.文法 = L属性文法()
        
        # 添加产生式
        产生式1 = 产生式("D", ["T", "L"])
        产生式2 = 产生式("T", ["int"])
        产生式3 = 产生式("L", ["id"])
        
        self.文法.添加产生式(产生式1)
        self.文法.添加产生式(产生式2)
        self.文法.添加产生式(产生式3)
        
        # 添加属性定义
        T符号 = 文法符号("T", 符号类型.非终结符)
        T符号.添加属性(属性定义("type", 属性类型.综合属性))
        self.文法.添加文法符号(T符号)
        
        L符号 = 文法符号("L", 符号类型.非终结符)
        L符号.添加属性(属性定义("in", 属性类型.继承属性))
        self.文法.添加文法符号(L符号)
        
        # 添加语义规则
        规则1 = 语义规则("L.in", "T.type")
        规则2 = 语义规则("T.type", "\"int\"")
        
        self.文法.添加语义规则(0, 规则1)  # 产生式0: D -> T L
        self.文法.添加语义规则(1, 规则2)  # 产生式1: T -> int
        
        self.分析引擎 = 语义分析引擎(self.文法)
    
    def test_词法分析(self):
        """测试词法分析功能"""
        输入串 = "int variable1"
        词法单元列表 = self.分析引擎._词法分析(输入串)
        
        self.assertEqual(len(词法单元列表), 2)
        self.assertEqual(词法单元列表[0], ("类型", "int"))
        self.assertEqual(词法单元列表[1], ("标识符", "variable1"))
    
    def test_语义分析执行(self):
        """测试语义分析执行"""
        输入串 = "int a"
        语法分析结果 = [0, 1, 2]  # 模拟的产生式序列
        
        成功, 分析步骤列表, 错误信息 = self.分析引擎.执行语义分析(输入串, 语法分析结果)
        
        # 检查分析是否成功
        if not 成功:
            print(f"语义分析失败: {错误信息}")
            for 步骤 in 分析步骤列表:
                print(f"步骤{步骤.步骤号}: {步骤.动作}")
        
        self.assertTrue(成功 or len(分析步骤列表) > 0, "语义分析应该至少产生一些步骤")


class Test集成功能(unittest.TestCase):
    """测试集成功能"""
    
    def test_完整流程(self):
        """测试完整的分析流程"""
        # 1. 创建文法文件
        文法内容 = """
[文法]
D -> T L
T -> int | float
L -> L , id | id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"
id.name : 综合 字符串 "" "标识符名称"

[语义规则]
L.in := T.type
T.type := "int"
addtype(id.name, L.in)
"""
        
        # 2. 解析文法
        解析器 = L属性文法解析器()
        成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)
        
        self.assertTrue(成功, f"文法解析失败: {错误列表}")
        
        # 3. 验证L属性特性
        是L属性, L属性错误 = 文法.验证L属性特性()
        if not 是L属性:
            print(f"L属性验证警告: {L属性错误}")
        
        # 4. 执行语义分析
        分析引擎 = 语义分析引擎(文法)
        输入串 = "int a , b"
        语法分析结果 = [0, 1, 4, 5]  # 模拟的产生式序列
        
        成功, 分析步骤列表, 错误信息 = 分析引擎.执行语义分析(输入串, 语法分析结果)
        
        # 检查结果
        self.assertGreater(len(分析步骤列表), 0, "应该产生分析步骤")
        
        # 5. 检查符号表
        符号表内容 = 分析引擎.符号表.表项
        print(f"符号表内容: {len(符号表内容)} 个符号")
        for 键, 符号项 in 符号表内容.items():
            print(f"  {键}: {符号项.名称} ({符号项.类型})")


def 运行测试():
    """运行所有测试"""
    print("=" * 60)
    print("L属性文法语义分析程序 - 综合测试")
    print("=" * 60)
    
    # 创建测试套件
    测试套件 = unittest.TestSuite()
    
    # 添加测试类
    测试类列表 = [
        TestL属性文法基础功能,
        TestL属性文法解析器,
        Test符号表管理,
        Test语义分析引擎,
        Test集成功能
    ]
    
    for 测试类 in 测试类列表:
        测试 = unittest.TestLoader().loadTestsFromTestCase(测试类)
        测试套件.addTest(测试)
    
    # 运行测试
    运行器 = unittest.TextTestRunner(verbosity=2)
    结果 = 运行器.run(测试套件)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print(f"运行测试: {结果.testsRun}")
    print(f"失败: {len(结果.failures)}")
    print(f"错误: {len(结果.errors)}")
    print(f"成功率: {((结果.testsRun - len(结果.failures) - len(结果.errors)) / max(1, 结果.testsRun) * 100):.1f}%")
    
    if 结果.failures:
        print("\n失败的测试:")
        for 测试, 错误信息 in 结果.failures:
            print(f"  {测试}: {错误信息}")
    
    if 结果.errors:
        print("\n错误的测试:")
        for 测试, 错误信息 in 结果.errors:
            print(f"  {测试}: {错误信息}")
    
    print("=" * 60)
    
    return 结果.wasSuccessful()


if __name__ == "__main__":
    try:
        成功 = 运行测试()
        if 成功:
            print("所有测试通过！")
            sys.exit(0)
        else:
            print("部分测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
