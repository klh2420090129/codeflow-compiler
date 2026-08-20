import sys
import os
from typing import List, Optional

# Add parent dir to path if running directly for testing
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.lexer.lexer import Token, TokenType, Lexer
from compiler.errors import ParserError, LexicalError
from compiler.ast import nodes

class Parser:
    """Recursive descent parser for MiniLang."""
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> nodes.Program:
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return nodes.Program(statements)

    # --- Helper Methods ---

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParserError(f"{message} Found '{token.lexeme}'.", token.line, token.column)

    # --- Statement Parsing ---

    def parse_statement(self) -> nodes.ASTNode:
        if self.match(TokenType.LET):
            return self.parse_variable_declaration()
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        if self.match(TokenType.LBRACE):
            return self.parse_block()
        
        return self.parse_assignment()

    def parse_variable_declaration(self) -> nodes.VariableDeclaration:
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name.")
        initializer = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return nodes.VariableDeclaration(nodes.Identifier(name_token.lexeme), initializer)

    def parse_assignment(self) -> nodes.Assignment:
        # MiniLang doesn't allow expression statements except assignments
        name_token = self.consume(TokenType.IDENTIFIER, "Expected statement start.")
        self.consume(TokenType.ASSIGN, "Expected '=' after identifier for assignment.")
        value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after assignment.")
        return nodes.Assignment(nodes.Identifier(name_token.lexeme), value)

    def parse_if_statement(self) -> nodes.IfStatement:
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after if condition.")
        
        self.consume(TokenType.LBRACE, "Expected '{' before if block.")
        then_block = self.parse_block()
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.LBRACE, "Expected '{' before else block.")
            else_block = self.parse_block()
            
        return nodes.IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> nodes.WhileStatement:
        self.consume(TokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after while condition.")
        
        self.consume(TokenType.LBRACE, "Expected '{' before while block.")
        body = self.parse_block()
        
        return nodes.WhileStatement(condition, body)

    def parse_print_statement(self) -> nodes.PrintStatement:
        self.consume(TokenType.LPAREN, "Expected '(' after 'print'.")
        expr = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after print expression.")
        self.consume(TokenType.SEMICOLON, "Expected ';' after print statement.")
        return nodes.PrintStatement(expr)

    def parse_block(self) -> nodes.Block:
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_statement())
        self.consume(TokenType.RBRACE, "Expected '}' after block.")
        return nodes.Block(statements)

    # --- Expression Parsing (Precedence) ---

    def parse_expression(self) -> nodes.ASTNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> nodes.ASTNode:
        expr = self.parse_logical_and()
        while self.match(TokenType.OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_logical_and(self) -> nodes.ASTNode:
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_equality(self) -> nodes.ASTNode:
        expr = self.parse_relational()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_relational(self) -> nodes.ASTNode:
        expr = self.parse_additive()
        while self.match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_additive(self) -> nodes.ASTNode:
        expr = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_multiplicative(self) -> nodes.ASTNode:
        expr = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.MOD):
            op = self.previous().lexeme
            right = self.parse_unary()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_unary(self) -> nodes.ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_unary()
            return nodes.UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> nodes.ASTNode:
        if self.match(TokenType.FALSE):
            return nodes.Literal(False, "BOOLEAN")
        if self.match(TokenType.TRUE):
            return nodes.Literal(True, "BOOLEAN")
        if self.match(TokenType.INTEGER):
            return nodes.Literal(int(self.previous().lexeme), "INTEGER")
        if self.match(TokenType.FLOAT):
            return nodes.Literal(float(self.previous().lexeme), "FLOAT")
        if self.match(TokenType.IDENTIFIER):
            return nodes.Identifier(self.previous().lexeme)
        
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expr

        token = self.peek()
        raise ParserError("Expected expression.", token.line, token.column)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.parser.parser <source_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
            
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        print("========== AST ==========\n")
        print(ast)
            
    except (LexicalError, ParserError) as e:
        print(e)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
