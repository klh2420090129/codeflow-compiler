import sys
import os
from typing import List, Optional, Set, Dict, Tuple

from compiler.frontends.cpp.lexer import CPPToken, CPPTokenType
from compiler.errors import ParserError, SemanticError
from compiler.ast import nodes

class CPPParser:
    """
    Structured recursive-descent parser for the supported C++ subset.
    Translates C++ AST directly into unified CodeFlow AST nodes.

    Recognizes canonical entry point:
        int main() {
            ...
        }
    Also supports top-level statements directly for shorthand convenience.
    """

    def __init__(self, tokens: List[CPPToken]):
        self.tokens = tokens
        self.current = 0
        # Symbol tracking at the frontend level: name -> (norm_type, decl_token)
        self.declared_symbols: Dict[str, Tuple[str, CPPToken]] = {}

    def parse(self) -> nodes.Program:
        # Check if program uses canonical int main() wrapper
        if self.check(CPPTokenType.INT) and self.peek(1).type == CPPTokenType.MAIN:
            statements = self.parse_main_wrapper()
        else:
            statements = self.parse_statement_list()

        return nodes.Program(statements)

    # --- Wrapper Parsing ---

    def parse_main_wrapper(self) -> List[nodes.ASTNode]:
        self.consume(CPPTokenType.INT, "Expected 'int' return type for main().")
        main_tok = self.consume(CPPTokenType.MAIN, "Expected 'main' function identifier.")
        self.consume(CPPTokenType.LPAREN, "Expected '(' after 'main'.")
        # Handle optional void or empty inside main()
        if self.check(CPPTokenType.RPAREN):
            self.advance()
        else:
            tok = self.peek()
            raise ParserError(f"Parameters in main() are not supported in this C++ subset. Found '{tok.lexeme}'.", tok.line, tok.column)

        self.consume(CPPTokenType.LBRACE, "Expected '{' before main body.")
        statements: List[nodes.ASTNode] = []
        while not self.check(CPPTokenType.RBRACE) and not self.is_at_end():
            # Handle return 0; optionally at end of main
            if self.check(CPPTokenType.RETURN):
                self.advance()
                if not self.check(CPPTokenType.SEMICOLON):
                    self.parse_expression() # consume return value expr
                self.consume(CPPTokenType.SEMICOLON, "Expected ';' after return statement.")
                continue

            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        self.consume(CPPTokenType.RBRACE, "Expected '}' after main function body.")

        # Check if there are any additional functions or definitions
        if not self.is_at_end():
            tok = self.peek()
            raise ParserError(f"Additional functions or code outside main() are not supported. Found '{tok.lexeme}'.", tok.line, tok.column)

        return statements

    def parse_statement_list(self) -> List[nodes.ASTNode]:
        statements: List[nodes.ASTNode] = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    # --- Helper methods ---

    def peek(self, offset: int = 0) -> CPPToken:
        idx = self.current + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def previous(self) -> CPPToken:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == CPPTokenType.EOF

    def check(self, token_type: CPPTokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> CPPToken:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: CPPTokenType) -> bool:
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: CPPTokenType, message: str) -> CPPToken:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParserError(f"{message} Found '{token.lexeme}'.", token.line, token.column)

    # --- Statement Parsing ---

    def parse_statement(self) -> nodes.ASTNode:
        # Check for primitive declarations: int, double, bool
        if self.match(CPPTokenType.INT, CPPTokenType.DOUBLE, CPPTokenType.BOOL):
            # Check if this is an illegal additional function definition e.g. int foo()
            if self.check(CPPTokenType.IDENTIFIER) and self.peek(1).type == CPPTokenType.LPAREN:
                func_tok = self.advance()
                raise ParserError(f"User-defined functions are not supported in this C++ subset: found '{func_tok.lexeme}()'. Only 'int main()' is allowed.", func_tok.line, func_tok.column)
            return self.parse_variable_declaration()

        if self.match(CPPTokenType.IF):
            return self.parse_if_statement()
        if self.match(CPPTokenType.WHILE):
            return self.parse_while_statement()
        if self.match(CPPTokenType.STD_COUT):
            return self.parse_cout_statement()
        if self.match(CPPTokenType.LBRACE):
            return self.parse_block()

        # Empty statements (stray semicolons)
        if self.match(CPPTokenType.SEMICOLON):
            return self.parse_statement()

        return self.parse_assignment()

    def parse_variable_declaration(self) -> nodes.VariableDeclaration:
        type_token = self.previous()
        type_name = type_token.lexeme # 'int', 'double', or 'bool'
        norm_type = "float" if type_name == "double" else ("bool" if type_name == "bool" else "int")

        name_token = self.consume(CPPTokenType.IDENTIFIER, "Expected variable name in declaration.")
        var_name = name_token.lexeme

        # Check duplicate declaration in same scope
        if var_name in self.declared_symbols:
            raise SemanticError(f"Variable '{var_name}' is already declared.", name_token.line, name_token.column)

        initializer: Optional[nodes.ASTNode] = None
        if self.match(CPPTokenType.ASSIGN):
            initializer = self.parse_expression()
            self.consume(CPPTokenType.SEMICOLON, "Expected ';' after variable declaration.")
        else:
            self.consume(CPPTokenType.SEMICOLON, "Expected ';' after variable declaration.")
            # Default initialization in C++ subset: int -> 0, double -> 0.0, bool -> false
            if norm_type == "int":
                initializer = nodes.Literal(0, "INTEGER")
            elif norm_type == "float":
                initializer = nodes.Literal(0.0, "FLOAT")
            else:
                initializer = nodes.Literal(False, "BOOLEAN")

        # Static type check between declared type and initializer type
        init_type = self._infer_expr_type(initializer)
        if init_type is not None:
            if norm_type == "bool" and init_type != "bool":
                raise SemanticError(f"Type mismatch: cannot convert from {init_type} to bool for variable '{var_name}'.", name_token.line, name_token.column)
            if norm_type in ("int", "float") and init_type == "bool":
                raise SemanticError(f"Type mismatch: cannot convert from bool to {type_name} for variable '{var_name}'.", name_token.line, name_token.column)
            if norm_type == "int" and init_type == "float":
                raise SemanticError(f"Type mismatch: narrowing conversion from double to int for variable '{var_name}'.", name_token.line, name_token.column)

        self.declared_symbols[var_name] = (norm_type, name_token)
        return nodes.VariableDeclaration(nodes.Identifier(var_name), initializer)

    def parse_assignment(self) -> nodes.Assignment:
        if self.check(CPPTokenType.IDENTIFIER):
            name_token = self.advance()
            var_name = name_token.lexeme

            if not self.check(CPPTokenType.ASSIGN):
                token = self.peek()
                raise ParserError(f"Expected assignment '=' after identifier '{var_name}'. Found '{token.lexeme}'.", token.line, token.column)

            if var_name not in self.declared_symbols:
                raise SemanticError(f"Variable '{var_name}' is not declared.", name_token.line, name_token.column)

            norm_type, _ = self.declared_symbols[var_name]
            self.advance() # consume '='
            value = self.parse_expression()
            self.consume(CPPTokenType.SEMICOLON, "Expected ';' after assignment.")

            val_type = self._infer_expr_type(value)
            if val_type is not None:
                if norm_type == "bool" and val_type != "bool":
                    raise SemanticError(f"Type mismatch: cannot assign {val_type} to bool variable '{var_name}'.", name_token.line, name_token.column)
                if norm_type in ("int", "float") and val_type == "bool":
                    raise SemanticError(f"Type mismatch: cannot assign bool to numeric variable '{var_name}'.", name_token.line, name_token.column)
                if norm_type == "int" and val_type == "float":
                    raise SemanticError(f"Type mismatch: narrowing conversion assigning double to int variable '{var_name}'.", name_token.line, name_token.column)

            return nodes.Assignment(nodes.Identifier(var_name), value)

        token = self.peek()
        raise ParserError(f"Expected statement, found '{token.lexeme}'.", token.line, token.column)

    def parse_cout_statement(self) -> nodes.PrintStatement:
        # std::cout already consumed
        self.consume(CPPTokenType.STREAM_OUT, "Expected '<<' after 'std::cout'.")
        expr = self.parse_expression()

        # Check for optional << std::endl
        if self.match(CPPTokenType.STREAM_OUT):
            self.consume(CPPTokenType.STD_ENDL, "Expected 'std::endl' after '<<'.")

        self.consume(CPPTokenType.SEMICOLON, "Expected ';' after std::cout statement.")
        return nodes.PrintStatement(expr)

    def parse_if_statement(self) -> nodes.IfStatement:
        self.consume(CPPTokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(CPPTokenType.RPAREN, "Expected ')' after if condition.")

        cond_type = self._infer_expr_type(condition)
        if cond_type is not None and cond_type != "bool":
            raise SemanticError(f"Type mismatch: condition must be of type bool, found {cond_type}.", self.previous().line, self.previous().column)

        self.consume(CPPTokenType.LBRACE, "Expected '{' before if body.")
        then_block = self.parse_block()

        else_block = None
        if self.match(CPPTokenType.ELSE):
            if self.match(CPPTokenType.IF):
                # else if -> wrap in block
                nested_if = self.parse_if_statement()
                else_block = nodes.Block([nested_if])
            else:
                self.consume(CPPTokenType.LBRACE, "Expected '{' before else body.")
                else_block = self.parse_block()

        return nodes.IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> nodes.WhileStatement:
        self.consume(CPPTokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(CPPTokenType.RPAREN, "Expected ')' after while condition.")

        cond_type = self._infer_expr_type(condition)
        if cond_type is not None and cond_type != "bool":
            raise SemanticError(f"Type mismatch: condition must be of type bool, found {cond_type}.", self.previous().line, self.previous().column)

        self.consume(CPPTokenType.LBRACE, "Expected '{' before while body.")
        body = self.parse_block()

        return nodes.WhileStatement(condition, body)

    def parse_block(self) -> nodes.Block:
        statements: List[nodes.ASTNode] = []
        while not self.check(CPPTokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        self.consume(CPPTokenType.RBRACE, "Expected '}' to close block.")
        return nodes.Block(statements)

    # --- Expression Parsing with Precedence ---

    def parse_expression(self) -> nodes.ASTNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> nodes.ASTNode:
        expr = self.parse_logical_and()
        while self.match(CPPTokenType.OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_logical_and(self) -> nodes.ASTNode:
        expr = self.parse_equality()
        while self.match(CPPTokenType.AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_equality(self) -> nodes.ASTNode:
        expr = self.parse_relational()
        while self.match(CPPTokenType.EQUAL_EQUAL, CPPTokenType.NOT_EQUAL):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_relational(self) -> nodes.ASTNode:
        expr = self.parse_additive()
        while self.match(CPPTokenType.LESS, CPPTokenType.LESS_EQUAL, CPPTokenType.GREATER, CPPTokenType.GREATER_EQUAL):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_additive(self) -> nodes.ASTNode:
        expr = self.parse_multiplicative()
        while self.match(CPPTokenType.PLUS, CPPTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_multiplicative(self) -> nodes.ASTNode:
        expr = self.parse_unary()
        while self.match(CPPTokenType.STAR, CPPTokenType.SLASH, CPPTokenType.MOD):
            op = self.previous().lexeme
            right = self.parse_unary()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_unary(self) -> nodes.ASTNode:
        if self.match(CPPTokenType.NOT, CPPTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_unary()
            return nodes.UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> nodes.ASTNode:
        if self.match(CPPTokenType.TRUE):
            return nodes.Literal(True, "BOOLEAN")
        if self.match(CPPTokenType.FALSE):
            return nodes.Literal(False, "BOOLEAN")
        if self.match(CPPTokenType.INTEGER_LITERAL):
            return nodes.Literal(int(self.previous().lexeme), "INTEGER")
        if self.match(CPPTokenType.FLOAT_LITERAL):
            return nodes.Literal(float(self.previous().lexeme), "FLOAT")
        if self.match(CPPTokenType.IDENTIFIER):
            return nodes.Identifier(self.previous().lexeme)

        if self.match(CPPTokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(CPPTokenType.RPAREN, "Expected ')' after expression.")
            return expr

        token = self.peek()
        raise ParserError(f"Expected expression, found '{token.lexeme}'.", token.line, token.column)

    def _infer_expr_type(self, node: nodes.ASTNode) -> Optional[str]:
        """Returns 'int', 'float', 'bool', or None if unresolved."""
        if isinstance(node, nodes.Literal):
            if node.literal_type == "INTEGER": return "int"
            if node.literal_type == "FLOAT": return "float"
            if node.literal_type == "BOOLEAN": return "bool"
        elif isinstance(node, nodes.Identifier):
            if node.name in self.declared_symbols:
                return self.declared_symbols[node.name][0]
        elif isinstance(node, nodes.BinaryExpression):
            left_t = self._infer_expr_type(node.left)
            right_t = self._infer_expr_type(node.right)
            if node.operator in ("+", "-", "*", "/", "%"):
                if left_t == "float" or right_t == "float": return "float"
                if left_t == "int" and right_t == "int": return "int"
            elif node.operator in ("<", "<=", ">", ">=", "==", "!=", "&&", "||"):
                return "bool"
        elif isinstance(node, nodes.UnaryExpression):
            if node.operator == "!": return "bool"
            if node.operator == "-": return self._infer_expr_type(node.right)
        return None
