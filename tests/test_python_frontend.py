import pytest
import io
import sys
from compiler.pipeline import compile_source
from compiler.frontends.python.frontend import PythonFrontend

# --- Phase 14 Required Tests ---

def test_python_arithmetic_and_precedence():
    """TEST 1: x = 10; y = 20; z = x + y * 2; print(z) -> 50"""
    source = """x = 10
y = 20
z = x + y * 2
print(z)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["50"]
    assert res.tokens is not None and len(res.tokens) > 0
    assert res.ast is not None
    assert res.symbol_table is not None
    assert res.tac is not None
    assert res.basic_blocks is not None
    assert res.cfg is not None
    assert res.optimized_tac is not None
    assert res.target_code is not None

def test_python_if_condition():
    """TEST 2: x = 10; if x > 5: print(x) -> 10"""
    source = """x = 10
if x > 5:
    print(x)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_python_if_else_condition():
    """TEST 3: x = 10; if x > 20: print(1); else: print(0) -> 0"""
    source = """x = 10
if x > 20:
    print(1)
else:
    print(0)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_python_while_loop():
    """TEST 4: x = 0; while x < 3: print(x); x = x + 1 -> 0, 1, 2"""
    source = """x = 0
while x < 3:
    print(x)
    x = x + 1"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2"]

def test_python_constant_folding_optimizer():
    """TEST 5: Constant folding opportunity in Python pipeline"""
    source = """a = 20 * 2
print(a)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["40"]
    # Verify optimizer actually operated on Python-generated TAC
    assert res.optimization_stats is not None
    assert res.optimization_stats.get("constant_folds", 0) >= 1
    step_rules = [step["rule"] for step in res.optimization_steps]
    assert "constant_binary_expression" in step_rules

def test_python_algebraic_simplification():
    """TEST 6: Algebraic simplification opportunity: x * 1, x + 0"""
    source = """x = 42
y = x * 1 + 0
print(y)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["42"]
    assert res.optimization_stats.get("algebraic_simplifications", 0) >= 1

def test_python_undefined_variable():
    """TEST 7: Undefined variable detection during semantic analysis"""
    source = """x = 10
y = x + unknown_var
print(y)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is False
    assert res.error is not None
    assert res.error["phase"] == "semantic"
    assert "unknown_var" in res.error["message"]

def test_python_unsupported_constructs():
    """TEST 8: Unsupported Python constructs fail gracefully with clear messages"""
    unsupported_cases = [
        ("def foo():\n    pass", "Function definitions"),
        ("class MyClass:\n    pass", "Class definitions"),
        ("import math", "Imports"),
        ("for i in range(5):\n    print(i)", "For-loops"),
        ("try:\n    x = 1\nexcept:\n    x = 2", "Exception handling"),
        ("x = [1, 2, 3]", "Data structures"),
        ("x = {'a': 1}", "Data structures"),
    ]
    for src, expected_msg_part in unsupported_cases:
        res = compile_source(src, execute=True, language="python")
        assert res.success is False
        assert res.error is not None
        assert expected_msg_part in res.error["message"]

def test_python_boolean_logic_and_comparisons():
    """Test logical and comparison operators (and, or, not, <=, >=, ==, !=)"""
    source = """flag = True
val = 15
if flag and not (val < 10) and val == 15:
    print(1)
else:
    print(0)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["1"]

def test_python_augmented_assignment():
    """Test x += 5 and x -= 2"""
    source = """x = 10
x += 5
x -= 3
print(x)"""
    res = compile_source(source, execute=True, language="python")
    assert res.success is True
    assert res.execution_output == ["12"]

def test_python_runtime_comparison():
    """PHASE 15: Compare CodeFlow VM output with actual Python execution for verification"""
    test_programs = [
        "x = 10\ny = 20\nprint(x + y * 2)",
        "x = 10\nif x > 5:\n    print(x)\nelse:\n    print(0)",
        "x = 0\nwhile x < 4:\n    print(x)\n    x = x + 1"
    ]
    for code in test_programs:
        # CodeFlow VM output
        cf_res = compile_source(code, execute=True, language="python")
        assert cf_res.success is True
        
        # Real Python output via stdout capture (for validation comparison only)
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        exec(code, {})
        sys.stdout = old_stdout
        py_output = [line for line in buffer.getvalue().strip().split('\n') if line]
        
        assert cf_res.execution_output == py_output

def test_api_compile_minilang_and_python():
    """Verify Flask /api/compile works properly for both MiniLang and Python"""
    from app import app
    client = app.test_client()

    # MiniLang (default)
    res1 = client.post('/api/compile', json={"source": "let a = 9; print(a);"})
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1["success"] is True
    assert data1["execution_output"] == ["9"]

    # Python
    res2 = client.post('/api/compile', json={"source": "a = 9\nprint(a)", "language": "python"})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["success"] is True
    assert data2["execution_output"] == ["9"]
