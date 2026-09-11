from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
from compiler.errors import LexicalError

class CPPTokenType(Enum):
    # Keywords
    INT = "INT"
    DOUBLE = "DOUBLE"
    BOOL = "BOOL"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    MAIN = "MAIN"
    RETURN = "RETURN"

    # std::cout and std::endl tokens
    STD_COUT = "STD_COUT"
    STD_ENDL = "STD_ENDL"

    # Identifiers and literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"

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

    # Stream insertion operator <<
    STREAM_OUT = "STREAM_OUT"

    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"

    EOF = "EOF"

@dataclass
class CPPToken:
    type: CPPTokenType
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

CPP_KEYWORDS = {
    "int": CPPTokenType.INT,
    "double": CPPTokenType.DOUBLE,
    "bool": CPPTokenType.BOOL,
    "true": CPPTokenType.TRUE,
    "false": CPPTokenType.FALSE,
    "if": CPPTokenType.IF,
    "else": CPPTokenType.ELSE,
    "while": CPPTokenType.WHILE,
    "main": CPPTokenType.MAIN,
    "return": CPPTokenType.RETURN,
}

CPP_UNSUPPORTED_KEYWORDS = {
    "alignas", "alignof", "and", "and_eq", "asm", "atomic_cancel",
    "atomic_commit", "atomic_noexcept", "auto", "bitand", "bitor",
    "break", "case", "catch", "char", "char8_t", "char16_t", "char32_t",
    "class", "compl", "concept", "const", "consteval", "constexpr",
    "constinit", "const_cast", "continue", "co_await", "co_return",
    "co_yield", "decltype", "default", "delete", "do", "dynamic_cast",
    "enum", "explicit", "export", "extern", "float", "for", "friend",
    "goto", "inline", "long", "mutable", "namespace", "new", "noexcept",
    "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private",
    "protected", "public", "reflexpr", "register", "reinterpret_cast",
    "requires", "short", "signed", "sizeof", "static", "static_assert",
    "static_cast", "struct", "switch", "synchronized", "template",
    "this", "thread_local", "throw", "try", "typedef", "typeid",
    "typename", "union", "unsigned", "using", "virtual", "void",
    "volatile", "wchar_t", "xor", "xor_eq"
}

class CPPLexer:
    """Lexer for supported C++ subset."""
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

    def tokenize(self) -> List[CPPToken]:
        tokens: List[CPPToken] = []
        while self.pos < self.length:
            c = self.peek()

            if c.isspace():
                self.advance()
                continue

            start_line = self.line
            start_col = self.column

            # Reject preprocessor directives immediately: #include, #define, etc.
            if c == '#':
                self.advance()
                while self.pos < self.length and self.peek() not in ('\n', '\0'):
                    self.advance()
                raise LexicalError("Preprocessor directives (#include, #define, etc.) are not supported in this CodeFlow C++ subset.", start_line, start_col)

            # Single-line comment //
            if c == '/' and self.peek(1) == '/':
                self.skip_line_comment()
                continue

            # Multi-line comment /* ... */
            if c == '/' and self.peek(1) == '*':
                self.skip_block_comment()
                continue

            # Check for std::cout and std::endl
            if self.source.startswith("std::cout", self.pos):
                next_pos = self.pos + len("std::cout")
                if next_pos >= self.length or not (self.source[next_pos].isalnum() or self.source[next_pos] == '_'):
                    for _ in range(len("std::cout")):
                        self.advance()
                    tokens.append(CPPToken(CPPTokenType.STD_COUT, "std::cout", start_line, start_col))
                    continue

            if self.source.startswith("std::endl", self.pos):
                next_pos = self.pos + len("std::endl")
                if next_pos >= self.length or not (self.source[next_pos].isalnum() or self.source[next_pos] == '_'):
                    for _ in range(len("std::endl")):
                        self.advance()
                    tokens.append(CPPToken(CPPTokenType.STD_ENDL, "std::endl", start_line, start_col))
                    continue

            # Identifiers and keywords
            if c.isalpha() or c in ('_', '$'):
                tokens.append(self.lex_identifier(start_line, start_col))
            elif c.isdigit():
                tokens.append(self.lex_number(start_line, start_col))
            else:
                tokens.append(self.lex_operator_or_delimiter(start_line, start_col))

        tokens.append(CPPToken(type=CPPTokenType.EOF, lexeme="<EOF>", line=self.line, column=self.column))
        return tokens

    def skip_line_comment(self):
        self.advance() # /
        self.advance() # /
        while self.pos < self.length and self.peek() != '\n':
            self.advance()

    def skip_block_comment(self):
        start_line = self.line
        start_col = self.column
        self.advance() # /
        self.advance() # *
        while self.pos < self.length:
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance() # *
                self.advance() # /
                return
            self.advance()
        raise LexicalError("Unterminated block comment /* ... */ in C++ source.", start_line, start_col)

    def lex_identifier(self, start_line: int, start_col: int) -> CPPToken:
        chars = []
        while self.pos < self.length and (self.peek().isalnum() or self.peek() in ('_', '$')):
            chars.append(self.advance())
        lexeme = "".join(chars)

        if lexeme in CPP_UNSUPPORTED_KEYWORDS:
            raise LexicalError(f"C++ keyword '{lexeme}' is not supported in this CodeFlow subset.", start_line, start_col)

        tok_type = CPP_KEYWORDS.get(lexeme, CPPTokenType.IDENTIFIER)
        return CPPToken(tok_type, lexeme, start_line, start_col)

    def lex_number(self, start_line: int, start_col: int) -> CPPToken:
        chars = []
        is_float = False
        while self.pos < self.length and self.peek().isdigit():
            chars.append(self.advance())

        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            chars.append(self.advance())
            while self.pos < self.length and self.peek().isdigit():
                chars.append(self.advance())

        lexeme = "".join(chars)
        tok_type = CPPTokenType.FLOAT_LITERAL if is_float else CPPTokenType.INTEGER_LITERAL
        return CPPToken(tok_type, lexeme, start_line, start_col)

    def lex_operator_or_delimiter(self, start_line: int, start_col: int) -> CPPToken:
        c = self.advance()

        if c == '=':
            if self.peek() == '=':
                self.advance()
                return CPPToken(CPPTokenType.EQUAL_EQUAL, "==", start_line, start_col)
            return CPPToken(CPPTokenType.ASSIGN, "=", start_line, start_col)

        elif c == '!':
            if self.peek() == '=':
                self.advance()
                return CPPToken(CPPTokenType.NOT_EQUAL, "!=", start_line, start_col)
            return CPPToken(CPPTokenType.NOT, "!", start_line, start_col)

        elif c == '<':
            if self.peek() == '<':
                self.advance()
                return CPPToken(CPPTokenType.STREAM_OUT, "<<", start_line, start_col)
            elif self.peek() == '=':
                self.advance()
                return CPPToken(CPPTokenType.LESS_EQUAL, "<=", start_line, start_col)
            return CPPToken(CPPTokenType.LESS, "<", start_line, start_col)

        elif c == '>':
            if self.peek() == '=':
                self.advance()
                return CPPToken(CPPTokenType.GREATER_EQUAL, ">=", start_line, start_col)
            return CPPToken(CPPTokenType.GREATER, ">", start_line, start_col)

        elif c == '&':
            if self.peek() == '&':
                self.advance()
                return CPPToken(CPPTokenType.AND, "&&", start_line, start_col)
            raise LexicalError("Bitwise/address-of '&' is not supported in this C++ subset. Use '&&'.", start_line, start_col)

        elif c == '|':
            if self.peek() == '|':
                self.advance()
                return CPPToken(CPPTokenType.OR, "||", start_line, start_col)
            raise LexicalError("Bitwise '|' is not supported in this C++ subset. Use '||'.", start_line, start_col)

        elif c == '+': return CPPToken(CPPTokenType.PLUS, "+", start_line, start_col)
        elif c == '-': return CPPToken(CPPTokenType.MINUS, "-", start_line, start_col)
        elif c == '*': return CPPToken(CPPTokenType.STAR, "*", start_line, start_col)
        elif c == '/': return CPPToken(CPPTokenType.SLASH, "/", start_line, start_col)
        elif c == '%': return CPPToken(CPPTokenType.MOD, "%", start_line, start_col)
        elif c == '(': return CPPToken(CPPTokenType.LPAREN, "(", start_line, start_col)
        elif c == ')': return CPPToken(CPPTokenType.RPAREN, ")", start_line, start_col)
        elif c == '{': return CPPToken(CPPTokenType.LBRACE, "{", start_line, start_col)
        elif c == '}': return CPPToken(CPPTokenType.RBRACE, "}", start_line, start_col)
        elif c == ';': return CPPToken(CPPTokenType.SEMICOLON, ";", start_line, start_col)

        elif c in ('"', "'"):
            raise LexicalError("String literals are not supported in this CodeFlow C++ subset.", start_line, start_col)
        elif c in ('[', ']'):
            raise LexicalError("Arrays and pointer indexing are not supported in this CodeFlow C++ subset.", start_line, start_col)

        else:
            raise LexicalError(f"Unrecognized or unsupported character: '{c}'", start_line, start_col)
