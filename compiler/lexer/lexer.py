import sys
from enum import Enum
from dataclasses import dataclass
from typing import List
import os

# Add parent dir to path if running directly for testing
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.errors import LexicalError

class TokenType(Enum):
    # Keywords
    LET = "LET"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    PRINT = "PRINT"
    TRUE = "TRUE"
    FALSE = "FALSE"
    
    # Literals & Identifiers
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    
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
    
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __str__(self):
        return f"{self.type.name:<15} '{self.lexeme:<5}'   line={self.line:<3} column={self.column:<3}"

KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE
}

class Lexer:
    """Lexical analyzer for MiniLang."""
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < self.length:
            c = self.peek()
            
            if c.isspace():
                self.skip_whitespace()
                continue
                
            # Note on comments: Comments are not currently defined in grammar.md.
            # Decision: Do not implement comments to avoid inventing undocumented features.
            
            if c.isalpha() or c == '_':
                tokens.append(self.lex_identifier_or_keyword())
            elif c.isdigit():
                tokens.append(self.lex_number())
            else:
                tokens.append(self.lex_operator_or_delimiter())
                
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def advance(self) -> str:
        """Consumes the current character and advances the position."""
        if self.pos >= self.length:
            return ""
        c = self.source[self.pos]
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def peek(self, offset=0) -> str:
        """Looks at the current or upcoming character without consuming it."""
        if self.pos + offset >= self.length:
            return ""
        return self.source[self.pos + offset]

    def match(self, expected: str) -> bool:
        """Consumes the next character if it matches expected."""
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def skip_whitespace(self):
        while self.pos < self.length and self.peek().isspace():
            self.advance()

    def lex_identifier_or_keyword(self) -> Token:
        start_col = self.column
        lexeme = ""
        while self.pos < self.length and (self.peek().isalnum() or self.peek() == '_'):
            lexeme += self.advance()
            
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, self.line, start_col)

    def lex_number(self) -> Token:
        start_col = self.column
        lexeme = ""
        is_float = False
        
        while self.pos < self.length and self.peek().isdigit():
            lexeme += self.advance()
            
        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            lexeme += self.advance() # consume '.'
            while self.pos < self.length and self.peek().isdigit():
                lexeme += self.advance()
                
        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        return Token(token_type, lexeme, self.line, start_col)

    def lex_operator_or_delimiter(self) -> Token:
        start_col = self.column
        c = self.advance()
        
        # Operators with potential multi-character matches (longest-match rule)
        if c == '=':
            if self.match('='): return Token(TokenType.EQUAL_EQUAL, "==", self.line, start_col)
            return Token(TokenType.ASSIGN, "=", self.line, start_col)
        elif c == '!':
            if self.match('='): return Token(TokenType.NOT_EQUAL, "!=", self.line, start_col)
            return Token(TokenType.NOT, "!", self.line, start_col)
        elif c == '<':
            if self.match('='): return Token(TokenType.LESS_EQUAL, "<=", self.line, start_col)
            return Token(TokenType.LESS, "<", self.line, start_col)
        elif c == '>':
            if self.match('='): return Token(TokenType.GREATER_EQUAL, ">=", self.line, start_col)
            return Token(TokenType.GREATER, ">", self.line, start_col)
        elif c == '&':
            if self.match('&'): return Token(TokenType.AND, "&&", self.line, start_col)
            raise LexicalError(f"Unexpected character '{c}', did you mean '&&'?", self.line, start_col)
        elif c == '|':
            if self.match('|'): return Token(TokenType.OR, "||", self.line, start_col)
            raise LexicalError(f"Unexpected character '{c}', did you mean '||'?", self.line, start_col)
            
        # Single character operators & delimiters
        single_chars = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.MOD,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON
        }
        
        if c in single_chars:
            return Token(single_chars[c], c, self.line, start_col)
            
        raise LexicalError(f"Unexpected character '{c}'", self.line, start_col)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.lexer.lexer <source_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
            
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        for token in tokens:
            print(token)
            
    except LexicalError as e:
        print(e)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
