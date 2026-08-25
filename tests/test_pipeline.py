import pytest
from compiler.pipeline import compile_source

def test_successful_compilation():
    source = "let x = 10; let y = 20; let z = x + y * 2; print(z);"
    res = compile_source(source, execute=True, trace=True)
    assert res.success is True
    assert res.tokens is not None
    assert res.ast is not None
    assert res.symbol_table is not None
    assert res.tac is not None
    assert res.basic_blocks is not None
    assert res.cfg is not None
    assert res.optimized_tac is not None
    assert res.target_code is not None
    assert res.execution_output == ["50"]
    assert res.execution_trace is not None
    assert res.error is None

def test_lexical_error():
    source = "let x = @;"
    res = compile_source(source)
    assert res.success is False
    assert res.error["phase"] == "lexical"
    assert res.tokens is None

def test_syntax_error():
    source = "let x = ;"
    res = compile_source(source)
    assert res.success is False
    assert res.error["phase"] == "syntax"
    assert res.tokens is not None
    assert res.ast is None

def test_semantic_error():
    source = "let x = 10; x = y;"
    res = compile_source(source)
    assert res.success is False
    assert res.error["phase"] == "semantic"
    assert res.ast is not None
    assert res.tac is None

def test_runtime_error():
    source = "let x = 10; print(x / 0);"
    res = compile_source(source, execute=True)
    assert res.success is False
    assert res.error["phase"] == "vm"
    assert res.target_code is not None

def test_execute_false():
    source = "let x = 10; print(x);"
    res = compile_source(source, execute=False)
    assert res.success is True
    assert res.execution_output is None
    assert res.basic_blocks is not None
    assert res.cfg is not None

def test_trace_false():
    source = "let x = 10; print(x);"
    res = compile_source(source, execute=True, trace=False)
    assert res.success is True
    assert res.execution_trace is None
    assert res.execution_output == ["10"]

def test_if_else():
    source = "let x = 10; if (x < 5) { print(1); } else { print(2); }"
    res = compile_source(source)
    assert res.success is True
    assert res.execution_output == ["2"]
    assert len(res.basic_blocks) == 4
    assert len(res.cfg["edges"]) == 4

def test_while():
    source = "let x = 0; while (x < 3) { print(x); x = x + 1; }"
    res = compile_source(source)
    assert res.success is True
    assert res.execution_output == ["0", "1", "2"]
    assert len(res.basic_blocks) == 4
    assert len(res.cfg["edges"]) == 4
