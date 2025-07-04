# 词法分析程序 - GUI版本

## 概述

本程序是一个功能完整的词法分析器，提供了图形用户界面和可视化功能。支持Pascal语言的词法分析、正则表达式到自动机的转换，以及自动机的可视化展示。

## 功能特性

### 🔍 词法分析
- 支持Pascal语言的完整词法分析
- 识别关键字、标识符、数字、字符串、运算符、分隔符等
- 提供详细的Token信息（类型、值、位置）
- 统计分析结果
- 错误检测和报告

### 🔄 正则表达式转换
- 正则表达式到NFA转换
- NFA到DFA转换（子集构造算法）
- DFA最小化（分割算法）
- 支持基本正则表达式操作符：`|`、`*`、`+`、`?`

### 📊 可视化功能
- NFA状态转换图
- DFA状态转换图
- 最小DFA状态转换图
- 交互式图形界面
- 支持保存图片

### 💾 文件操作
- 加载代码文件
- 保存分析结果
- 导出可视化图片
- 支持多种文件格式

## 安装和运行

### 环境要求
- Python 3.7+
- tkinter（Python内置）
- matplotlib
- networkx
- numpy

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python lexical_analyzer_gui.py
```

## 使用说明

### 词法分析标签页

1. **输入代码**：在左侧文本框中输入Pascal代码
2. **执行分析**：点击"分析代码"按钮
3. **查看结果**：右侧表格显示识别的Token
4. **统计信息**：底部显示各类型Token的统计
5. **文件操作**：
   - 点击"加载文件"导入代码文件
   - 点击"保存结果"导出分析结果
   - 点击"清空"清除输入和结果

### 正则表达式转换标签页

1. **输入正则表达式**：在输入框中输入正则表达式
2. **选择转换步骤**：
   - "转换为NFA"：将正则表达式转换为NFA
   - "NFA转DFA"：将NFA转换为DFA
   - "DFA最小化"：最小化DFA
   - "完整流程"：一次性执行所有转换步骤
3. **查看结果**：转换结果显示在下方文本区域

### 自动机可视化标签页

1. **选择自动机类型**：选择要可视化的自动机（NFA、DFA、最小DFA）
2. **生成图形**：点击"生成图形"按钮
3. **查看图形**：状态转换图显示在下方
4. **保存图片**：点击"保存图片"导出可视化结果

## 支持的Token类型

### 关键字
- `program`, `var`, `begin`, `end`
- `if`, `then`, `else`
- `while`, `do`, `for`, `to`
- `repeat`, `until`
- `function`, `procedure`

### 数据类型
- `integer`, `real`, `boolean`, `char`, `string`

### 运算符
- 算术运算符：`+`, `-`, `*`, `/`
- 赋值运算符：`:=`
- 比较运算符：`=`, `<>`, `<`, `>`, `<=`, `>=`

### 分隔符
- `;`, `,`, `.`, `:`
- `(`, `)`, `[`, `]`

### 其他
- 标识符：以字母或下划线开头
- 数字：整数和浮点数
- 字符串：单引号包围
- 注释：`//` 单行注释，`/* */` 多行注释

## 正则表达式语法

### 基本操作符
- **字符**：直接输入字符，如 `a`
- **选择**：使用 `|` 分隔选项，如 `a|b`
- **连接**：直接连写，如 `ab`
- **Kleene闭包**：使用 `*`，如 `a*`
- **正闭包**：使用 `+`，如 `a+`
- **可选**：使用 `?`，如 `a?`
- **分组**：使用括号，如 `(ab)*`

### 示例
- `(a|b)*abb`：以abb结尾的a和b组成的字符串
- `[0-9]+`：一个或多个数字
- `[a-zA-Z][a-zA-Z0-9]*`：标识符模式

## 快捷键

- `Ctrl+O`：加载文件
- `Ctrl+S`：保存结果
- `F5`：执行分析
- `Ctrl+L`：清空输入

## 示例代码

```pascal
program Example;
var
    x, y: integer;
    result: real;
begin
    x := 10;
    y := 20;
    if x > y then
        result := x / y
    else
        result := y / x;
    writeln(result);
end.
```

## 技术实现

### 核心算法
- **Thompson构造算法**：正则表达式到NFA转换
- **子集构造算法**：NFA到DFA转换
- **分割算法**：DFA最小化

### 数据结构
- **State类**：表示自动机状态
- **NFA类**：非确定性有限自动机
- **DFA类**：确定性有限自动机
- **Token类**：词法单元

### GUI框架
- **tkinter**：主要GUI框架
- **matplotlib**：图形绘制
- **networkx**：图形布局算法

## 故障排除

### 常见问题

1. **程序无法启动**
   - 检查Python版本（需要3.7+）
   - 确认已安装所有依赖包
   - 运行 `pip install -r requirements.txt`

2. **中文显示乱码**
   - 程序会自动设置中文字体
   - 如果仍有问题，请安装SimHei或Microsoft YaHei字体

3. **可视化图形不显示**
   - 确认matplotlib正确安装
   - 检查是否有图形显示权限

4. **正则表达式转换失败**
   - 检查正则表达式语法
   - 当前版本支持基本操作符，复杂表达式可能不支持

### 性能优化

- 对于大型自动机，可视化可能较慢
- 建议先测试小规模的正则表达式
- 复杂的DFA可能包含大量状态

## 扩展功能

### 可能的改进
- 支持更复杂的正则表达式语法
- 添加更多编程语言的词法规则
- 实现语法分析功能
- 添加代码高亮显示
- 支持自定义词法规则

## 许可证

本程序仅供学习和研究使用。

## 联系信息

如有问题或建议，请联系开发者。

---

**注意**：本程序是编译原理课程的实验项目，主要用于教学和学习目的。