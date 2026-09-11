import sys
import os
from typing import List, Optional, Set, Dict

from compiler.frontends.javascript.lexer import JSToken, JSTokenType
from compiler.errors import ParserError, SemanticError
from compiler.ast import nodes

class JSParser:
    """
    Recursive-descent parser for the supported JavaScript subset.
    Translates JS AST directly into unified CodeFlow AST nodes.
    
    Operator Precedence (lowest to highest):
    - Assignment (=) (at statement level)
    - Logical OR (||)
    - Logical AND (&&)
    - Equality (==, !=)
    - Relational (<, <=, >, >=)
    - Additive (+, -)
    - Multiplicative (*, /, %)
    - Unary (!, -)
    - Primary (literals, identifiers, parentheses)
    """

    def __init__(self, tokens: List[JSToken]):
        self.tokens = tokens
        self.current = 0
        # Track const variables: name -> declaration token
        self.const_variables: Dict[str, JSToken] = {}
        # Track all declared variables at frontend scope level
        self.declared_variables: Set[str] = set()

    def parse(self) -> nodes.Program:
        statements: List[nodes.ASTNode] = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return nodes.Program(statements)

    # --- Helper methods ---

    def peek(self) -> JSToken:
        return self.tokens[self.current]

    def previous(self) -> JSToken:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == JSTokenType.EOF

    def check(self, token_type: JSTokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> JSToken:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: JSTokenType) -> bool:
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: JSTokenType, message: str) -> JSToken:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParserError(f"{message} Found '{token.lexeme}'.", token.line, token.column)

    # --- Statement Parsing ---

    def parse_statement(self) -> nodes.ASTNode:
        if self.match(JSTokenType.LET, JSTokenType.CONST, JSTokenType.VAR):
            return self.parse_variable_declaration(self.previous())
        if self.match(JSTokenType.IF):
            return self.parse_if_statement()
        if self.match(JSTokenType.WHILE):
            return self.parse_while_statement()
        if self.match(JSTokenType.CONSOLE_LOG):
            return self.parse_console_log()
        if self.match(JSTokenType.LBRACE):
            return self.parse_block()

        # Check for empty statements (stray semicolons)
        if self.match(JSTokenType.SEMICOLON):
            return self.parse_statement()

        return self.parse_assignment_or_expression_statement()

    def parse_variable_declaration(self, kind_token: JSToken) -> nodes.VariableDeclaration:
        name_token = self.consume(JSTokenType.IDENTIFIER, "Expected variable name after declaration keyword.")
        var_name = name_token.lexeme

        # In const declarations, initializer is strictly required
        if kind_token.type == JSTokenType.CONST:
            if not self.check(JSTokenType.ASSIGN):
                raise ParserError(f"Missing initializer in const declaration '{var_name}'.", name_token.line, name_token.column)

        self.consume(JSTokenType.ASSIGN, f"Expected '=' initializer for variable '{var_name}'.")
        initializer = self.parse_expression()
        self.consume(JSTokenType.SEMICOLON, "Expected ';' after variable declaration.")

        if kind_token.type == JSTokenType.CONST:
            self.const_variables[var_name] = name_token

        self.declared_variables.add(var_name)
        return nodes.VariableDeclaration(nodes.Identifier(var_name), initializer)

    def parse_assignment_or_expression_statement(self) -> nodes.Assignment:
        if self.check(JSTokenType.IDENTIFIER):
            name_token = self.advance()
            var_name = name_token.lexeme

            # Check if attempting to reassign a const variable
            if self.check(JSTokenType.ASSIGN):
                if var_name in self.const_variables:
                    raise SemanticError(
                        f"TypeError: Assignment to constant variable '{var_name}'.",
                        name_token.line,
                        name_token.column
                    )

                self.advance() # consume '='
                value = self.parse_expression()
                self.consume(JSTokenType.SEMICOLON, "Expected ';' after assignment.")
                return nodes.Assignment(nodes.Identifier(var_name), value)
            else:
                token = self.peek()
                raise ParserError(
                    f"Expressions without assignment or function call are not supported statements in this CodeFlow JavaScript subset. Found '{token.lexeme}'.",
                    token.line,
                    token.column
                )

        token = self.peek()
        raise ParserError(f"Expected statement start, found '{token.lexeme}'.", token.line, token.column)

    def parse_console_log(self) -> nodes.PrintStatement:
        # We already consumed 'console.log' token
        self.consume(JSTokenType.LPAREN, "Expected '(' after 'console.log'.")
        expr = self.parse_expression()
        self.consume(JSTokenType.RPAREN, "Expected ')' after console.log expression.")
        self.consume(JSTokenType.SEMICOLON, "Expected ';' after console.log statement.")
        return nodes.PrintStatement(expr)

    def parse_if_statement(self) -> nodes.IfStatement:
        self.consume(JSTokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(JSTokenType.RPAREN, "Expected ')' after if condition.")

        # Require block { ... } for if statement
        self.consume(JSTokenType.LBRACE, "Expected '{' before if body.")
        then_block = self.parse_block()

        else_block = None
        if self.match(JSTokenType.ELSE):
            if self.match(JSTokenType.IF):
                # else if -> wrap in block or parse as nested if
                nested_if = self.parse_if_statement()
                else_block = nodes.Block([nested_if])
            else:
                self.consume(JSTokenType.LBRACE, "Expected '{' before else body.")
                else_block = self.parse_block()

        return nodes.IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> nodes.WhileStatement:
        self.consume(JSTokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(JSTokenType.RPAREN, "Expected ')' after while condition.")

        self.consume(JSTokenType.LBRACE, "Expected '{' before while body.")
        body = self.parse_block()

        return nodes.WhileStatement(condition, body)

    def parse_block(self) -> nodes.Block:
        statements: List[nodes.ASTNode] = []
        while not self.check(JSTokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        self.consume(JSTokenType.RBRACE, "Expected '}' to close block.")
        return nodes.Block(statements)

    # --- Expression Parsing with Precedence ---

    def parse_expression(self) -> nodes.ASTNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> nodes.ASTNode:
        expr = self.parse_logical_and()
        while self.match(JSTokenType.OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_logical_and(self) -> nodes.ASTNode:
        expr = self.parse_equality()
        while self.match(JSTokenType.AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_equality(self) -> nodes.ASTNode:
        expr = self.parse_relational()
        while self.match(JSTokenType.EQUAL_EQUAL, JSTokenType.NOT_EQUAL):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_relational(self) -> nodes.ASTNode:
        expr = self.parse_additive()
        while self.match(JSTokenType.LESS, JSTokenType.LESS_EQUAL, JSTokenType.GREATER, JSTokenType.GREATER_EQUAL):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_additive(self) -> nodes.ASTNode:
        expr = self.parse_multiplicative()
        while self.match(JSTokenType.PLUS, JSTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_multiplicative(self) -> nodes.ASTNode:
        expr = self.parse_unary()
        while self.match(JSTokenType.STAR, JSTokenType.SLASH, JSTokenType.MOD):
            op = self.previous().lexeme
            right = self.parse_unary()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_unary(self) -> nodes.ASTNode:
        if self.match(JSTokenType.NOT, JSTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_unary()
            return nodes.UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> nodes.ASTNode:
        if self.match(JSTokenType.TRUE):
            return nodes.Literal(True, "BOOLEAN")
        if self.match(JSTokenType.FALSE):
            return nodes.Literal(False, "BOOLEAN")
        if self.match(JSTokenType.INTEGER_LITERAL):
            return nodes.Literal(int(self.previous().lexeme), "INTEGER")
        if self.match(JSTokenType.FLOAT_LITERAL):
            return nodes.Literal(float(self.previous().lexeme), "FLOAT")
        if self.match(JSTokenType.IDENTIFIER):
            return nodes.Identifier(self.previous().lexeme)

        if self.match(JSTokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(JSTokenType.RPAREN, "Expected ')' after expression.")
            return expr

        token = self.peek()
        raise ParserError(f"Expected expression, found '{token.lexeme}'.", token.line, token.column)
