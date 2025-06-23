#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token定义模块

定义编译器中使用的所有Token类型和Token数据结构。
支持多种编程语言的Token类型。
"""

import enum
from dataclasses import dataclass
from typing import Optional, Any, Tuple


class TokenType(enum.Enum):
    """Token类型枚举
    
    包含常见编程语言的所有Token类型，支持Pascal、C等语言。
    """
    
    # === Pascal关键字 ===
    PROGRAM = "PROGRAM"
    VAR = "VAR"
    CONST = "CONST"
    PROCEDURE = "PROCEDURE"
    FUNCTION = "FUNCTION"
    BEGIN = "BEGIN"
    END = "END"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    FOR = "FOR"
    TO = "TO"
    DOWNTO = "DOWNTO"
    REPEAT = "REPEAT"
    UNTIL = "UNTIL"
    CASE = "CASE"
    OF = "OF"
    
    # === C关键字 ===
    AUTO = "AUTO"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    DEFAULT = "DEFAULT"
    ENUM = "ENUM"
    EXTERN = "EXTERN"
    GOTO = "GOTO"
    REGISTER = "REGISTER"
    RETURN = "RETURN"
    SIZEOF = "SIZEOF"
    STATIC = "STATIC"
    STRUCT = "STRUCT"
    SWITCH = "SWITCH"
    TYPEDEF = "TYPEDEF"
    TYPE = "TYPE"
    UNION = "UNION"
    VOLATILE = "VOLATILE"
    
    # === 数据类型 ===
    # Pascal类型
    INTEGER = "INTEGER"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    CHAR = "CHAR"
    STRING = "STRING"
    
    # C类型
    INT = "INT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    VOID = "VOID"
    SHORT = "SHORT"
    LONG = "LONG"
    SIGNED = "SIGNED"
    UNSIGNED = "UNSIGNED"
    
    # === 标识符和字面量 ===
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"
    
    # === 运算符 ===
    # 算术运算符
    PLUS = "PLUS"                    # +
    MINUS = "MINUS"                  # -
    MULTIPLY = "MULTIPLY"            # *
    DIVIDE = "DIVIDE"                # /
    MODULO = "MODULO"                # %
    MOD = "MOD"                      # mod (Pascal)
    DIV = "DIV"                      # div (Pascal)
    
    # 赋值运算符
    ASSIGN = "ASSIGN"                # := (Pascal) 或 = (C)
    PLUS_ASSIGN = "PLUS_ASSIGN"      # +=
    MINUS_ASSIGN = "MINUS_ASSIGN"    # -=
    MUL_ASSIGN = "MUL_ASSIGN"        # *=
    MULTIPLY_ASSIGN = "MULTIPLY_ASSIGN"  # *=
    DIV_ASSIGN = "DIV_ASSIGN"        # /=
    DIVIDE_ASSIGN = "DIVIDE_ASSIGN"  # /=
    MODULO_ASSIGN = "MODULO_ASSIGN"  # %=
    BITWISE_AND_ASSIGN = "BITWISE_AND_ASSIGN"  # &=
    BITWISE_OR_ASSIGN = "BITWISE_OR_ASSIGN"    # |=
    BITWISE_XOR_ASSIGN = "BITWISE_XOR_ASSIGN"  # ^=
    MOD_ASSIGN = "MOD_ASSIGN"        # %=
    LEFT_SHIFT_ASSIGN = "LEFT_SHIFT_ASSIGN"  # <<=
    RIGHT_SHIFT_ASSIGN = "RIGHT_SHIFT_ASSIGN"  # >>=
    
    # 比较运算符
    EQUAL = "EQUAL"                  # = (Pascal) 或 == (C)
    EQUAL_EQUAL = "EQUAL_EQUAL"      # == (C)
    NOT_EQUAL = "NOT_EQUAL"          # <> (Pascal) 或 != (C)
    LESS = "LESS"                    # <
    LESS_EQUAL = "LESS_EQUAL"        # <=
    GREATER = "GREATER"              # >
    GREATER_EQUAL = "GREATER_EQUAL"  # >=
    
    # 逻辑运算符
    AND = "AND"                      # and (Pascal) 或 && (C)
    OR = "OR"                        # or (Pascal) 或 || (C)
    NOT = "NOT"                      # not (Pascal) 或 ! (C)
    LOGICAL_AND = "LOGICAL_AND"      # && (C)
    LOGICAL_OR = "LOGICAL_OR"        # || (C)
    LOGICAL_NOT = "LOGICAL_NOT"      # ! (C)
    
    # 位运算符
    BITWISE_AND = "BITWISE_AND"      # &
    BITWISE_OR = "BITWISE_OR"        # |
    BITWISE_XOR = "BITWISE_XOR"      # ^
    BITWISE_NOT = "BITWISE_NOT"      # ~
    LEFT_SHIFT = "LEFT_SHIFT"        # <<
    RIGHT_SHIFT = "RIGHT_SHIFT"      # >>
    
    # 自增自减
    INCREMENT = "INCREMENT"          # ++
    DECREMENT = "DECREMENT"          # --
    
    # === 分隔符 ===
    SEMICOLON = "SEMICOLON"          # ;
    COMMA = "COMMA"                  # ,
    DOT = "DOT"                      # .
    COLON = "COLON"                  # :
    QUESTION = "QUESTION"            # ?
    
    # 括号
    LPAREN = "LPAREN"                # (
    RPAREN = "RPAREN"                # )
    LBRACKET = "LBRACKET"            # [
    RBRACKET = "RBRACKET"            # ]
    LBRACE = "LBRACE"                # {
    RBRACE = "RBRACE"                # }
    
    # 指针和引用 (C)
    POINTER = "POINTER"              # *
    ADDRESS = "ADDRESS"              # &
    ARROW = "ARROW"                  # ->
    
    # 预处理器 (C)
    HASH = "HASH"                    # #
    PREPROCESSOR = "PREPROCESSOR"    # 预处理指令
    
    # === 特殊Token ===
    EOF = "EOF"                      # 文件结束
    NEWLINE = "NEWLINE"              # 换行
    WHITESPACE = "WHITESPACE"        # 空白字符
    COMMENT = "COMMENT"              # 注释
    ERROR = "ERROR"                  # 错误Token
    UNKNOWN = "UNKNOWN"              # 未知Token


@dataclass
class Token:
    """Token数据结构
    
    表示词法分析过程中识别出的一个Token。
    
    Attributes:
        type: Token类型
        value: Token的字符串值
        line: 所在行号 (从1开始)
        column: 所在列号 (从1开始)
        length: Token长度
        metadata: 附加元数据
    """
    type: TokenType
    value: str
    line: int
    column: int
    length: Optional[int] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.length is None:
            self.length = len(self.value)
        if self.metadata is None:
            self.metadata = {}
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"Token(type={self.type.value}, value='{self.value}', "
                f"line={self.line}, column={self.column}, length={self.length})") 
    
    def is_keyword(self) -> bool:
        """判断是否为关键字"""
        keywords = {
            # Pascal关键字
            TokenType.PROGRAM, TokenType.VAR, TokenType.CONST, TokenType.PROCEDURE,
            TokenType.FUNCTION, TokenType.BEGIN, TokenType.END, TokenType.IF,
            TokenType.THEN, TokenType.ELSE, TokenType.WHILE, TokenType.DO,
            TokenType.FOR, TokenType.TO, TokenType.REPEAT, TokenType.UNTIL,
            TokenType.CASE, TokenType.OF, TokenType.MOD, TokenType.DIV,
            TokenType.AND, TokenType.OR, TokenType.NOT,
            
            # C关键字
            TokenType.AUTO, TokenType.BREAK, TokenType.CONTINUE, TokenType.DEFAULT,
            TokenType.ENUM, TokenType.EXTERN, TokenType.GOTO, TokenType.REGISTER,
            TokenType.RETURN, TokenType.SIZEOF, TokenType.STATIC, TokenType.STRUCT,
            TokenType.SWITCH, TokenType.TYPEDEF, TokenType.UNION, TokenType.VOLATILE,
            
            # 数据类型
            TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN, TokenType.CHAR,
            TokenType.STRING, TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.VOID, TokenType.SHORT, TokenType.LONG, TokenType.SIGNED,
            TokenType.UNSIGNED
        }
        return self.type in keywords
    
    def is_operator(self) -> bool:
        """判断是否为运算符"""
        operators = {
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.MOD, TokenType.DIV, TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.MUL_ASSIGN,
            TokenType.DIV_ASSIGN, TokenType.MOD_ASSIGN, TokenType.EQUAL,
            TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.AND, TokenType.OR,
            TokenType.NOT, TokenType.BITWISE_AND, TokenType.BITWISE_OR,
            TokenType.BITWISE_XOR, TokenType.BITWISE_NOT, TokenType.LEFT_SHIFT,
            TokenType.RIGHT_SHIFT, TokenType.INCREMENT, TokenType.DECREMENT,
            TokenType.POINTER, TokenType.ADDRESS, TokenType.ARROW
        }
        return self.type in operators
    
    def is_literal(self) -> bool:
        """判断是否为字面量"""
        literals = {
            TokenType.NUMBER, TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL,
            TokenType.STRING_LITERAL, TokenType.CHAR_LITERAL
        }
        return self.type in literals
    
    def is_delimiter(self) -> bool:
        """判断是否为分隔符"""
        delimiters = {
            TokenType.SEMICOLON, TokenType.COMMA, TokenType.DOT, TokenType.COLON,
            TokenType.QUESTION, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.LBRACE, TokenType.RBRACE
        }
        return self.type in delimiters
    
    def is_whitespace(self) -> bool:
        """判断是否为空白字符"""
        return self.type in {TokenType.WHITESPACE, TokenType.NEWLINE}
    
    def get_end_position(self) -> Tuple[int, int]:
        """获取Token结束位置"""
        if '\n' in self.value:
            lines = self.value.split('\n')
            end_line = self.line + len(lines) - 1
            end_column = len(lines[-1]) if len(lines) > 1 else self.column + len(self.value)
        else:
            end_line = self.line
            end_column = self.column + len(self.value)
        return end_line, end_column


class TokenCategory(enum.Enum):
    """Token分类
    
    用于将Token按功能分类，便于语法分析和语义分析。
    """
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"
    SPECIAL = "SPECIAL"
    ERROR = "ERROR"


def get_token_category(token_type: TokenType) -> TokenCategory:
    """获取Token的分类
    
    Args:
        token_type: Token类型
        
    Returns:
        Token分类
    """
    # 创建一个临时Token来使用其方法
    temp_token = Token(token_type, "", 0, 0)
    
    if temp_token.is_keyword():
        return TokenCategory.KEYWORD
    elif token_type == TokenType.IDENTIFIER:
        return TokenCategory.IDENTIFIER
    elif temp_token.is_literal():
        return TokenCategory.LITERAL
    elif temp_token.is_operator():
        return TokenCategory.OPERATOR
    elif temp_token.is_delimiter():
        return TokenCategory.DELIMITER
    elif temp_token.is_whitespace():
        return TokenCategory.WHITESPACE
    elif token_type == TokenType.COMMENT:
        return TokenCategory.COMMENT
    elif token_type in {TokenType.EOF, TokenType.HASH}:
        return TokenCategory.SPECIAL
    else:
        return TokenCategory.ERROR