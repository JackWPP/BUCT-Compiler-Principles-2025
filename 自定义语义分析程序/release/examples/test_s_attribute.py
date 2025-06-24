#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S属性文法语义分析器测试程序

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

from custom_semantic_analyzer import *

def 测试S属性文法分析器():
    """测试S属性文法分析器的功能"""
    print("=== S属性文法语义分析器测试 ===\n")
    
    # 创建语义分析引擎管理器
    引擎 = 语义分析引擎管理器()
    
    # 定义测试文法（简单的算术表达式文法）
    测试文法 = """
[文法]
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
E.val := E.val + T.val  # 产生式0
E.val := T.val          # 产生式1
T.val := T.val * F.val  # 产生式2
T.val := F.val          # 产生式3
F.val := E.val          # 产生式4
F.val := num.val        # 产生式5
"""
    
    print("1. 加载测试文法...")
    成功, 错误列表 = 引擎.加载文法(测试文法)
    
    if not 成功:
        print("文法加载失败:")
        for 错误 in 错误列表:
            print(f"  {错误}")
        return False
    
    print("✓ 文法加载成功")
    
    # 显示文法信息
    文法 = 引擎.当前文法
    print(f"\n开始符号: {文法.开始符号}")
    print(f"终结符: {', '.join(sorted(文法.终结符集合))}")
    print(f"非终结符: {', '.join(sorted(文法.非终结符集合))}")
    
    print("\n产生式列表:")
    for i, 产生式 in enumerate(文法.产生式列表):
        print(f"  {i}: {产生式}")
    
    print("\n属性定义:")
    for 符号名, 符号 in 文法.文法符号.items():
        if 符号.属性列表:
            print(f"  {符号名}:")
            for 属性 in 符号.属性列表:
                print(f"    {属性.名称} ({属性.类型.value}, {属性.数据类型.value})")
    
    print("\n语义规则:")
    for 产生式编号, 规则列表 in 文法.语义规则表.items():
        if 规则列表:
            print(f"  产生式{产生式编号}:")
            for 规则 in 规则列表:
                print(f"    {规则}")
    
    print("\n2. 验证S属性特性...")
    验证成功, 验证错误 = 引擎.验证文法特性(语义分析类型.S属性文法)
    
    if not 验证成功:
        print("S属性文法验证失败:")
        for 错误 in 验证错误:
            print(f"  {错误}")
        return False
    
    print("✓ S属性文法验证通过")
    
    print("\n3. 执行语义分析测试...")
    
    # 测试用例：简单表达式 "3 + 2 * 4"
    # 对应的语法分析结果（自底向上归约序列）
    # 假设的归约序列：num->F, F->T, num->F, F->T, T*F->T, T->E, num->F, F->T, T->E, E+T->E
    测试输入 = "3 + 2 * 4"
    语法分析结果 = [5, 3, 5, 3, 2, 1, 5, 3, 1, 0]  # 产生式编号序列
    
    print(f"输入串: {测试输入}")
    print(f"语法分析结果: {语法分析结果}")
    
    分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
        语义分析类型.S属性文法, 测试输入, 语法分析结果
    )
    
    if not 分析成功:
        print(f"语义分析失败: {错误信息}")
        return False
    
    print("✓ 语义分析成功")
    
    print("\n分析步骤:")
    for 步骤 in 分析步骤:
        print(f"  步骤{步骤.步骤号}: {步骤.动作}")
        if 步骤.描述:
            print(f"    {步骤.描述}")
        if 步骤.属性计算:
            for 计算 in 步骤.属性计算:
                print(f"    {计算}")
    
    print("\n=== 测试完成 ===")
    return True

def 测试错误处理():
    """测试错误处理功能"""
    print("\n=== 错误处理测试 ===\n")
    
    引擎 = 语义分析引擎管理器()
    
    # 测试格式错误的文法
    错误文法 = """
[文法]
E -> E +  # 缺少右部符号
T -> 
F -> ( E  # 缺少右括号

[属性定义]
E.val 综合 整数  # 缺少冒号

[语义规则]
E.val = T.val  # 应该使用 :=
"""
    
    print("1. 测试错误文法处理...")
    成功, 错误列表 = 引擎.加载文法(错误文法)
    
    if 成功:
        print("错误：应该检测到文法错误")
        return False
    
    print("✓ 正确检测到文法错误:")
    for 错误 in 错误列表:
        print(f"  {错误}")
    
    print("\n=== 错误处理测试完成 ===")
    return True

if __name__ == "__main__":
    print("S属性文法语义分析器测试程序")
    print("=" * 50)
    
    try:
        # 运行基本功能测试
        基本测试成功 = 测试S属性文法分析器()
        
        # 运行错误处理测试
        错误测试成功 = 测试错误处理()
        
        if 基本测试成功 and 错误测试成功:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 部分测试失败")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
