import pytest
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.errors import ParserError
from compiler.ast import nodes

def get_ast(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def test_empty_program():
    ast = get_ast("")
    assert isinstance(ast, nodes.Program)
    assert len(ast.statements) == 0

def test_single_variable_declaration():
    ast = get_ast("let x = 10;")
    assert len(ast.statements) == 1
    decl = ast.statements[0]
    assert isinstance(decl, nodes.VariableDeclaration)
    assert decl.name.name == "x"
    assert isinstance(decl.initializer, nodes.Literal)
    assert decl.initializer.value == 10

def test_multiple_declarations():
    ast = get_ast("let x = 10;\nlet y = 20;")
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], nodes.VariableDeclaration)
    assert isinstance(ast.statements[1], nodes.VariableDeclaration)

def test_assignment():
    ast = get_ast("x = 30;")
    assert len(ast.statements) == 1
    assign = ast.statements[0]
    assert isinstance(assign, nodes.Assignment)
    assert assign.name.name == "x"
    assert assign.value.value == 30

def test_print():
    ast = get_ast("print(x);")
    assert len(ast.statements) == 1
    p = ast.statements[0]
    assert isinstance(p, nodes.PrintStatement)
    assert isinstance(p.expression, nodes.Identifier)
    assert p.expression.name == "x"

def test_arithmetic_expression():
    ast = get_ast("let z = x + y * 2;")
    decl = ast.statements[0]
    expr = decl.initializer
    assert isinstance(expr, nodes.BinaryExpression)
    assert expr.operator == "+"
    assert isinstance(expr.left, nodes.Identifier)
    assert expr.left.name == "x"
    assert isinstance(expr.right, nodes.BinaryExpression)
    assert expr.right.operator == "*"

def test_operator_precedence():
    # x + y * z -> x + (y * z)
    ast = get_ast("x = a + b * c;")
    expr = ast.statements[0].value
    assert expr.operator == "+"
    assert expr.right.operator == "*"

def test_parentheses():
    # (x + y) * z
    ast = get_ast("x = (a + b) * c;")
    expr = ast.statements[0].value
    assert expr.operator == "*"
    assert expr.left.operator == "+"

def test_unary_operator():
    ast = get_ast("x = !y;")
    expr = ast.statements[0].value
    assert isinstance(expr, nodes.UnaryExpression)
    assert expr.operator == "!"

def test_comparison():
    ast = get_ast("x = a < b;")
    expr = ast.statements[0].value
    assert expr.operator == "<"

def test_equality():
    ast = get_ast("x = a == b;")
    expr = ast.statements[0].value
    assert expr.operator == "=="

def test_logical_operators():
    ast = get_ast("x = a && b || c;")
    expr = ast.statements[0].value
    assert expr.operator == "||"
    assert expr.left.operator == "&&"

def test_if_statement():
    ast = get_ast("if (x > 0) { print(x); }")
    stmt = ast.statements[0]
    assert isinstance(stmt, nodes.IfStatement)
    assert stmt.else_block is None
    assert len(stmt.then_block.statements) == 1

def test_if_else_statement():
    ast = get_ast("if (x > 0) { print(x); } else { print(0); }")
    stmt = ast.statements[0]
    assert isinstance(stmt, nodes.IfStatement)
    assert stmt.else_block is not None
    assert len(stmt.else_block.statements) == 1

def test_while_loop():
    ast = get_ast("while (x < 10) { x = x + 1; }")
    stmt = ast.statements[0]
    assert isinstance(stmt, nodes.WhileStatement)
    assert len(stmt.body.statements) == 1

def test_nested_blocks():
    ast = get_ast("if (true) { if (false) { x = 1; } }")
    stmt = ast.statements[0]
    inner = stmt.then_block.statements[0]
    assert isinstance(inner, nodes.IfStatement)
    assert isinstance(inner.then_block.statements[0], nodes.Assignment)

def test_nested_expressions():
    ast = get_ast("x = a + b * (c - d) / e;")
    expr = ast.statements[0].value
    assert expr.operator == "+"
    assert expr.right.operator == "/"
    assert expr.right.left.operator == "*"
    assert expr.right.left.right.operator == "-"

def test_syntax_error_missing_semicolon():
    with pytest.raises(ParserError) as excinfo:
        get_ast("let x = 10")
    assert "Expected ';'" in str(excinfo.value)

def test_syntax_error_missing_parentheses():
    with pytest.raises(ParserError) as excinfo:
        get_ast("print x;")
    assert "Expected '('" in str(excinfo.value)

def test_syntax_error_missing_braces():
    with pytest.raises(ParserError) as excinfo:
        get_ast("if (x) print(x);")
    assert "Expected '{'" in str(excinfo.value)

def test_invalid_statement_start():
    with pytest.raises(ParserError) as excinfo:
        get_ast("= 10;")
    assert "Expected statement start" in str(excinfo.value)

def test_eof_handling():
    with pytest.raises(ParserError) as excinfo:
        get_ast("let x = ")
    assert "Expected expression" in str(excinfo.value)

def test_integration_test():
    source = "let x = 10;\nlet y = 20;\nlet z = x + y * 2;\nprint(z);"
    ast = get_ast(source)
    assert len(ast.statements) == 4
    
    decl_x = ast.statements[0]
    assert isinstance(decl_x, nodes.VariableDeclaration)
    assert decl_x.name.name == "x"
    assert decl_x.initializer.value == 10
    
    decl_y = ast.statements[1]
    assert isinstance(decl_y, nodes.VariableDeclaration)
    
    decl_z = ast.statements[2]
    assert isinstance(decl_z, nodes.VariableDeclaration)
    assert isinstance(decl_z.initializer, nodes.BinaryExpression)
    assert decl_z.initializer.operator == "+"
    assert decl_z.initializer.right.operator == "*"
    
    print_stmt = ast.statements[3]
    assert isinstance(print_stmt, nodes.PrintStatement)
    assert print_stmt.expression.name == "z"
