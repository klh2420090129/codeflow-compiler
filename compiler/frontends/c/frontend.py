from typing import List, Dict, Any
from compiler.frontends.c.lexer import CLexer, CToken
from compiler.frontends.c.parser import CParser
from compiler.ast import nodes

class CFrontend:
    """
    Experimental C Frontend for CodeFlow.
    Tokenizes C source using CLexer and parses it into CodeFlow AST nodes via CParser.
    """

    def __init__(self, source: str):
        self.source = source
        self.lexer = CLexer(source)
        self.tokens: List[CToken] = []

    def tokenize(self) -> List[Dict[str, Any]]:
        """Tokenizes the C source, returning serialized token dictionaries for the IDE."""
        self.tokens = self.lexer.tokenize()
        return [t.to_dict() for t in self.tokens]

    def parse_to_codeflow_ast(self) -> nodes.Program:
        """Parses the token stream into standard CodeFlow AST nodes."""
        if not self.tokens:
            self.tokens = self.lexer.tokenize()
        parser = CParser(self.tokens)
        return parser.parse()
