import pytest
from compiler.intermediate.tac import Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
from compiler.codegen.codegen import CodeGenerator, TargetInstruction

def test_assignment_literal():
    cg = CodeGenerator()
    instrs = [Assignment("x", "10")]
    prog = cg.generate(instrs).to_list()
    assert len(prog) == 3 # PUSH 10, STORE x, HALT
    assert prog[0].opcode == "PUSH"
    assert prog[0].operand == 10
    assert prog[1].opcode == "STORE"
    assert prog[1].operand == "x"

def test_assignment_variable():
    cg = CodeGenerator()
    instrs = [Assignment("x", "y")]
    prog = cg.generate(instrs).to_list()
    assert prog[0].opcode == "LOAD"
    assert prog[0].operand == "y"
    assert prog[1].opcode == "STORE"
    assert prog[1].operand == "x"

def test_addition():
    cg = CodeGenerator()
    instrs = [Binary("t1", "x", "+", "y")]
    prog = cg.generate(instrs).to_list()
    assert len(prog) == 5 # LOAD x, LOAD y, ADD, STORE t1, HALT
    assert prog[0].opcode == "LOAD"
    assert prog[1].opcode == "LOAD"
    assert prog[2].opcode == "ADD"
    assert prog[3].opcode == "STORE"
    assert prog[3].operand == "t1"

def test_subtraction():
    prog = CodeGenerator().generate([Binary("t1", "x", "-", "y")]).to_list()
    assert prog[2].opcode == "SUB"

def test_multiplication():
    prog = CodeGenerator().generate([Binary("t1", "x", "*", "y")]).to_list()
    assert prog[2].opcode == "MUL"

def test_division():
    prog = CodeGenerator().generate([Binary("t1", "x", "/", "y")]).to_list()
    assert prog[2].opcode == "DIV"

def test_modulo():
    prog = CodeGenerator().generate([Binary("t1", "x", "%", "y")]).to_list()
    assert prog[2].opcode == "MOD"

def test_unary_negation():
    prog = CodeGenerator().generate([Unary("t1", "-", "x")]).to_list()
    assert prog[0].opcode == "LOAD"
    assert prog[1].opcode == "NEG"
    assert prog[2].opcode == "STORE"

def test_logical_not():
    prog = CodeGenerator().generate([Unary("t1", "!", "x")]).to_list()
    assert prog[1].opcode == "NOT"

def test_cmp_lt():
    prog = CodeGenerator().generate([Binary("t1", "x", "<", "y")]).to_list()
    assert prog[2].opcode == "CMP_LT"

def test_cmp_gt():
    prog = CodeGenerator().generate([Binary("t1", "x", ">", "y")]).to_list()
    assert prog[2].opcode == "CMP_GT"

def test_cmp_le():
    prog = CodeGenerator().generate([Binary("t1", "x", "<=", "y")]).to_list()
    assert prog[2].opcode == "CMP_LE"

def test_cmp_ge():
    prog = CodeGenerator().generate([Binary("t1", "x", ">=", "y")]).to_list()
    assert prog[2].opcode == "CMP_GE"

def test_cmp_eq():
    prog = CodeGenerator().generate([Binary("t1", "x", "==", "y")]).to_list()
    assert prog[2].opcode == "CMP_EQ"

def test_cmp_ne():
    prog = CodeGenerator().generate([Binary("t1", "x", "!=", "y")]).to_list()
    assert prog[2].opcode == "CMP_NE"

def test_and():
    prog = CodeGenerator().generate([Binary("t1", "x", "&&", "y")]).to_list()
    assert prog[2].opcode == "AND"

def test_or():
    prog = CodeGenerator().generate([Binary("t1", "x", "||", "y")]).to_list()
    assert prog[2].opcode == "OR"

def test_print_variable():
    prog = CodeGenerator().generate([Print("x")]).to_list()
    assert prog[0].opcode == "LOAD"
    assert prog[1].opcode == "PRINT"

def test_print_literal():
    prog = CodeGenerator().generate([Print("50")]).to_list()
    assert prog[0].opcode == "PUSH"
    assert prog[0].operand == 50
    assert prog[1].opcode == "PRINT"

def test_label():
    prog = CodeGenerator().generate([Label("L1")]).to_list()
    assert prog[0].opcode == "LABEL"
    assert prog[0].operand == "L1"

def test_goto():
    prog = CodeGenerator().generate([Goto("L1")]).to_list()
    assert prog[0].opcode == "JMP"
    assert prog[0].operand == "L1"

def test_if_false():
    prog = CodeGenerator().generate([ConditionalJump("t1", "L1", True)]).to_list()
    assert prog[0].opcode == "LOAD"
    assert prog[1].opcode == "JMP_IF_FALSE"
    assert prog[1].operand == "L1"

def test_if_true():
    prog = CodeGenerator().generate([ConditionalJump("t1", "L1", False)]).to_list()
    assert prog[1].opcode == "JMP_IF_TRUE"
    assert prog[1].operand == "L1"

def test_while_loop_tac():
    # L1: IF_FALSE t1 GOTO L2; PRINT x; GOTO L1; L2:
    instrs = [Label("L1"), ConditionalJump("t1", "L2", True), Print("x"), Goto("L1"), Label("L2")]
    prog = CodeGenerator().generate(instrs).to_list()
    assert prog[0].opcode == "LABEL"
    assert prog[1].opcode == "LOAD"
    assert prog[2].opcode == "JMP_IF_FALSE"
    assert prog[3].opcode == "LOAD"
    assert prog[4].opcode == "PRINT"
    assert prog[5].opcode == "JMP"
    assert prog[6].opcode == "LABEL"

def test_if_else_tac():
    instrs = [ConditionalJump("t1", "L1", True), Print("1"), Goto("L2"), Label("L1"), Print("2"), Label("L2")]
    prog = CodeGenerator().generate(instrs).to_list()
    # LOAD, JMP_IF_FALSE, PUSH, PRINT, JMP, LABEL, PUSH, PRINT, LABEL, HALT
    assert len(prog) == 10

def test_multiple_statements():
    instrs = [Assignment("x", "10"), Assignment("y", "20"), Print("x")]
    prog = CodeGenerator().generate(instrs).to_list()
    # PUSH, STORE, PUSH, STORE, LOAD, PRINT, HALT
    assert len(prog) == 7

def test_halt_generation():
    prog = CodeGenerator().generate([]).to_list()
    assert len(prog) == 1
    assert prog[0].opcode == "HALT"

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator
from compiler.optimizer.optimizer import Optimizer

def test_integration_codegen():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    tac_gen = TACGenerator()
    original_tac = tac_gen.generate(ast)
    optimizer = Optimizer()
    optimized_tac = optimizer.optimize(original_tac)
    
    codegen = CodeGenerator()
    target_prog = codegen.generate(optimized_tac).to_list()
    
    # optimized_tac is: x=10, y=20, z=50, PRINT 50
    # target_prog:
    # PUSH 10; STORE x; PUSH 20; STORE y; PUSH 50; STORE z; PUSH 50; PRINT; HALT
    assert len(target_prog) == 9
    assert target_prog[0].opcode == "PUSH"
    assert target_prog[0].operand == 10
    assert target_prog[-1].opcode == "HALT"
