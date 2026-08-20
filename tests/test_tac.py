import pytest
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator, Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print

def get_tac(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = TACGenerator()
    return generator.generate(ast)

def test_simple_assignment():
    instructions = get_tac("let x = 10;")
    assert len(instructions) == 1
    assert isinstance(instructions[0], Assignment)
    assert instructions[0].result == "x"
    assert instructions[0].arg1 == "10"

def test_arithmetic_expression():
    instructions = get_tac("let x = 10 + 20;")
    assert len(instructions) == 2
    assert isinstance(instructions[0], Binary)
    assert instructions[0].result == "t1"
    assert instructions[0].arg1 == "10"
    assert instructions[0].op == "+"
    assert instructions[0].arg2 == "20"
    assert isinstance(instructions[1], Assignment)
    assert instructions[1].result == "x"
    assert instructions[1].arg1 == "t1"

def test_operator_precedence():
    instructions = get_tac("let x = 1; let y = 2; let z = x + y * 2;")
    # Assignments for x and y + Binary + Binary + Assignment for z = 5 instructions
    assert len(instructions) == 5
    assert isinstance(instructions[2], Binary)
    assert instructions[2].op == "*"
    assert instructions[2].arg1 == "y"
    assert instructions[2].arg2 == "2"
    assert isinstance(instructions[3], Binary)
    assert instructions[3].op == "+"
    assert instructions[3].arg1 == "x"
    assert instructions[3].arg2 == instructions[2].result
    assert isinstance(instructions[4], Assignment)
    assert instructions[4].result == "z"
    assert instructions[4].arg1 == instructions[3].result

def test_parentheses():
    instructions = get_tac("let x = 1; let y = 2; let z = (x + y) * 2;")
    assert len(instructions) == 5
    assert isinstance(instructions[2], Binary)
    assert instructions[2].op == "+"
    assert isinstance(instructions[3], Binary)
    assert instructions[3].op == "*"
    assert instructions[3].arg1 == instructions[2].result
    assert instructions[3].arg2 == "2"

def test_nested_expressions():
    instructions = get_tac("let a = 1; let b = 2; let c = 3; let d = 4; let z = (a + b) / (c - d);")
    assert len(instructions) == 8 # 4 vars + 3 binary + 1 assign
    assert instructions[4].op == "+"
    assert instructions[5].op == "-"
    assert instructions[6].op == "/"
    assert instructions[6].arg1 == instructions[4].result
    assert instructions[6].arg2 == instructions[5].result

def test_variable_assignment():
    instructions = get_tac("let y = 5; let x = 10; x = y + 10;")
    assert len(instructions) == 4
    assert isinstance(instructions[2], Binary)
    assert instructions[2].arg1 == "y"
    assert instructions[2].arg2 == "10"
    assert isinstance(instructions[3], Assignment)
    assert instructions[3].result == "x"

def test_print_variable():
    instructions = get_tac("let x = 1; print(x);")
    assert len(instructions) == 2
    assert isinstance(instructions[1], Print)
    assert instructions[1].value == "x"

def test_print_expression():
    instructions = get_tac("let x = 1; let y = 2; print(x + y);")
    assert len(instructions) == 4
    assert isinstance(instructions[2], Binary)
    assert isinstance(instructions[3], Print)
    assert instructions[3].value == instructions[2].result

def test_comparison():
    instructions = get_tac("let x = 1; let y = 2; let r = x < y;")
    assert len(instructions) == 4
    assert isinstance(instructions[2], Binary)
    assert instructions[2].op == "<"

def test_logical_operators():
    instructions = get_tac("let x = true; let y = false; let r = x && y;")
    assert len(instructions) == 4
    assert isinstance(instructions[2], Binary)
    assert instructions[2].op == "&&"

def test_unary_operator():
    instructions = get_tac("let x = true; let r = !x;")
    assert len(instructions) == 3
    assert isinstance(instructions[1], Unary)
    assert instructions[1].op == "!"
    assert instructions[1].arg1 == "x"

def test_if():
    instructions = get_tac("let x = 20; if (x > 10) { print(x); }")
    assert len(instructions) == 5 # assign x, binary > , condjump, print, label
    assert isinstance(instructions[1], Binary)
    assert isinstance(instructions[2], ConditionalJump)
    assert instructions[2].condition == instructions[1].result
    assert instructions[2].jump_if_false is True
    assert isinstance(instructions[3], Print)
    assert isinstance(instructions[4], Label)
    assert instructions[4].name == instructions[2].target

def test_if_else():
    instructions = get_tac("let x = 20; if (x > 10) { print(x); } else { print(0); }")
    assert len(instructions) == 8
    assert isinstance(instructions[2], ConditionalJump)
    assert isinstance(instructions[4], Goto)
    assert isinstance(instructions[5], Label)
    assert instructions[5].name == instructions[2].target
    assert isinstance(instructions[7], Label)
    assert instructions[7].name == instructions[4].target

def test_while():
    instructions = get_tac("let x = 0; while (x < 10) { x = x + 1; }")
    assert len(instructions) == 8
    assert isinstance(instructions[1], Label)
    assert isinstance(instructions[2], Binary)
    assert isinstance(instructions[3], ConditionalJump)
    assert isinstance(instructions[6], Goto)
    assert instructions[6].target == instructions[1].name
    assert isinstance(instructions[7], Label)
    assert instructions[7].name == instructions[3].target

def test_nested_if():
    instructions = get_tac("let a = 1; let b = 1; if (a > 0) { if (b > 0) { print(1); } }")
    # assign a, assign b, a>0, IF_FALSE, b>0, IF_FALSE, print 1, L2, L1 = 9 instructions
    assert len(instructions) == 9

def test_nested_loops():
    instructions = get_tac("let i = 0; let j = 0; while (i < 5) { while (j < 5) { j = j + 1; } i = i + 1; }")
    labels = [type(instr) for instr in instructions].count(Label)
    assert labels == 4 # start/end for outer, start/end for inner

def test_temporary_generation():
    instructions = get_tac("let a = 1 + 2 + 3 + 4;")
    assert len(instructions) == 4
    assert instructions[0].result == "t1"
    assert instructions[1].result == "t2"
    assert instructions[2].result == "t3"

def test_label_generation():
    instructions = get_tac("let a = 0; let b = 0; if (a < 1) { print(1); } if (b < 2) { print(2); }")
    labels = [instr.name for instr in instructions if isinstance(instr, Label)]
    assert labels == ["L1", "L2"]

def test_multiple_statements():
    instructions = get_tac("let x = 1; let y = 2; print(x+y);")
    assert len(instructions) == 4

def test_empty_program():
    instructions = get_tac("")
    assert len(instructions) == 0

def test_integration_structured():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    instructions = get_tac(source)
    assert len(instructions) == 6
    assert isinstance(instructions[0], Assignment) # x = 10
    assert isinstance(instructions[1], Assignment) # y = 20
    assert isinstance(instructions[2], Binary) # t1 = y * 2
    assert isinstance(instructions[3], Binary) # t2 = x + t1
    assert isinstance(instructions[4], Assignment) # z = t2
    assert isinstance(instructions[5], Print) # PRINT z
