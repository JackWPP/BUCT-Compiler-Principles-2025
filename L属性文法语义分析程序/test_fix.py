#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的L属性文法语义分析器

作者: 王海翔
学号: 2021060187
班级: 计科2203
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from l_attribute_main import L属性文法解析器

def test_sample_grammar():
    """测试示例文法解析"""
    print("=== 测试示例文法解析 ===")
    
    # 读取示例文法文件
    try:
        with open('sample_grammar.txt', 'r', encoding='utf-8') as f:
            文法内容 = f.read()
        
        print("✓ 成功读取示例文法文件")
        print(f"文法内容长度: {len(文法内容)} 字符")
        
    except Exception as e:
        print(f"✗ 读取示例文法文件失败: {e}")
        return False
    
    # 解析文法
    解析器 = L属性文法解析器()
    
    try:
        成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)
        
        if 成功:
            print("✓ 文法解析成功！")
            print(f"产生式数量: {len(文法.产生式列表)}")
            print(f"文法符号数量: {len(文法.文法符号)}")
            print(f"语义规则数量: {sum(len(规则列表) for 规则列表 in 文法.语义规则表.values())}")
            
            # 显示产生式
            print("\n产生式列表:")
            for i, 产生式 in enumerate(文法.产生式列表):
                print(f"  {i}: {产生式}")
            
            # 显示语义规则
            print("\n语义规则:")
            for 产生式编号, 规则列表 in 文法.语义规则表.items():
                if 规则列表:
                    print(f"  产生式{产生式编号}:")
                    for 规则 in 规则列表:
                        print(f"    {规则}")
            
            # 验证L属性特性
            是L属性, L属性错误 = 文法.验证L属性特性()
            if 是L属性:
                print("\n✓ L属性特性验证通过")
            else:
                print(f"\n✗ L属性特性验证失败:")
                for 错误 in L属性错误:
                    print(f"  - {错误}")
            
            return True
            
        else:
            print("✗ 文法解析失败！")
            print("错误列表:")
            for 错误 in 错误列表:
                print(f"  - {错误}")
            return False
            
    except Exception as e:
        print(f"✗ 解析过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_example():
    """测试GUI中的示例文法"""
    print("\n=== 测试GUI示例文法 ===")
    
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
    
    解析器 = L属性文法解析器()
    
    try:
        成功, 文法, 错误列表 = 解析器.解析文法文件(示例文法)
        
        if 成功:
            print("✓ GUI示例文法解析成功！")
            print(f"产生式数量: {len(文法.产生式列表)}")
            print(f"语义规则数量: {sum(len(规则列表) for 规则列表 in 文法.语义规则表.values())}")
            return True
        else:
            print("✗ GUI示例文法解析失败！")
            print("错误列表:")
            for 错误 in 错误列表:
                print(f"  - {错误}")
            return False
            
    except Exception as e:
        print(f"✗ 解析过程中发生异常: {e}")
        return False

def test_semantic_analysis():
    """测试语义分析功能"""
    print("\n=== 测试语义分析功能 ===")

    # 读取示例文法文件
    try:
        with open('sample_grammar.txt', 'r', encoding='utf-8') as f:
            文法内容 = f.read()

        print("✓ 成功读取示例文法文件")

    except Exception as e:
        print(f"✗ 读取示例文法文件失败: {e}")
        return False

    # 解析文法
    解析器 = L属性文法解析器()

    try:
        成功, 文法, 错误列表 = 解析器.解析文法文件(文法内容)

        if not 成功:
            print("✗ 文法解析失败")
            return False

        print("✓ 文法解析成功")

        # 创建语义分析引擎
        from l_attribute_main import 语义分析引擎
        分析引擎 = 语义分析引擎(文法)

        # 测试语义分析
        输入串 = "int a , b , c"
        语法分析结果 = [0, 1, 4, 4, 5]  # 模拟的产生式序列

        成功, 分析步骤列表, 错误信息 = 分析引擎.执行语义分析(输入串, 语法分析结果)

        if 成功:
            print("✓ 语义分析执行成功")
            print(f"分析步骤数量: {len(分析步骤列表)}")
            print(f"符号表项数量: {len(分析引擎.符号表.表项)}")

            # 检查符号表内容
            符号表项 = list(分析引擎.符号表.表项.values())
            if 符号表项:
                print("符号表内容:")
                for 项 in 符号表项:
                    print(f"  {项.名称}: {项.类型}")

            return True
        else:
            print(f"✗ 语义分析失败: {错误信息}")
            return False

    except Exception as e:
        print(f"✗ 语义分析测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("L属性文法语义分析器 - 修复验证测试")
    print("=" * 50)

    测试结果 = []

    # 测试示例文法文件
    测试结果.append(("示例文法文件", test_sample_grammar()))

    # 测试GUI示例文法
    测试结果.append(("GUI示例文法", test_gui_example()))

    # 测试语义分析功能
    测试结果.append(("语义分析功能", test_semantic_analysis()))

    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")

    成功数 = 0
    总数 = len(测试结果)

    for 测试名, 结果 in 测试结果:
        状态 = "✓ 通过" if 结果 else "✗ 失败"
        print(f"  {测试名}: {状态}")
        if 结果:
            成功数 += 1

    print(f"\n总体结果: {成功数}/{总数} 测试通过")
    print(f"成功率: {(成功数/总数*100):.1f}%")

    if 成功数 == 总数:
        print("\n🎉 所有测试通过！修复成功。")
        return True
    else:
        print(f"\n⚠️  有 {总数-成功数} 个测试失败，需要进一步修复。")
        return False

if __name__ == "__main__":
    try:
        成功 = main()
        sys.exit(0 if 成功 else 1)
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
