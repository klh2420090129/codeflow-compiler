# CodeFlow — Experimental C Frontend Documentation

## 1. Overview & Pedagogical Objective
CodeFlow provides an **experimental C frontend** for a controlled, pedagogical subset of C syntax and semantics.

> [!NOTE]
> **Academic & Defensive Positioning**:
> CodeFlow is **not** a full C99/C11/C17 compiler. It is not an alternative to GCC, Clang, or MSVC. Rather, it serves as a compiler architecture laboratory, demonstrating how C source code can be parsed and mapped directly into CodeFlow's unified intermediate representation (IR), then processed through the **exact same 12-stage compiler pipeline**:
> 
> C Source → C Lexer → C Parser → CodeFlow AST → Semantic Analysis → TAC Generation → Basic Block Partitioning → Control Flow Graph (CFG) → Multi-Pass Optimizer → Code Generation → Custom Stack-Based Virtual Machine (VM) Execution & Tracing.
> 
> **Zero External Fallbacks**: CodeFlow does not invoke GCC, Clang, or an embedded C runtime interpreter. All execution occurs inside CodeFlow's custom stack VM.

---

## 2. Supported C Language Subset

| Construct Category | Supported Syntax | Example |
| :--- | :--- | :--- |
| **Declarations** | `int <name>;`, `float <name>;` | `int x;`, `float rate;` |
| **Initializations** | `int <name> = <expr>;`, `float <name> = <expr>;` | `int x = 10;`, `float y = 2.5;` |
| **Assignments** | `<name> = <expr>;` | `x = x + 5;` |
| **Arithmetic Operators** | `+`, `-`, `*`, `/`, `%` | `int z = (x + y) * 2 - 8 / 4;` |
| **Unary Operators** | `-` (negation), `!` (logical NOT) | `int neg = -x;`, `int inv = !flag;` |
| **Relational Operators** | `<`, `>`, `<=`, `>=`, `==`, `!=` | `if (x >= 18) { ... }` |
| **Logical Operators** | `&&`, `||`, `!` | `if (x > 0 && y != 0) { ... }` |
| **Conditionals** | `if (condition) { ... } [else { ... }]` | `if (a > b) { printf("%d\n", a); } else { printf("%d\n", b); }` |
| **Loops** | `while (condition) { ... }` | `while (i < 5) { printf("%d\n", i); i = i + 1; }` |
| **Formatted Output** | `printf("%d\n", expr);`, `printf("%f\n", expr);` (also `%d`, `%f`, `%i`) | `printf("%d\n", total);` |
| **Comments** | Single-line `// ...` and block `/* ... */` | `// counter`<br>`/* loop block */` |
| **Scoping & Blocks** | Compound statement blocks `{ ... }` | `{ int inner = 5; printf("%d\n", inner); }` |

---

## 3. Explicitly Unsupported Constructs

The C frontend explicitly parses and rejects unsupported C language features with informative line/column error diagnostics:
- **Pointers and addresses**: `*ptr`, `&var`, pointer arithmetic
- **Arrays & Indexing**: `int arr[10];`, `arr[i]`
- **Structs, Unions, Enums**: `struct Point { int x; int y; };`
- **Functions**: `int main()`, `void foo()`, recursion, `return`
- **Memory Management**: `malloc()`, `free()`
- **Preprocessor Directives**: `#include`, `#define`, `#ifdef`
- **Control Flow Statements**: `for`, `do/while`, `switch/case/default`, `goto`, `break`, `continue`
- **Variadic / Arbitrary printf**: Multi-argument format strings or specifiers other than `%d`/`%f`
- **Type Qualifiers & Specifiers**: `const`, `static`, `typedef`, `unsigned`, `char`, `double`, `void`

---

## 4. Architecture & Data Flow

```text
C Source Code
      ↓
compiler.frontends.c.lexer.CLexer
      ├── Comment stripping (// and /* ... */)
      ├── Directive check (rejects #include, etc.)
      └── Token generation (INT, FLOAT, IDENTIFIER, NUMBER, PRINTF, etc.)
      ↓
compiler.frontends.c.parser.CParser
      ├── Recursive descent with C operator precedence hierarchy
      └── AST translation into CodeFlow AST nodes
      ↓
CodeFlow AST (nodes.Program, nodes.VariableDeclaration, nodes.Assignment, etc.)
      ↓
compiler.semantic.analyzer.SemanticAnalyzer (Symbol table, scope hierarchy, type verification)
      ↓
compiler.intermediate.tac.TACGenerator (Linear Three-Address Code)
      ↓
compiler.analysis.basic_blocks.BasicBlockAnalyzer (Leader identification)
      ↓
compiler.analysis.cfg.CFGBuilder (Directed Graph with Jump/True/False/Fallthrough edges)
      ↓
compiler.optimizer.optimizer.Optimizer (Multi-pass constant folding, propagation, simplification, DCE)
      ↓
compiler.codegen.codegen.CodeGenerator (Stack bytecode: PUSH, LOAD, STORE, ADD, CMP_GT, JMP_IF_FALSE, PRINT, HALT)
      ↓
compiler.vm.virtual_machine.VirtualMachine (Isolated Stack & Memory execution and tracing)
```

---

## 5. Demonstration Examples

### Example 1: Arithmetic & Operator Precedence
```c
int x = 10;
int y = 20;
int z = x + y * 2;
printf("%d\n", z);
```
**VM Output:**
```text
50
```

### Example 2: While Loop with Formatted Output
```c
int count = 0;
while (count < 5) {
    printf("%d\n", count);
    count = count + 1;
}
```
**VM Output:**
```text
0
1
2
3
4
```

### Example 3: Constant Folding Optimization on C TAC
```c
int x = 10 + 20 * 2;
printf("%d\n", x);
```
**Optimizer Result:**
- `20 * 2` is folded to `40`.
- `10 + 40` is folded to `50`.
- Emits direct `PUSH 50` in bytecode.
