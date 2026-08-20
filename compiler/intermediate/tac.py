import sys
import os
from typing import List, Optional, Union, Any

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.ast import nodes
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.errors import LexicalError, ParserError, SemanticError

class TACInstruction:
    def __str__(self) -> str:
        raise NotImplementedError()

class Assignment(TACInstruction):
    def __init__(self, result: str, arg1: Any):
        self.result = result
        self.arg1 = arg1
    def __str__(self) -> str:
        return f"{self.result} = {self.arg1}"

class Binary(TACInstruction):
    def __init__(self, result: str, arg1: Any, op: str, arg2: Any):
        self.result = result
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
    def __str__(self) -> str:
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"

class Unary(TACInstruction):
    def __init__(self, result: str, op: str, arg1: Any):
        self.result = result
        self.op = op
        self.arg1 = arg1
    def __str__(self) -> str:
        return f"{self.result} = {self.op}{self.arg1}"

class Label(TACInstruction):
    def __init__(self, name: str):
        self.name = name
    def __str__(self) -> str:
        return f"{self.name}:"

class Goto(TACInstruction):
    def __init__(self, target: str):
        self.target = target
    def __str__(self) -> str:
        return f"GOTO {self.target}"

class ConditionalJump(TACInstruction):
    def __init__(self, condition: Any, target: str, jump_if_false: bool = True):
        self.condition = condition
        self.target = target
        self.jump_if_false = jump_if_false
    def __str__(self) -> str:
        instr = "IF_FALSE" if self.jump_if_false else "IF_TRUE"
        return f"{instr} {self.condition} GOTO {self.target}"

class Print(TACInstruction):
    def __init__(self, value: Any):
        self.value = value
    def __str__(self) -> str:
        return f"PRINT {self.value}"


class TACGenerator:
    """Generates Three-Address Code from an AST."""
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction: TACInstruction):
        self.instructions.append(instruction)

    def generate(self, ast: nodes.Program) -> List[TACInstruction]:
        self.visit(ast)
        return self.instructions

    def visit(self, node: nodes.ASTNode) -> str:
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
            raise RuntimeError(f"TACGenerator: Unknown AST node type: {type(node).__name__}")

    def visit_program(self, node: nodes.Program) -> str:
        for stmt in node.statements:
            self.visit(stmt)
        return ""

    def visit_block(self, node: nodes.Block) -> str:
        for stmt in node.statements:
            self.visit(stmt)
        return ""

    def visit_variable_declaration(self, node: nodes.VariableDeclaration) -> str:
        init_val = self.visit(node.initializer)
        self.emit(Assignment(node.name.name, init_val))
        return ""

    def visit_assignment(self, node: nodes.Assignment) -> str:
        val = self.visit(node.value)
        self.emit(Assignment(node.name.name, val))
        return ""

    def visit_print_statement(self, node: nodes.PrintStatement) -> str:
        val = self.visit(node.expression)
        self.emit(Print(val))
        return ""

    def visit_if_statement(self, node: nodes.IfStatement) -> str:
        cond_val = self.visit(node.condition)
        
        l_false = self.new_label()
        
        self.emit(ConditionalJump(cond_val, l_false, jump_if_false=True))
        self.visit(node.then_block)
        
        if node.else_block:
            l_end = self.new_label()
            self.emit(Goto(l_end))
            self.emit(Label(l_false))
            self.visit(node.else_block)
            self.emit(Label(l_end))
        else:
            self.emit(Label(l_false))
        
        return ""

    def visit_while_statement(self, node: nodes.WhileStatement) -> str:
        l_start = self.new_label()
        l_end = self.new_label()
        
        self.emit(Label(l_start))
        cond_val = self.visit(node.condition)
        self.emit(ConditionalJump(cond_val, l_end, jump_if_false=True))
        
        self.visit(node.body)
        self.emit(Goto(l_start))
        
        self.emit(Label(l_end))
        return ""

    def visit_binary_expression(self, node: nodes.BinaryExpression) -> str:
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        
        temp = self.new_temp()
        self.emit(Binary(temp, left_val, node.operator, right_val))
        return temp

    def visit_unary_expression(self, node: nodes.UnaryExpression) -> str:
        val = self.visit(node.right)
        
        temp = self.new_temp()
        self.emit(Unary(temp, node.operator, val))
        return temp

    def visit_literal(self, node: nodes.Literal) -> str:
        if isinstance(node.value, bool):
            return str(node.value).lower()
        return str(node.value)

    def visit_identifier(self, node: nodes.Identifier) -> str:
        return node.name

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.intermediate.tac <source_file>")
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
        
        generator = TACGenerator()
        instructions = generator.generate(ast)
        
        print("========== THREE ADDRESS CODE ==========\n")
        for instr in instructions:
            print(instr)
            
    except (LexicalError, ParserError, SemanticError) as e:
        print(f"\n========== COMPILER ERROR ==========\n")
        print(f"✗ {e}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
