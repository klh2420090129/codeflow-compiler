import pytest
from compiler.pipeline import compile_source
from compiler.frontends.javascript.lexer import JSLexer, JSTokenType
from compiler.frontends.javascript.parser import JSParser
from compiler.frontends.javascript.frontend import JSFrontend
from compiler.errors import LexicalError, ParserError, SemanticError

# ==============================================================================
# PHASE 8 & 9 TEST SUITE: JavaScript Frontend for CodeFlow
# Covers at least 20 targeted tests + Smoke Tests 1-5 + VM Trace Verification
# ==============================================================================

def test_js_let_declaration():
    """Test 1: let variable declaration and initialization"""
    code = "let a = 42; console.log(a);"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["42"]

def test_js_const_declaration():
    """Test 2: const variable declaration and initialization"""
    code = "const pi = 3.14; console.log(pi);"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["3.14"]

def test_js_const_reassignment_error():
    """Test 3: Attempting to reassign a const variable produces a semantic error"""
    code = "const MAX = 100; MAX = 200;"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert "Assignment to constant variable" in res.error["message"]
    assert res.error["phase"] == "semantic"

def test_js_assignment():
    """Test 4: Variable reassignment for let"""
    code = """
    let x = 10;
    x = 25;
    console.log(x);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["25"]

def test_js_arithmetic_operations():
    """Test 5: Arithmetic operators (+, -, *, /, %)"""
    code = """
    let a = 10 + 5;
    let b = a - 3;
    let c = b * 2;
    let d = c / 4;
    let e = d % 3;
    console.log(e);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_js_operator_precedence():
    """Test 6: Operator precedence (multiplication before addition)"""
    code = """
    let x = 2 + 3 * 4;
    console.log(x);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["14"]

def test_js_parentheses():
    """Test 7: Parentheses overriding operator precedence"""
    code = """
    let x = (2 + 3) * 4;
    console.log(x);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_js_unary_minus():
    """Test 8: Unary negation"""
    code = """
    let x = 42;
    let y = -x;
    console.log(y);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["-42"]

def test_js_logical_not():
    """Test 9: Unary logical NOT operator"""
    code = """
    let flag = false;
    let res = !flag;
    console.log(res);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["true"]

def test_js_comparisons():
    """Test 10: Comparison operators (<, <=, >, >=, ==, !=)"""
    code = """
    let a = 10;
    let b = 20;
    let c1 = a < b;
    let c2 = a <= 10;
    let c3 = b > a;
    let c4 = b >= 20;
    let c5 = a == 10;
    let c6 = a != b;
    console.log(c1);
    console.log(c2);
    console.log(c3);
    console.log(c4);
    console.log(c5);
    console.log(c6);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["true", "true", "true", "true", "true", "true"]

def test_js_logical_and():
    """Test 11: Logical AND operator"""
    code = """
    let a = true && true;
    let b = true && false;
    console.log(a);
    console.log(b);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_js_logical_or():
    """Test 12: Logical OR operator"""
    code = """
    let a = true || false;
    let b = false || false;
    console.log(a);
    console.log(b);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_js_if_statement():
    """Test 13: Single if statement (true condition)"""
    code = """
    let x = 10;
    if (x > 5) {
        console.log(999);
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["999"]

def test_js_if_else_statement():
    """Test 14: if/else branching"""
    code = """
    let x = 5;
    if (x > 10) {
        console.log(1);
    } else {
        console.log(2);
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["2"]

def test_js_while_loop():
    """Test 15: while loop iteration"""
    code = """
    let sum = 0;
    let i = 1;
    while (i <= 4) {
        sum = sum + i;
        i = i + 1;
    }
    console.log(sum);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_js_nested_blocks():
    """Test 16: Nested compound blocks"""
    code = """
    let a = 1;
    {
        let b = 2;
        console.log(a + b);
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["3"]

def test_js_console_log_expressions():
    """Test 17: console.log with complex expressions"""
    code = """
    let x = 7;
    let y = 3;
    console.log((x + y) * 2);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_js_comments_single_and_multi():
    """Test 18: Single-line and multi-line comments"""
    code = """
    // This is a single-line comment
    let x = 10; /* inline block comment */
    /*
       Multi-line
       block comment
    */
    console.log(x);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_js_undefined_variable_error():
    """Test 19: Referencing an undeclared/undefined variable produces a semantic error"""
    code = """
    let x = 10;
    console.log(unknown_var);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert "not declared" in res.error["message"]

def test_js_unsupported_keyword_function():
    """Test 20: Unsupported construct (function) raises explicit frontend error"""
    code = "function add(a, b) { return a + b; }"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert "function" in res.error["message"]

def test_js_unsupported_strict_equality():
    """Test 21: Strict equality '===' is explicitly rejected with helpful message"""
    code = "let x = 10 === 10;"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert "Strict equality" in res.error["message"]

def test_js_unsupported_arrow_function():
    """Test 22: Arrow function '=>' is explicitly rejected"""
    code = "const f = () => 42;"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert "Arrow functions" in res.error["message"]

def test_js_malformed_syntax_error():
    """Test 23: Malformed syntax produces a clear syntax error"""
    code = "let x = ;"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is False
    assert res.error is not None
    assert res.error["phase"] in ("syntax", "lexical")

def test_js_var_support():
    """Test 24: 'var' keyword works identically to 'let' in this subset"""
    code = "var num = 77; console.log(num);"
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["77"]


# ==============================================================================
# PHASE 9 & 10: Specific Smoke Tests & VM Trace Verification
# ==============================================================================

def test_smoke_1_arithmetic():
    """Smoke Test 1: let x = 10; let y = 20; let z = x + y * 2; console.log(z); -> 50"""
    code = """
    let x = 10;
    let y = 20;
    let z = x + y * 2;
    console.log(z);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["50"]

def test_smoke_2_if_else_true_branch():
    """Smoke Test 2: let x = 15; if (x > 10) { console.log(x); } else { console.log(0); } -> 15"""
    code = """
    let x = 15;
    if (x > 10) {
        console.log(x);
    } else {
        console.log(0);
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["15"]

def test_smoke_3_if_else_false_branch():
    """Smoke Test 3: let x = 5; if (x > 20) { console.log(x); } else { console.log(0); } -> 0"""
    code = """
    let x = 5;
    if (x > 20) {
        console.log(x);
    } else {
        console.log(0);
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_smoke_4_while_loop():
    """Smoke Test 4: let x = 0; while (x < 5) { console.log(x); x = x + 1; } -> 0, 1, 2, 3, 4"""
    code = """
    let x = 0;
    while (x < 5) {
        console.log(x);
        x = x + 1;
    }
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2", "3", "4"]

def test_smoke_5_optimization_constant_folding():
    """Smoke Test 5: let x = 10 + 20 * 2; console.log(x); -> 50 with optimizer constant folding"""
    code = """
    let x = 10 + 20 * 2;
    console.log(x);
    """
    res = compile_source(code, execute=True, language="javascript")
    assert res.success is True
    assert res.execution_output == ["50"]
    assert res.optimization_stats is not None
    # Verify optimizer performed constant folding or propagation
    assert res.optimization_stats.get("constant_folds", 0) > 0 or res.optimization_stats.get("constant_propagations", 0) > 0

def test_phase_10_vm_trace():
    """Phase 10: Verify while loop executes through the CodeFlow VM with real instructions"""
    code = """
    let x = 0;
    while (x < 5) {
        console.log(x);
        x = x + 1;
    }
    """
    res = compile_source(code, execute=True, trace=True, language="javascript")
    assert res.success is True
    assert res.execution_trace is not None
    assert len(res.execution_trace) > 0

    instructions = [entry["instruction"].split()[0] for entry in res.execution_trace]
    expected_opcodes = {"PUSH", "LOAD", "STORE", "CMP_LT", "JMP_IF_FALSE", "JMP", "PRINT"}
    for op in expected_opcodes:
        assert op in instructions, f"Expected opcode {op} in VM trace but got: {set(instructions)}"

def test_api_compile_javascript():
    """Verify Flask /api/compile works properly for JavaScript language"""
    from app import app
    client = app.test_client()

    res = client.post('/api/compile', json={"source": "let x = 77; console.log(x);", "language": "javascript"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["execution_output"] == ["77"]

    # Test unsupported construct returned with error structure
    res_err = client.post('/api/compile', json={"source": "function foo() {}", "language": "javascript"})
    assert res_err.status_code == 200
    data_err = res_err.get_json()
    assert data_err["success"] is False
    assert data_err["error"] is not None
    assert "function" in data_err["error"]["message"]
