from typing import List, Dict, Any
from compiler.ast import nodes
from compiler.frontends.java.lexer import JavaLexer
from compiler.frontends.java.parser import JavaParser

class JavaFrontend:
    """
    Experimental Java Frontend for CodeFlow.
    Tokenizes Java source using JavaLexer and parses a controlled
    subset into unified CodeFlow AST nodes using JavaParser.
    """

    def __init__(self, source: str):
        self.source = source
        self.lexer = JavaLexer(source)
        self._tokens = None

    def tokenize(self) -> List[Dict[str, Any]]:
        """
        Tokenizes the Java source code and returns serialized token dictionaries
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
        parser = JavaParser(self._tokens)
        return parser.parse()
