class CompilerError(Exception):
    """Base class for all compiler errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")

class LexicalError(CompilerError):
    """Exception raised for lexical errors like invalid characters."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexical Error: {message}", line, column)

class ParserError(CompilerError):
    """Exception raised for syntax errors during parsing."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Syntax Error: {message}", line, column)

class SemanticError(CompilerError):
    """Exception raised for semantic errors like undefined variables or type mismatches."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(f"Semantic Error: {message}", line, column)

class VMRuntimeError(CompilerError):
    """Exception raised for runtime errors during VM execution."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(f"VM Runtime Error: {message}", line, column)
