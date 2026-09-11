from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
from compiler.errors import LexicalError

class JSTokenType(Enum):
    # Keywords
    LET = "LET"
    CONST = "CONST"
    VAR = "VAR"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    TRUE = "TRUE"
    FALSE = "FALSE"
    
    # Special console.log
    CONSOLE_LOG = "CONSOLE_LOG"
    
    # Identifiers & Literals
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
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    
    EOF = "EOF"

@dataclass
class JSToken:
    type: JSTokenType
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

JS_KEYWORDS = {
    "let": JSTokenType.LET,
    "const": JSTokenType.CONST,
    "var": JSTokenType.VAR,
    "if": JSTokenType.IF,
    "else": JSTokenType.ELSE,
    "while": JSTokenType.WHILE,
    "true": JSTokenType.TRUE,
    "false": JSTokenType.FALSE,
}

JS_UNSUPPORTED_KEYWORDS = {
    "function", "class", "return", "import", "export", "default", "from",
    "async", "await", "yield", "try", "catch", "finally", "throw", "new",
    "switch", "case", "break", "continue", "for", "do", "typeof", "instanceof",
    "in", "of", "delete", "void", "this", "super", "debugger", "with"
}

class JSLexer:
    """Lexer for supported JavaScript subset."""
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

    def tokenize(self) -> List[JSToken]:
        tokens: List[JSToken] = []
        while self.pos < self.length:
            c = self.peek()

            if c.isspace():
                self.advance()
                continue

            # Single-line comment //
            if c == '/' and self.peek(1) == '/':
                self.skip_line_comment()
                continue

            # Multi-line comment /* ... */
            if c == '/' and self.peek(1) == '*':
                self.skip_block_comment()
                continue

            start_line = self.line
            start_col = self.column

            # Check for console.log
            if self.source.startswith("console.log", self.pos):
                # Verify that it is a distinct token boundary
                next_pos = self.pos + len("console.log")
                if next_pos >= self.length or not (self.source[next_pos].isalnum() or self.source[next_pos] == '_'):
                    for _ in range(len("console.log")):
                        self.advance()
                    tokens.append(JSToken(JSTokenType.CONSOLE_LOG, "console.log", start_line, start_col))
                    continue

            # Identifiers and keywords
            if c.isalpha() or c in ('_', '$'):
                tokens.append(self.lex_identifier(start_line, start_col))
            elif c.isdigit():
                tokens.append(self.lex_number(start_line, start_col))
            else:
                tokens.append(self.lex_operator_or_delimiter(start_line, start_col))

        tokens.append(JSToken(type=JSTokenType.EOF, lexeme="<EOF>", line=self.line, column=self.column))
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
        raise LexicalError("Unterminated block comment /* ... */ in JavaScript source.", start_line, start_col)

    def lex_identifier(self, start_line: int, start_col: int) -> JSToken:
        chars = []
        while self.pos < self.length and (self.peek().isalnum() or self.peek() in ('_', '$')):
            chars.append(self.advance())
        lexeme = "".join(chars)

        if lexeme in JS_UNSUPPORTED_KEYWORDS:
            raise LexicalError(f"JavaScript keyword '{lexeme}' is not supported in this CodeFlow subset.", start_line, start_col)

        tok_type = JS_KEYWORDS.get(lexeme, JSTokenType.IDENTIFIER)
        return JSToken(tok_type, lexeme, start_line, start_col)

    def lex_number(self, start_line: int, start_col: int) -> JSToken:
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
        tok_type = JSTokenType.FLOAT_LITERAL if is_float else JSTokenType.INTEGER_LITERAL
        return JSToken(tok_type, lexeme, start_line, start_col)

    def lex_operator_or_delimiter(self, start_line: int, start_col: int) -> JSToken:
        c = self.advance()

        # Check for strict equality === or !==
        if c == '=':
            if self.peek() == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    raise LexicalError("Strict equality '===' is not supported in this subset. Use '=='.", start_line, start_col)
                return JSToken(JSTokenType.EQUAL_EQUAL, "==", start_line, start_col)
            elif self.peek() == '>':
                # Arrow function =>
                self.advance()
                raise LexicalError("Arrow functions '=>' are not supported in this CodeFlow JavaScript subset.", start_line, start_col)
            return JSToken(JSTokenType.ASSIGN, "=", start_line, start_col)

        elif c == '!':
            if self.peek() == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    raise LexicalError("Strict inequality '!==' is not supported in this subset. Use '!='.", start_line, start_col)
                return JSToken(JSTokenType.NOT_EQUAL, "!=", start_line, start_col)
            return JSToken(JSTokenType.NOT, "!", start_line, start_col)

        elif c == '<':
            if self.peek() == '=':
                self.advance()
                return JSToken(JSTokenType.LESS_EQUAL, "<=", start_line, start_col)
            return JSToken(JSTokenType.LESS, "<", start_line, start_col)

        elif c == '>':
            if self.peek() == '=':
                self.advance()
                return JSToken(JSTokenType.GREATER_EQUAL, ">=", start_line, start_col)
            return JSToken(JSTokenType.GREATER, ">", start_line, start_col)

        elif c == '&':
            if self.peek() == '&':
                self.advance()
                return JSToken(JSTokenType.AND, "&&", start_line, start_col)
            raise LexicalError("Bitwise '&' is not supported in this subset. Use '&&'.", start_line, start_col)

        elif c == '|':
            if self.peek() == '|':
                self.advance()
                return JSToken(JSTokenType.OR, "||", start_line, start_col)
            raise LexicalError("Bitwise '|' is not supported in this subset. Use '||'.", start_line, start_col)

        elif c == '+': return JSToken(JSTokenType.PLUS, "+", start_line, start_col)
        elif c == '-': return JSToken(JSTokenType.MINUS, "-", start_line, start_col)
        elif c == '*': return JSToken(JSTokenType.STAR, "*", start_line, start_col)
        elif c == '/': return JSToken(JSTokenType.SLASH, "/", start_line, start_col)
        elif c == '%': return JSToken(JSTokenType.MOD, "%", start_line, start_col)
        elif c == '(': return JSToken(JSTokenType.LPAREN, "(", start_line, start_col)
        elif c == ')': return JSToken(JSTokenType.RPAREN, ")", start_line, start_col)
        elif c == '{': return JSToken(JSTokenType.LBRACE, "{", start_line, start_col)
        elif c == '}': return JSToken(JSTokenType.RBRACE, "}", start_line, start_col)
        elif c == ';': return JSToken(JSTokenType.SEMICOLON, ";", start_line, start_col)
        elif c == '.': return JSToken(JSTokenType.DOT, ".", start_line, start_col)

        elif c in ('"', "'", '`'):
            raise LexicalError("Strings and template literals are not supported in this CodeFlow JavaScript subset.", start_line, start_col)
        elif c in ('[', ']'):
            raise LexicalError("Array literals and indexing are not supported in this CodeFlow JavaScript subset.", start_line, start_col)

        else:
            raise LexicalError(f"Unrecognized or unsupported character: '{c}'", start_line, start_col)
