import sys
import os
import copy
from typing import List, Dict, Any, Set, Optional

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

    def to_dict(self) -> Dict[str, int]:
        return {
            "constant_folds": self.constant_folds,
            "constant_propagations": self.constant_propagations,
            "algebraic_simplifications": self.algebraic_simplifications,
            "dead_code_eliminations": self.dead_code_eliminations
        }

class OptimizationStep:
    def __init__(self, step_number: int, pass_name: str, rule: str, before: str, after: str, explanation: str, affected_target: Optional[str] = None):
        self.step_number = step_number
        self.pass_name = pass_name
        self.rule = rule
        self.before = before
        self.after = after
        self.explanation = explanation
        self.affected_target = affected_target

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "pass_name": self.pass_name,
            "rule": self.rule,
            "before": self.before,
            "after": self.after,
            "explanation": self.explanation,
            "affected_target": self.affected_target
        }

    def __repr__(self) -> str:
        return f"OptimizationStep(#{self.step_number}, pass='{self.pass_name}', rule='{self.rule}', before='{self.before}', after='{self.after}')"

class Optimizer:
    def __init__(self):
        self.stats = OptimizationStats()
        self.steps: List[OptimizationStep] = []
        self.step_counter = 0

    def record_step(self, pass_name: str, rule: str, before: str, after: str, explanation: str, affected_target: Optional[str] = None):
        self.step_counter += 1
        step = OptimizationStep(
            step_number=self.step_counter,
            pass_name=pass_name,
            rule=rule,
            before=before,
            after=after,
            explanation=explanation,
            affected_target=affected_target
        )
        self.steps.append(step)

    def get_summary(self, before_count: int, after_count: int) -> Dict[str, Any]:
        removed = max(0, before_count - after_count)
        reduction_pct = round((removed / before_count * 100.0), 2) if before_count > 0 else 0.0
        return {
            "total_steps": len(self.steps),
            "passes": {
                "constant_propagation": self.stats.constant_propagations,
                "constant_folding": self.stats.constant_folds,
                "algebraic_simplification": self.stats.algebraic_simplifications,
                "dead_code_elimination": self.stats.dead_code_eliminations
            },
            "before_instruction_count": before_count,
            "after_instruction_count": after_count,
            "instructions_removed": removed,
            "reduction_percentage": reduction_pct
        }
        
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
                    orig_var = instr.arg1
                    const_val = constants[instr.arg1]
                    instr.arg1 = const_val
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var}",
                        after=f"{const_val}",
                        explanation=f"Replaced variable '{orig_var}' with its known compile-time constant value '{const_val}' in assignment to '{instr.result}'.",
                        affected_target=instr.result
                    )
                
                if self.is_constant(instr.arg1):
                    constants[instr.result] = instr.arg1
                else:
                    if instr.result in constants:
                        del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, Binary):
                if isinstance(instr.arg1, str) and instr.arg1 in constants:
                    orig_var1 = instr.arg1
                    const_val1 = constants[instr.arg1]
                    instr.arg1 = const_val1
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var1}",
                        after=f"{const_val1}",
                        explanation=f"Replaced left operand variable '{orig_var1}' with known constant value '{const_val1}' in binary operation for '{instr.result}'.",
                        affected_target=instr.result
                    )
                if isinstance(instr.arg2, str) and instr.arg2 in constants:
                    orig_var2 = instr.arg2
                    const_val2 = constants[instr.arg2]
                    instr.arg2 = const_val2
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var2}",
                        after=f"{const_val2}",
                        explanation=f"Replaced right operand variable '{orig_var2}' with known constant value '{const_val2}' in binary operation for '{instr.result}'.",
                        affected_target=instr.result
                    )
                
                if instr.result in constants:
                    del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, Unary):
                if isinstance(instr.arg1, str) and instr.arg1 in constants:
                    orig_var = instr.arg1
                    const_val = constants[instr.arg1]
                    instr.arg1 = const_val
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var}",
                        after=f"{const_val}",
                        explanation=f"Replaced operand variable '{orig_var}' with known constant value '{const_val}' in unary operation for '{instr.result}'.",
                        affected_target=instr.result
                    )
                
                if instr.result in constants:
                    del constants[instr.result]
                result.append(instr)
                
            elif isinstance(instr, ConditionalJump):
                if isinstance(instr.condition, str) and instr.condition in constants:
                    orig_var = instr.condition
                    const_val = constants[instr.condition]
                    instr.condition = const_val
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var}",
                        after=f"{const_val}",
                        explanation=f"Replaced branch condition variable '{orig_var}' with known constant value '{const_val}'.",
                        affected_target=None
                    )
                result.append(instr)
                constants.clear()
                
            elif isinstance(instr, Goto):
                result.append(instr)
                constants.clear()
                
            elif isinstance(instr, Print):
                if isinstance(instr.value, str) and instr.value in constants:
                    orig_var = instr.value
                    const_val = constants[instr.value]
                    instr.value = const_val
                    self.stats.constant_propagations += 1
                    self.record_step(
                        pass_name="Constant Propagation",
                        rule="replace_known_constant",
                        before=f"{orig_var}",
                        after=f"{const_val}",
                        explanation=f"Replaced print argument variable '{orig_var}' with known constant value '{const_val}'.",
                        affected_target=None
                    )
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
                            folded_str = self.format_constant(res)
                            before_expr = f"{instr.arg1} {instr.op} {instr.arg2}"
                            self.record_step(
                                pass_name="Constant Folding",
                                rule="constant_binary_expression",
                                before=f"{instr.result} = {before_expr}",
                                after=f"{instr.result} = {folded_str}",
                                explanation=f"Both operands ({instr.arg1} and {instr.arg2}) are compile-time constants; evaluated '{before_expr}' to '{folded_str}' at compile time.",
                                affected_target=instr.result
                            )
                            result.append(Assignment(instr.result, folded_str))
                            continue
                    except Exception:
                        pass
                
                # Algebraic simplifications
                if instr.op == '+' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="add_zero_identity",
                        before=f"{instr.result} = {instr.arg1} + 0",
                        after=f"{instr.result} = {instr.arg1}",
                        explanation=f"Adding 0 to '{instr.arg1}' is an identity operation; simplified to '{instr.arg1}'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '+' and c1 and self.get_constant_value(instr.arg1) == 0:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="zero_add_identity",
                        before=f"{instr.result} = 0 + {instr.arg2}",
                        after=f"{instr.result} = {instr.arg2}",
                        explanation=f"Adding 0 to '{instr.arg2}' is an identity operation; simplified to '{instr.arg2}'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, instr.arg2))
                    continue
                if instr.op == '-' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="subtract_zero_identity",
                        before=f"{instr.result} = {instr.arg1} - 0",
                        after=f"{instr.result} = {instr.arg1}",
                        explanation=f"Subtracting 0 from '{instr.arg1}' is an identity operation; simplified to '{instr.arg1}'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '*' and c2 and self.get_constant_value(instr.arg2) == 1:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="multiply_by_one",
                        before=f"{instr.result} = {instr.arg1} * 1",
                        after=f"{instr.result} = {instr.arg1}",
                        explanation=f"Multiplying '{instr.arg1}' by 1 is an identity operation; simplified to '{instr.arg1}'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, instr.arg1))
                    continue
                if instr.op == '*' and c1 and self.get_constant_value(instr.arg1) == 1:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="one_multiplication_identity",
                        before=f"{instr.result} = 1 * {instr.arg2}",
                        after=f"{instr.result} = {instr.arg2}",
                        explanation=f"Multiplying 1 by '{instr.arg2}' is an identity operation; simplified to '{instr.arg2}'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, instr.arg2))
                    continue
                if instr.op == '*' and c2 and self.get_constant_value(instr.arg2) == 0:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="multiply_by_zero",
                        before=f"{instr.result} = {instr.arg1} * 0",
                        after=f"{instr.result} = 0",
                        explanation=f"Multiplying '{instr.arg1}' by 0 always yields 0; simplified to '0'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, "0"))
                    continue
                if instr.op == '*' and c1 and self.get_constant_value(instr.arg1) == 0:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="zero_multiplication",
                        before=f"{instr.result} = 0 * {instr.arg2}",
                        after=f"{instr.result} = 0",
                        explanation=f"Multiplying 0 by '{instr.arg2}' always yields 0; simplified to '0'.",
                        affected_target=instr.result
                    )
                    result.append(Assignment(instr.result, "0"))
                    continue
                if instr.op == '/' and c2 and self.get_constant_value(instr.arg2) == 1:
                    self.stats.algebraic_simplifications += 1
                    self.record_step(
                        pass_name="Algebraic Simplification",
                        rule="divide_by_one",
                        before=f"{instr.result} = {instr.arg1} / 1",
                        after=f"{instr.result} = {instr.arg1}",
                        explanation=f"Dividing '{instr.arg1}' by 1 is an identity operation; simplified to '{instr.arg1}'.",
                        affected_target=instr.result
                    )
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
                            folded_str = self.format_constant(res)
                            before_expr = f"{instr.op}{instr.arg1}"
                            self.record_step(
                                pass_name="Constant Folding",
                                rule="constant_unary_expression",
                                before=f"{instr.result} = {before_expr}",
                                after=f"{instr.result} = {folded_str}",
                                explanation=f"Unary operand '{instr.arg1}' is a compile-time constant; evaluated '{before_expr}' to '{folded_str}' at compile time.",
                                affected_target=instr.result
                            )
                            result.append(Assignment(instr.result, folded_str))
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
                    self.record_step(
                        pass_name="Dead Code Elimination",
                        rule="unused_temporary",
                        before=f"{str(instr)}",
                        after="<removed>",
                        explanation=f"Temporary variable '{instr.result}' is never read downstream in this scope; safely eliminated the assignment.",
                        affected_target=instr.result
                    )
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

        print("\n========== OPTIMIZATION EXPLANATION TRACE ==========\n")
        for step in optimizer.steps:
            print(f"[{step.step_number:02d}] {step.pass_name} ({step.rule}): {step.before} -> {step.after}")
            print(f"     Explanation: {step.explanation}")
            
    except (LexicalError, ParserError, SemanticError) as e:
        print(f"\n========== COMPILER ERROR ==========\n")
        print(f"✗ {e}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
