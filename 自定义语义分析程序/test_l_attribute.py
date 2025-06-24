#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L属性文法语义分析器测试程序

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

from custom_semantic_analyzer import *

def 测试L属性文法分析器():
    """测试L属性文法分析器的功能"""
    print("=== L属性文法语义分析器测试 ===\n")
    
    # 创建语义分析引擎管理器
    引擎 = 语义分析引擎管理器()
    
    # 定义测试文法（简单的变量声明文法）
    测试文法 = """
[文法]
D -> T L
T -> int
T -> float
L -> id , L
L -> id

[属性定义]
T.type : 综合 字符串 "" "类型信息"
L.in : 继承 字符串 "" "继承类型"
id.name : 综合 字符串 "" "标识符名称"

[语义规则]
L.in := T.type
T.type := "int"
T.type := "float"
L.in := L.in
L.in := L.in
"""
    
    print("1. 加载测试文法...")
    成功, 错误列表 = 引擎.加载文法(测试文法)
    
    if not 成功:
        print("文法加载失败:")
        for 错误 in 错误列表:
            print(f"  {错误}")
        return False
    
    print("√ 文法加载成功")
    
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
    
    print("\n2. 验证L属性特性...")
    验证成功, 验证错误 = 引擎.验证文法特性(语义分析类型.L属性文法)
    
    if not 验证成功:
        print("L属性文法验证失败:")
        for 错误 in 验证错误:
            print(f"  {错误}")
        # 继续测试，即使验证失败
    else:
        print("√ L属性文法验证通过")
    
    print("\n3. 执行语义分析测试...")
    
    # 测试用例：变量声明 "int a , b"
    # 对应的语法分析结果（自底向上归约序列）
    测试输入 = "int a , b"
    语法分析结果 = [1, 4, 3, 0]  # 产生式编号序列
    
    print(f"输入串: {测试输入}")
    print(f"语法分析结果: {语法分析结果}")
    
    分析成功, 分析步骤, 错误信息 = 引擎.执行语义分析(
        语义分析类型.L属性文法, 测试输入, 语法分析结果
    )
    
    if not 分析成功:
        print(f"语义分析失败: {错误信息}")
        return False
    
    print("√ 语义分析成功")
    
    print("\n分析步骤:")
    for 步骤 in 分析步骤:
        print(f"  步骤{步骤.步骤号}: {步骤.动作}")
        if 步骤.描述:
            print(f"    {步骤.描述}")
        if 步骤.属性计算:
            for 计算 in 步骤.属性计算:
                print(f"    {计算}")
        if 步骤.符号表状态:
            print(f"    符号表: {len(步骤.符号表状态)} 个符号")
    
    print("\n=== 测试完成 ===")
    return True

def 测试L属性特性验证():
    """测试L属性特性验证功能"""
    print("\n=== L属性特性验证测试 ===\n")
    
    引擎 = 语义分析引擎管理器()
    
    # 测试违反L属性特性的文法
    违反L属性文法 = """
[文法]
A -> B C
B -> b
C -> c

[属性定义]
A.s : 综合 字符串 "" "综合属性"
B.i : 继承 字符串 "" "继承属性"
C.s : 综合 字符串 "" "综合属性"

[语义规则]
B.i := C.s
"""
    
    print("1. 测试违反L属性特性的文法...")
    成功, 错误列表 = 引擎.加载文法(违反L属性文法)
    
    if 成功:
        验证成功, 验证错误 = 引擎.验证文法特性(语义分析类型.L属性文法)
        
        if 验证成功:
            print("错误：应该检测到L属性特性违反")
            return False
        else:
            print("√ 正确检测到L属性特性违反:")
            for 错误 in 验证错误:
                print(f"  {错误}")
    else:
        print(f"文法加载失败: {错误列表}")
        return False
    
    print("\n=== L属性特性验证测试完成 ===")
    return True

def 测试综合功能():
    """测试S属性和L属性文法的综合功能"""
    print("\n=== 综合功能测试 ===\n")
    
    引擎 = 语义分析引擎管理器()
    
    # 定义一个既有综合属性又有继承属性的文法
    综合文法 = """
[文法]
E -> T E'
E' -> + T E'
E' -> ε
T -> F T'
T' -> * F T'
T' -> ε
F -> ( E )
F -> num

[属性定义]
E.val : 综合 整数 0 "表达式值"
E'.inh : 继承 整数 0 "继承值"
E'.syn : 综合 整数 0 "综合值"
T.val : 综合 整数 0 "项值"
T'.inh : 继承 整数 0 "继承值"
T'.syn : 综合 整数 0 "综合值"
F.val : 综合 整数 0 "因子值"
num.val : 综合 整数 0 "数字值"

[语义规则]
E'.inh := T.val         # 产生式0
E.val := E'.syn         # 产生式0
E'.inh := T.val         # 产生式1
E'.syn := E'.inh + T.val # 产生式1
E'.syn := E'.inh        # 产生式2
T'.inh := F.val         # 产生式3
T.val := T'.syn         # 产生式3
T'.inh := F.val         # 产生式4
T'.syn := T'.inh * F.val # 产生式4
T'.syn := T'.inh        # 产生式5
F.val := E.val          # 产生式6
F.val := num.val        # 产生式7
"""
    
    print("1. 加载综合测试文法...")
    成功, 错误列表 = 引擎.加载文法(综合文法)
    
    if not 成功:
        print("文法加载失败:")
        for 错误 in 错误列表:
            print(f"  {错误}")
        return False
    
    print("√ 文法加载成功")
    
    # 测试S属性特性
    print("\n2. 测试S属性特性验证...")
    S验证成功, S验证错误 = 引擎.验证文法特性(语义分析类型.S属性文法)
    print(f"S属性验证结果: {'通过' if S验证成功 else '失败'}")
    if not S验证成功:
        for 错误 in S验证错误:
            print(f"  {错误}")
    
    # 测试L属性特性
    print("\n3. 测试L属性特性验证...")
    L验证成功, L验证错误 = 引擎.验证文法特性(语义分析类型.L属性文法)
    print(f"L属性验证结果: {'通过' if L验证成功 else '失败'}")
    if not L验证成功:
        for 错误 in L验证错误:
            print(f"  {错误}")
    
    print("\n=== 综合功能测试完成 ===")
    return True

if __name__ == "__main__":
    print("L属性文法语义分析器测试程序")
    print("=" * 50)
    
    try:
        # 运行基本功能测试
        基本测试成功 = 测试L属性文法分析器()
        
        # 运行L属性特性验证测试
        验证测试成功 = 测试L属性特性验证()
        
        # 运行综合功能测试
        综合测试成功 = 测试综合功能()
        
        if 基本测试成功 and 验证测试成功 and 综合测试成功:
            print("\n* 所有测试通过！")
        else:
            print("\n× 部分测试失败")
            
    except Exception as e:
        print(f"\n! 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
