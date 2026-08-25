import pytest
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.intermediate.tac import (
    TACGenerator, Assignment, Binary, Label, Goto, ConditionalJump, Print
)
from compiler.analysis.basic_blocks import BasicBlockAnalyzer, BasicBlock

def test_empty_instructions():
    analyzer = BasicBlockAnalyzer()
    blocks = analyzer.analyze([])
    assert blocks == []

def test_linear_basic_blocks():
    # Linear program with no jumps: only 1 basic block
    instrs = [
        Assignment("x", 10),
        Assignment("y", 20),
        Binary("t1", "x", "+", "y"),
        Print("t1")
    ]
    analyzer = BasicBlockAnalyzer()
    blocks = analyzer.analyze(instrs)
    
    assert len(blocks) == 1
    assert blocks[0].id == "B0"
    assert blocks[0].start_index == 0
    assert blocks[0].end_index == 3
    assert len(blocks[0].instructions) == 4

def test_if_else_basic_blocks():
    # TAC for: if (x > 5) { y = 1; } else { y = 2; }
    instrs = [
        Binary("t1", "x", ">", 5),            # 0: Leader (rule 1)
        ConditionalJump("t1", "L1", True),     # 1: Jump
        Assignment("y", 1),                   # 2: Leader (rule 3)
        Goto("L2"),                           # 3: Jump
        Label("L1"),                          # 4: Leader (rule 2)
        Assignment("y", 2),                   # 5
        Label("L2"),                          # 6: Leader (rule 2)
        Print("y")                            # 7
    ]
    analyzer = BasicBlockAnalyzer()
    blocks = analyzer.analyze(instrs)
    
    # Leaders should be: 0, 2, 4, 6
    assert len(blocks) == 4
    assert blocks[0].id == "B0"
    assert blocks[0].start_index == 0
    assert blocks[0].end_index == 1
    
    assert blocks[1].id == "B1"
    assert blocks[1].start_index == 2
    assert blocks[1].end_index == 3
    
    assert blocks[2].id == "B2"
    assert blocks[2].start_index == 4
    assert blocks[2].end_index == 5
    assert blocks[2].label == "L1"
    
    assert blocks[3].id == "B3"
    assert blocks[3].start_index == 6
    assert blocks[3].end_index == 7
    assert blocks[3].label == "L2"

def test_while_loop_basic_blocks():
    # TAC for: while (x < 5) { x = x + 1; }
    instrs = [
        Label("L1"),                          # 0: Leader (rule 1 & label)
        Binary("t1", "x", "<", 5),            # 1
        ConditionalJump("t1", "L2", True),     # 2: Jump
        Binary("t2", "x", "+", 1),            # 3: Leader (rule 3)
        Assignment("x", "t2"),                # 4
        Goto("L1"),                           # 5: Jump
        Label("L2"),                          # 6: Leader (rule 2 & 3)
        Print("x")                            # 7
    ]
    analyzer = BasicBlockAnalyzer()
    blocks = analyzer.analyze(instrs)
    
    # Leaders: 0, 3, 6
    assert len(blocks) == 3
    assert blocks[0].id == "B0"
    assert blocks[0].start_index == 0
    assert blocks[0].end_index == 2
    assert blocks[0].label == "L1"
    
    assert blocks[1].id == "B1"
    assert blocks[1].start_index == 3
    assert blocks[1].end_index == 5
    
    assert blocks[2].id == "B2"
    assert blocks[2].start_index == 6
    assert blocks[2].end_index == 7
    assert blocks[2].label == "L2"

def test_basic_block_serialization():
    instrs = [Assignment("x", 10), Print("x")]
    analyzer = BasicBlockAnalyzer()
    blocks = analyzer.analyze(instrs)
    d = blocks[0].to_dict()
    assert d["id"] == "B0"
    assert d["start_index"] == 0
    assert d["end_index"] == 1
    assert d["instructions"] == ["x = 10", "PRINT x"]
    assert d["successors"] == []
    assert d["predecessors"] == []
