import pytest
from compiler.intermediate.tac import Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
from compiler.optimizer.optimizer import Optimizer

def test_constant_folding_addition():
    opt = Optimizer()
    # t1 = 10 + 20
    instrs = [Binary("x", "10", "+", "20")]
    opt_instrs = opt.optimize(instrs)
    assert len(opt_instrs) == 1
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "30"
    assert opt.stats.constant_folds == 1

def test_constant_folding_subtraction():
    opt = Optimizer()
    instrs = [Binary("x", "20", "-", "5")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "15"

def test_constant_folding_multiplication():
    opt = Optimizer()
    instrs = [Binary("x", "10", "*", "2")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "20"

def test_constant_folding_division():
    opt = Optimizer()
    instrs = [Binary("x", "20", "/", "5")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "4" # or 4.0 if floating, our script returns float but format_constant drops .0

def test_constant_folding_modulo():
    opt = Optimizer()
    instrs = [Binary("x", "10", "%", "3")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "1"

def test_constant_comparison():
    opt = Optimizer()
    instrs = [Binary("x", "10", "<", "20")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "true"

def test_constant_boolean_operation():
    opt = Optimizer()
    instrs = [Binary("x", "true", "&&", "false")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "false"

def test_constant_propagation():
    opt = Optimizer()
    # x = 10; y = x
    instrs = [Assignment("x", "10"), Assignment("y", "x")]
    opt_instrs = opt.optimize(instrs)
    assert opt_instrs[1].arg1 == "10"
    assert opt.stats.constant_propagations == 1

def test_propagation_followed_by_folding():
    opt = Optimizer()
    # x = 10; y = x + 20 -> x = 10; y = 30
    instrs = [Assignment("x", "10"), Binary("y", "x", "+", "20")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[1], Assignment)
    assert opt_instrs[1].arg1 == "30"

def test_reassignment_invalidates_propagation():
    opt = Optimizer()
    # x = 10; x = 20; y = x  -> y = 20
    instrs = [Assignment("x", "10"), Assignment("x", "20"), Assignment("y", "x")]
    opt_instrs = opt.optimize(instrs)
    assert opt_instrs[2].arg1 == "20"

def test_algebraic_simplification_plus_0():
    opt = Optimizer()
    instrs = [Binary("x", "x", "+", "0")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "x"
    assert opt.stats.algebraic_simplifications == 1

def test_algebraic_simplification_mul_1():
    opt = Optimizer()
    instrs = [Binary("x", "x", "*", "1")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "x"

def test_algebraic_simplification_mul_0():
    opt = Optimizer()
    instrs = [Binary("x", "x", "*", "0")]
    opt_instrs = opt.optimize(instrs)
    assert isinstance(opt_instrs[0], Assignment)
    assert opt_instrs[0].arg1 == "0"

def test_dead_temporary_elimination():
    opt = Optimizer()
    # t1 = 10; t2 = 20; x = t2
    instrs = [Assignment("t1", "10"), Assignment("t2", "20"), Assignment("x", "t2")]
    opt_instrs = opt.optimize(instrs)
    # t1 is eliminated, t2 is eliminated because it gets folded via propagation into x = 20? 
    # Wait, t2 is propagated: x = 20. Then t2 is dead. So only x = 20 remains.
    assert len(opt_instrs) == 1
    assert opt_instrs[0].result == "x"
    assert opt_instrs[0].arg1 == "20"

def test_preserve_print():
    opt = Optimizer()
    instrs = [Assignment("x", "10"), Print("x")]
    opt_instrs = opt.optimize(instrs)
    assert len(opt_instrs) == 2
    assert isinstance(opt_instrs[1], Print)
    assert opt_instrs[1].value == "10" # propagated

def test_preserve_label_goto_condjump():
    opt = Optimizer()
    instrs = [Label("L1"), Goto("L2"), ConditionalJump("true", "L3")]
    opt_instrs = opt.optimize(instrs)
    assert len(opt_instrs) == 3
    assert isinstance(opt_instrs[0], Label)
    assert isinstance(opt_instrs[1], Goto)
    assert isinstance(opt_instrs[2], ConditionalJump)

def test_division_by_zero_handling():
    opt = Optimizer()
    instrs = [Binary("x", "10", "/", "0")]
    opt_instrs = opt.optimize(instrs)
    # Should not optimize, should leave as Binary to let runtime handle it
    assert isinstance(opt_instrs[0], Binary)
    assert opt_instrs[0].arg2 == "0"

def test_multiple_optimization_passes():
    opt = Optimizer()
    # x = 10; y = 20; t1 = x + y; z = t1
    # 1. prop: t1 = 10 + 20
    # 2. fold: t1 = 30
    # 3. prop: z = 30
    # 4. DCE: t1 is dead code
    instrs = [Assignment("x", "10"), Assignment("y", "20"), Binary("t1", "x", "+", "y"), Assignment("z", "t1")]
    opt_instrs = opt.optimize(instrs)
    assert len(opt_instrs) == 3
    assert opt_instrs[2].result == "z"
    assert opt_instrs[2].arg1 == "30"

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.intermediate.tac import TACGenerator

def test_integration_optimization():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = TACGenerator()
    original_tac = generator.generate(ast)
    
    opt = Optimizer()
    optimized_tac = opt.optimize(original_tac)
    
    # Original has 6 instructions: x=10, y=20, t1=y*2, t2=x+t1, z=t2, PRINT z
    # Optimized:
    # y*2 -> 20*2 = 40 (t1=40)
    # x+t1 -> 10+40 = 50 (t2=50)
    # z=t2 -> z=50
    # PRINT z -> PRINT 50
    # Then t1, t2 are eliminated
    assert len(optimized_tac) == 4
    assert isinstance(optimized_tac[0], Assignment) # x = 10
    assert isinstance(optimized_tac[1], Assignment) # y = 20
    assert isinstance(optimized_tac[2], Assignment) # z = 50
    assert isinstance(optimized_tac[3], Print)      # PRINT 50
    assert optimized_tac[3].value == "50"
