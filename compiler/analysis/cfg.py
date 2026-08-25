import sys
import os
from typing import List, Dict, Any, Optional

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.intermediate.tac import (
    TACInstruction, Label, Goto, ConditionalJump
)
from compiler.analysis.basic_blocks import BasicBlock, BasicBlockAnalyzer

class CFGEdge:
    def __init__(self, from_block: str, to_block: str, edge_type: str):
        self.from_block = from_block
        self.to_block = to_block
        self.type = edge_type  # "jump", "true", "false", "fallthrough"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_block,
            "to": self.to_block,
            "type": self.type
        }

    def __repr__(self) -> str:
        return f"CFGEdge({self.from_block} -> {self.to_block}, type='{self.type}')"

class ControlFlowGraph:
    def __init__(self, blocks: List[BasicBlock], edges: List[CFGEdge], entry_block: Optional[str], exit_blocks: List[str], label_map: Dict[str, str]):
        self.blocks = blocks
        self.edges = edges
        self.entry_block = entry_block
        self.exit_blocks = exit_blocks
        self.label_map = label_map

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blocks": [b.to_dict() for b in self.blocks],
            "edges": [e.to_dict() for e in self.edges],
            "entry": self.entry_block,
            "exits": list(self.exit_blocks),
            "label_map": dict(self.label_map)
        }

class CFGBuilder:
    """Constructs a Control Flow Graph from Basic Blocks."""

    def __init__(self):
        pass

    def build(self, blocks: List[BasicBlock]) -> ControlFlowGraph:
        if not blocks:
            return ControlFlowGraph(
                blocks=[],
                edges=[],
                entry_block=None,
                exit_blocks=[],
                label_map={}
            )

        # Map labels to containing block IDs
        label_to_block_id: Dict[str, str] = {}
        for block in blocks:
            for instr in block.instructions:
                if isinstance(instr, Label):
                    label_to_block_id[instr.name] = block.id

        edges: List[CFGEdge] = []

        for i, block in enumerate(blocks):
            if not block.instructions:
                # If block is empty, just fall through to next block if exists
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    edges.append(CFGEdge(block.id, next_block.id, "fallthrough"))
                    block.successors.append(next_block.id)
                continue

            last_instr = block.instructions[-1]

            if isinstance(last_instr, Goto):
                # Unconditional jump
                target_block_id = label_to_block_id.get(last_instr.target)
                if target_block_id:
                    edges.append(CFGEdge(block.id, target_block_id, "jump"))
                    if target_block_id not in block.successors:
                        block.successors.append(target_block_id)
                # Note: No fallthrough edge for unconditional jump

            elif isinstance(last_instr, ConditionalJump):
                # Conditional jump
                target_block_id = label_to_block_id.get(last_instr.target)
                branch_type = "false" if last_instr.jump_if_false else "true"
                other_type = "true" if last_instr.jump_if_false else "false"

                if target_block_id:
                    edges.append(CFGEdge(block.id, target_block_id, branch_type))
                    if target_block_id not in block.successors:
                        block.successors.append(target_block_id)

                # Fallthrough to the next sequential block
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    edges.append(CFGEdge(block.id, next_block.id, other_type))
                    if next_block.id not in block.successors:
                        block.successors.append(next_block.id)

            else:
                # Block ends without a jump: fallthrough to the next block if exists
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    edges.append(CFGEdge(block.id, next_block.id, "fallthrough"))
                    if next_block.id not in block.successors:
                        block.successors.append(next_block.id)

        # Derive predecessors from successors
        for block in blocks:
            block.predecessors = []

        block_map = {b.id: b for b in blocks}
        for block in blocks:
            for succ_id in block.successors:
                if succ_id in block_map:
                    succ_block = block_map[succ_id]
                    if block.id not in succ_block.predecessors:
                        succ_block.predecessors.append(block.id)

        entry_block = blocks[0].id if blocks else None
        exit_blocks = [b.id for b in blocks if len(b.successors) == 0]

        return ControlFlowGraph(
            blocks=blocks,
            edges=edges,
            entry_block=entry_block,
            exit_blocks=exit_blocks,
            label_map=label_to_block_id
        )
