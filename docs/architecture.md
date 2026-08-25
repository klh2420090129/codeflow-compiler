# CodeFlow Architecture

CodeFlow follows a modular architecture separating the compiler backend from the web frontend.

## Compiler Pipeline
1. **Lexical Analysis:** Converts raw source code into streams of tokens.
2. **Syntax Analysis:** A recursive descent parser that validates syntax and builds an Abstract Syntax Tree (AST).
3. **Semantic Analysis:** Traverses the AST for type checking, scope validation, and symbol table management. Ensures variables are declared before use and operations are type-safe.
4. **Intermediate Code Generation:** Traverses the AST to generate Three-Address Code (TAC), maintaining deterministic label and temporary variable generation.
5. **Control Flow Graph (CFG) Analysis:** Analyzes the TAC instruction stream to identify leaders, partition into Basic Blocks, and construct a deterministic Control Flow Graph with typed edges (jump, true, false, fallthrough), entry/exit detection, and predecessor/successor tracking.
6. **Optimization & Explanation Engine:** Applies educational optimization passes over the TAC (Constant Folding, Propagation, Simplification, DCE) to generate Optimized TAC, while recording an event-driven trace of every optimization step, its rule, transformation, and educational rationale.
7. **Target Code Generation:** Maps optimized TAC to an educational stack/register Virtual Machine Instruction Set (PUSH, LOAD, ADD, etc.).
8. **Virtual Machine Execution:** Runs the generated target code natively on the python-backed educational interpreter, pushing strings to output streams instead of printing instantly to emulate isolated runtime limits.

## Unified Pipeline API
A robust orchestrator wraps all stages to sequentially push valid models downwards, catching errors gracefully.
- `compile_source()` accepts raw input text and emits a `PipelineResult`.
- `PipelineResult` exposes the source, tokens, ast, tac, optimizations, target_code, and `execution_output` simultaneously.
- If execution stops early (e.g., Semantic Analyzer catches a scope leak), the engine skips TAC/VM generation returning the collected tokens and AST alongside a structured `CompilerError` indicating phase origins.

## Web Backend
A `Flask` application sitting internally exposes `app.py`.
- `POST /api/compile`: Submits source code triggering the pipeline mapping JSON outputs recursively.
- `GET /api/health`: Base endpoint for status checks.

## Directory Structure
- `compiler/`: Core compiler modules representing each phase and `pipeline.py`.
- `frontend/`: Web interface components (HTML, CSS, JS).
- `examples/`: Sample MiniLang source files.
- `tests/`: Automated unit tests for all compiler phases.
