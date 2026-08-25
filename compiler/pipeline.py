import traceback
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from compiler.lexer.lexer import Lexer, Token
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable, Scope
from compiler.intermediate.tac import TACGenerator, TACInstruction, Assignment, Binary, Unary, Label, Goto, ConditionalJump, Print
from compiler.analysis.basic_blocks import BasicBlockAnalyzer, BasicBlock
from compiler.analysis.cfg import CFGBuilder, ControlFlowGraph
from compiler.optimizer.optimizer import Optimizer
from compiler.codegen.codegen import CodeGenerator, TargetInstruction, TargetProgram
from compiler.vm.virtual_machine import VirtualMachine, ExecutionTrace
from compiler.errors import CompilerError

@dataclass
class PipelineResult:
    success: bool
    source: str
    tokens: Optional[List[Dict[str, Any]]] = None
    ast: Optional[Dict[str, Any]] = None
    symbol_table: Optional[Dict[str, Any]] = None
    tac: Optional[List[Dict[str, Any]]] = None
    basic_blocks: Optional[List[Dict[str, Any]]] = None
    cfg: Optional[Dict[str, Any]] = None
    optimized_tac: Optional[List[Dict[str, Any]]] = None
    optimization_stats: Optional[Dict[str, int]] = None
    optimization_steps: Optional[List[Dict[str, Any]]] = None
    optimization_summary: Optional[Dict[str, Any]] = None
    target_code: Optional[List[Dict[str, Any]]] = None
    execution_output: Optional[List[str]] = None
    execution_trace: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "source": self.source,
            "tokens": self.tokens,
            "ast": self.ast,
            "symbol_table": self.symbol_table,
            "tac": self.tac,
            "basic_blocks": self.basic_blocks,
            "cfg": self.cfg,
            "optimized_tac": self.optimized_tac,
            "optimization_stats": self.optimization_stats,
            "optimization_steps": self.optimization_steps,
            "optimization_summary": self.optimization_summary,
            "target_code": self.target_code,
            "execution_output": self.execution_output,
            "execution_trace": self.execution_trace,
            "error": self.error
        }

def serialize_token(token: Token) -> Dict[str, Any]:
    return {
        "type": token.type.name,
        "value": token.lexeme,
        "line": token.line,
        "column": token.column
    }

def serialize_scope(scope: Scope) -> Dict[str, Any]:
    return {
        "name": scope.name,
        "symbols": {k: {"type_name": v.type_name, "initialized": v.initialized} for k, v in scope.symbols.items()}
    }

def serialize_symbol_table(st: SymbolTable) -> Dict[str, Any]:
    return {
        "scopes": [serialize_scope(s) for s in st.all_scopes]
    }

def serialize_tac(instr: TACInstruction) -> Dict[str, Any]:
    if isinstance(instr, Assignment):
        return {"type": "Assignment", "result": instr.result, "arg1": instr.arg1}
    elif isinstance(instr, Binary):
        return {"type": "Binary", "result": instr.result, "arg1": instr.arg1, "operator": instr.op, "arg2": instr.arg2}
    elif isinstance(instr, Unary):
        return {"type": "Unary", "result": instr.result, "operator": instr.op, "arg1": instr.arg1}
    elif isinstance(instr, Label):
        return {"type": "Label", "name": instr.name}
    elif isinstance(instr, Goto):
        return {"type": "Goto", "target": instr.target}
    elif isinstance(instr, ConditionalJump):
        return {"type": "ConditionalJump", "condition": instr.condition, "target": instr.target, "jump_if_false": instr.jump_if_false}
    elif isinstance(instr, Print):
        return {"type": "Print", "value": instr.value}
    return {"type": "Unknown"}

def serialize_target_code(instr: TargetInstruction) -> Dict[str, Any]:
    return {
        "opcode": instr.opcode,
        "operand": instr.operand
    }

def serialize_error(e: Exception, phase: str) -> Dict[str, Any]:
    if isinstance(e, CompilerError):
        return {
            "phase": phase,
            "type": type(e).__name__,
            "message": str(e),
            "line": e.line,
            "column": e.column
        }
    return {
        "phase": phase,
        "type": type(e).__name__,
        "message": str(e),
        "line": 0,
        "column": 0
    }

def compile_source(source: str, execute: bool = True, trace: bool = False) -> PipelineResult:
    result = PipelineResult(success=True, source=source)
    
    try:
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            result.tokens = [serialize_token(t) for t in tokens]
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "lexical")
            return result
            
        try:
            parser = Parser(tokens)
            ast = parser.parse()
            if hasattr(ast, "to_dict"):
                result.ast = ast.to_dict()
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "syntax")
            return result
            
        try:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            result.symbol_table = serialize_symbol_table(analyzer.symbol_table)
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "semantic")
            return result
            
        try:
            tac_gen = TACGenerator()
            tac = tac_gen.generate(ast)
            result.tac = [serialize_tac(t) for t in tac]
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "tac")
            return result

        # Basic Block Analysis & CFG Construction
        try:
            bb_analyzer = BasicBlockAnalyzer()
            basic_blocks = bb_analyzer.analyze(tac)
            result.basic_blocks = [b.to_dict() for b in basic_blocks]

            cfg_builder = CFGBuilder()
            cfg = cfg_builder.build(basic_blocks)
            result.cfg = cfg.to_dict()
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "analysis")
            return result
            
        try:
            opt = Optimizer()
            optimized_tac = opt.optimize(tac)
            result.optimized_tac = [serialize_tac(t) for t in optimized_tac]
            result.optimization_stats = opt.stats.to_dict()
            result.optimization_steps = [s.to_dict() for s in opt.steps]
            result.optimization_summary = opt.get_summary(len(tac), len(optimized_tac))
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "optimization")
            return result
            
        try:
            codegen = CodeGenerator()
            target_prog = codegen.generate(optimized_tac)
            result.target_code = [serialize_target_code(t) for t in target_prog.to_list()]
        except Exception as e:
            result.success = False
            result.error = serialize_error(e, "codegen")
            return result
            
        if execute:
            try:
                vm = VirtualMachine(target_prog, trace=trace)
                vm.run()
                result.execution_output = vm.get_output()
                if trace:
                    result.execution_trace = [t.to_dict() for t in vm.trace_log]
            except Exception as e:
                result.success = False
                result.error = serialize_error(e, "vm")
                return result
                
        return result
        
    except Exception as e:
        result.success = False
        result.error = {
            "phase": "unknown",
            "type": "SystemError",
            "message": f"Unexpected compiler error: {str(e)}",
            "line": 0,
            "column": 0
        }
        return result

if __name__ == "__main__":
    import sys
    import json
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
            res = compile_source(source, execute=True, trace=False)
            
            print("SOURCE\n", res.source, "\n")
            if res.tokens: print(f"TOKENS\n{len(res.tokens)} tokens generated\n")
            if res.ast: print(f"AST\nGenerated\n")
            if res.symbol_table: print(f"SYMBOL TABLE\nGenerated\n")
            if res.tac: print(f"TAC\n{len(res.tac)} instructions\n")
            if res.basic_blocks: print(f"BASIC BLOCKS\n{len(res.basic_blocks)} blocks\n")
            if res.cfg: print(f"CFG\n{len(res.cfg['edges'])} edges\n")
            if res.optimized_tac: print(f"OPTIMIZED TAC\n{len(res.optimized_tac)} instructions\n")
            if res.target_code: print(f"TARGET CODE\n{len(res.target_code)} instructions\n")
            if res.execution_output: print(f"EXECUTION OUTPUT\n" + "\n".join(res.execution_output))
            if res.error: print(f"\nERROR: {res.error['message']}")
