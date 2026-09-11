import pytest
from compiler.pipeline import compile_source
from compiler.frontends.cpp.lexer import CPPLexer, CPPTokenType
from compiler.frontends.cpp.parser import CPPParser
from compiler.frontends.cpp.frontend import CPPFrontend
from compiler.errors import LexicalError, ParserError, SemanticError

# ==============================================================================
# PHASE 10 TEST SUITE: C++ Frontend for CodeFlow (At least 25 tests)
# ==============================================================================

def test_cpp_main_wrapper():
    """Test 1: Standard canonical int main() wrapper"""
    code = """
    int main() {
        int x = 42;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["42"]

def test_cpp_int_declaration_and_default():
    """Test 2: int declaration with default initialization to 0"""
    code = """
    int main() {
        int x;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_cpp_double_declaration():
    """Test 3: double variable declaration and initialization"""
    code = """
    int main() {
        double pi = 3.14;
        std::cout << pi << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["3.14"]

def test_cpp_bool_declaration():
    """Test 4: bool variable declaration and output"""
    code = """
    int main() {
        bool flag1 = true;
        bool flag2 = false;
        std::cout << flag1 << std::endl;
        std::cout << flag2 << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_cpp_initialization():
    """Test 5: Explicit variable initialization"""
    code = """
    int main() {
        int a = 100;
        double b = 20.5;
        std::cout << a << std::endl;
        std::cout << b << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["100", "20.5"]

def test_cpp_assignment():
    """Test 6: Variable assignment and modification"""
    code = """
    int main() {
        int x = 10;
        x = 25;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["25"]

def test_cpp_arithmetic():
    """Test 7: Arithmetic operations (+, -, *, /, %)"""
    code = """
    int main() {
        int a = 10 + 5;
        int b = a - 3;
        int c = b * 2;
        int d = c / 4;
        int e = d % 3;
        std::cout << e << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_cpp_operator_precedence():
    """Test 8: Operator precedence (* before +)"""
    code = """
    int main() {
        int x = 2 + 3 * 4;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["14"]

def test_cpp_parentheses():
    """Test 9: Parentheses overriding precedence"""
    code = """
    int main() {
        int x = (2 + 3) * 4;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_cpp_unary_minus():
    """Test 10: Unary negation"""
    code = """
    int main() {
        int x = 42;
        int y = -x;
        std::cout << y << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["-42"]

def test_cpp_logical_not():
    """Test 11: Logical NOT operator"""
    code = """
    int main() {
        bool flag = false;
        bool notFlag = !flag;
        std::cout << notFlag << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["true"]

def test_cpp_comparisons():
    """Test 12: Comparison operators (<, <=, >, >=, ==, !=)"""
    code = """
    int main() {
        int a = 10;
        int b = 20;
        std::cout << (a < b) << std::endl;
        std::cout << (a <= 10) << std::endl;
        std::cout << (b > a) << std::endl;
        std::cout << (b >= 20) << std::endl;
        std::cout << (a == 10) << std::endl;
        std::cout << (a != b) << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["true", "true", "true", "true", "true", "true"]

def test_cpp_logical_and():
    """Test 13: Logical AND operator"""
    code = """
    int main() {
        bool a = true && true;
        bool b = true && false;
        std::cout << a << std::endl;
        std::cout << b << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_cpp_logical_or():
    """Test 14: Logical OR operator"""
    code = """
    int main() {
        bool a = true || false;
        bool b = false || false;
        std::cout << a << std::endl;
        std::cout << b << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_cpp_if_statement():
    """Test 15: Single if statement"""
    code = """
    int main() {
        int x = 10;
        if (x > 5) {
            std::cout << 999 << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["999"]

def test_cpp_if_else():
    """Test 16: if/else branching"""
    code = """
    int main() {
        int x = 5;
        if (x > 10) {
            std::cout << 1 << std::endl;
        } else {
            std::cout << 2 << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["2"]

def test_cpp_else_if():
    """Test 17: else-if chain"""
    code = """
    int main() {
        int score = 75;
        if (score >= 90) {
            std::cout << 1 << std::endl;
        } else if (score >= 70) {
            std::cout << 2 << std::endl;
        } else {
            std::cout << 3 << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["2"]

def test_cpp_while_loop():
    """Test 18: while loop execution"""
    code = """
    int main() {
        int sum = 0;
        int i = 1;
        while (i <= 4) {
            sum = sum + i;
            i = i + 1;
        }
        std::cout << sum << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_cpp_nested_blocks():
    """Test 19: Nested blocks in C++"""
    code = """
    int main() {
        int a = 10;
        {
            int b = 20;
            std::cout << a + b << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["30"]

def test_cpp_std_cout_expressions():
    """Test 20: std::cout with compound expressions"""
    code = """
    int main() {
        int x = 7;
        int y = 3;
        std::cout << (x + y) * 2 << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_cpp_comments():
    """Test 21: Single-line and multi-line comments"""
    code = """
    // Leading comment
    int main() {
        /* Multi-line
           comment block */
        int val = 123; // trailing comment
        std::cout << val << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["123"]

def test_cpp_undefined_variable():
    """Test 22: Error on referencing undefined variable"""
    code = """
    int main() {
        std::cout << unknownVar << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "not declared" in res.error["message"]

def test_cpp_duplicate_declaration():
    """Test 23: Duplicate declaration error in same scope"""
    code = """
    int main() {
        int x = 10;
        int x = 20;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "already declared" in res.error["message"]

def test_cpp_type_mismatch():
    """Test 24: Incompatible type assignment error"""
    code = """
    int main() {
        int x = true;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "Type mismatch" in res.error["message"]

def test_cpp_unsupported_preprocessor():
    """Test 25: Preprocessor directives like #include are explicitly rejected"""
    code = """
    #include <iostream>
    int main() {
        int x = 10;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "Preprocessor directives" in res.error["message"]

def test_cpp_unsupported_multiple_functions():
    """Test 26: User-defined functions are rejected"""
    code = """
    int foo() {
        return 10;
    }
    int main() {
        int x = foo();
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "User-defined functions are not supported" in res.error["message"]

def test_cpp_unsupported_class():
    """Test 27: Class keyword is rejected"""
    code = """
    class Person {
        int age;
    };
    int main() {}
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "class" in res.error["message"]

def test_cpp_unsupported_for_loop():
    """Test 28: For loop keyword is rejected"""
    code = """
    int main() {
        for (int i = 0; i < 5; i++) {}
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is False
    assert res.error is not None
    assert "for" in res.error["message"]


# ==============================================================================
# PHASE 11 & 12: Smoke Tests 1-5, VM Trace Verification & API Tests
# ==============================================================================

def test_smoke_1_arithmetic():
    """Smoke Test 1: Arithmetic expression"""
    code = """
    int main() {
        int x = 10;
        int y = 20;
        int z = x + y * 2;

        std::cout << z << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["50"]

def test_smoke_2_if_else_true_branch():
    """Smoke Test 2: if/else true branch"""
    code = """
    int main() {
        int x = 15;

        if (x > 10) {
            std::cout << x << std::endl;
        } else {
            std::cout << 0 << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["15"]

def test_smoke_3_if_else_false_branch():
    """Smoke Test 3: if/else false branch"""
    code = """
    int main() {
        int x = 5;

        if (x > 20) {
            std::cout << x << std::endl;
        } else {
            std::cout << 0 << std::endl;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_smoke_4_while_loop():
    """Smoke Test 4: while loop iteration"""
    code = """
    int main() {
        int x = 0;

        while (x < 5) {
            std::cout << x << std::endl;
            x = x + 1;
        }
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2", "3", "4"]

def test_smoke_5_optimization_constant_folding():
    """Smoke Test 5: Optimizer constant folding on C++ program"""
    code = """
    int main() {
        int x = 10 + 20 * 2;
        std::cout << x << std::endl;
    }
    """
    res = compile_source(code, execute=True, language="cpp")
    assert res.success is True
    assert res.execution_output == ["50"]
    assert res.optimization_stats is not None
    assert res.optimization_stats.get("constant_folds", 0) > 0 or res.optimization_stats.get("constant_propagations", 0) > 0

def test_phase_12_vm_trace():
    """Phase 12: Verify while loop executes through the CodeFlow VM with real instructions"""
    code = """
    int main() {
        int x = 0;

        while (x < 5) {
            std::cout << x << std::endl;
            x = x + 1;
        }
    }
    """
    res = compile_source(code, execute=True, trace=True, language="cpp")
    assert res.success is True
    assert res.execution_trace is not None
    assert len(res.execution_trace) > 0

    instructions = [entry["instruction"].split()[0] for entry in res.execution_trace]
    expected_opcodes = {"PUSH", "LOAD", "STORE", "CMP_LT", "JMP_IF_FALSE", "JMP", "PRINT", "ADD", "HALT"}
    for op in expected_opcodes:
        assert op in instructions, f"Expected opcode {op} in VM trace but got: {set(instructions)}"

def test_api_compile_cpp():
    """Phase 14: Verify Flask /api/compile works properly for C++ language"""
    from app import app
    client = app.test_client()

    code = "int main() { int num = 99; std::cout << num << std::endl; }"
    res = client.post('/api/compile', json={"source": code, "language": "cpp"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["execution_output"] == ["99"]

    # Test error reporting
    err_code = "#include <vector>\nint main() {}"
    res_err = client.post('/api/compile', json={"source": err_code, "language": "cpp"})
    assert res_err.status_code == 200
    data_err = res_err.get_json()
    assert data_err["success"] is False
    assert data_err["error"] is not None
    assert "Preprocessor directives" in data_err["error"]["message"]
