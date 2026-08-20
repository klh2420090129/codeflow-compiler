from dataclasses import dataclass
from typing import List, Optional, Any

class ASTNode:
    def to_dict(self) -> dict:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self._tree_str("").strip()
        
    def _tree_str(self, prefix: str) -> str:
        return f"{prefix}{self.__class__.__name__}\n"

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    
    def to_dict(self):
        return {"type": "Program", "statements": [s.to_dict() for s in self.statements]}

    def _tree_str(self, prefix: str) -> str:
        res = "Program\n"
        for i, stmt in enumerate(self.statements):
            is_last = (i == len(self.statements) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            res += f"{prefix}{connector}{stmt._tree_str(child_prefix)}"
        return res

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def to_dict(self):
        return {"type": "Block", "statements": [s.to_dict() for s in self.statements]}

    def _tree_str(self, prefix: str) -> str:
        res = "Block\n"
        for i, stmt in enumerate(self.statements):
            is_last = (i == len(self.statements) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            res += f"{prefix}{connector}{stmt._tree_str(child_prefix)}"
        return res

@dataclass
class Identifier(ASTNode):
    name: str

    def to_dict(self):
        return {"type": "Identifier", "name": self.name}
        
    def _tree_str(self, prefix: str) -> str:
        return f"Identifier: {self.name}\n"

@dataclass
class Literal(ASTNode):
    value: Any
    literal_type: str # 'INTEGER', 'FLOAT', 'BOOLEAN'

    def to_dict(self):
        return {"type": "Literal", "value": self.value, "literal_type": self.literal_type}

    def _tree_str(self, prefix: str) -> str:
        # Convert True/False to lowercase string if boolean for consistent output
        val_str = str(self.value).lower() if isinstance(self.value, bool) else str(self.value)
        return f"Literal: {val_str}\n"

@dataclass
class VariableDeclaration(ASTNode):
    name: Identifier
    initializer: ASTNode

    def to_dict(self):
        return {"type": "VariableDeclaration", "name": self.name.name, "initializer": self.initializer.to_dict()}
        
    def _tree_str(self, prefix: str) -> str:
        res = f"VariableDeclaration: {self.name.name}\n"
        res += f"{prefix}└── {self.initializer._tree_str(prefix + '    ')}"
        return res

@dataclass
class Assignment(ASTNode):
    name: Identifier
    value: ASTNode

    def to_dict(self):
        return {"type": "Assignment", "name": self.name.name, "value": self.value.to_dict()}

    def _tree_str(self, prefix: str) -> str:
        res = f"Assignment: {self.name.name}\n"
        res += f"{prefix}└── {self.value._tree_str(prefix + '    ')}"
        return res

@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode

    def to_dict(self):
        return {"type": "PrintStatement", "expression": self.expression.to_dict()}
        
    def _tree_str(self, prefix: str) -> str:
        res = f"PrintStatement\n"
        res += f"{prefix}└── {self.expression._tree_str(prefix + '    ')}"
        return res

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_block: Block
    else_block: Optional[Block]

    def to_dict(self):
        d = {"type": "IfStatement", "condition": self.condition.to_dict(), "then_block": self.then_block.to_dict()}
        if self.else_block:
            d["else_block"] = self.else_block.to_dict()
        return d
        
    def _tree_str(self, prefix: str) -> str:
        res = "IfStatement\n"
        res += f"{prefix}├── Condition\n"
        res += f"{prefix}│   └── {self.condition._tree_str(prefix + '│       ')}"
        
        if self.else_block:
            res += f"{prefix}├── Then\n"
            res += f"{prefix}│   └── {self.then_block._tree_str(prefix + '│       ')}"
            res += f"{prefix}└── Else\n"
            res += f"{prefix}    └── {self.else_block._tree_str(prefix + '        ')}"
        else:
            res += f"{prefix}└── Then\n"
            res += f"{prefix}    └── {self.then_block._tree_str(prefix + '        ')}"
        return res

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: Block

    def to_dict(self):
        return {"type": "WhileStatement", "condition": self.condition.to_dict(), "body": self.body.to_dict()}
        
    def _tree_str(self, prefix: str) -> str:
        res = "WhileStatement\n"
        res += f"{prefix}├── Condition\n"
        res += f"{prefix}│   └── {self.condition._tree_str(prefix + '│       ')}"
        res += f"{prefix}└── Body\n"
        res += f"{prefix}    └── {self.body._tree_str(prefix + '        ')}"
        return res

@dataclass
class BinaryExpression(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode

    def to_dict(self):
        return {"type": "BinaryExpression", "operator": self.operator, "left": self.left.to_dict(), "right": self.right.to_dict()}

    def _tree_str(self, prefix: str) -> str:
        res = f"BinaryExpression: {self.operator}\n"
        res += f"{prefix}├── {self.left._tree_str(prefix + '│   ')}"
        res += f"{prefix}└── {self.right._tree_str(prefix + '    ')}"
        return res

@dataclass
class UnaryExpression(ASTNode):
    operator: str
    right: ASTNode

    def to_dict(self):
        return {"type": "UnaryExpression", "operator": self.operator, "right": self.right.to_dict()}

    def _tree_str(self, prefix: str) -> str:
        res = f"UnaryExpression: {self.operator}\n"
        res += f"{prefix}└── {self.right._tree_str(prefix + '    ')}"
        return res
