import pytest
from compiler.pipeline import compile_source

# Helper format strings
FMT_D = '"%d\\n"'
FMT_F = '"%f\\n"'

# --- C Frontend Test Suite (Phase 5) ---

def test_c_simple_declaration():
    """Test 1: Simple uninitialized declaration (int x; int y;)"""
    source = "int x;\nint y;\nx = 5;\ny = x * 2;\nprintf(" + FMT_D + ", y);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_c_declaration_with_initialization():
    """Test 2: Declaration with initialization (int x = 10; float y = 2.5;)"""
    source = "int x = 10;\nfloat y = 2.5;\nprintf(" + FMT_D + ", x);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_c_assignment():
    """Test 3: Variable reassignment without type keyword"""
    source = "int a = 5;\na = a + 7;\na = a * 2;\nprintf(" + FMT_D + ", a);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["24"]

def test_c_arithmetic_precedence():
    """Test 4: Arithmetic operator precedence (* before +, / before -)"""
    source = "int res = 10 + 20 * 2 - 8 / 4;\nprintf(" + FMT_D + ", res);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    # 10 + 40 - 2 = 48
    assert res.execution_output == ["48"]

def test_c_parenthesized_expressions():
    """Test 5: Parentheses overriding precedence"""
    source = "int val = (10 + 20) * (5 - 3);\nprintf(" + FMT_D + ", val);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["60"]

def test_c_comparisons():
    """Test 6: Relational comparisons (<, >, <=, >=, ==, !=)"""
    source = """
    int x = 10;
    int y = 20;
    if (x < y) {
        printf(""" + FMT_D + """, 1);
    } else {
        printf(""" + FMT_D + """, 0);
    }
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["1"]

def test_c_if_statement():
    """Test 7: if statement without else"""
    source = "int x = 10;\nif (x > 5) {\n    printf(" + FMT_D + ", x);\n}"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_c_if_else_statement():
    """Test 8: if/else statement with false condition"""
    source = """
    int score = 45;
    if (score >= 50) {
        printf(""" + FMT_D + """, 1);
    } else {
        printf(""" + FMT_D + """, 0);
    }
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_c_while_loop():
    """Test 9: while loop execution"""
    source = """
    int i = 0;
    while (i < 4) {
        printf(""" + FMT_D + """, i);
        i = i + 1;
    }
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2", "3"]

def test_c_nested_blocks():
    """Test 10: Nested blocks and lexical scoping in C"""
    source = """
    int a = 1;
    {
        int b = 2;
        printf(""" + FMT_D + """, a + b);
    }
    printf(""" + FMT_D + """, a);
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["3", "1"]

def test_c_comments():
    """Test 11: Single-line (//) and multi-line (/* */) comments"""
    source = """
    // Leading comment
    int x = 10; // Inline line comment
    /* Multi-line
       block comment */
    int y = 20;
    /* Another single-line block comment */
    printf(""" + FMT_D + """, x + y);
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["30"]

def test_c_integer_output():
    """Test 12: Integer output via printf("%d\\n", ...)"""
    source = "int count = 100;\nprintf(" + FMT_D + ", count);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["100"]

def test_c_floating_point_output():
    """Test 13: Floating-point arithmetic and output via printf("%f\\n", ...)"""
    source = "float f1 = 2.5;\nfloat f2 = 1.25;\nprintf(" + FMT_F + ", f1 + f2);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["3.75"]

def test_c_undefined_variable_error():
    """Test 14: Semantic error on undefined variable"""
    source = "int x = y + 10;\nprintf(" + FMT_D + ", x);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is False
    assert res.error["phase"] == "semantic"
    assert "y" in res.error["message"]

def test_c_malformed_syntax_error():
    """Test 15: Syntax error on missing semicolon or malformed statement"""
    source = "int x = 10\nprintf(" + FMT_D + ", x);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is False
    assert res.error["phase"] == "syntax"

def test_c_unsupported_construct_errors():
    """Test 16: Explicit, readable rejection of unsupported C constructs"""
    cases = [
        ("#include <stdio.h>\nint x = 1;", "Preprocessor directives"),
        ("for (int i = 0; i < 5; i++) {}", "keyword 'for'"),
        ("switch (x) { case 1: break; }", "keyword 'switch'"),
        ("int* ptr = &x;", "Bitwise '&' or pointer"),
    ]
    for src, expected_msg_part in cases:
        res = compile_source(src, execute=True, language="c")
        assert res.success is False
        assert res.error is not None
        assert expected_msg_part in res.error["message"]

def test_c_unary_minus_and_not():
    """Test 18: Unary minus and logical NOT operators"""
    source = """
    int x = -10;
    int y = -x;
    printf(""" + FMT_D + """, y);
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_c_logical_operators():
    """Test 19: Logical operators (&&, ||, !)"""
    source = """
    int a = 5;
    int b = 10;
    if (!(a > 10) && (b == 10 || a == 0)) {
        printf(""" + FMT_D + """, 1);
    } else {
        printf(""" + FMT_D + """, 0);
    }
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["1"]

def test_c_multiple_variables():
    """Test 20: Program with multiple variables interacting"""
    source = """
    int a = 2;
    int b = 3;
    int c = 4;
    int total = a * b + c;
    printf(""" + FMT_D + """, total);
    """
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["10"]

# --- Integration Tests through Entire Pipeline (AST -> TAC -> CFG -> Optimizer -> VM) ---

def test_c_full_pipeline_verification():
    """Integration: Verify C program produces tokens, AST, symbol table, TAC, CFG, Optimizer, Bytecode, VM output"""
    source = "int x = 10;\nint y = 20;\nint z = x + y * 2;\nprintf(" + FMT_D + ", z);"
    res = compile_source(source, execute=True, trace=True, language="c")
    assert res.success is True
    assert res.tokens is not None and len(res.tokens) > 0
    assert res.ast is not None
    assert res.symbol_table is not None
    assert res.tac is not None and len(res.tac) > 0
    assert res.basic_blocks is not None and len(res.basic_blocks) > 0
    assert res.cfg is not None
    assert res.optimized_tac is not None
    assert res.target_code is not None and len(res.target_code) > 0
    assert res.execution_output == ["50"]
    assert res.execution_trace is not None and len(res.execution_trace) > 0

def test_c_optimizer_constant_folding():
    """Integration: Verify existing CodeFlow optimizer constant folds C arithmetic in TAC"""
    source = "int x = 10 + 20 * 2;\nprintf(" + FMT_D + ", x);"
    res = compile_source(source, execute=True, language="c")
    assert res.success is True
    assert res.execution_output == ["50"]
    assert res.optimization_stats is not None
    assert res.optimization_stats.get("constant_folds", 0) >= 1

def test_c_vm_trace_instruction_types():
    """Phase 7: Capture and verify VM trace contains expected opcodes (PUSH, LOAD, STORE, CMP, JMP, etc.)"""
    source = """
    int x = 0;
    while (x < 3) {
        printf(""" + FMT_D + """, x);
        x = x + 1;
    }
    """
    res = compile_source(source, execute=True, trace=True, language="c")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2"]
    assert res.execution_trace is not None
    opcodes = {t["instruction"].split()[0] for t in res.execution_trace}
    assert "PUSH" in opcodes
    assert "STORE" in opcodes
    assert "LOAD" in opcodes
    assert "PRINT" in opcodes
    assert any("CMP" in op for op in opcodes)
    assert any("JMP" in op for op in opcodes)

def test_api_compile_c_endpoint():
    """Phase 9: Verify Flask /api/compile accepts language='c'"""
    from app import app
    client = app.test_client()

    res = client.post('/api/compile', json={"source": "int a = 42;\nprintf(" + FMT_D + ", a);", "language": "c"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["execution_output"] == ["42"]
