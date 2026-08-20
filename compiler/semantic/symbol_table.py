from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class Symbol:
    name: str
    type_name: str
    initialized: bool

class Scope:
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, name: str, type_name: str, initialized: bool = True) -> Optional[Symbol]:
        if name in self.symbols:
            return None # Already defined in this scope
        symbol = Symbol(name, type_name, initialized)
        self.symbols[name] = symbol
        return symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("Global")
        self.current_scope = self.global_scope
        self.all_scopes: List[Scope] = [self.global_scope]
        self.block_counter = 0

    def enter_scope(self):
        self.block_counter += 1
        new_scope = Scope(f"Block {self.block_counter}", self.current_scope)
        self.all_scopes.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def define(self, name: str, type_name: str, initialized: bool = True) -> Optional[Symbol]:
        return self.current_scope.define(name, type_name, initialized)

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.current_scope.lookup(name)

    def display(self) -> str:
        res = "========== SYMBOL TABLE ==========\n"
        for scope in self.all_scopes:
            res += f"\nScope: {scope.name}\n\n"
            res += f"{'Name':<15} {'Type':<15} {'Initialized':<15}\n"
            res += "-" * 45 + "\n"
            if not scope.symbols:
                res += " (empty)\n"
            for name, symbol in scope.symbols.items():
                init_str = "yes" if symbol.initialized else "no"
                res += f"{name:<15} {symbol.type_name:<15} {init_str:<15}\n"
        return res
