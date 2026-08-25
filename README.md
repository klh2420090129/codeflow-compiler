# CodeFlow — Compiler-Based Source Code Processing System

**CodeFlow** is an interactive, academically defensible compiler design laboratory and execution environment built to demonstrate the classical and modern phases of compiler engineering. The system processes source programs written in **MiniLang** (a custom educational programming language) through a multi-pass pipeline: from lexical analysis to AST construction, semantic validation, three-address code (TAC) generation, basic block & control flow graph (CFG) analysis, multi-pass optimization with real-time reasoning explanations, target code generation, and execution on a custom stack-based Virtual Machine (VM).

---

## 1. Abstract
In computer science curricula, compiler design is often taught with heavy theoretical emphasis, leaving a pedagogical gap between formal grammar derivations and runtime machine execution. **CodeFlow** bridges this gap by providing a fully modular, transparent, and interactive compiler pipeline. Source code is processed through 12 formal compiler phases without relying on third-party black-box parser generators or native `eval()` shortcuts. Every intermediate data structure—tokens, AST nodes, symbol scopes, TAC instructions, basic blocks, CFG edge topologies, optimization traces, target bytecode, and stack execution snapshots—is serialized and visualized in an interactive Developer IDE.

---

## 2. Problem Statement & Objectives
- **Problem**: Understanding intermediate representations, control-flow graphs, optimization transformations, and virtual machine stack dynamics is difficult when compilers act as monolithic black boxes.
- **Objectives**:
  1. Implement a complete, working compiler pipeline in Python following standard textbook principles.
  2. Implement an LL(1) recursive-descent parser and strongly typed AST.
  3. Enforce lexical scope rules and type safety using a formal Symbol Table.
  4. Generate clean Three-Address Code (TAC) intermediate representation.
  5. Partition TAC into Basic Blocks and construct a deterministic Control Flow Graph (CFG).
  6. Perform multi-pass optimizations and generate pedagogical explanations for every optimization event.
  7. Generate target bytecode and execute it on a custom stack-based Virtual Machine with live tracing.
  8. Provide a web-based laboratory IDE for live inspection of every compiler stage.

---

## 3. Compiler Architecture & Pipeline
CodeFlow processes source code through the following sequential pipeline:

```text
Source Code
    ↓
1.  Lexical Analysis (Deterministic Scanner)
    ↓ Tokens
2.  Syntax Analysis (LL(1) Recursive Descent Parser)
    ↓ Parse Tree / AST
3.  Abstract Syntax Tree (Dataclass Node Hierarchy)
    ↓
4.  Semantic Analysis (Scope Resolution & Type Checking)
    ↓ Validated AST + Symbol Table
5.  Intermediate Code Generation (Three-Address Code)
    ↓ Linear TAC Stream
6.  Basic Block Identification (Leader Analysis)
    ↓ Partitioned Basic Blocks
7.  Control Flow Graph (CFG) Construction
    ↓ Typed Directed Graph (Jump / True / False / Fallthrough)
8.  Code Optimization (Folding, Propagation, Simplification, DCE)
    ↓ Optimized TAC
9.  Optimization Explanation Engine (Event-Driven Reasoning Trace)
    ↓
10. Target Code Generation (Stack Bytecode Emission)
    ↓ TargetInstruction Stream
11. Virtual Machine (Isolated Stack & Memory Interpreter)
    ↓
12. Program Execution Output & VM State Trace
```

---

## 4. Supported Language Features (MiniLang)
- **Variable Declarations & Assignments**: `let x = 10;`, `let y = 15.5;`, `x = x + 1;`
- **Control Flow**: `if (cond) { ... } else { ... }`, `while (cond) { ... }`
- **Data Types**: `int`, `float`, `bool` (`true`, `false`)
- **Arithmetic Operators**: `+`, `-`, `*`, `/`, `%`
- **Relational Operators**: `<`, `>`, `<=`, `>=`, `==`, `!=`
- **Logical Operators**: `&&`, `||`, `!`
- **I/O Output**: `print(expression);`

---

## 5. Key Compiler Components

### A. Lexical & Syntax Analysis
- **Lexer**: Character-by-character scanner tracking exact line and column coordinates, enforcing longest-match tokenization.
- **Parser**: Hand-written recursive-descent parser mapping operator precedence structurally across expression levels.
- **AST**: Structured node dataclasses (`Program`, `VariableDeclaration`, `BinaryExpression`, `IfStatement`, etc.) supporting JSON export.

### B. Semantic Analysis & Symbol Table
- **Scoping**: Lexical scope stack managing variable lifetimes, shadowing, and block hierarchies.
- **Type Checking**: Validates type compatibility for arithmetic, boolean logic, and branching conditions.

### C. Intermediate Representation (TAC)
- Quadruple/triplet-style linear intermediate instructions: `Assignment`, `Binary`, `Unary`, `Label`, `Goto`, `ConditionalJump`, `Print`.

### D. Basic Block & Control Flow Graph (CFG)
- **Leader Detection Rules**: (1) First instruction, (2) Jump targets, (3) Instructions following jumps.
- **CFG Graph**: Directed graph with typed edges (`jump`, `true`, `false`, `fallthrough`), predecessor/successor derivation, and entry/exit node tracking.

### E. Optimization & Explanation Engine
- **Passes**: Constant Propagation, Constant Folding, Algebraic Simplification, Dead Code Elimination.
- **Explanation Trace**: Emits an `OptimizationStep` whenever a rewrite rule fires, documenting rule name, before/after values, and pedagogical rationale.
- **Summary Metrics**: Tracks instruction count reductions and percentage improvement.

### F. Target Code & Virtual Machine
- **Instruction Set**: `PUSH`, `LOAD`, `STORE`, `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `NEG`, `NOT`, `CMP_*`, `AND`, `OR`, `JMP`, `JMP_IF_TRUE`, `JMP_IF_FALSE`, `PRINT`, `HALT`.
- **VM Engine**: Emulates instruction pointer, operand stack, and memory heap with runtime error guards and step-by-step tracing.

---

## 6. Installation & Quickstart

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/klh2420090129/codeflow-compiler.git
cd codeflow-compiler

# Install dependencies
pip install -r requirements.txt
```

### Running the Web IDE
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### Running via CLI
```bash
# Full compiler pipeline JSON dump
python -m compiler.pipeline examples/basic.cf

# Virtual machine direct execution
python -m compiler.vm.virtual_machine examples/arithmetic.cf
```

### Running Tests
```bash
python -m pytest
```
All **193 automated unit and integration tests** will execute and validate the pipeline.

---

## 7. Example Program

```minilang
let x = 10;
let y = 20;
let z = x + y * 2;
print(z);
```

### Compilation & Optimization Flow
- **Original TAC**:
  ```text
  00: x = 10
  01: y = 20
  02: t1 = y * 2
  03: t2 = x + t1
  04: z = t2
  05: PRINT z
  ```
- **Optimization Trace**:
  - `[01] Constant Propagation`: `y` $\rightarrow$ `20`
  - `[02] Constant Propagation`: `x` $\rightarrow$ `10`
  - `[03] Constant Folding`: `20 * 2` $\rightarrow$ `40`
  - `[04] Constant Propagation`: `t1` $\rightarrow$ `40`
  - `[05] Constant Folding`: `10 + 40` $\rightarrow$ `50`
  - `[06] Dead Code Elimination`: `t1 = 40` $\rightarrow$ `<removed>`
  - `[07] Constant Propagation`: `t2` $\rightarrow$ `50`
  - `[08] Constant Propagation`: `z` $\rightarrow$ `50`
  - `[09] Dead Code Elimination`: `t2 = 50` $\rightarrow$ `<removed>`
- **Optimized TAC**:
  ```text
  00: x = 10
  01: y = 20
  02: z = 50
  03: PRINT 50
  ```
- **Execution Output**: `50`

---

## 8. Technology Stack
- **Language**: Python 3.10+
- **Web Backend**: Flask, Flask-CORS
- **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Developer IDE theme), Modern Vanilla JavaScript
- **Test Framework**: pytest
- **Architecture**: Modular compiler pipeline with isolated phase responsibilities

---

## 9. Academic Relevance & Future Scope
### Academic Relevance
- Directly maps to college and university **Compiler Design** syllabi (Aho, Lam, Sethi, Ullman).
- Transparently illustrates frontend analysis, intermediate representation, code optimization, control flow graphs, and runtime code execution.

### Future Scope
- User-defined functions, activation records, and call-stack frame management.
- Static Single Assignment (SSA) form representation.
- Register allocation algorithms (Graph Coloring / Linear Scan).
- Array data structures and string operations.
- Native assembly target emission (x86-64 / ARM / WebAssembly).

---

## 10. License
This project is licensed under the MIT License for educational and academic research use.
