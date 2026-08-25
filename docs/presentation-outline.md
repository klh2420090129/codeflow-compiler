# CodeFlow — Academic Presentation Outline

A structured 15-slide presentation designed for university project evaluation and viva defense.

---

### Slide 1: Title & Overview
- **Title**: CodeFlow — Compiler-Based Source Code Processing System
- **Subtitle**: An Interactive Compiler Design Laboratory & Virtual Machine
- **Course**: Compiler Design (Project-Based Learning)
- **Presenter Notes**: Welcome the evaluators. State that CodeFlow is an end-to-end multi-pass compiler processing a custom language from raw source to VM execution.

---

### Slide 2: Problem Statement & Motivation
- **The Challenge**: Traditional compilers (GCC, Clang) are black boxes; textbooks teach compiler phases as isolated equations.
- **The Solution**: An open, modular compiler that exposes every intermediate representation (AST, TAC, CFG, Optimization Trace, VM Bytecode) interactively.
- **Presenter Notes**: Emphasize that CodeFlow was engineered without third-party parser generators (`yacc`/`bison`/`antlr`) or native `eval()` tricks.

---

### Slide 3: Objectives
- Hand-craft an LL(1) Recursive Descent Parser and AST.
- Enforce strict typing and scope rules with a formal Symbol Table.
- Generate Three-Address Code (TAC) and construct Control Flow Graphs (CFG).
- Build a multi-pass optimizer with real-time pedagogical explanations.
- Execute target bytecode on a custom stack-based Virtual Machine.
- **Presenter Notes**: Highlight the pedagogical focus: enabling students to inspect *why* and *how* code transforms.

---

### Slide 4: System Architecture
- High-level diagram showing Frontend $\rightarrow$ Intermediate $\rightarrow$ Backend $\rightarrow$ Execution.
- Decoupled pipeline where each phase operates purely on the output of the preceding stage.
- **Presenter Notes**: Point out the clean separation between compiler algorithms and the Flask/Vanilla JS web interface.

---

### Slide 5: The MiniLang Source Language
- **Primitives**: `int`, `float`, `bool` (`true`, `false`).
- **Control Structures**: `if-else`, `while` loops.
- **Operators**: Arithmetic (`+`, `-`, `*`, `/`, `%`), Relational (`<`, `>`, `==`, etc.), Logical (`&&`, `||`, `!`).
- **I/O**: Built-in `print()` statement.
- **Presenter Notes**: Show a clean sample MiniLang snippet to demonstrate language syntax.

---

### Slide 6: Lexical & Syntax Analysis
- **Lexer**: Character-by-character scanner tracking line/column, matching multi-char operators (`==`, `!=`).
- **Parser**: Hand-crafted LL(1) recursive descent enforcing operator precedence structurally.
- **AST**: Strongly typed dataclasses representing language grammar nodes.
- **Presenter Notes**: Explain how left-recursion was eliminated by using iterative matching in grammar rules.

---

### Slide 7: Semantic Analysis & Symbol Table
- **Scope Hierarchy**: Lexical scope stack for variable lifetimes and block nesting.
- **Static Semantic Validation**:
  - Variable declaration before use.
  - Prohibition of duplicate declaration in same scope.
  - Type checking for binary/unary expressions and boolean condition enforcement.
- **Presenter Notes**: Mention that semantic errors stop compilation before code generation occurs.

---

### Slide 8: Intermediate Code (TAC) & CFG Analysis
- **Three-Address Code (TAC)**: Flattens complex expressions using temporaries (`t1`) and labels (`L1`).
- **Basic Block Identification**: 3 standard leader detection rules.
- **Control Flow Graph (CFG)**: Directed graph with typed edges (`jump`, `true`, `false`, `fallthrough`), predecessor/successor tracking, and entry/exit nodes.
- **Presenter Notes**: Explain how the CFG captures control branches and loop back-edges deterministically.

---

### Slide 9: Optimization & Explanation Engine
- **Optimization Passes**: Constant Propagation, Constant Folding, Algebraic Simplification, Dead Code Elimination.
- **Explanation Engine**: Records an `OptimizationStep` at the moment a rewrite occurs.
- **Metrics**: Computes instruction count reduction and percentage efficiency gains.
- **Presenter Notes**: This is a major differentiator: CodeFlow explains *why* each optimization is safe and legal.

---

### Slide 10: Target Code Generation & Virtual Machine
- **Target ISA**: Stack-based bytecode instructions (`PUSH`, `LOAD`, `STORE`, `ADD`, `CMP_*`, `JMP`, `HALT`).
- **Virtual Machine**: Sandboxed interpreter maintaining an instruction pointer, operand stack, and memory heap.
- **Execution Trace**: Logs stack and memory state for every executed instruction.
- **Presenter Notes**: Explain that execution is completely isolated and cannot crash the host operating system.

---

### Slide 11: CodeFlow Interactive Web IDE
- **Interface**: Custom Dark Developer IDE built with HTML5, CSS3, and Vanilla JavaScript.
- **Features**: Live source editor, pipeline stage indicators, AST visualizer, CFG block viewer, before/after optimizer split-view, and step-by-step VM trace viewer.
- **Presenter Notes**: Emphasize that all UI data is dynamically fetched from backend API endpoints.

---

### Slide 12: Error Handling Architecture
- **Layered Error Types**: `LexicalError`, `ParserError`, `SemanticError`, `VMRuntimeError`.
- **User Experience**: Highlights exact error phase, line, column, and description without exposing Python stack traces.
- **Presenter Notes**: Show how partial pipeline results are preserved up to the failure phase.

---

### Slide 13: Testing & Quality Assurance
- **Framework**: `pytest` test suite.
- **Coverage**: 193 automated tests across all 12 phases.
- **Regression Status**: 100% pass rate with zero regressions across all iterative phases.
- **Presenter Notes**: State the test count with confidence (193/193 tests passing).

---

### Slide 14: Advantages & Future Scope
- **Advantages**: 100% transparent, educational explanations, interactive UI, robust error handling.
- **Future Scope**: Functions & activation records, SSA form representation, graph-coloring register allocation, native x86-64 assembly generation.
- **Presenter Notes**: Highlight that the modular architecture makes future extensions straightforward.

---

### Slide 15: Conclusion & Q&A
- **Summary**: CodeFlow fulfills all requirements of a complete, academically sound compiler processing system.
- **Open for Questions**: Invite evaluators to examine specific phases or suggest live code snippets for demonstration.
- **Presenter Notes**: Thank the committee and invite questions.
