import pytest
from compiler.codegen.codegen import TargetProgram, TargetInstruction
from compiler.vm.virtual_machine import VirtualMachine
from compiler.errors import VMRuntimeError

def create_prog(instrs):
    tp = TargetProgram()
    for i in instrs: tp.append(i)
    return tp

def test_push():
    vm = VirtualMachine(create_prog([TargetInstruction("PUSH", 10), TargetInstruction("HALT")]))
    vm.run()
    assert vm.stack == [10]

def test_load_store():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10),
        TargetInstruction("STORE", "x"),
        TargetInstruction("LOAD", "x"),
        TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.memory["x"] == 10
    assert vm.stack == [10]

def test_undefined_variable():
    vm = VirtualMachine(create_prog([TargetInstruction("LOAD", "x"), TargetInstruction("HALT")]))
    with pytest.raises(VMRuntimeError, match="Undefined variable 'x'"):
        vm.run()

def test_arithmetic_add():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 20), TargetInstruction("ADD"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [30]

def test_arithmetic_sub():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 3), TargetInstruction("SUB"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [7]

def test_arithmetic_mul():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 3), TargetInstruction("MUL"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [30]

def test_arithmetic_div():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 2), TargetInstruction("DIV"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [5]

def test_arithmetic_mod():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 3), TargetInstruction("MOD"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [1]

def test_negation():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("NEG"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [-10]

def test_not():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", True), TargetInstruction("NOT"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [False]

def test_cmp_lt():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 20), TargetInstruction("CMP_LT"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [True]

def test_cmp_gt():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 20), TargetInstruction("CMP_GT"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [False]

def test_cmp_le():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 20), TargetInstruction("PUSH", 20), TargetInstruction("CMP_LE"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [True]

def test_cmp_ge():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 20), TargetInstruction("PUSH", 20), TargetInstruction("CMP_GE"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [True]

def test_cmp_eq():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 20), TargetInstruction("PUSH", 20), TargetInstruction("CMP_EQ"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [True]

def test_cmp_ne():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 20), TargetInstruction("PUSH", 20), TargetInstruction("CMP_NE"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [False]

def test_and():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", True), TargetInstruction("PUSH", False), TargetInstruction("AND"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [False]

def test_or():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", True), TargetInstruction("PUSH", False), TargetInstruction("OR"), TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [True]

def test_jmp():
    vm = VirtualMachine(create_prog([
        TargetInstruction("JMP", "L1"),
        TargetInstruction("PUSH", 10), # Should skip
        TargetInstruction("LABEL", "L1"),
        TargetInstruction("PUSH", 20),
        TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [20]

def test_jmp_if_false():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", False),
        TargetInstruction("JMP_IF_FALSE", "L1"),
        TargetInstruction("PUSH", 10),
        TargetInstruction("LABEL", "L1"),
        TargetInstruction("PUSH", 20),
        TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [20]

def test_jmp_if_true():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", True),
        TargetInstruction("JMP_IF_TRUE", "L1"),
        TargetInstruction("PUSH", 10),
        TargetInstruction("LABEL", "L1"),
        TargetInstruction("PUSH", 20),
        TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.stack == [20]

def test_print():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10),
        TargetInstruction("PRINT"),
        TargetInstruction("HALT")
    ]))
    vm.run()
    assert vm.get_output() == ["10"]
    assert len(vm.stack) == 0

def test_stack_underflow():
    vm = VirtualMachine(create_prog([TargetInstruction("ADD"), TargetInstruction("HALT")]))
    with pytest.raises(VMRuntimeError, match="Stack underflow while executing ADD"):
        vm.run()

def test_div_by_zero():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 0), TargetInstruction("DIV"), TargetInstruction("HALT")
    ]))
    with pytest.raises(VMRuntimeError, match="Division by zero"):
        vm.run()

def test_mod_by_zero():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("PUSH", 0), TargetInstruction("MOD"), TargetInstruction("HALT")
    ]))
    with pytest.raises(VMRuntimeError, match="Modulo by zero"):
        vm.run()

def test_invalid_jump():
    vm = VirtualMachine(create_prog([
        TargetInstruction("JMP", "L1"), TargetInstruction("HALT")
    ]))
    with pytest.raises(VMRuntimeError, match="Invalid jump target 'L1'"):
        vm.run()

def test_invalid_operand_type():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("NOT"), TargetInstruction("HALT")
    ]))
    with pytest.raises(VMRuntimeError, match="Expected boolean operand"):
        vm.run()

def test_execution_tracing():
    vm = VirtualMachine(create_prog([
        TargetInstruction("PUSH", 10), TargetInstruction("STORE", "x"), TargetInstruction("HALT")
    ]), trace=True)
    vm.run()
    assert len(vm.trace_log) == 3
    assert vm.trace_log[0].instruction == "PUSH 10"
    assert vm.trace_log[0].stack == []
    assert vm.trace_log[1].stack == [10]

# --- Integration Tests ---

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator
from compiler.optimizer.optimizer import Optimizer
from compiler.codegen.codegen import CodeGenerator

def run_pipeline(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    SemanticAnalyzer().analyze(ast)
    tac = TACGenerator().generate(ast)
    opt = Optimizer().optimize(tac)
    target = CodeGenerator().generate(opt)
    vm = VirtualMachine(target)
    vm.run()
    return vm.get_output()

def test_integration_arithmetic():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    assert run_pipeline(source) == ["50"]

def test_integration_if():
    source = "let x = 10; if (x > 5) { print(x); }"
    assert run_pipeline(source) == ["10"]

def test_integration_while():
    source = "let x = 0; while (x < 5) { print(x); x = x + 1; }"
    assert run_pipeline(source) == ["0", "1", "2", "3", "4"]

def test_integration_if_else():
    source = "let x = 10; if (x < 5) { print(1); } else { print(2); }"
    assert run_pipeline(source) == ["2"]
