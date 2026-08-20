import sys
import os
from typing import List, Dict, Any, Optional
import json

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.codegen.codegen import TargetInstruction, TargetProgram
from compiler.errors import VMRuntimeError

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator
from compiler.optimizer.optimizer import Optimizer
from compiler.codegen.codegen import CodeGenerator

class ExecutionTrace:
    def __init__(self, ip: int, instruction: str, stack: List[Any], memory: Dict[str, Any]):
        self.ip = ip
        self.instruction = instruction
        self.stack = list(stack)
        self.memory = dict(memory)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "instruction": self.instruction,
            "stack": self.stack,
            "memory": self.memory
        }
        
    def __str__(self):
        return f"IP={self.ip}\nInstruction: {self.instruction}\nStack: {self.stack}\nMemory: {self.memory}\n"

class VirtualMachine:
    def __init__(self, program: TargetProgram, trace: bool = False):
        self.program = program.to_list()
        self.stack: List[Any] = []
        self.memory: Dict[str, Any] = {}
        self.ip: int = 0
        self.labels: Dict[str, int] = {}
        self.output: List[str] = []
        self.halted: bool = False
        
        self.trace_enabled = trace
        self.trace_log: List[ExecutionTrace] = []
        
        self._build_label_table()
        
    def _build_label_table(self):
        for idx, instr in enumerate(self.program):
            if instr.opcode == "LABEL":
                self.labels[instr.operand] = idx

    def get_output(self) -> List[str]:
        return self.output
        
    def _pop(self) -> Any:
        if not self.stack:
            raise VMRuntimeError("Stack underflow.")
        return self.stack.pop()
        
    def _require_operands(self, count: int, instr: str):
        if len(self.stack) < count:
            raise VMRuntimeError(f"Stack underflow while executing {instr}.")

    def _require_boolean(self, val: Any) -> bool:
        if not isinstance(val, bool):
            raise VMRuntimeError(f"Expected boolean operand, got {type(val).__name__}.")
        return val
        
    def run(self):
        while not self.halted and self.ip < len(self.program):
            instr = self.program[self.ip]
            
            if self.trace_enabled:
                self.trace_log.append(ExecutionTrace(self.ip, str(instr), self.stack, self.memory))
                
            self._execute_instruction(instr)
            
            if instr.opcode not in ["JMP", "JMP_IF_FALSE", "JMP_IF_TRUE"]:
                self.ip += 1

    def _execute_instruction(self, instr: TargetInstruction):
        opcode = instr.opcode
        
        if opcode == "HALT":
            self.halted = True
            
        elif opcode == "PUSH":
            self.stack.append(instr.operand)
            
        elif opcode == "LOAD":
            if instr.operand not in self.memory:
                raise VMRuntimeError(f"Undefined variable '{instr.operand}'.")
            self.stack.append(self.memory[instr.operand])
            
        elif opcode == "STORE":
            val = self._pop()
            self.memory[instr.operand] = val
            
        elif opcode == "ADD":
            self._require_operands(2, "ADD")
            r = self._pop()
            l = self._pop()
            self.stack.append(l + r)
            
        elif opcode == "SUB":
            self._require_operands(2, "SUB")
            r = self._pop()
            l = self._pop()
            self.stack.append(l - r)
            
        elif opcode == "MUL":
            self._require_operands(2, "MUL")
            r = self._pop()
            l = self._pop()
            self.stack.append(l * r)
            
        elif opcode == "DIV":
            self._require_operands(2, "DIV")
            r = self._pop()
            l = self._pop()
            if r == 0:
                raise VMRuntimeError("Division by zero.")
            self.stack.append(l / r)
            
        elif opcode == "MOD":
            self._require_operands(2, "MOD")
            r = self._pop()
            l = self._pop()
            if r == 0:
                raise VMRuntimeError("Modulo by zero.")
            self.stack.append(l % r)
            
        elif opcode == "NEG":
            self._require_operands(1, "NEG")
            v = self._pop()
            self.stack.append(-v)
            
        elif opcode == "NOT":
            self._require_operands(1, "NOT")
            v = self._pop()
            self.stack.append(not self._require_boolean(v))
            
        elif opcode == "CMP_LT":
            self._require_operands(2, "CMP_LT")
            r = self._pop()
            l = self._pop()
            self.stack.append(l < r)
            
        elif opcode == "CMP_GT":
            self._require_operands(2, "CMP_GT")
            r = self._pop()
            l = self._pop()
            self.stack.append(l > r)
            
        elif opcode == "CMP_LE":
            self._require_operands(2, "CMP_LE")
            r = self._pop()
            l = self._pop()
            self.stack.append(l <= r)
            
        elif opcode == "CMP_GE":
            self._require_operands(2, "CMP_GE")
            r = self._pop()
            l = self._pop()
            self.stack.append(l >= r)
            
        elif opcode == "CMP_EQ":
            self._require_operands(2, "CMP_EQ")
            r = self._pop()
            l = self._pop()
            self.stack.append(l == r)
            
        elif opcode == "CMP_NE":
            self._require_operands(2, "CMP_NE")
            r = self._pop()
            l = self._pop()
            self.stack.append(l != r)
            
        elif opcode == "AND":
            self._require_operands(2, "AND")
            r = self._require_boolean(self._pop())
            l = self._require_boolean(self._pop())
            self.stack.append(l and r)
            
        elif opcode == "OR":
            self._require_operands(2, "OR")
            r = self._require_boolean(self._pop())
            l = self._require_boolean(self._pop())
            self.stack.append(l or r)
            
        elif opcode == "LABEL":
            pass # No op
            
        elif opcode == "JMP":
            if instr.operand not in self.labels:
                raise VMRuntimeError(f"Invalid jump target '{instr.operand}'.")
            self.ip = self.labels[instr.operand]
            
        elif opcode == "JMP_IF_FALSE":
            self._require_operands(1, "JMP_IF_FALSE")
            cond = self._require_boolean(self._pop())
            if not cond:
                if instr.operand not in self.labels:
                    raise VMRuntimeError(f"Invalid jump target '{instr.operand}'.")
                self.ip = self.labels[instr.operand]
            else:
                self.ip += 1
                
        elif opcode == "JMP_IF_TRUE":
            self._require_operands(1, "JMP_IF_TRUE")
            cond = self._require_boolean(self._pop())
            if cond:
                if instr.operand not in self.labels:
                    raise VMRuntimeError(f"Invalid jump target '{instr.operand}'.")
                self.ip = self.labels[instr.operand]
            else:
                self.ip += 1
                
        elif opcode == "PRINT":
            self._require_operands(1, "PRINT")
            val = self._pop()
            if isinstance(val, bool):
                val = str(val).lower()
            elif isinstance(val, float) and val.is_integer():
                val = int(val)
            self.output.append(str(val))
            
        else:
            raise VMRuntimeError(f"Unknown opcode '{opcode}'.")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python -m compiler.vm.virtual_machine <source_file>")
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
        
        vm = VirtualMachine(target_prog)
        vm.run()
        
        print("========== OPTIMIZED TAC ==========\n")
        for i in optimized_tac:
            print(i)
            
        print("\n========== TARGET CODE ==========\n")
        for i in target_prog.to_list():
            print(i)
            
        print("\n========== EXECUTION OUTPUT ==========\n")
        for line in vm.get_output():
            print(line)
            
    except Exception as e:
        print(f"\n========== COMPILER ERROR ==========\n")
        print(f"✗ {e}")
