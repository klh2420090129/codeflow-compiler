import sys
import os
from typing import List, Dict, Any, Optional, Set

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compiler.intermediate.tac import (
    TACInstruction, Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
)

class BasicBlock:
    def __init__(self, block_id: str, instructions: List[TACInstruction], start_index: int, end_index: int, label: Optional[str] = None):
        self.id = block_id
        self.instructions = instructions
        self.start_index = start_index
        self.end_index = end_index
        self.label = label
        self.successors: List[str] = []
        self.predecessors: List[str] = []

    def __repr__(self) -> str:
        return f"BasicBlock(id={self.id}, start={self.start_index}, end={self.end_index}, label={self.label}, instrs={len(self.instructions)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "label": self.label,
            "instructions": [str(instr) for instr in self.instructions],
            "successors": list(self.successors),
            "predecessors": list(self.predecessors)
        }

class BasicBlockAnalyzer:
    """Partitions a linear list of TAC instructions into Basic Blocks using leader identification."""
    
    def __init__(self):
        pass

    def identify_leaders(self, instructions: List[TACInstruction]) -> List[int]:
        if not instructions:
            return []

        leaders: Set[int] = set()
        
        # Rule 1: The first instruction is a leader.
        leaders.add(0)

        # Build mapping from label name to instruction index
        label_to_index: Dict[str, int] = {}
        for idx, instr in enumerate(instructions):
            if isinstance(instr, Label):
                label_to_index[instr.name] = idx

        for idx, instr in enumerate(instructions):
            # Rule 2: Target of a jump is a leader.
            if isinstance(instr, (Goto, ConditionalJump)):
                target_label = instr.target
                if target_label in label_to_index:
                    leaders.add(label_to_index[target_label])
                
                # Rule 3: Instruction immediately following a jump is a leader.
                if idx + 1 < len(instructions):
                    leaders.add(idx + 1)
            elif isinstance(instr, Label):
                # Any explicit label in TAC marks the start of a target or block
                leaders.add(idx)

        return sorted(list(leaders))

    def analyze(self, instructions: List[TACInstruction]) -> List[BasicBlock]:
        if not instructions:
            return []

        leader_indices = self.identify_leaders(instructions)
        blocks: List[BasicBlock] = []

        for i, start_idx in enumerate(leader_indices):
            block_id = f"B{i}"
            if i + 1 < len(leader_indices):
                end_idx = leader_indices[i + 1] - 1
            else:
                end_idx = len(instructions) - 1

            block_instrs = instructions[start_idx:end_idx + 1]
            
            # Determine if the block starts with a label
            label_name = None
            if block_instrs and isinstance(block_instrs[0], Label):
                label_name = block_instrs[0].name

            block = BasicBlock(
                block_id=block_id,
                instructions=block_instrs,
                start_index=start_idx,
                end_index=end_idx,
                label=label_name
            )
            blocks.append(block)

        return blocks
