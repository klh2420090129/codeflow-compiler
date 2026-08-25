# CodeFlow — Master Project Report
## Project Title: Compiler-Based Source Code Processing System

---

## 1. Abstract
The construction of a modern compiler involves intricate software engineering principles, theoretical formalisms, and complex multi-pass transformations. **CodeFlow** is an academically defensible, end-to-end compiler-based source code processing laboratory designed to demonstrate every classical phase of compiler engineering. It translates a custom strongly typed language (**MiniLang**) through lexical scanning, LL(1) recursive descent parsing, Abstract Syntax Tree (AST) creation, semantic type and scope analysis, Three-Address Code (TAC) generation, Basic Block leader identification, Control Flow Graph (CFG) analysis, multi-pass optimization with rule-level explanation generation, target bytecode generation, and virtual machine execution. A browser-based Developer IDE allows students and evaluators to inspect every intermediate representation in real time.

---

## 2. Introduction & Problem Statement
Compiler courses in computer science curricula require students to understand abstract mathematical models such as context-free grammars, symbol tables, intermediate representations, control-flow analysis, and bytecode interpretation. However, traditional compilers (such as GCC, Clang, or Python's bytecode engine) are vast and opaque, making step-by-step visual inspection difficult.

**CodeFlow** solves this problem by providing a transparent, pedagogical compiler where every phase is completely decoupled, rigorously tested, and exposed via clean data models and visualization inspectors.

---

## 3. Objectives
1. Implement a complete compiler pipeline in Python without external black-box parser generators.
2. Construct a hand-crafted recursive descent parser enforcing operator precedence and building a clean AST.
3. Perform static semantic checks (scope resolution, declaration checks, and type validation) using hierarchical Symbol Tables.
4. Generate Three-Address Code (TAC) representing instructions with explicit temporaries and control labels.
5. Partition TAC into Basic Blocks using standard leader rules and build a Control Flow Graph with typed branch edges.
6. Implement multi-pass optimizations (Constant Propagation, Constant Folding, Algebraic Simplification, Dead Code Elimination) and an Explanation Engine that records the educational justification for every rewrite.
7. Translate optimized TAC into stack-based bytecode and execute it on a custom Virtual Machine with state tracing.
8. Deliver an interactive web-based IDE for live compilation and phase inspection.

---

## 4. System Architecture & Pipeline

```text
Source Code (MiniLang)
    │
    ▼
[Phase 1: Lexer] ─────────────► Token Stream (type, lexeme, line, col)
    │
    ▼
[Phase 2: Parser] ────────────► Abstract Syntax Tree (AST Nodes)
    │
    ▼
[Phase 3: Semantic Analyzer] ─► Symbol Table & Scopes (Type & Scope Validation)
    │
    ▼
[Phase 4: TAC Generator] ─────► Three-Address Code (Linear Instruction Stream)
    │
    ▼
[Phase 5: CFG Analyzer] ──────► Basic Blocks & Control Flow Graph (Typed Edges)
    │
    ▼
[Phase 6: Optimizer] ─────────► Optimized TAC + Optimization Explanation Trace
    │
    ▼
[Phase 7: Code Generator] ────► Target Bytecode (Stack Machine ISA)
    │
    ▼
[Phase 8: Virtual Machine] ───► Program Output + Execution State Trace
```

---

## 5. Detailed Phase Implementations

### Phase 1: Lexical Analysis
- **Module**: `compiler/lexer/lexer.py`
- **Technique**: Deterministic character-by-character scanner with lookahead.
- **Features**: Exact line/column tracking, longest-match operator recognition (`==`, `<=`, `&&`, etc.), and structured `LexicalError` exceptions for unrecognized characters.

### Phase 2: Syntax Analysis & AST Construction
- **Modules**: `compiler/parser/parser.py`, `compiler/ast/nodes.py`
- **Technique**: Hand-written LL(1) Recursive Descent Parsing without left recursion.
- **Precedence Hierarchy**: Logical OR $\rightarrow$ Logical AND $\rightarrow$ Equality $\rightarrow$ Relational $\rightarrow$ Additive $\rightarrow$ Multiplicative $\rightarrow$ Unary $\rightarrow$ Primary.
- **Output**: Typed AST nodes serialized to structured dictionary trees.

### Phase 3: Semantic Analysis & Symbol Table
- **Modules**: `compiler/semantic/analyzer.py`, `compiler/semantic/symbol_table.py`
- **Technique**: AST Visitor pattern with scoped Symbol Tables.
- **Checks**: Variable declaration before use, duplicate declarations in the same scope, type compatibility for binary/unary operators, and boolean constraints on conditional branches (`if`/`while`).

### Phase 4: Intermediate Code Generation (TAC)
- **Module**: `compiler/intermediate/tac.py`
- **Technique**: Linearizes nested expression trees into atomic 3-address instructions using dynamically generated temporaries (`t1`, `t2`) and control labels (`L1`, `L2`).
- **Instruction Types**: `Assignment`, `Binary`, `Unary`, `Label`, `Goto`, `ConditionalJump`, `Print`.

### Phase 5: Basic Block & Control Flow Graph (CFG) Analysis
- **Modules**: `compiler/analysis/basic_blocks.py`, `compiler/analysis/cfg.py`
- **Technique**: Leader identification using 3 standard rules:
  1. Instruction 0 is a leader.
  2. Any target of a jump (`Goto`, `ConditionalJump`) is a leader.
  3. Any instruction following a jump is a leader.
- **CFG Builder**: Derives directed graph edges with semantic types (`jump`, `true`, `false`, `fallthrough`), resolves labels to block IDs, computes predecessors/successors, and identifies entry and exit blocks.

### Phase 6: Code Optimization & Explanation Engine
- **Module**: `compiler/optimizer/optimizer.py`
- **Technique**: Iterative fixed-point optimization passes over the TAC.
- **Supported Passes**:
  - **Constant Propagation**: Substitutes known constant values into downstream variable reads.
  - **Constant Folding**: Evaluates constant arithmetic/relational operations at compile time.
  - **Algebraic Simplification**: Removes identity operations ($x+0 \rightarrow x$, $x \cdot 1 \rightarrow x$, $x \cdot 0 \rightarrow 0$, etc.).
  - **Dead Code Elimination**: Prunes unused temporary variable assignments.
- **Explanation Engine**: Records an `OptimizationStep` at the instant a rule fires, capturing the rule name, before/after values, and human-readable pedagogical rationale.

### Phase 7: Target Code Generation
- **Module**: `compiler/codegen/codegen.py`
- **Technique**: Translates optimized TAC into stack-based Virtual Machine bytecode instructions (`PUSH`, `LOAD`, `STORE`, `ADD`, `SUB`, `CMP_*`, `JMP`, `HALT`).

### Phase 8: Virtual Machine & Execution Tracing
- **Module**: `compiler/vm/virtual_machine.py`
- **Technique**: Custom bytecode interpreter maintaining an isolated instruction pointer, LIFO operand stack, and variable heap dictionary.
- **Features**: Controlled runtime error reporting (division-by-zero, stack underflow) and step-by-step state snapshot logging (`ExecutionTrace`).

### Phase 9: Unified Pipeline & Web IDE
- **Modules**: `compiler/pipeline.py`, `app.py`, `frontend/`
- **Technique**: Single orchestrator `compile_source()` providing structured JSON output consumed by a dark-themed developer-tool web interface built with HTML5, CSS3, and modern Vanilla JavaScript.

---

## 6. Verification & Test Suite
The codebase is validated with a comprehensive automated test suite in `pytest`:
- `tests/test_lexer.py` (15 tests)
- `tests/test_parser.py` (23 tests)
- `tests/test_semantic.py` (26 tests)
- `tests/test_tac.py` (21 tests)
- `tests/test_basic_blocks.py` (5 tests)
- `tests/test_cfg.py` (5 tests)
- `tests/test_optimizer.py` (19 tests)
- `tests/test_optimization_explanations.py` (10 tests)
- `tests/test_codegen.py` (28 tests)
- `tests/test_vm.py` (32 tests)
- `tests/test_pipeline.py` (9 tests)

**Total Test Count**: **193 passed, 0 failed, 0 regressions.**

---

## 7. Advantages & Academic Significance
1. **100% Transparent Architecture**: Every compiler phase can be inspected individually.
2. **Pedagogical Explanation Engine**: Shows *why* optimizations occur, helping students learn compiler optimization principles.
3. **Control Flow Graph Visualization**: Makes basic block partitioning and branch topology tangible.
4. **Resilient Error Reporting**: Produces precise line and column error messages without exposing Python tracebacks.
5. **No Heavy Frameworks**: Built using clean standard library Python and lightweight Flask/Vanilla JS.

---

## 8. Limitations & Future Scope
### Current Limitations
- Supports a single flat compilation unit without separate module linking.
- Functions and user-defined call stacks are not yet included.
- Target code targets a custom virtual stack machine rather than physical hardware (x86/ARM).

### Future Scope
- **Functions & Activation Records**: Add function declarations, parameter passing, and call-frame stacks.
- **Static Single Assignment (SSA)**: Convert TAC into SSA form with $\phi$-nodes.
- **Register Allocation**: Implement Graph Coloring or Linear Scan register allocation algorithms.
- **Native Assembly Code Generation**: Target x86-64 NASM or WebAssembly (Wasm).

---

## 9. Conclusion
**CodeFlow** successfully demonstrates the complete software lifecycle of a compiler-based source code processing system. By maintaining strict separation of concerns across 12 compiler phases and coupling them with an interactive developer laboratory interface, CodeFlow serves as a comprehensive, defensible, and robust academic project for Compiler Design.
