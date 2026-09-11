import ast
import tokenize
import io
from typing import List, Dict, Any, Tuple, Set, Optional

from compiler.ast import nodes
from compiler.errors import LexicalError, ParserError, SemanticError

class PythonFrontend:
    """
    Experimental Python Frontend for CodeFlow.
    Extracts tokens via Python's `tokenize` module and converts a supported
    Python AST subset into CodeFlow AST nodes (nodes.Program, nodes.Assignment, etc.)
    """

    def __init__(self, source: str):
        self.source = source
        self.declared_symbols: Set[str] = set()

    def tokenize(self) -> List[Dict[str, Any]]:
        """
        Tokenizes Python source using the standard `tokenize` module,
        returning serialized token dictionaries matching CodeFlow's token format.
        """
        tokens: List[Dict[str, Any]] = []
        try:
            reader = io.BytesIO(self.source.encode('utf-8')).readline
            raw_tokens = tokenize.tokenize(reader)
            
            for tok in raw_tokens:
                # Filter out encoding header and comment/nl/eof bookkeeping if empty
                if tok.type == tokenize.ENCODING:
                    continue
                if tok.type == tokenize.ENDMARKER:
                    tokens.append({
                        "type": "EOF",
                        "value": "<EOF>",
                        "line": tok.start[0],
                        "column": tok.start[1] + 1
                    })
                    break

                # Map token type to human-readable category
                tok_type_name = tokenize.tok_name.get(tok.type, "UNKNOWN")
                
                # Format string value nicely
                val = tok.string
                if val == "\n":
                    val = "\\n"

                tokens.append({
                    "type": tok_type_name,
                    "value": val,
                    "line": tok.start[0],
                    "column": tok.start[1] + 1
                })
                
            return tokens
        except tokenize.TokenError as e:
            msg, (line, col) = e.args
            raise LexicalError(f"Python Lexical Error: {msg}", line, col + 1)
        except Exception as e:
            raise LexicalError(f"Python Lexical Error: {str(e)}", 1, 1)

    def parse_to_codeflow_ast(self) -> nodes.Program:
        """
        Parses Python source using `ast.parse` and converts the supported subset
        into CodeFlow AST nodes.
        """
        try:
            py_ast = ast.parse(self.source)
        except SyntaxError as e:
            raise ParserError(f"Python Syntax Error: {e.msg}", e.lineno or 1, e.offset or 1)

        self.declared_symbols.clear()
        statements: List[nodes.ASTNode] = []
        
        for stmt in py_ast.body:
            cf_stmt = self._convert_statement(stmt)
            if isinstance(cf_stmt, list):
                statements.extend(cf_stmt)
            else:
                statements.append(cf_stmt)

        return nodes.Program(statements)

    def _convert_statement(self, stmt: ast.stmt) -> nodes.ASTNode:
        lineno = getattr(stmt, 'lineno', 1)
        col_offset = getattr(stmt, 'col_offset', 0) + 1

        if isinstance(stmt, ast.Assign):
            # Target must be a single identifier
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise ParserError("CodeFlow Python only supports assignment to a single variable name.", lineno, col_offset)
            
            var_name = stmt.targets[0].id
            expr_val = self._convert_expression(stmt.value)

            # In Python, variables are defined upon their first assignment.
            # In CodeFlow's semantic analyzer, a variable must first be declared with VariableDeclaration
            # before subsequent assignments.
            if var_name not in self.declared_symbols:
                self.declared_symbols.add(var_name)
                return nodes.VariableDeclaration(nodes.Identifier(var_name), expr_val)
            else:
                return nodes.Assignment(nodes.Identifier(var_name), expr_val)

        elif isinstance(stmt, ast.AugAssign):
            # e.g., x += 1 -> x = x + 1
            if not isinstance(stmt.target, ast.Name):
                raise ParserError("CodeFlow Python only supports augmented assignment to a variable name.", lineno, col_offset)
            var_name = stmt.target.id
            if var_name not in self.declared_symbols:
                raise SemanticError(f"Variable '{var_name}' is not declared.", lineno, col_offset)
            
            op_sym = self._convert_binop_operator(stmt.op, lineno, col_offset)
            rhs = self._convert_expression(stmt.value)
            bin_expr = nodes.BinaryExpression(op_sym, nodes.Identifier(var_name), rhs)
            return nodes.Assignment(nodes.Identifier(var_name), bin_expr)

        elif isinstance(stmt, ast.Expr):
            # Expression statements: only print(...) function calls are supported in CodeFlow
            if isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Name) and call.func.id == "print":
                    if len(call.args) != 1:
                        raise ParserError("CodeFlow Python print() currently expects exactly 1 argument.", lineno, col_offset)
                    arg_expr = self._convert_expression(call.args[0])
                    return nodes.PrintStatement(arg_expr)
                else:
                    func_name = call.func.id if isinstance(call.func, ast.Name) else "function"
                    raise ParserError(f"Unsupported function call '{func_name}()'. Only print() is supported in this subset.", lineno, col_offset)
            else:
                raise ParserError("Standalone expressions other than print(...) are not supported as statements.", lineno, col_offset)

        elif isinstance(stmt, ast.If):
            cond = self._convert_expression(stmt.test)
            
            then_stmts: List[nodes.ASTNode] = []
            for s in stmt.body:
                conv = self._convert_statement(s)
                if isinstance(conv, list):
                    then_stmts.extend(conv)
                else:
                    then_stmts.append(conv)
            then_block = nodes.Block(then_stmts)

            else_block: Optional[nodes.Block] = None
            if stmt.orelse:
                else_stmts: List[nodes.ASTNode] = []
                for s in stmt.orelse:
                    conv = self._convert_statement(s)
                    if isinstance(conv, list):
                        else_stmts.extend(conv)
                    else:
                        else_stmts.append(conv)
                else_block = nodes.Block(else_stmts)

            return nodes.IfStatement(cond, then_block, else_block)

        elif isinstance(stmt, ast.While):
            cond = self._convert_expression(stmt.test)
            body_stmts: List[nodes.ASTNode] = []
            for s in stmt.body:
                conv = self._convert_statement(s)
                if isinstance(conv, list):
                    body_stmts.extend(conv)
                else:
                    body_stmts.append(conv)
            body_block = nodes.Block(body_stmts)
            return nodes.WhileStatement(cond, body_block)

        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ParserError("Function definitions ('def') are not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(stmt, ast.ClassDef):
            raise ParserError("Class definitions ('class') are not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
            raise ParserError("Imports ('import', 'from') are not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(stmt, ast.For):
            raise ParserError("For-loops are not currently supported in the CodeFlow Python subset. Please use 'while'.", lineno, col_offset)
        elif isinstance(stmt, (ast.Try, ast.TryStar, ast.Raise)):
            raise ParserError("Exception handling ('try/except/raise') is not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(stmt, ast.Pass):
            # Return empty block or no-op assignment if needed, or error
            return nodes.Block([])
        else:
            stmt_type = type(stmt).__name__
            raise ParserError(f"Unsupported Python statement '{stmt_type}'.", lineno, col_offset)

    def _convert_expression(self, expr: ast.expr) -> nodes.ASTNode:
        lineno = getattr(expr, 'lineno', 1)
        col_offset = getattr(expr, 'col_offset', 0) + 1

        if isinstance(expr, ast.Constant):
            val = expr.value
            if isinstance(val, bool):
                return nodes.Literal(val, "BOOLEAN")
            elif isinstance(val, int):
                return nodes.Literal(val, "INTEGER")
            elif isinstance(val, float):
                return nodes.Literal(val, "FLOAT")
            else:
                raise ParserError(f"Unsupported literal type '{type(val).__name__}'. Only int, float, and bool are supported.", lineno, col_offset)

        elif isinstance(expr, ast.Name):
            return nodes.Identifier(expr.id)

        elif isinstance(expr, ast.BinOp):
            left = self._convert_expression(expr.left)
            right = self._convert_expression(expr.right)
            op = self._convert_binop_operator(expr.op, lineno, col_offset)
            return nodes.BinaryExpression(op, left, right)

        elif isinstance(expr, ast.UnaryOp):
            right = self._convert_expression(expr.operand)
            if isinstance(expr.op, ast.USub):
                return nodes.UnaryExpression("-", right)
            elif isinstance(expr.op, ast.Not):
                return nodes.UnaryExpression("!", right)
            elif isinstance(expr.op, ast.UAdd):
                # +x is just x
                return right
            else:
                raise ParserError(f"Unsupported unary operator '{type(expr.op).__name__}'.", lineno, col_offset)

        elif isinstance(expr, ast.Compare):
            if len(expr.ops) != 1 or len(expr.comparators) != 1:
                raise ParserError("Chained comparisons (e.g. 1 < x < 10) are not supported. Use 'and'.", lineno, col_offset)
            left = self._convert_expression(expr.left)
            right = self._convert_expression(expr.comparators[0])
            op = self._convert_cmp_operator(expr.ops[0], lineno, col_offset)
            return nodes.BinaryExpression(op, left, right)

        elif isinstance(expr, ast.BoolOp):
            # In Python, 'and' / 'or' can have multiple values: a and b and c
            op = "&&" if isinstance(expr.op, ast.And) else "||"
            res = self._convert_expression(expr.values[0])
            for next_val in expr.values[1:]:
                rhs = self._convert_expression(next_val)
                res = nodes.BinaryExpression(op, res, rhs)
            return res

        elif isinstance(expr, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
            raise ParserError("Data structures (lists, tuples, dicts, sets) are not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(expr, ast.Lambda):
            raise ParserError("Lambdas are not supported in the CodeFlow Python subset.", lineno, col_offset)
        elif isinstance(expr, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            raise ParserError("Comprehensions and generators are not supported in the CodeFlow Python subset.", lineno, col_offset)
        else:
            expr_type = type(expr).__name__
            raise ParserError(f"Unsupported Python expression '{expr_type}'.", lineno, col_offset)

    def _convert_binop_operator(self, op: ast.operator, lineno: int, col: int) -> str:
        if isinstance(op, ast.Add): return "+"
        if isinstance(op, ast.Sub): return "-"
        if isinstance(op, ast.Mult): return "*"
        if isinstance(op, ast.Div): return "/"
        if isinstance(op, ast.Mod): return "%"
        if isinstance(op, ast.FloorDiv):
            # Map floor division to regular division in integer context
            return "/"
        raise ParserError(f"Unsupported arithmetic operator '{type(op).__name__}'.", lineno, col)

    def _convert_cmp_operator(self, op: ast.cmpop, lineno: int, col: int) -> str:
        if isinstance(op, ast.Lt): return "<"
        if isinstance(op, ast.Gt): return ">"
        if isinstance(op, ast.LtE): return "<="
        if isinstance(op, ast.GtE): return ">="
        if isinstance(op, ast.Eq): return "=="
        if isinstance(op, ast.NotEq): return "!="
        raise ParserError(f"Unsupported comparison operator '{type(op).__name__}'.", lineno, col)
