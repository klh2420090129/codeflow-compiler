import sys
import os
import copy
from typing import List, Dict, Any, Set

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator, TACInstruction, Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
from compiler.errors import LexicalError, ParserError, SemanticError

class OptimizationStats:
    def __init__(self):
        self.constant_folds = 0
        self.constant_propagations = 0
        self.algebraic_simplifications = 0
        self.dead_code_eliminations = 0
        
    def __str__(self):
        return (f"Constant Folding: {self.constant_folds}\n"
                f"Constant Propagation: {self.constant_propagations}\n"
                f"Algebraic Simplification: {self.algebraic_simplifications}\n"
                f"Dead Code Elimination: {self.dead_code_eliminations}")

class Optimizer:
    def __init__(self):
        self.stats = OptimizationStats()
        
    def is_constant(self, val: Any) -> bool:
        if isinstance(val, (int, float, bool)):
            return True
        if isinstance(val, str):
            if val.lower() in ['true', 'false']:
                return True
            try:
                float(val)
                return True
            except ValueError:
                return False
        return False
        
    def get_constant_value(self, val: Any) -> Any:
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            if val.lower() == 'true': return True
            if val.lower() == 'false': return False
            try:
                if '.' in val: return float(val)
                return int(val)
            except ValueError:
                return val
        return val

    def format_constant(self, val: Any) -> str:
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

    def optimize(self, instructions: List[TACInstruction], max_iterations: int = 10) -> List[TACInstruction]:
        current_instructions = copy.deepcopy(instructions)
        
        for _ in range(max_iterations):
            prev_folds = self.stats.constant_folds
            prev_props = self.stats.constant_propagations
            prev_algs = self.stats.algebraic_simplifications
            prev_dces = self.stats.dead_code_eliminations
            
            current_instructions = self.constant_propagation(current_instructions)
            current_instructions = self.constant_folding_and_algebraic(current_instructions)
            current_instructions = self.dead_code_elimination(current_instructions)
            
            if (prev_folds == self.stats.constant_folds and
                prev_props == self.stats.constant_propagations and
                prev_algs == self.stats.algebraic_simplifications and
                prev_dces == self.stats.dead_code_eliminations):
                break
                
        return current_instructions

    def constant_propagation(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        constants: Dict[str, Any] = {}
        result = []
        
        for instr in instructions:
            if isinstance(instr, Label):
                constants.clear()
                result.append(instr)
            elif isinstance(instr, Assignment):
                if isinstance(instr.arg1, str) and instr.arg1 in constants:
                    instr.arg1 = constants[instr.arg1]
                    self.stats.constant_propagations += 1
                
                if self.is_constant(instr.arg1):
                    constants[instr.result] = instr.arg1
                else:
                    if instr.result in constants:
                        del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, Binary):
                if isinstance(instr.arg1, str) and instr.arg1 in constants:
                    instr.arg1 = constants[instr.arg1]
                    self.stats.constant_propagations += 1
                if isinstance(instr.arg2, str) and instr.arg2 in constants:
                    instr.arg2 = constants[instr.arg2]
                    self.stats.constant_propagations += 1
                
                if instr.result in constants:
                    del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, Unary):
                if isinstance(instr.arg1, str) and instr.arg1 in constants:
                    instr.arg1 = constants[instr.arg1]
                    self.stats.constant_propagations += 1
                
                if instr.result in constants:
                    del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, ConditionalJump):
                if isinstance(instr.condition, str) and instr.condition in constants:
                    instr.condition = constants[instr.condition]
                    self.stats.constant_propagations += 1
                result.append(instr)
                constants.clear()
                
            elif isinstance(instr, Goto):
                result.append(instr)
                constants.clear()
                
            elif isinstance(instr, Print):
                if isinstance(instr.value, str) and instr.value in constants:
                    instr.value = constants[instr.value]
                    self.stats.constant_propagations += 1
                result.append(instr)
            else:
                result.append(instr)
                
        return result

    def constant_folding_and_algebraic(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        result = []
        for instr in instructions:
            if isinstance(instr, Binary):
                c1 = self.is_constant(instr.arg1)
                c2 = self.is_constant(instr.arg2)
                
                if c1 and c2:
                    val1 = self.get_constant_value(instr.arg1)
                    val2 = self.get_constant_value(instr.arg2)
                    
                    try:
                        res = None
                        if instr.op == '+': res = val1 + val2
                        elif instr.op == '-': res = val1 - val2
                        elif instr.op == '*': res = val1 * val2
                        elif instr.op == '/': 
                            if val2 == 0:
                                result.append(instr)
                                continue
                            res = val1 / val2
                        elif instr.op == '%': 
                            if val2 == 0:
                                result.append(instr)
                                continue
                            res = val1 % val2
                        elif instr.op == '<': res = val1 < val2
                        elif instr.op == '>': res = val1 > val2
                        elif instr.op == '<=': res = val1 <= val2
                        elif instr.op == '>=': res = val1 >= val2
                        elif instr.op == '==': res = val1 == val2
                        elif instr.op == '!=': res = val1 != val2
                        elif instr.op == '&&': res = val1 and val2
                        elif instr.op == '||': res = val1 or val2
                        
                        if res is not None:
                            self.stats.constant_folds += 1
                            result.append(Assignment(instr.result, self.format_constant(res)))
                            continue
                    except Exception:
                        pass
                
                if instr.op == '+' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '+' and c1 and self.get_constant_value(instr.arg1) == 0:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg2))
                    continue
                if instr.op == '-' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '*' and c2 and self.get_constant_value(instr.arg2) == 1:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '*' and c1 and self.get_constant_value(instr.arg1) == 1:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg2))
                    continue
                if instr.op == '*' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, "0"))
                    continue
                if instr.op == '*' and c1 and self.get_constant_value(instr.arg1) == 0:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, "0"))
                    continue
                if instr.op == '/' and c2 and self.get_constant_value(instr.arg2) == 1:
                    self.stats.algebraic_simplifications += 1
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
            
            elif isinstance(instr, Unary):
                c1 = self.is_constant(instr.arg1)
                if c1:
                    val1 = self.get_constant_value(instr.arg1)
                    try:
                        res = None
                        if instr.op == '!': res = not val1
                        elif instr.op == '-': res = -val1
                        
                        if res is not None:
                            self.stats.constant_folds += 1
                            result.append(Assignment(instr.result, self.format_constant(res)))
                            continue
                    except Exception:
                        pass
                        
            result.append(instr)
        return result

    def dead_code_elimination(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        used = set()
        for instr in instructions:
            if isinstance(instr, Assignment):
                if not self.is_constant(instr.arg1): used.add(str(instr.arg1))
            elif isinstance(instr, Binary):
                if not self.is_constant(instr.arg1): used.add(str(instr.arg1))
                if not self.is_constant(instr.arg2): used.add(str(instr.arg2))
            elif isinstance(instr, Unary):
                if not self.is_constant(instr.arg1): used.add(str(instr.arg1))
            elif isinstance(instr, ConditionalJump):
                if not self.is_constant(instr.condition): used.add(str(instr.condition))
            elif isinstance(instr, Print):
                if not self.is_constant(instr.value): used.add(str(instr.value))
        
        result = []
        for instr in instructions:
            if isinstance(instr, (Assignment, Binary, Unary)):
                if str(instr.result).startswith('t') and str(instr.result) not in used:
                    self.stats.dead_code_eliminations += 1
                    continue
            result.append(instr)
            
        return result

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.optimizer.optimizer <source_file>")
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
        original_instructions = generator.generate(ast)
        
        optimizer = Optimizer()
        optimized_instructions = optimizer.optimize(original_instructions)
        
        print("========== ORIGINAL TAC ==========\n")
        for instr in original_instructions:
            print(instr)
            
        print("\n========== OPTIMIZED TAC ==========\n")
        for instr in optimized_instructions:
            print(instr)
            
        print("\n========== OPTIMIZATION STATISTICS ==========\n")
        print(optimizer.stats)
            
    except (LexicalError, ParserError, SemanticError) as e:
        print(f"\n========== COMPILER ERROR ==========\n")
        print(f"✗ {e}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
