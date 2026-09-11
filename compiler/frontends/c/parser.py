from typing import List, Optional, Set
from compiler.frontends.c.lexer import CToken, CTokenType
from compiler.ast import nodes
from compiler.errors import ParserError, SemanticError

class CParser:
    """
    Recursive-descent parser that parses supported C constructs and
    directly constructs standard CodeFlow AST nodes (nodes.Program, nodes.VariableDeclaration,
    nodes.Assignment, nodes.BinaryExpression, nodes.IfStatement, nodes.WhileStatement, nodes.PrintStatement).
    """

    def __init__(self, tokens: List[CToken]):
        self.tokens = tokens
        self.current = 0
        # Track declared variable types for strict C declaration checking:
        # e.g. 'x': 'int' or 'float'
        self.declared_variables: Set[str] = set()

    def parse(self) -> nodes.Program:
        statements: List[nodes.ASTNode] = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return nodes.Program(statements)

    # --- Token Stream Helpers ---

    def peek(self) -> CToken:
        return self.tokens[self.current]

    def previous(self) -> CToken:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == CTokenType.EOF

    def check(self, token_type: CTokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> CToken:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: CTokenType) -> bool:
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: CTokenType, message: str) -> CToken:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParserError(f"{message} Found '{token.lexeme}'.", token.line, token.column)

    # --- Grammar Rules ---

    def parse_statement(self) -> nodes.ASTNode:
        # Variable declaration: int x; or float y = 2.5;
        if self.check(CTokenType.INT) or self.check(CTokenType.FLOAT):
            return self.parse_variable_declaration()
        
        # If statement: if (...) { ... } [else { ... }]
        if self.match(CTokenType.IF):
            return self.parse_if_statement()

        # While statement: while (...) { ... }
        if self.match(CTokenType.WHILE):
            return self.parse_while_statement()

        # printf statement: printf("%d\n", expr);
        if self.match(CTokenType.PRINTF):
            return self.parse_printf_statement()

        # Block: { ... }
        if self.match(CTokenType.LBRACE):
            return self.parse_block()

        # Assignment statement: x = expr;
        if self.check(CTokenType.IDENTIFIER):
            return self.parse_assignment()

        tok = self.peek()
        raise ParserError(f"Unexpected token at statement start: '{tok.lexeme}'.", tok.line, tok.column)

    def parse_variable_declaration(self) -> nodes.VariableDeclaration:
        type_tok = self.advance() # 'int' or 'float'
        declared_type = type_tok.lexeme

        name_tok = self.consume(CTokenType.IDENTIFIER, "Expected variable name in declaration.")
        var_name = name_tok.lexeme

        initializer: nodes.ASTNode
        if self.match(CTokenType.ASSIGN):
            initializer = self.parse_expression()
        else:
            # Uninitialized in C: int x; -> provide default literal 0 or 0.0
            if declared_type == "int":
                initializer = nodes.Literal(0, "INTEGER")
            else:
                initializer = nodes.Literal(0.0, "FLOAT")

        self.consume(CTokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return nodes.VariableDeclaration(nodes.Identifier(var_name), initializer)

    def parse_assignment(self) -> nodes.Assignment:
        name_tok = self.consume(CTokenType.IDENTIFIER, "Expected variable name in assignment.")
        var_name = name_tok.lexeme

        self.consume(CTokenType.ASSIGN, "Expected '=' in assignment statement.")
        value_expr = self.parse_expression()
        self.consume(CTokenType.SEMICOLON, "Expected ';' after assignment statement.")

        return nodes.Assignment(nodes.Identifier(var_name), value_expr)

    def parse_if_statement(self) -> nodes.IfStatement:
        self.consume(CTokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(CTokenType.RPAREN, "Expected ')' after condition.")

        # Require { ... } block for clean CodeFlow AST and CFG generation
        self.consume(CTokenType.LBRACE, "Expected '{' to start then-block of 'if'.")
        then_block = self.parse_block()

        else_block: Optional[nodes.Block] = None
        if self.match(CTokenType.ELSE):
            self.consume(CTokenType.LBRACE, "Expected '{' to start else-block.")
            else_block = self.parse_block()

        return nodes.IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> nodes.WhileStatement:
        self.consume(CTokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(CTokenType.RPAREN, "Expected ')' after condition.")

        self.consume(CTokenType.LBRACE, "Expected '{' to start while loop body.")
        body_block = self.parse_block()

        return nodes.WhileStatement(condition, body_block)

    def parse_printf_statement(self) -> nodes.PrintStatement:
        start_tok = self.previous()
        self.consume(CTokenType.LPAREN, "Expected '(' after printf.")

        # First argument must be a format string literal: "%d\n", "%f\n", "%d", etc.
        fmt_tok = self.consume(CTokenType.STRING_LITERAL, "Expected format string literal as first argument to printf.")
        fmt_str = fmt_tok.lexeme

        # Validate that format string is a single supported specifier
        supported_formats = ["%d", "%d\\n", "%f", "%f\\n", "%i", "%i\\n"]
        if fmt_str not in supported_formats:
            raise ParserError(
                f"Unsupported printf format '{fmt_str}'. In this CodeFlow C subset, only '%d\\n', '%d', '%f\\n', and '%f' are supported.",
                fmt_tok.line, fmt_tok.column
            )

        self.consume(CTokenType.COMMA, "Expected ',' after printf format string.")
        arg_expr = self.parse_expression()
        self.consume(CTokenType.RPAREN, "Expected ')' after printf arguments.")
        self.consume(CTokenType.SEMICOLON, "Expected ';' after printf statement.")

        return nodes.PrintStatement(arg_expr)

    def parse_block(self) -> nodes.Block:
        statements: List[nodes.ASTNode] = []
        while not self.check(CTokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_statement())
        self.consume(CTokenType.RBRACE, "Expected '}' after block.")
        return nodes.Block(statements)

    # --- Expression Precedence Hierarchy ---
    # Logical OR  (||)
    # Logical AND (&&)
    # Equality    (==, !=)
    # Relational  (<, <=, >, >=)
    # Additive    (+, -)
    # Multiplicative (*, /, %)
    # Unary       (!, -)
    # Primary     (literals, identifiers, (expr))

    def parse_expression(self) -> nodes.ASTNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> nodes.ASTNode:
        expr = self.parse_logical_and()
        while self.match(CTokenType.OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_logical_and(self) -> nodes.ASTNode:
        expr = self.parse_equality()
        while self.match(CTokenType.AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_equality(self) -> nodes.ASTNode:
        expr = self.parse_relational()
        while self.match(CTokenType.EQUAL_EQUAL, CTokenType.NOT_EQUAL):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_relational(self) -> nodes.ASTNode:
        expr = self.parse_additive()
        while self.match(CTokenType.LESS, CTokenType.LESS_EQUAL, CTokenType.GREATER, CTokenType.GREATER_EQUAL):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_additive(self) -> nodes.ASTNode:
        expr = self.parse_multiplicative()
        while self.match(CTokenType.PLUS, CTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_multiplicative(self) -> nodes.ASTNode:
        expr = self.parse_unary()
        while self.match(CTokenType.STAR, CTokenType.SLASH, CTokenType.MOD):
            op = self.previous().lexeme
            right = self.parse_unary()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_unary(self) -> nodes.ASTNode:
        if self.match(CTokenType.NOT, CTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_unary()
            return nodes.UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> nodes.ASTNode:
        if self.match(CTokenType.INTEGER_LITERAL):
            return nodes.Literal(int(self.previous().lexeme), "INTEGER")
        if self.match(CTokenType.FLOAT_LITERAL):
            return nodes.Literal(float(self.previous().lexeme), "FLOAT")
        if self.match(CTokenType.IDENTIFIER):
            return nodes.Identifier(self.previous().lexeme)

        if self.match(CTokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(CTokenType.RPAREN, "Expected ')' after grouped expression.")
            return expr

        tok = self.peek()
        raise ParserError(f"Expected expression, found '{tok.lexeme}'.", tok.line, tok.column)
