#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词法分析器核心模块

实现词法分析的核心功能：
- 词法规则管理
- 词法分析算法
- Token识别和生成
- 错误处理
"""

import re
from typing import List, Dict, Optional, Tuple
from .token import Token, TokenType
from .automata import RegexToNFA, NFAToDFA, DFAMinimizer, NFA, DFA


class LexicalRule:
    """词法规则类"""
    
    def __init__(self, pattern: str, token_type: TokenType, priority: int = 0):
        self.pattern = pattern
        self.token_type = token_type
        self.priority = priority
        self.regex = re.compile(pattern)
        
        # 构建NFA/DFA（可选，用于高级功能）
        self.nfa: Optional[NFA] = None
        self.dfa: Optional[DFA] = None
    
    def build_automata(self):
        """构建自动机"""
        try:
            converter = RegexToNFA()
            self.nfa = converter.convert(self.pattern, self.token_type)
            
            nfa_to_dfa = NFAToDFA()
            self.dfa = nfa_to_dfa.convert(self.nfa)
        except Exception:
            # 如果构建失败，保持为None
            pass
    
    def match(self, text: str, position: int) -> Optional[re.Match]:
        """在指定位置匹配文本"""
        return self.regex.match(text, position)
    
    def __str__(self):
        return f"Rule({self.pattern}, {self.token_type.value}, {self.priority})"


class LexicalAnalyzer:
    """词法分析器主类"""
    
    def __init__(self):
        self.rules: List[LexicalRule] = []
        self.tokens: List[Token] = []
        self.errors: List[str] = []
        self.current_line = 1
        self.current_column = 1
        self.keywords: Dict[str, TokenType] = {}
        
        # 初始化默认规则
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认的词法规则（Pascal语言）"""
        # Pascal关键字
        keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'const': TokenType.CONST,
            'type': TokenType.TYPE,
            'function': TokenType.FUNCTION,
            'procedure': TokenType.PROCEDURE,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'for': TokenType.FOR,
            'to': TokenType.TO,
            'downto': TokenType.DOWNTO,
            'repeat': TokenType.REPEAT,
            'until': TokenType.UNTIL,
            'case': TokenType.CASE,
            'of': TokenType.OF,
            'integer': TokenType.INTEGER,
            'real': TokenType.REAL,
            'boolean': TokenType.BOOLEAN,
            'char': TokenType.CHAR,
            'string': TokenType.STRING,
            'mod': TokenType.MOD,
            'div': TokenType.DIV,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
        }
        self.keywords = keywords
        
        # 词法规则（按优先级排序）
        rules = [
            # 注释
            (r'\{[^}]*\}', TokenType.COMMENT, 10),
            (r'//.*', TokenType.COMMENT, 10),
            
            # 字符串和字符字面量
            (r"'([^'\\]|\\.)*'", TokenType.STRING_LITERAL, 9),
            (r"'([^'\\]|\\.)'?", TokenType.CHAR_LITERAL, 9),
            
            # 数字
            (r'\d+\.\d+', TokenType.NUMBER, 8),  # 实数
            (r'\d+', TokenType.NUMBER, 8),       # 整数
            
            # 双字符运算符
            (r':=', TokenType.ASSIGN, 7),
            (r'<=', TokenType.LESS_EQUAL, 7),
            (r'>=', TokenType.GREATER_EQUAL, 7),
            (r'<>', TokenType.NOT_EQUAL, 7),
            
            # 单字符运算符和分隔符
            (r'\+', TokenType.PLUS, 6),
            (r'-', TokenType.MINUS, 6),
            (r'\*', TokenType.MULTIPLY, 6),
            (r'/', TokenType.DIVIDE, 6),
            (r'=', TokenType.EQUAL, 6),
            (r'<', TokenType.LESS, 6),
            (r'>', TokenType.GREATER, 6),
            (r';', TokenType.SEMICOLON, 6),
            (r',', TokenType.COMMA, 6),
            (r'\.', TokenType.DOT, 6),
            (r':', TokenType.COLON, 6),
            (r'\(', TokenType.LPAREN, 6),
            (r'\)', TokenType.RPAREN, 6),
            (r'\[', TokenType.LBRACKET, 6),
            (r'\]', TokenType.RBRACKET, 6),
            
            # 标识符（必须在关键字检查之后）
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER, 5),
            
            # 空白字符
            (r'\n', TokenType.NEWLINE, 1),
            (r'[ \t]+', TokenType.WHITESPACE, 1),
        ]
        
        for pattern, token_type, priority in rules:
            self.add_rule(pattern, token_type, priority)
    
    def init_c_rules(self):
        """初始化C语言的词法规则"""
        self.rules.clear()
        
        # C语言关键字
        c_keywords = {
            'auto': TokenType.AUTO,
            'break': TokenType.BREAK,
            'case': TokenType.CASE,
            'char': TokenType.CHAR,
            'const': TokenType.CONST,
            'continue': TokenType.CONTINUE,
            'default': TokenType.DEFAULT,
            'do': TokenType.DO,
            'double': TokenType.DOUBLE,
            'else': TokenType.ELSE,
            'enum': TokenType.ENUM,
            'extern': TokenType.EXTERN,
            'float': TokenType.FLOAT,
            'for': TokenType.FOR,
            'goto': TokenType.GOTO,
            'if': TokenType.IF,
            'int': TokenType.INT,
            'long': TokenType.LONG,
            'register': TokenType.REGISTER,
            'return': TokenType.RETURN,
            'short': TokenType.SHORT,
            'signed': TokenType.SIGNED,
            'sizeof': TokenType.SIZEOF,
            'static': TokenType.STATIC,
            'struct': TokenType.STRUCT,
            'switch': TokenType.SWITCH,
            'typedef': TokenType.TYPEDEF,
            'union': TokenType.UNION,
            'unsigned': TokenType.UNSIGNED,
            'void': TokenType.VOID,
            'volatile': TokenType.VOLATILE,
            'while': TokenType.WHILE,
        }
        self.keywords = c_keywords
        
        # C语言词法规则
        c_rules = [
            # 预处理指令
            (r'#[^\n]*', TokenType.PREPROCESSOR, 10),
            
            # 注释
            (r'/\*[\s\S]*?\*/', TokenType.COMMENT, 10),  # 多行注释
            (r'//.*', TokenType.COMMENT, 10),            # 单行注释
            
            # 字符串和字符字面量
            (r'"([^"\\]|\\.)*"', TokenType.STRING_LITERAL, 9),
            (r"'([^'\\]|\\.)'?", TokenType.CHAR_LITERAL, 9),
            
            # 数字字面量
            (r'0[xX][0-9a-fA-F]+[lLuU]*', TokenType.NUMBER, 8),  # 十六进制
            (r'0[0-7]+[lLuU]*', TokenType.NUMBER, 8),            # 八进制
            (r'\d+\.\d+[fFlL]?', TokenType.NUMBER, 8),           # 浮点数
            (r'\d+[lLuU]*', TokenType.NUMBER, 8),               # 十进制整数
            
            # 三字符运算符
            (r'<<=', TokenType.LEFT_SHIFT_ASSIGN, 7),
            (r'>>=', TokenType.RIGHT_SHIFT_ASSIGN, 7),
            
            # 双字符运算符
            (r'\+\+', TokenType.INCREMENT, 7),
            (r'--', TokenType.DECREMENT, 7),
            (r'<<', TokenType.LEFT_SHIFT, 7),
            (r'>>', TokenType.RIGHT_SHIFT, 7),
            (r'<=', TokenType.LESS_EQUAL, 7),
            (r'>=', TokenType.GREATER_EQUAL, 7),
            (r'==', TokenType.EQUAL_EQUAL, 7),
            (r'!=', TokenType.NOT_EQUAL, 7),
            (r'&&', TokenType.LOGICAL_AND, 7),
            (r'\|\|', TokenType.LOGICAL_OR, 7),
            (r'\+=', TokenType.PLUS_ASSIGN, 7),
            (r'-=', TokenType.MINUS_ASSIGN, 7),
            (r'\*=', TokenType.MULTIPLY_ASSIGN, 7),
            (r'/=', TokenType.DIVIDE_ASSIGN, 7),
            (r'%=', TokenType.MODULO_ASSIGN, 7),
            (r'&=', TokenType.BITWISE_AND_ASSIGN, 7),
            (r'\|=', TokenType.BITWISE_OR_ASSIGN, 7),
            (r'\^=', TokenType.BITWISE_XOR_ASSIGN, 7),
            (r'->', TokenType.ARROW, 7),
            
            # 单字符运算符和分隔符
            (r'\+', TokenType.PLUS, 6),
            (r'-', TokenType.MINUS, 6),
            (r'\*', TokenType.MULTIPLY, 6),
            (r'/', TokenType.DIVIDE, 6),
            (r'%', TokenType.MODULO, 6),
            (r'=', TokenType.ASSIGN, 6),
            (r'<', TokenType.LESS, 6),
            (r'>', TokenType.GREATER, 6),
            (r'&', TokenType.BITWISE_AND, 6),
            (r'\|', TokenType.BITWISE_OR, 6),
            (r'\^', TokenType.BITWISE_XOR, 6),
            (r'~', TokenType.BITWISE_NOT, 6),
            (r'!', TokenType.LOGICAL_NOT, 6),
            (r'\?', TokenType.QUESTION, 6),
            (r';', TokenType.SEMICOLON, 6),
            (r',', TokenType.COMMA, 6),
            (r'\.', TokenType.DOT, 6),
            (r':', TokenType.COLON, 6),
            (r'\(', TokenType.LPAREN, 6),
            (r'\)', TokenType.RPAREN, 6),
            (r'\[', TokenType.LBRACKET, 6),
            (r'\]', TokenType.RBRACKET, 6),
            (r'\{', TokenType.LBRACE, 6),
            (r'\}', TokenType.RBRACE, 6),
            
            # 标识符
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER, 5),
            
            # 空白字符
            (r'\n', TokenType.NEWLINE, 1),
            (r'[ \t]+', TokenType.WHITESPACE, 1),
        ]
        
        for pattern, token_type, priority in c_rules:
            self.add_rule(pattern, token_type, priority)
    
    def add_rule(self, pattern: str, token_type: TokenType, priority: int = 0):
        """添加词法规则"""
        rule = LexicalRule(pattern, token_type, priority)
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda x: x.priority, reverse=True)
    
    def load_rules_from_file(self, filename: str) -> bool:
        """从文件加载词法规则"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            pattern = parts[0]
                            token_type_name = parts[1]
                            priority = int(parts[2]) if len(parts) > 2 else 0
                            
                            # 查找对应的TokenType
                            token_type = None
                            for tt in TokenType:
                                if tt.value == token_type_name:
                                    token_type = tt
                                    break
                            
                            if token_type:
                                self.add_rule(pattern, token_type, priority)
                            else:
                                self.errors.append(f"第{line_num}行: 未知的Token类型 '{token_type_name}'")
                        else:
                            self.errors.append(f"第{line_num}行: 格式错误，应为 '模式\t类型\t优先级'")
            return True
        except Exception as e:
            self.errors.append(f"加载规则文件失败: {e}")
            return False
    
    def analyze(self, text: str) -> List[Token]:
        """执行词法分析"""
        self.tokens = []
        self.errors = []
        self.current_line = 1
        self.current_column = 1
        
        position = 0
        while position < len(text):
            matched = False
            
            # 尝试匹配每个规则
            for rule in self.rules:
                match = rule.match(text, position)
                if match:
                    value = match.group(0)
                    token_type = rule.token_type
                    
                    # 检查是否为关键字
                    if token_type == TokenType.IDENTIFIER and value.lower() in self.keywords:
                        token_type = self.keywords[value.lower()]
                    
                    # 创建Token（跳过空白字符和注释）
                    if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                        token = Token(token_type, value, self.current_line, self.current_column)
                        self.tokens.append(token)
                    
                    # 更新位置信息
                    if token_type == TokenType.NEWLINE:
                        self.current_line += 1
                        self.current_column = 1
                    else:
                        self.current_column += len(value)
                    
                    position = match.end()
                    matched = True
                    break
            
            if not matched:
                # 未匹配的字符，报告错误
                char = text[position]
                error_msg = f"未识别的字符 '{char}' 在第 {self.current_line} 行第 {self.current_column} 列"
                self.errors.append(error_msg)
                
                # 创建错误Token
                error_token = Token(TokenType.ERROR, char, self.current_line, self.current_column)
                self.tokens.append(error_token)
                
                position += 1
                self.current_column += 1
        
        # 添加EOF Token
        eof_token = Token(TokenType.EOF, '', self.current_line, self.current_column)
        self.tokens.append(eof_token)
        
        return self.tokens
    
    def analyze_with_automata(self, text: str) -> List[Token]:
        """使用自动机进行词法分析（实验性功能）"""
        # 为所有规则构建自动机
        for rule in self.rules:
            if rule.dfa is None:
                rule.build_automata()
        
        # 使用标准方法分析（自动机方法需要更复杂的实现）
        return self.analyze(text)
    
    def get_tokens_table(self) -> List[List[str]]:
        """获取Token表格"""
        table = []
        table.append(["序号", "Token类型", "值", "行号", "列号"])
        
        for i, token in enumerate(self.tokens, 1):
            table.append([
                str(i),
                token.type.value,
                token.value,
                str(token.line),
                str(token.column)
            ])
        
        return table
    
    def get_token_statistics(self) -> Dict[str, int]:
        """获取Token统计信息"""
        stats = {}
        for token in self.tokens:
            token_name = token.type.value
            stats[token_name] = stats.get(token_name, 0) + 1
        return stats
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
        return len(self.errors) > 0 or any(token.type == TokenType.ERROR for token in self.tokens)
    
    def clear(self):
        """清空分析结果"""
        self.tokens = []
        self.errors = []
        self.current_line = 1
        self.current_column = 1
    
    def get_rule_count(self) -> int:
        """获取规则数量"""
        return len(self.rules)
    
    def get_rules_info(self) -> List[Dict[str, str]]:
        """获取规则信息"""
        info = []
        for rule in self.rules:
            info.append({
                'pattern': rule.pattern,
                'token_type': rule.token_type.value,
                'priority': str(rule.priority)
            })
        return info


def create_pascal_analyzer() -> LexicalAnalyzer:
    """创建Pascal语言词法分析器"""
    analyzer = LexicalAnalyzer()
    # 默认已经是Pascal规则
    return analyzer


def create_c_analyzer() -> LexicalAnalyzer:
    """创建C语言词法分析器"""
    analyzer = LexicalAnalyzer()
    analyzer.init_c_rules()
    return analyzer


def analyze_file(filename: str, language: str = 'pascal') -> Tuple[List[Token], List[str]]:
    """分析文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if language.lower() == 'c':
            analyzer = create_c_analyzer()
        else:
            analyzer = create_pascal_analyzer()
        
        tokens = analyzer.analyze(content)
        errors = analyzer.get_errors()
        
        return tokens, errors
    except Exception as e:
        return [], [f"读取文件失败: {e}"]