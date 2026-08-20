import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.ast import nodes
from compiler.semantic.symbol_table import SymbolTable
from compiler.errors import SemanticError, ParserError, LexicalError
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, ast: nodes.Program):
        self.visit(ast)

    def visit(self, node: nodes.ASTNode) -> str:
        """Returns the semantic type as a string."""
        if isinstance(node, nodes.Program):
            return self.visit_program(node)
        elif isinstance(node, nodes.Block):
            return self.visit_block(node)
        elif isinstance(node, nodes.VariableDeclaration):
            return self.visit_variable_declaration(node)
        elif isinstance(node, nodes.Assignment):
            return self.visit_assignment(node)
        elif isinstance(node, nodes.PrintStatement):
            return self.visit_print_statement(node)
        elif isinstance(node, nodes.IfStatement):
            return self.visit_if_statement(node)
        elif isinstance(node, nodes.WhileStatement):
            return self.visit_while_statement(node)
        elif isinstance(node, nodes.BinaryExpression):
            return self.visit_binary_expression(node)
        elif isinstance(node, nodes.UnaryExpression):
            return self.visit_unary_expression(node)
        elif isinstance(node, nodes.Literal):
            return self.visit_literal(node)
        elif isinstance(node, nodes.Identifier):
            return self.visit_identifier(node)
        else:
            raise SemanticError(f"Unknown AST node type: {type(node).__name__}")

    def visit_program(self, node: nodes.Program) -> str:
        for stmt in node.statements:
            self.visit(stmt)
        return "void"

    def visit_block(self, node: nodes.Block) -> str:
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        return "void"

    def visit_variable_declaration(self, node: nodes.VariableDeclaration) -> str:
        name = node.name.name
        init_type = self.visit(node.initializer)
        
        symbol = self.symbol_table.define(name, init_type, initialized=True)
        if symbol is None:
            raise SemanticError(f"Variable '{name}' is already declared in this scope.")
        return "void"

    def visit_assignment(self, node: nodes.Assignment) -> str:
        name = node.name.name
        symbol = self.symbol_table.lookup(name)
        if not symbol:
            raise SemanticError(f"Variable '{name}' is not declared.")
        
        val_type = self.visit(node.value)
        # Assuming simple types, must match. E.g. float to float, int to int.
        # But we allow int assigned to float and float assigned to int for simplicity.
        if symbol.type_name == 'bool' and val_type != 'bool':
             raise SemanticError(f"Cannot assign {val_type} to boolean variable '{name}'.")
        if symbol.type_name in ['int', 'float'] and val_type == 'bool':
             raise SemanticError(f"Cannot assign bool to numeric variable '{name}'.")
        
        symbol.initialized = True
        return "void"

    def visit_print_statement(self, node: nodes.PrintStatement) -> str:
        self.visit(node.expression)
        return "void"

    def visit_if_statement(self, node: nodes.IfStatement) -> str:
        cond_type = self.visit(node.condition)
        if cond_type != "bool":
            raise SemanticError("If condition must evaluate to boolean.")
        
        self.visit(node.then_block)
        
        if node.else_block:
            self.visit(node.else_block)
        return "void"

    def visit_while_statement(self, node: nodes.WhileStatement) -> str:
        cond_type = self.visit(node.condition)
        if cond_type != "bool":
            raise SemanticError("While condition must evaluate to boolean.")
        
        self.visit(node.body)
        return "void"

    def visit_binary_expression(self, node: nodes.BinaryExpression) -> str:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        arithmetic_ops = ["+", "-", "*", "/", "%"]
        relational_ops = ["<", ">", "<=", ">="]
        equality_ops = ["==", "!="]
        logical_ops = ["&&", "||"]

        if node.operator in arithmetic_ops:
            if left_type in ["int", "float"] and right_type in ["int", "float"]:
                return "float" if "float" in [left_type, right_type] else "int"
            raise SemanticError(f"Operator '{node.operator}' cannot be applied to {left_type} and {right_type}.")
        
        if node.operator in relational_ops:
            if left_type in ["int", "float"] and right_type in ["int", "float"]:
                return "bool"
            raise SemanticError(f"Operator '{node.operator}' cannot be applied to {left_type} and {right_type}.")

        if node.operator in equality_ops:
            if left_type == right_type or (left_type in ["int", "float"] and right_type in ["int", "float"]):
                return "bool"
            raise SemanticError(f"Operator '{node.operator}' cannot be applied to {left_type} and {right_type}.")

        if node.operator in logical_ops:
            if left_type == "bool" and right_type == "bool":
                return "bool"
            raise SemanticError(f"Operator '{node.operator}' cannot be applied to {left_type} and {right_type}.")

        raise SemanticError(f"Unknown binary operator: {node.operator}")

    def visit_unary_expression(self, node: nodes.UnaryExpression) -> str:
        right_type = self.visit(node.right)
        
        if node.operator == "!":
            if right_type != "bool":
                raise SemanticError(f"Operator '!' cannot be applied to {right_type}.")
            return "bool"
        if node.operator == "-":
            if right_type not in ["int", "float"]:
                raise SemanticError(f"Operator '-' cannot be applied to {right_type}.")
            return right_type

        raise SemanticError(f"Unknown unary operator: {node.operator}")

    def visit_literal(self, node: nodes.Literal) -> str:
        if node.literal_type == "INTEGER": return "int"
        if node.literal_type == "FLOAT": return "float"
        if node.literal_type == "BOOLEAN": return "bool"
        raise SemanticError(f"Unknown literal type: {node.literal_type}")

    def visit_identifier(self, node: nodes.Identifier) -> str:
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Variable '{node.name}' is not declared.")
        return symbol.type_name

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.semantic.analyzer <source_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
            
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        print(analyzer.symbol_table.display())
        print("========== SEMANTIC ANALYSIS ==========\n")
        print("✓ No semantic errors found.")
            
    except (LexicalError, ParserError, SemanticError) as e:
        print(f"\n========== SEMANTIC ANALYSIS ==========\n")
        print(f"✗ {e}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
