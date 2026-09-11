from typing import List, Dict, Any
from compiler.ast import nodes
from compiler.frontends.javascript.lexer import JSLexer
from compiler.frontends.javascript.parser import JSParser

class JSFrontend:
    """
    Experimental JavaScript Frontend for CodeFlow.
    Tokenizes JavaScript source using JSLexer and parses a controlled
    subset into unified CodeFlow AST nodes using JSParser.
    """

    def __init__(self, source: str):
        self.source = source
        self.lexer = JSLexer(source)
        self._tokens = None

    def tokenize(self) -> List[Dict[str, Any]]:
        """
        Tokenizes the JavaScript source code and returns serialized token dictionaries
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
        parser = JSParser(self._tokens)
        return parser.parse()
