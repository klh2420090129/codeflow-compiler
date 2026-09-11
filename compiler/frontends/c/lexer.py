from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Any
from compiler.errors import LexicalError

class CTokenType(Enum):
    # Keywords / Types
    INT = "INT"
    FLOAT = "FLOAT"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    PRINTF = "PRINTF"
    
    # Identifiers & Literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    MOD = "MOD"
    ASSIGN = "ASSIGN"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    GREATER = "GREATER"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    
    EOF = "EOF"

@dataclass
class CToken:
    type: CTokenType
    lexeme: str
    line: int
    column: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.name,
            "value": self.lexeme,
            "line": self.line,
            "column": self.column
        }

C_KEYWORDS = {
    "int": CTokenType.INT,
    "float": CTokenType.FLOAT,
    "if": CTokenType.IF,
    "else": CTokenType.ELSE,
    "while": CTokenType.WHILE,
    "printf": CTokenType.PRINTF,
}

# Unsupported C keywords to produce clear, explicit syntax errors immediately
C_UNSUPPORTED_KEYWORDS = {
    "for", "switch", "case", "default", "break", "continue", "return", "goto",
    "struct", "union", "enum", "typedef", "sizeof", "static", "const", "volatile",
    "char", "double", "long", "short", "signed", "unsigned", "void", "extern",
    "register", "auto", "do"
}

class CLexer:
    """Lexer for supported C subset with comment handling and precise diagnostics."""
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx >= self.length:
            return '\0'
        return self.source[idx]

    def advance(self) -> str:
        if self.pos >= self.length:
            return '\0'
        c = self.source[self.pos]
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def tokenize(self) -> List[CToken]:
        tokens: List[CToken] = []
        while self.pos < self.length:
            c = self.peek()

            # Whitespace
            if c.isspace():
                self.advance()
                continue

            # Preprocessor directives: explicitly reject #include, #define, etc.
            if c == '#':
                start_line = self.line
                start_col = self.column
                raise LexicalError("Preprocessor directives (#include, #define) are not supported in the CodeFlow C subset.", start_line, start_col)

            # Comments: single-line // and multi-line /* ... */
            if c == '/' and self.peek(1) == '/':
                self.skip_line_comment()
                continue
            if c == '/' and self.peek(1) == '*':
                self.skip_block_comment()
                continue

            start_line = self.line
            start_col = self.column

            # Identifiers and keywords
            if c.isalpha() or c == '_':
                tokens.append(self.lex_identifier(start_line, start_col))
            # Numeric literals
            elif c.isdigit():
                tokens.append(self.lex_number(start_line, start_col))
            # String literals (for printf format strings)
            elif c == '"':
                tokens.append(self.lex_string(start_line, start_col))
            else:
                tokens.append(self.lex_operator_or_delimiter(start_line, start_col))

        tokens.append(CToken(type=CTokenType.EOF, lexeme="<EOF>", line=self.line, column=self.column))
        return tokens

    def skip_line_comment(self):
        # consume //
        self.advance()
        self.advance()
        while self.pos < self.length and self.peek() != '\n':
            self.advance()

    def skip_block_comment(self):
        start_line = self.line
        start_col = self.column
        # consume /*
        self.advance()
        self.advance()
        while self.pos < self.length:
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance() # consume *
                self.advance() # consume /
                return
            self.advance()
        raise LexicalError("Unterminated block comment /* ... */.", start_line, start_col)

    def lex_identifier(self, start_line: int, start_col: int) -> CToken:
        lexeme_chars = []
        while self.pos < self.length and (self.peek().isalnum() or self.peek() == '_'):
            lexeme_chars.append(self.advance())
        lexeme = "".join(lexeme_chars)

        if lexeme in C_UNSUPPORTED_KEYWORDS:
            raise LexicalError(f"C keyword '{lexeme}' is not supported in this CodeFlow subset.", start_line, start_col)

        tok_type = C_KEYWORDS.get(lexeme, CTokenType.IDENTIFIER)
        return CToken(tok_type, lexeme, start_line, start_col)

    def lex_number(self, start_line: int, start_col: int) -> CToken:
        chars = []
        is_float = False
        while self.pos < self.length and self.peek().isdigit():
            chars.append(self.advance())

        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            chars.append(self.advance()) # '.'
            while self.pos < self.length and self.peek().isdigit():
                chars.append(self.advance())

        lexeme = "".join(chars)
        tok_type = CTokenType.FLOAT_LITERAL if is_float else CTokenType.INTEGER_LITERAL
        return CToken(tok_type, lexeme, start_line, start_col)

    def lex_string(self, start_line: int, start_col: int) -> CToken:
        # consume opening quote
        self.advance()
        chars = []
        while self.pos < self.length and self.peek() != '"':
            if self.peek() == '\n':
                raise LexicalError("Unterminated string literal.", start_line, start_col)
            if self.peek() == '\\':
                chars.append(self.advance())
                if self.pos < self.length:
                    chars.append(self.advance())
            else:
                chars.append(self.advance())

        if self.pos >= self.length:
            raise LexicalError("Unterminated string literal.", start_line, start_col)
        self.advance() # consume closing quote
        return CToken(CTokenType.STRING_LITERAL, "".join(chars), start_line, start_col)

    def lex_operator_or_delimiter(self, start_line: int, start_col: int) -> CToken:
        c = self.advance()

        # Two-character operators
        if c == '=':
            if self.peek() == '=':
                self.advance()
                return CToken(CTokenType.EQUAL_EQUAL, "==", start_line, start_col)
            return CToken(CTokenType.ASSIGN, "=", start_line, start_col)
        elif c == '!':
            if self.peek() == '=':
                self.advance()
                return CToken(CTokenType.NOT_EQUAL, "!=", start_line, start_col)
            return CToken(CTokenType.NOT, "!", start_line, start_col)
        elif c == '<':
            if self.peek() == '=':
                self.advance()
                return CToken(CTokenType.LESS_EQUAL, "<=", start_line, start_col)
            return CToken(CTokenType.LESS, "<", start_line, start_col)
        elif c == '>':
            if self.peek() == '=':
                self.advance()
                return CToken(CTokenType.GREATER_EQUAL, ">=", start_line, start_col)
            return CToken(CTokenType.GREATER, ">", start_line, start_col)
        elif c == '&':
            if self.peek() == '&':
                self.advance()
                return CToken(CTokenType.AND, "&&", start_line, start_col)
            raise LexicalError("Bitwise '&' or pointer address-of is not supported in this subset. Use '&&'.", start_line, start_col)
        elif c == '|':
            if self.peek() == '|':
                self.advance()
                return CToken(CTokenType.OR, "||", start_line, start_col)
            raise LexicalError("Bitwise '|' is not supported in this subset. Use '||'.", start_line, start_col)
        
        # Single-character arithmetic and delimiters
        elif c == '+': return CToken(CTokenType.PLUS, "+", start_line, start_col)
        elif c == '-': return CToken(CTokenType.MINUS, "-", start_line, start_col)
        elif c == '*': return CToken(CTokenType.STAR, "*", start_line, start_col)
        elif c == '/': return CToken(CTokenType.SLASH, "/", start_line, start_col)
        elif c == '%': return CToken(CTokenType.MOD, "%", start_line, start_col)
        elif c == '(': return CToken(CTokenType.LPAREN, "(", start_line, start_col)
        elif c == ')': return CToken(CTokenType.RPAREN, ")", start_line, start_col)
        elif c == '{': return CToken(CTokenType.LBRACE, "{", start_line, start_col)
        elif c == '}': return CToken(CTokenType.RBRACE, "}", start_line, start_col)
        elif c == ';': return CToken(CTokenType.SEMICOLON, ";", start_line, start_col)
        elif c == ',': return CToken(CTokenType.COMMA, ",", start_line, start_col)
        
        else:
            raise LexicalError(f"Unrecognized or unsupported character: '{c}'", start_line, start_col)
