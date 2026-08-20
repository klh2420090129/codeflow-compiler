import pytest
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.errors import SemanticError

def analyze(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer

def test_valid_variable_declaration():
    analyzer = analyze("let x = 10;")
    assert analyzer.symbol_table.lookup("x") is not None

def test_duplicate_declaration():
    with pytest.raises(SemanticError, match="already declared"):
        analyze("let x = 10; let x = 20;")

def test_undefined_variable():
    with pytest.raises(SemanticError, match="not declared"):
        analyze("print(x);")

def test_valid_assignment():
    analyze("let x = 10; x = 20;")

def test_assignment_to_undefined_variable():
    with pytest.raises(SemanticError, match="not declared"):
        analyze("x = 10;")

def test_integer_type_inference():
    analyzer = analyze("let x = 10;")
    assert analyzer.symbol_table.lookup("x").type_name == "int"

def test_float_type_inference():
    analyzer = analyze("let x = 10.5;")
    assert analyzer.symbol_table.lookup("x").type_name == "float"

def test_boolean_type_inference():
    analyzer = analyze("let x = true;")
    assert analyzer.symbol_table.lookup("x").type_name == "bool"

def test_arithmetic_type_checking():
    analyzer = analyze("let x = 10 + 20.5;")
    assert analyzer.symbol_table.lookup("x").type_name == "float"

def test_logical_type_checking():
    analyzer = analyze("let x = true && false;")
    assert analyzer.symbol_table.lookup("x").type_name == "bool"

def test_comparison_type_checking():
    analyzer = analyze("let x = 10 < 20;")
    assert analyzer.symbol_table.lookup("x").type_name == "bool"

def test_equality_type_checking():
    analyzer = analyze("let x = 10 == 20;")
    assert analyzer.symbol_table.lookup("x").type_name == "bool"

def test_invalid_arithmetic_operands():
    with pytest.raises(SemanticError, match="cannot be applied"):
        analyze("let x = 10 + true;")

def test_invalid_logical_operands():
    with pytest.raises(SemanticError, match="cannot be applied"):
        analyze("let x = true && 10;")

def test_invalid_if_condition():
    with pytest.raises(SemanticError, match="evaluate to boolean"):
        analyze("if (10) { print(10); }")

def test_invalid_while_condition():
    with pytest.raises(SemanticError, match="evaluate to boolean"):
        analyze("while (10) { print(10); }")

def test_nested_scope():
    analyze("let x = 10; if (true) { let y = 20; }")

def test_outer_variable_accessible_from_inner_scope():
    analyze("let x = 10; if (true) { print(x); }")

def test_inner_variable_inaccessible_from_outer_scope():
    with pytest.raises(SemanticError, match="not declared"):
        analyze("if (true) { let x = 10; } print(x);")

def test_shadowing_behavior():
    # Inner x shadows outer x, which is allowed in nested scopes.
    analyze("let x = 10; if (true) { let x = 20; } print(x);")

def test_valid_if_else():
    analyze("if (true) { print(1); } else { print(0); }")

def test_valid_while():
    analyze("let x = 0; while (x < 10) { x = x + 1; }")

def test_print_expressions():
    analyze("let x = 10; print(x + 5);")

def test_complex_nested_expression():
    analyze("let x = 10; let y = 20.5; let z = (x + y) * 2 > 50 && true;")

def test_integration_valid_program():
    source = "let x = 10;\nlet y = 20;\nlet z = x + y * 2;\nif (z > 40) {\nprint(z);\n}"
    analyze(source)

def test_integration_invalid_program():
    with pytest.raises(SemanticError):
        analyze("let x = 10; if (x) { print(x); }")
