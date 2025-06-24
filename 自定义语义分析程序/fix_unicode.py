#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复测试文件中的Unicode字符编码问题
"""

import os
import re

def 修复文件Unicode(文件路径):
    """修复单个文件的Unicode字符"""
    try:
        with open(文件路径, 'r', encoding='utf-8') as f:
            内容 = f.read()
        
        # 替换Unicode字符
        替换映射 = {
            '✓': '√',
            '❌': '×',
            '⚠️': '!',
            '🎉': '*',
            '💥': '!',
        }
        
        原始内容 = 内容
        for 原字符, 新字符 in 替换映射.items():
            内容 = 内容.replace(原字符, 新字符)
        
        if 内容 != 原始内容:
            with open(文件路径, 'w', encoding='utf-8') as f:
                f.write(内容)
            print(f"√ 修复文件: {文件路径}")
            return True
        else:
            print(f"- 无需修复: {文件路径}")
            return False
            
    except Exception as e:
        print(f"× 修复失败: {文件路径} - {e}")
        return False

def main():
    """主函数"""
    print("修复测试文件Unicode字符")
    print("=" * 30)
    
    测试文件列表 = [
        "test_s_attribute.py",
        "test_l_attribute.py",
        "test_dependency_graph.py",
        "comprehensive_test.py",
        "final_acceptance_test.py"
    ]
    
    修复计数 = 0
    
    for 文件 in 测试文件列表:
        if os.path.exists(文件):
            if 修复文件Unicode(文件):
                修复计数 += 1
        else:
            print(f"- 文件不存在: {文件}")
    
    print(f"\n修复完成，共修复 {修复计数} 个文件")

if __name__ == "__main__":
    main()
