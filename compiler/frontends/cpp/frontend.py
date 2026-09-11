from typing import List, Dict, Any
from compiler.ast import nodes
from compiler.frontends.cpp.lexer import CPPLexer
from compiler.frontends.cpp.parser import CPPParser

class CPPFrontend:
    """
    Experimental C++ Frontend for CodeFlow.
    Tokenizes C++ source using CPPLexer and parses a controlled
    subset into unified CodeFlow AST nodes using CPPParser.
    """

    def __init__(self, source: str):
        self.source = source
        self.lexer = CPPLexer(source)
        self._tokens = None

    def tokenize(self) -> List[Dict[str, Any]]:
        """
        Tokenizes the C++ source code and returns serialized token dictionaries
        matching the format used across CodeFlow frontends.
        """
        if self._tokens is None:
            self._tokens = self.lexer.tokenize()
        return [tok.to_dict() for tok in self._tokens]

    def parse_to_codeflow_ast(self) -> nodes.Program:
        """
        Parses tokens into unified CodeFlow AST nodes.
        """
        if self._tokens is None:
            self._tokens = self.lexer.tokenize()
        parser = CPPParser(self._tokens)
        return parser.parse()
