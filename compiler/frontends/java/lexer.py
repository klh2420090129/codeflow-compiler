from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
from compiler.errors import LexicalError

class JavaTokenType(Enum):
    # Keywords
    PUBLIC = "PUBLIC"
    CLASS = "CLASS"
    STATIC = "STATIC"
    VOID = "VOID"
    MAIN = "MAIN"
    STRING = "STRING"
    INT = "INT"
    DOUBLE = "DOUBLE"
    BOOLEAN = "BOOLEAN"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    TRUE = "TRUE"
    FALSE = "FALSE"
    FINAL = "FINAL"
    
    # Special System.out.println
    SYSTEM_OUT_PRINTLN = "SYSTEM_OUT_PRINTLN"
    
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
    
    # Delimiters & Punctuation
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    
    EOF = "EOF"

@dataclass
class JavaToken:
    type: JavaTokenType
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

JAVA_KEYWORDS = {
    "public": JavaTokenType.PUBLIC,
    "class": JavaTokenType.CLASS,
    "static": JavaTokenType.STATIC,
    "void": JavaTokenType.VOID,
    "main": JavaTokenType.MAIN,
    "String": JavaTokenType.STRING,
    "int": JavaTokenType.INT,
    "double": JavaTokenType.DOUBLE,
    "boolean": JavaTokenType.BOOLEAN,
    "if": JavaTokenType.IF,
    "else": JavaTokenType.ELSE,
    "while": JavaTokenType.WHILE,
    "true": JavaTokenType.TRUE,
    "false": JavaTokenType.FALSE,
    "final": JavaTokenType.FINAL,
}

JAVA_UNSUPPORTED_KEYWORDS = {
    "abstract", "assert", "break", "byte", "case", "catch", "char", "const",
    "continue", "default", "do", "enum", "extends", "finally", "float", "for",
    "goto", "implements", "import", "instanceof", "interface", "long", "native",
    "new", "package", "private", "protected", "return", "short", "strictfp",
    "super", "switch", "synchronized", "this", "throw", "throws", "transient",
    "try", "volatile"
}

class JavaLexer:
    """Lexer for supported Java subset."""
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

    def tokenize(self) -> List[JavaToken]:
        tokens: List[JavaToken] = []
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

            # Check for System.out.println
            if self.source.startswith("System.out.println", self.pos):
                next_pos = self.pos + len("System.out.println")
                if next_pos >= self.length or not (self.source[next_pos].isalnum() or self.source[next_pos] == '_'):
                    for _ in range(len("System.out.println")):
                        self.advance()
                    tokens.append(JavaToken(JavaTokenType.SYSTEM_OUT_PRINTLN, "System.out.println", start_line, start_col))
                    continue

            # Identifiers and keywords
            if c.isalpha() or c in ('_', '$'):
                tokens.append(self.lex_identifier(start_line, start_col))
            elif c.isdigit():
                tokens.append(self.lex_number(start_line, start_col))
            else:
                tokens.append(self.lex_operator_or_delimiter(start_line, start_col))

        tokens.append(JavaToken(type=JavaTokenType.EOF, lexeme="<EOF>", line=self.line, column=self.column))
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
        raise LexicalError("Unterminated block comment /* ... */ in Java source.", start_line, start_col)

    def lex_identifier(self, start_line: int, start_col: int) -> JavaToken:
        chars = []
        while self.pos < self.length and (self.peek().isalnum() or self.peek() in ('_', '$')):
            chars.append(self.advance())
        lexeme = "".join(chars)

        if lexeme in JAVA_UNSUPPORTED_KEYWORDS:
            raise LexicalError(f"Java keyword '{lexeme}' is not supported in this CodeFlow subset.", start_line, start_col)

        tok_type = JAVA_KEYWORDS.get(lexeme, JavaTokenType.IDENTIFIER)
        return JavaToken(tok_type, lexeme, start_line, start_col)

    def lex_number(self, start_line: int, start_col: int) -> JavaToken:
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
        tok_type = JavaTokenType.FLOAT_LITERAL if is_float else JavaTokenType.INTEGER_LITERAL
        return JavaToken(tok_type, lexeme, start_line, start_col)

    def lex_operator_or_delimiter(self, start_line: int, start_col: int) -> JavaToken:
        c = self.advance()

        if c == '=':
            if self.peek() == '=':
                self.advance()
                return JavaToken(JavaTokenType.EQUAL_EQUAL, "==", start_line, start_col)
            return JavaToken(JavaTokenType.ASSIGN, "=", start_line, start_col)

        elif c == '!':
            if self.peek() == '=':
                self.advance()
                return JavaToken(JavaTokenType.NOT_EQUAL, "!=", start_line, start_col)
            return JavaToken(JavaTokenType.NOT, "!", start_line, start_col)

        elif c == '<':
            if self.peek() == '=':
                self.advance()
                return JavaToken(JavaTokenType.LESS_EQUAL, "<=", start_line, start_col)
            return JavaToken(JavaTokenType.LESS, "<", start_line, start_col)

        elif c == '>':
            if self.peek() == '=':
                self.advance()
                return JavaToken(JavaTokenType.GREATER_EQUAL, ">=", start_line, start_col)
            return JavaToken(JavaTokenType.GREATER, ">", start_line, start_col)

        elif c == '&':
            if self.peek() == '&':
                self.advance()
                return JavaToken(JavaTokenType.AND, "&&", start_line, start_col)
            raise LexicalError("Bitwise '&' is not supported in this Java subset. Use '&&'.", start_line, start_col)

        elif c == '|':
            if self.peek() == '|':
                self.advance()
                return JavaToken(JavaTokenType.OR, "||", start_line, start_col)
            raise LexicalError("Bitwise '|' is not supported in this Java subset. Use '||'.", start_line, start_col)

        elif c == '+': return JavaToken(JavaTokenType.PLUS, "+", start_line, start_col)
        elif c == '-': return JavaToken(JavaTokenType.MINUS, "-", start_line, start_col)
        elif c == '*': return JavaToken(JavaTokenType.STAR, "*", start_line, start_col)
        elif c == '/': return JavaToken(JavaTokenType.SLASH, "/", start_line, start_col)
        elif c == '%': return JavaToken(JavaTokenType.MOD, "%", start_line, start_col)
        elif c == '(': return JavaToken(JavaTokenType.LPAREN, "(", start_line, start_col)
        elif c == ')': return JavaToken(JavaTokenType.RPAREN, ")", start_line, start_col)
        elif c == '{': return JavaToken(JavaTokenType.LBRACE, "{", start_line, start_col)
        elif c == '}': return JavaToken(JavaTokenType.RBRACE, "}", start_line, start_col)
        elif c == '[': return JavaToken(JavaTokenType.LBRACKET, "[", start_line, start_col)
        elif c == ']': return JavaToken(JavaTokenType.RBRACKET, "]", start_line, start_col)
        elif c == ';': return JavaToken(JavaTokenType.SEMICOLON, ";", start_line, start_col)
        elif c == '.': return JavaToken(JavaTokenType.DOT, ".", start_line, start_col)

        elif c in ('"', "'"):
            raise LexicalError("String and character literals are not supported in this CodeFlow Java subset.", start_line, start_col)

        else:
            raise LexicalError(f"Unrecognized or unsupported character: '{c}'", start_line, start_col)
