import pytest
from compiler.intermediate.tac import (
    Assignment, Binary, Label, Goto, ConditionalJump, Print
)
from compiler.analysis.basic_blocks import BasicBlockAnalyzer
from compiler.analysis.cfg import CFGBuilder, ControlFlowGraph

def test_empty_cfg():
    builder = CFGBuilder()
    cfg = builder.build([])
    assert cfg.blocks == []
    assert cfg.edges == []
    assert cfg.entry_block is None
    assert cfg.exit_blocks == []

def test_linear_cfg():
    instrs = [
        Assignment("x", 10),
        Print("x")
    ]
    blocks = BasicBlockAnalyzer().analyze(instrs)
    cfg = CFGBuilder().build(blocks)
    
    assert len(cfg.blocks) == 1
    assert cfg.entry_block == "B0"
    assert cfg.exit_blocks == ["B0"]
    assert len(cfg.edges) == 0

def test_if_else_cfg():
    # TAC for: if (x > 5) { y = 1; } else { y = 2; }
    instrs = [
        Binary("t1", "x", ">", 5),            # 0 (B0)
        ConditionalJump("t1", "L1", True),     # 1 (B0) -> False edge to L1(B2), True edge fallthrough to B1
        Assignment("y", 1),                   # 2 (B1)
        Goto("L2"),                           # 3 (B1) -> Jump edge to L2(B3)
        Label("L1"),                          # 4 (B2)
        Assignment("y", 2),                   # 5 (B2) -> Fallthrough to B3
        Label("L2"),                          # 6 (B3)
        Print("y")                            # 7 (B3)
    ]
    blocks = BasicBlockAnalyzer().analyze(instrs)
    cfg = CFGBuilder().build(blocks)
    
    assert cfg.entry_block == "B0"
    assert cfg.exit_blocks == ["B3"]
    assert len(cfg.blocks) == 4
    
    # Check edges
    # B0 -> B2 (false branch)
    # B0 -> B1 (true branch)
    # B1 -> B3 (jump)
    # B2 -> B3 (fallthrough)
    edge_tuples = [(e.from_block, e.to_block, e.type) for e in cfg.edges]
    assert ("B0", "B2", "false") in edge_tuples
    assert ("B0", "B1", "true") in edge_tuples
    assert ("B1", "B3", "jump") in edge_tuples
    assert ("B2", "B3", "fallthrough") in edge_tuples
    
    # Check predecessors / successors
    b0 = [b for b in cfg.blocks if b.id == "B0"][0]
    b1 = [b for b in cfg.blocks if b.id == "B1"][0]
    b2 = [b for b in cfg.blocks if b.id == "B2"][0]
    b3 = [b for b in cfg.blocks if b.id == "B3"][0]
    
    assert set(b0.successors) == {"B1", "B2"}
    assert b0.predecessors == []
    
    assert set(b1.successors) == {"B3"}
    assert b1.predecessors == ["B0"]
    
    assert set(b2.successors) == {"B3"}
    assert b2.predecessors == ["B0"]
    
    assert b3.successors == []
    assert set(b3.predecessors) == {"B1", "B2"}

def test_while_loop_cfg():
    # TAC for: while (x < 5) { x = x + 1; }
    instrs = [
        Label("L1"),                          # 0 (B0)
        Binary("t1", "x", "<", 5),            # 1 (B0)
        ConditionalJump("t1", "L2", True),     # 2 (B0) -> false to L2(B2), true fallthrough to B1
        Binary("t2", "x", "+", 1),            # 3 (B1)
        Assignment("x", "t2"),                # 4 (B1)
        Goto("L1"),                           # 5 (B1) -> jump back to L1(B0)
        Label("L2"),                          # 6 (B2)
        Print("x")                            # 7 (B2)
    ]
    blocks = BasicBlockAnalyzer().analyze(instrs)
    cfg = CFGBuilder().build(blocks)
    
    assert cfg.entry_block == "B0"
    assert cfg.exit_blocks == ["B2"]
    
    edge_tuples = [(e.from_block, e.to_block, e.type) for e in cfg.edges]
    assert ("B0", "B2", "false") in edge_tuples
    assert ("B0", "B1", "true") in edge_tuples
    assert ("B1", "B0", "jump") in edge_tuples
    
    b0 = [b for b in cfg.blocks if b.id == "B0"][0]
    assert "B1" in b0.predecessors # loop back-edge

def test_cfg_serialization():
    instrs = [Assignment("x", 10), Print("x")]
    blocks = BasicBlockAnalyzer().analyze(instrs)
    cfg = CFGBuilder().build(blocks)
    d = cfg.to_dict()
    assert "blocks" in d
    assert "edges" in d
    assert d["entry"] == "B0"
    assert d["exits"] == ["B0"]
