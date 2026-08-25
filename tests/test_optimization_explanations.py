import pytest
from compiler.optimizer.optimizer import Optimizer, OptimizationStep, OptimizationStats
from compiler.intermediate.tac import (
    Assignment, Binary, Unary, Print, Label, Goto, ConditionalJump
)
from compiler.pipeline import compile_source

def test_optimization_step_serialization():
    step = OptimizationStep(
        step_number=1,
        pass_name="Constant Folding",
        rule="constant_binary_expression",
        before="t1 = 10 + 20",
        after="t1 = 30",
        explanation="Both operands are compile-time constants.",
        affected_target="t1"
    )
    d = step.to_dict()
    assert d["step_number"] == 1
    assert d["pass_name"] == "Constant Folding"
    assert d["rule"] == "constant_binary_expression"
    assert d["before"] == "t1 = 10 + 20"
    assert d["after"] == "t1 = 30"
    assert d["explanation"] == "Both operands are compile-time constants."
    assert d["affected_target"] == "t1"

def test_constant_propagation_explanation():
    opt = Optimizer()
    instrs = [
        Assignment("x", 10),
        Assignment("y", "x")
    ]
    opt.optimize(instrs)
    
    assert opt.stats.constant_propagations == 1
    assert len(opt.steps) >= 1
    prop_steps = [s for s in opt.steps if s.pass_name == "Constant Propagation"]
    assert len(prop_steps) == 1
    step = prop_steps[0]
    assert step.rule == "replace_known_constant"
    assert step.before == "x"
    assert step.after == "10"
    assert "known compile-time constant" in step.explanation
    assert step.affected_target == "y"

def test_constant_folding_explanation():
    opt = Optimizer()
    instrs = [
        Binary("t1", 20, "*", 2),
        Print("t1")
    ]
    opt.optimize(instrs)
    
    assert opt.stats.constant_folds == 1
    fold_steps = [s for s in opt.steps if s.pass_name == "Constant Folding"]
    assert len(fold_steps) == 1
    step = fold_steps[0]
    assert step.rule == "constant_binary_expression"
    assert step.before == "t1 = 20 * 2"
    assert step.after == "t1 = 40"
    assert "compile-time constants" in step.explanation

def test_algebraic_simplification_explanation():
    opt = Optimizer()
    instrs = [
        Binary("t1", "x", "+", 0),
        Print("t1")
    ]
    opt.optimize(instrs)
    
    assert opt.stats.algebraic_simplifications == 1
    alg_steps = [s for s in opt.steps if s.pass_name == "Algebraic Simplification"]
    assert len(alg_steps) == 1
    step = alg_steps[0]
    assert step.rule == "add_zero_identity"
    assert step.before == "t1 = x + 0"
    assert step.after == "t1 = x"
    assert "identity operation" in step.explanation

def test_dead_code_elimination_explanation():
    opt = Optimizer()
    instrs = [
        Assignment("x", 10),
        Assignment("y", 20),
        Binary("t1", "y", "*", 2),
        Binary("t2", "x", "+", "t1"),
        Assignment("z", "t2"),
        Print("z")
    ]
    # In this pipeline, t1 and t2 fold into constant 50 for z, leaving t1 & t2 unused
    opt.optimize(instrs)
    
    assert opt.stats.dead_code_eliminations >= 1
    dce_steps = [s for s in opt.steps if s.pass_name == "Dead Code Elimination"]
    assert len(dce_steps) >= 1
    step = dce_steps[0]
    assert step.rule == "unused_temporary"
    assert step.after == "<removed>"
    assert "never read downstream" in step.explanation

def test_multiple_step_optimization_trace():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    res = compile_source(source, execute=True)
    
    assert res.success is True
    assert res.execution_output == ["50"]
    assert len(res.optimization_steps) >= 4
    
    # Check that steps have sequential step numbers
    step_nums = [s["step_number"] for s in res.optimization_steps]
    assert step_nums == list(range(1, len(res.optimization_steps) + 1))
    
    passes_recorded = set(s["pass_name"] for s in res.optimization_steps)
    assert "Constant Propagation" in passes_recorded
    assert "Constant Folding" in passes_recorded
    assert "Dead Code Elimination" in passes_recorded

def test_optimization_summary():
    opt = Optimizer()
    instrs = [
        Assignment("x", 10),
        Assignment("y", "x")
    ]
    optimized = opt.optimize(instrs)
    summary = opt.get_summary(len(instrs), len(optimized))
    
    assert summary["total_steps"] == len(opt.steps)
    assert summary["before_instruction_count"] == 2
    assert summary["after_instruction_count"] == 2
    assert summary["instructions_removed"] == 0
    assert summary["reduction_percentage"] == 0.0
    assert summary["passes"]["constant_propagation"] == 1

def test_instruction_reduction_calculation():
    opt = Optimizer()
    # 5 instructions before, 2 after (removal of dead temporaries)
    instrs = [
        Assignment("x", 10),
        Binary("t1", 5, "*", 2),
        Print("x")
    ]
    optimized = opt.optimize(instrs)
    summary = opt.get_summary(len(instrs), len(optimized))
    
    assert summary["before_instruction_count"] == 3
    assert summary["after_instruction_count"] == 2
    assert summary["instructions_removed"] == 1
    assert summary["reduction_percentage"] == 33.33

def test_pipeline_result_json_serialization():
    source = "let a = 15.5; let b = 4.5; let result = (a + b) * 10 / 2; print(result);"
    res = compile_source(source, execute=True)
    d = res.to_dict()
    
    assert "optimization_stats" in d
    assert "optimization_steps" in d
    assert "optimization_summary" in d
    assert isinstance(d["optimization_stats"], dict)
    assert isinstance(d["optimization_steps"], list)
    assert isinstance(d["optimization_summary"], dict)
    assert d["execution_output"] == ["100"]

def test_execution_semantics_unchanged():
    source = "let x = 0; while (x < 3) { print(x); x = x + 1; }"
    res = compile_source(source, execute=True)
    assert res.success is True
    assert res.execution_output == ["0", "1", "2"]
