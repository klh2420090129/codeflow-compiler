import pytest
from compiler.pipeline import compile_source
from compiler.frontends.java.lexer import JavaLexer, JavaTokenType
from compiler.frontends.java.parser import JavaParser
from compiler.frontends.java.frontend import JavaFrontend
from compiler.errors import LexicalError, ParserError, SemanticError

# ==============================================================================
# PHASE 10 TEST SUITE: Java Frontend for CodeFlow (At least 25 tests)
# ==============================================================================

def test_java_standard_main_wrapper():
    """Test 1: Standard public class Main wrapper with public static void main"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 42;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["42"]

def test_java_int_declaration_and_default():
    """Test 2: int declaration with default initialization to 0"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_java_double_declaration():
    """Test 3: double variable declaration and initialization"""
    code = """
    public class Main {
        public static void main(String[] args) {
            double pi = 3.14;
            System.out.println(pi);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["3.14"]

def test_java_boolean_declaration():
    """Test 4: boolean variable declaration and output"""
    code = """
    public class Main {
        public static void main(String[] args) {
            boolean active = true;
            boolean inactive = false;
            System.out.println(active);
            System.out.println(inactive);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_java_initialization():
    """Test 5: Explicit variable initialization"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int a = 100;
            double b = 20.5;
            System.out.println(a);
            System.out.println(b);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["100", "20.5"]

def test_java_assignment():
    """Test 6: Variable reassignment"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            x = 25;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["25"]

def test_java_arithmetic():
    """Test 7: Arithmetic operations (+, -, *, /, %)"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int a = 10 + 5;
            int b = a - 3;
            int c = b * 2;
            int d = c / 4;
            int e = d % 3;
            System.out.println(e);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_java_operator_precedence():
    """Test 8: Operator precedence (* before +)"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 2 + 3 * 4;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["14"]

def test_java_parentheses():
    """Test 9: Parentheses overriding precedence"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = (2 + 3) * 4;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_java_unary_minus():
    """Test 10: Unary negation"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 42;
            int y = -x;
            System.out.println(y);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["-42"]

def test_java_logical_not():
    """Test 11: Logical NOT operator"""
    code = """
    public class Main {
        public static void main(String[] args) {
            boolean flag = false;
            boolean notFlag = !flag;
            System.out.println(notFlag);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["true"]

def test_java_comparisons():
    """Test 12: Relational and equality comparisons"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int a = 10;
            int b = 20;
            System.out.println(a < b);
            System.out.println(a <= 10);
            System.out.println(b > a);
            System.out.println(b >= 20);
            System.out.println(a == 10);
            System.out.println(a != b);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["true", "true", "true", "true", "true", "true"]

def test_java_logical_and():
    """Test 13: Logical AND operator"""
    code = """
    public class Main {
        public static void main(String[] args) {
            boolean a = true && true;
            boolean b = true && false;
            System.out.println(a);
            System.out.println(b);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_java_logical_or():
    """Test 14: Logical OR operator"""
    code = """
    public class Main {
        public static void main(String[] args) {
            boolean a = true || false;
            boolean b = false || false;
            System.out.println(a);
            System.out.println(b);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["true", "false"]

def test_java_if_statement():
    """Test 15: Single if statement"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            if (x > 5) {
                System.out.println(999);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["999"]

def test_java_if_else():
    """Test 16: if/else statement"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 5;
            if (x > 10) {
                System.out.println(1);
            } else {
                System.out.println(2);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["2"]

def test_java_else_if():
    """Test 17: else-if chain"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int score = 75;
            if (score >= 90) {
                System.out.println(1);
            } else if (score >= 70) {
                System.out.println(2);
            } else {
                System.out.println(3);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["2"]

def test_java_while_loop():
    """Test 18: while loop execution"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int sum = 0;
            int i = 1;
            while (i <= 4) {
                sum = sum + i;
                i = i + 1;
            }
            System.out.println(sum);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["10"]

def test_java_nested_blocks():
    """Test 19: Nested blocks"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int a = 10;
            {
                int b = 20;
                System.out.println(a + b);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["30"]

def test_java_system_out_println_expressions():
    """Test 20: System.out.println with compound expressions"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 7;
            int y = 3;
            System.out.println((x + y) * 2);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["20"]

def test_java_comments():
    """Test 21: Single-line and multi-line comments in Java"""
    code = """
    // Leading single line comment
    public class Main {
        /* Multi-line
           comment block */
        public static void main(String[] args) {
            int val = 123; // trailing comment
            System.out.println(val);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["123"]

def test_java_undefined_variable():
    """Test 22: Error on referencing undefined variable"""
    code = """
    public class Main {
        public static void main(String[] args) {
            System.out.println(unknownVar);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "not declared" in res.error["message"]

def test_java_duplicate_declaration():
    """Test 23: Duplicate variable declaration error in same scope"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            int x = 20;
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "already declared" in res.error["message"]

def test_java_type_mismatch():
    """Test 24: Type mismatch on incompatible assignment"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = true;
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "Type mismatch" in res.error["message"]

def test_java_unsupported_construct():
    """Test 25: Unsupported Java keywords produce explicit errors"""
    code = """
    public class Main {
        public static void main(String[] args) {
            for (int i = 0; i < 5; i++) {}
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "for" in res.error["message"]

def test_java_malformed_class_wrapper():
    """Test 26: Non-Main class name or malformed wrapper rejected"""
    code = """
    public class NotMain {
        public static void main(String[] args) {
            int x = 1;
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "Main" in res.error["message"]

def test_java_final_reassignment_error():
    """Test 27: final variable cannot be reassigned"""
    code = """
    public class Main {
        public static void main(String[] args) {
            final int MAX = 100;
            MAX = 200;
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is False
    assert res.error is not None
    assert "final variable" in res.error["message"]


# ==============================================================================
# PHASE 11 & 12: Smoke Tests 1-5, VM Trace Verification & API Tests
# ==============================================================================

def test_smoke_1_arithmetic():
    """Smoke Test 1: Arithmetic expression"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            int y = 20;
            int z = x + y * 2;

            System.out.println(z);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["50"]

def test_smoke_2_if_else_true_branch():
    """Smoke Test 2: if/else true branch"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 15;

            if (x > 10) {
                System.out.println(x);
            } else {
                System.out.println(0);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["15"]

def test_smoke_3_if_else_false_branch():
    """Smoke Test 3: if/else false branch"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 5;

            if (x > 20) {
                System.out.println(x);
            } else {
                System.out.println(0);
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["0"]

def test_smoke_4_while_loop():
    """Smoke Test 4: while loop iteration"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 0;

            while (x < 5) {
                System.out.println(x);
                x = x + 1;
            }
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["0", "1", "2", "3", "4"]

def test_smoke_5_optimization_constant_folding():
    """Smoke Test 5: Optimizer constant folding on Java program"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 10 + 20 * 2;
            System.out.println(x);
        }
    }
    """
    res = compile_source(code, execute=True, language="java")
    assert res.success is True
    assert res.execution_output == ["50"]
    assert res.optimization_stats is not None
    assert res.optimization_stats.get("constant_folds", 0) > 0 or res.optimization_stats.get("constant_propagations", 0) > 0

def test_phase_12_vm_trace():
    """Phase 12: Verify while loop executes through the CodeFlow VM with real instructions"""
    code = """
    public class Main {
        public static void main(String[] args) {
            int x = 0;

            while (x < 5) {
                System.out.println(x);
                x = x + 1;
            }
        }
    }
    """
    res = compile_source(code, execute=True, trace=True, language="java")
    assert res.success is True
    assert res.execution_trace is not None
    assert len(res.execution_trace) > 0

    instructions = [entry["instruction"].split()[0] for entry in res.execution_trace]
    expected_opcodes = {"PUSH", "LOAD", "STORE", "CMP_LT", "JMP_IF_FALSE", "JMP", "PRINT", "ADD", "HALT"}
    for op in expected_opcodes:
        assert op in instructions, f"Expected opcode {op} in VM trace but got: {set(instructions)}"

def test_api_compile_java():
    """Phase 14: Verify Flask /api/compile works properly for Java language"""
    from app import app
    client = app.test_client()

    code = "public class Main { public static void main(String[] args) { int num = 88; System.out.println(num); } }"
    res = client.post('/api/compile', json={"source": code, "language": "java"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["execution_output"] == ["88"]

    # Test error formatting
    err_code = "public class Main { public static void main(String[] args) { int x = true; } }"
    res_err = client.post('/api/compile', json={"source": err_code, "language": "java"})
    assert res_err.status_code == 200
    data_err = res_err.get_json()
    assert data_err["success"] is False
    assert data_err["error"] is not None
    assert "Type mismatch" in data_err["error"]["message"]
