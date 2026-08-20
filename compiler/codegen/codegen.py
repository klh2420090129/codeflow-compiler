import sys
import os
from typing import List, Any, Optional

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator, TACInstruction, Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
from compiler.optimizer.optimizer import Optimizer
from compiler.errors import LexicalError, ParserError, SemanticError

class TargetInstruction:
    def __init__(self, opcode: str, operand: Optional[Any] = None):
        self.opcode = opcode
        self.operand = operand
        
    def __str__(self):
        if self.operand is not None:
            return f"{self.opcode} {self.operand}"
        return f"{self.opcode}"

class TargetProgram:
    def __init__(self):
        self.instructions: List[TargetInstruction] = []
        
    def append(self, instr: TargetInstruction):
        self.instructions.append(instr)
        
    def to_list(self) -> List[TargetInstruction]:
        return self.instructions

class CodeGenerator:
    def __init__(self):
        pass
        
    def is_literal(self, val: Any) -> bool:
        if isinstance(val, (int, float, bool)):
            return True
        if isinstance(val, str):
            if val.lower() in ['true', 'false']: return True
            try:
                float(val)
                return True
            except ValueError:
                return False
        return False

    def _parse_literal(self, val: Any) -> Any:
        if isinstance(val, bool): return val
        if isinstance(val, str):
            if val.lower() == 'true': return True
            if val.lower() == 'false': return False
            try:
                if '.' in val: return float(val)
                return int(val)
            except ValueError:
                pass
        return val

    def generate(self, tac_instructions: List[TACInstruction]) -> TargetProgram:
        program = TargetProgram()
        
        for instr in tac_instructions:
            if isinstance(instr, Assignment):
                if self.is_literal(instr.arg1):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.arg1)))
                else:
                    program.append(TargetInstruction("LOAD", instr.arg1))
                program.append(TargetInstruction("STORE", instr.result))
                
            elif isinstance(instr, Binary):
                if self.is_literal(instr.arg1):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.arg1)))
                else:
                    program.append(TargetInstruction("LOAD", instr.arg1))
                    
                if self.is_literal(instr.arg2):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.arg2)))
                else:
                    program.append(TargetInstruction("LOAD", instr.arg2))
                    
                op_map = {
                    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD',
                    '<': 'CMP_LT', '>': 'CMP_GT', '<=': 'CMP_LE', '>=': 'CMP_GE',
                    '==': 'CMP_EQ', '!=': 'CMP_NE',
                    '&&': 'AND', '||': 'OR'
                }
                program.append(TargetInstruction(op_map[instr.op]))
                program.append(TargetInstruction("STORE", instr.result))
                
            elif isinstance(instr, Unary):
                if self.is_literal(instr.arg1):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.arg1)))
                else:
                    program.append(TargetInstruction("LOAD", instr.arg1))
                    
                op_map = {'-': 'NEG', '!': 'NOT'}
                program.append(TargetInstruction(op_map[instr.op]))
                program.append(TargetInstruction("STORE", instr.result))
                
            elif isinstance(instr, Label):
                program.append(TargetInstruction("LABEL", instr.name))
                
            elif isinstance(instr, Goto):
                program.append(TargetInstruction("JMP", instr.target))
                
            elif isinstance(instr, ConditionalJump):
                if self.is_literal(instr.condition):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.condition)))
                else:
                    program.append(TargetInstruction("LOAD", instr.condition))
                jump_op = "JMP_IF_FALSE" if instr.jump_if_false else "JMP_IF_TRUE"
                program.append(TargetInstruction(jump_op, instr.target))
                
            elif isinstance(instr, Print):
                if self.is_literal(instr.value):
                    program.append(TargetInstruction("PUSH", self._parse_literal(instr.value)))
                else:
                    program.append(TargetInstruction("LOAD", instr.value))
                program.append(TargetInstruction("PRINT"))
                
        program.append(TargetInstruction("HALT"))
        return program

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.codegen.codegen <source_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source = f.read()
            
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        tac_gen = TACGenerator()
        tac = tac_gen.generate(ast)
        optimizer = Optimizer()
        optimized_tac = optimizer.optimize(tac)
        
        codegen = CodeGenerator()
        target_prog = codegen.generate(optimized_tac)
        
        print("========== OPTIMIZED TAC ==========\n")
        for instr in optimized_tac:
            print(instr)
            
        print("\n========== TARGET CODE ==========\n")
        for instr in target_prog.to_list():
            print(instr)
            
    except (LexicalError, ParserError, SemanticError) as e:
        print(f"\n========== COMPILER ERROR ==========\n")
        print(f"✗ {e}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
