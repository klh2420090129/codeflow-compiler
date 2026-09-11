import sys
import os
from typing import List, Optional, Set, Dict, Tuple

from compiler.frontends.java.lexer import JavaToken, JavaTokenType
from compiler.errors import ParserError, SemanticError
from compiler.ast import nodes

class JavaParser:
    """
    Structured recursive-descent parser for the supported Java subset.
    Translates Java AST directly into unified CodeFlow AST nodes.

    Recognizes the canonical wrapper:
        public class Main {
            public static void main(String[] args) {
                ...
            }
        }
    Also supports top-level statements directly for shorthand testing convenience.
    """

    def __init__(self, tokens: List[JavaToken]):
        self.tokens = tokens
        self.current = 0
        # Symbol tracking at the frontend level: name -> (type_name, is_final, decl_token)
        self.declared_symbols: Dict[str, Tuple[str, bool, JavaToken]] = {}

    def parse(self) -> nodes.Program:
        # Check if the program uses the canonical public class Main wrapper
        if self.check(JavaTokenType.PUBLIC) or self.check(JavaTokenType.CLASS):
            statements = self.parse_class_wrapper()
        else:
            # Direct statement list shorthand
            statements = self.parse_statement_list()

        return nodes.Program(statements)

    # --- Wrapper Parsing ---

    def parse_class_wrapper(self) -> List[nodes.ASTNode]:
        self.consume(JavaTokenType.PUBLIC, "Expected 'public' at start of class declaration.")
        self.consume(JavaTokenType.CLASS, "Expected 'class' after 'public'.")
        
        class_name = self.consume(JavaTokenType.IDENTIFIER, "Expected class name.")
        if class_name.lexeme != "Main":
            raise ParserError(f"Educational Java subset requires class name to be 'Main', found '{class_name.lexeme}'.", class_name.line, class_name.column)

        self.consume(JavaTokenType.LBRACE, "Expected '{' after class name.")

        # Parse public static void main(String[] args)
        self.consume(JavaTokenType.PUBLIC, "Expected 'public' before method declaration.")
        self.consume(JavaTokenType.STATIC, "Expected 'static' after 'public'.")
        self.consume(JavaTokenType.VOID, "Expected 'void' after 'static'.")
        
        main_tok = self.consume(JavaTokenType.MAIN, "Expected 'main' method identifier.")
        self.consume(JavaTokenType.LPAREN, "Expected '(' after 'main'.")
        self.consume(JavaTokenType.STRING, "Expected 'String' parameter type for main().")
        self.consume(JavaTokenType.LBRACKET, "Expected '[' after 'String'.")
        self.consume(JavaTokenType.RBRACKET, "Expected ']' after '['.")
        self.consume(JavaTokenType.IDENTIFIER, "Expected parameter name (e.g. 'args').")
        self.consume(JavaTokenType.RPAREN, "Expected ')' after main parameters.")

        self.consume(JavaTokenType.LBRACE, "Expected '{' before main body.")
        statements: List[nodes.ASTNode] = []
        while not self.check(JavaTokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        self.consume(JavaTokenType.RBRACE, "Expected '}' after main method body.")

        # Check for any extra members inside Main class
        if not self.check(JavaTokenType.RBRACE) and not self.is_at_end():
            tok = self.peek()
            raise ParserError(f"Additional class members or methods are not supported in this Java subset. Found '{tok.lexeme}'.", tok.line, tok.column)

        self.consume(JavaTokenType.RBRACE, "Expected '}' after class body.")

        # Check if anything after class
        if not self.is_at_end():
            tok = self.peek()
            raise ParserError(f"Additional classes or code outside class Main are not supported. Found '{tok.lexeme}'.", tok.line, tok.column)

        return statements

    def parse_statement_list(self) -> List[nodes.ASTNode]:
        statements: List[nodes.ASTNode] = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    # --- Helper methods ---

    def peek(self) -> JavaToken:
        return self.tokens[self.current]

    def previous(self) -> JavaToken:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == JavaTokenType.EOF

    def check(self, token_type: JavaTokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> JavaToken:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: JavaTokenType) -> bool:
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: JavaTokenType, message: str) -> JavaToken:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParserError(f"{message} Found '{token.lexeme}'.", token.line, token.column)

    # --- Statement Parsing ---

    def parse_statement(self) -> nodes.ASTNode:
        # Check for final keyword
        if self.match(JavaTokenType.FINAL):
            return self.parse_variable_declaration(is_final=True)

        # Check for primitive type declarations: int, double, boolean
        if self.match(JavaTokenType.INT, JavaTokenType.DOUBLE, JavaTokenType.BOOLEAN):
            return self.parse_variable_declaration(is_final=False)

        if self.match(JavaTokenType.IF):
            return self.parse_if_statement()
        if self.match(JavaTokenType.WHILE):
            return self.parse_while_statement()
        if self.match(JavaTokenType.SYSTEM_OUT_PRINTLN):
            return self.parse_println_statement()
        if self.match(JavaTokenType.LBRACE):
            return self.parse_block()

        # Check for empty statements (stray semicolons)
        if self.match(JavaTokenType.SEMICOLON):
            return self.parse_statement()

        return self.parse_assignment()

    def parse_variable_declaration(self, is_final: bool) -> nodes.VariableDeclaration:
        type_token = self.previous()
        if is_final:
            # In 'final int x = ...', the type token comes next
            if not self.match(JavaTokenType.INT, JavaTokenType.DOUBLE, JavaTokenType.BOOLEAN):
                tok = self.peek()
                raise ParserError(f"Expected type (int, double, boolean) after 'final'. Found '{tok.lexeme}'.", tok.line, tok.column)
            type_token = self.previous()

        type_name = type_token.lexeme # 'int', 'double', or 'boolean'
        # Map double to float for CodeFlow semantic model
        norm_type = "float" if type_name == "double" else ("bool" if type_name == "boolean" else "int")

        name_token = self.consume(JavaTokenType.IDENTIFIER, "Expected variable name in declaration.")
        var_name = name_token.lexeme

        # Check duplicate declaration in same scope
        if var_name in self.declared_symbols:
            raise SemanticError(f"Variable '{var_name}' is already declared.", name_token.line, name_token.column)

        initializer: Optional[nodes.ASTNode] = None
        if self.match(JavaTokenType.ASSIGN):
            initializer = self.parse_expression()
            self.consume(JavaTokenType.SEMICOLON, "Expected ';' after variable declaration.")
        else:
            if is_final:
                raise SemanticError(f"Final variable '{var_name}' must be initialized upon declaration.", name_token.line, name_token.column)
            self.consume(JavaTokenType.SEMICOLON, "Expected ';' after variable declaration.")
            # Default initialization in Java: int -> 0, double -> 0.0, boolean -> false
            if norm_type == "int":
                initializer = nodes.Literal(0, "INTEGER")
            elif norm_type == "float":
                initializer = nodes.Literal(0.0, "FLOAT")
            else:
                initializer = nodes.Literal(False, "BOOLEAN")

        # Frontend type check between declared type and initializer type
        init_type = self._infer_expr_type(initializer)
        if init_type is not None:
            if norm_type == "bool" and init_type != "bool":
                raise SemanticError(f"Type mismatch: cannot convert from {init_type} to boolean for variable '{var_name}'.", name_token.line, name_token.column)
            if norm_type in ("int", "float") and init_type == "bool":
                raise SemanticError(f"Type mismatch: cannot convert from boolean to {type_name} for variable '{var_name}'.", name_token.line, name_token.column)
            if norm_type == "int" and init_type == "float":
                raise SemanticError(f"Type mismatch: possible loss of precision converting from double to int for variable '{var_name}'.", name_token.line, name_token.column)

        self.declared_symbols[var_name] = (norm_type, is_final, name_token)
        return nodes.VariableDeclaration(nodes.Identifier(var_name), initializer)

    def parse_assignment(self) -> nodes.Assignment:
        if self.check(JavaTokenType.IDENTIFIER):
            name_token = self.advance()
            var_name = name_token.lexeme

            if not self.check(JavaTokenType.ASSIGN):
                token = self.peek()
                raise ParserError(f"Expected assignment '=' after identifier '{var_name}'. Found '{token.lexeme}'.", token.line, token.column)

            # Check if variable was declared
            if var_name not in self.declared_symbols:
                raise SemanticError(f"Variable '{var_name}' is not declared.", name_token.line, name_token.column)

            norm_type, is_final, _ = self.declared_symbols[var_name]
            if is_final:
                raise SemanticError(f"Cannot assign a value to final variable '{var_name}'.", name_token.line, name_token.column)

            self.advance() # consume '='
            value = self.parse_expression()
            self.consume(JavaTokenType.SEMICOLON, "Expected ';' after assignment.")

            val_type = self._infer_expr_type(value)
            if val_type is not None:
                if norm_type == "bool" and val_type != "bool":
                    raise SemanticError(f"Type mismatch: cannot assign {val_type} to boolean variable '{var_name}'.", name_token.line, name_token.column)
                if norm_type in ("int", "float") and val_type == "bool":
                    raise SemanticError(f"Type mismatch: cannot assign boolean to numeric variable '{var_name}'.", name_token.line, name_token.column)
                if norm_type == "int" and val_type == "float":
                    raise SemanticError(f"Type mismatch: possible loss of precision assigning double to int variable '{var_name}'.", name_token.line, name_token.column)

            return nodes.Assignment(nodes.Identifier(var_name), value)

        token = self.peek()
        raise ParserError(f"Expected statement, found '{token.lexeme}'.", token.line, token.column)

    def parse_println_statement(self) -> nodes.PrintStatement:
        self.consume(JavaTokenType.LPAREN, "Expected '(' after 'System.out.println'.")
        expr = self.parse_expression()
        self.consume(JavaTokenType.RPAREN, "Expected ')' after println expression.")
        self.consume(JavaTokenType.SEMICOLON, "Expected ';' after System.out.println statement.")
        return nodes.PrintStatement(expr)

    def parse_if_statement(self) -> nodes.IfStatement:
        self.consume(JavaTokenType.LPAREN, "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(JavaTokenType.RPAREN, "Expected ')' after if condition.")

        # Ensure condition evaluates to boolean
        cond_type = self._infer_expr_type(condition)
        if cond_type is not None and cond_type != "bool":
            raise SemanticError(f"Type mismatch: cannot convert from {cond_type} to boolean in if condition.", self.previous().line, self.previous().column)

        self.consume(JavaTokenType.LBRACE, "Expected '{' before if body.")
        then_block = self.parse_block()

        else_block = None
        if self.match(JavaTokenType.ELSE):
            if self.match(JavaTokenType.IF):
                # else if -> wrap in Block
                nested_if = self.parse_if_statement()
                else_block = nodes.Block([nested_if])
            else:
                self.consume(JavaTokenType.LBRACE, "Expected '{' before else body.")
                else_block = self.parse_block()

        return nodes.IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> nodes.WhileStatement:
        self.consume(JavaTokenType.LPAREN, "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(JavaTokenType.RPAREN, "Expected ')' after while condition.")

        cond_type = self._infer_expr_type(condition)
        if cond_type is not None and cond_type != "bool":
            raise SemanticError(f"Type mismatch: cannot convert from {cond_type} to boolean in while condition.", self.previous().line, self.previous().column)

        self.consume(JavaTokenType.LBRACE, "Expected '{' before while body.")
        body = self.parse_block()

        return nodes.WhileStatement(condition, body)

    def parse_block(self) -> nodes.Block:
        statements: List[nodes.ASTNode] = []
        while not self.check(JavaTokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        self.consume(JavaTokenType.RBRACE, "Expected '}' to close block.")
        return nodes.Block(statements)

    # --- Expression Parsing with Precedence ---

    def parse_expression(self) -> nodes.ASTNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> nodes.ASTNode:
        expr = self.parse_logical_and()
        while self.match(JavaTokenType.OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_logical_and(self) -> nodes.ASTNode:
        expr = self.parse_equality()
        while self.match(JavaTokenType.AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_equality(self) -> nodes.ASTNode:
        expr = self.parse_relational()
        while self.match(JavaTokenType.EQUAL_EQUAL, JavaTokenType.NOT_EQUAL):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_relational(self) -> nodes.ASTNode:
        expr = self.parse_additive()
        while self.match(JavaTokenType.LESS, JavaTokenType.LESS_EQUAL, JavaTokenType.GREATER, JavaTokenType.GREATER_EQUAL):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_additive(self) -> nodes.ASTNode:
        expr = self.parse_multiplicative()
        while self.match(JavaTokenType.PLUS, JavaTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_multiplicative(self) -> nodes.ASTNode:
        expr = self.parse_unary()
        while self.match(JavaTokenType.STAR, JavaTokenType.SLASH, JavaTokenType.MOD):
            op = self.previous().lexeme
            right = self.parse_unary()
            expr = nodes.BinaryExpression(op, expr, right)
        return expr

    def parse_unary(self) -> nodes.ASTNode:
        if self.match(JavaTokenType.NOT, JavaTokenType.MINUS):
            op = self.previous().lexeme
            right = self.parse_unary()
            return nodes.UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> nodes.ASTNode:
        if self.match(JavaTokenType.TRUE):
            return nodes.Literal(True, "BOOLEAN")
        if self.match(JavaTokenType.FALSE):
            return nodes.Literal(False, "BOOLEAN")
        if self.match(JavaTokenType.INTEGER_LITERAL):
            return nodes.Literal(int(self.previous().lexeme), "INTEGER")
        if self.match(JavaTokenType.FLOAT_LITERAL):
            return nodes.Literal(float(self.previous().lexeme), "FLOAT")
        if self.match(JavaTokenType.IDENTIFIER):
            return nodes.Identifier(self.previous().lexeme)

        if self.match(JavaTokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(JavaTokenType.RPAREN, "Expected ')' after expression.")
            return expr

        token = self.peek()
        raise ParserError(f"Expected expression, found '{token.lexeme}'.", token.line, token.column)

    # --- Type Inference Helper ---

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
