# CodeFlow — Experimental C++ Frontend Documentation

## 1. Overview & Positioning

**C++ (Experimental)** — a controlled C++ subset frontend mapped into the CodeFlow compiler pipeline.

> [!NOTE]
> **Academic & Architectural Scope**:
> CodeFlow does **not** implement a full ISO C++ compiler or runtime library, nor does it rely on `g++`, `clang++`, `MSVC`, or any external C++ compiler or interpreter. Instead, it demonstrates CodeFlow's multi-language compiler capability by accepting a controlled C++ subset, translating it into the canonical CodeFlow AST/IR, and reusing 100% of the downstream compiler pipeline:
> - Semantic Analysis (symbol table, scopes, static type checking)
> - Three-Address Code (TAC) Generation
> - Basic Block Partitioning (leader analysis)
> - Control Flow Graph (CFG) Construction
> - Multi-Pass Optimizer (constant folding, constant propagation, dead code elimination)
> - Target Code Generator (stack bytecode)
> - CodeFlow Stack-Based Virtual Machine (VM) and Execution Trace

---

## 2. Canonical C++ Entry Point Wrapper

The frontend expects executable C++ statements to be contained in a canonical `int main()` wrapper:

```cpp
int main() {
    int x = 10;
    int y = 20;
    std::cout << x + y << std::endl;
}
```

- **Wrapper validation**: The entry function must be `int main()`.
- **Extraction**: Statements inside `main` are extracted directly into `nodes.Program`.
- **Rejected**: Multiple functions, headers (`#include <iostream>`), macros, and preprocessor directives produce immediate, informative frontend errors.

---

## 3. Pipeline Flow

```text
C++ Source Code
     ↓
compiler.frontends.cpp.CPPLexer
     ↓ (C++ Tokens: keywords, primitive types, operators, <<, std::cout, std::endl)
compiler.frontends.cpp.CPPParser
     ↓ (main() Wrapper Validation, Static Type Validation)
CodeFlow AST / IR (nodes.Program, nodes.VariableDeclaration, nodes.Assignment, etc.)
     ↓
Existing CodeFlow Semantic Analysis (Symbol Table, Scopes, Type Checking)
     ↓
Existing CodeFlow TAC Generation (Three-Address Code)
     ↓
Existing Basic Block Partitioning & CFG Construction
     ↓
Existing Multi-Pass Optimizer (Constant Folding, DCE, Simplification)
     ↓
Existing Target Code Generator (Stack Bytecode)
     ↓
Existing CodeFlow Virtual Machine (Stack & Memory Execution)
     ↓
Execution Output & VM Execution Trace
```

---

## 4. Supported C++ Subset

| Category | Syntax | CodeFlow AST Representation |
| :--- | :--- | :--- |
| **Entry Point** | `int main() { ... }` | Extracted into `nodes.Program` |
| **Variable Declarations** | `int x;`<br>`int x = 10;`<br>`double y = 2.5;`<br>`bool flag = true;` | `nodes.VariableDeclaration` |
| **Assignments** | `x = 20;`<br>`y = y + 1.5;` | `nodes.Assignment` |
| **Arithmetic Operators** | `+`, `-`, `*`, `/`, `%` | `nodes.BinaryExpression` |
| **Unary Operators** | `-x`, `!flag` | `nodes.UnaryExpression` |
| **Comparison Operators** | `<`, `>`, `<=`, `>=`, `==`, `!=` | `nodes.BinaryExpression` |
| **Logical Operators** | `&&`, `\|\|`, `!` | `nodes.BinaryExpression` |
| **Conditionals** | `if (cond) { ... } else { ... }`<br>`else if (cond) { ... }` | `nodes.IfStatement` |
| **Loops** | `while (condition) { ... }` | `nodes.WhileStatement` |
| **Output** | `std::cout << expr << std::endl;` | `nodes.PrintStatement` |
| **Literals** | Integers, Floats, Booleans (`true`, `false`) | `nodes.Literal` |
| **Compound Blocks** | `{ ... }` | `nodes.Block` |
| **Comments** | Single-line `//`, Multi-line `/* ... */` | Ignored during lexical scanning |

---

## 5. Output Translation (`std::cout`)

The controlled C++ output syntax:
```cpp
std::cout << expression << std::endl;
```
is parsed by `CPPParser` and translated directly into a unified CodeFlow `nodes.PrintStatement(expression)` node. No C++ `<iostream>` library or native streams runtime is invoked; the expression is evaluated and printed by the CodeFlow VM.

---

## 6. Static Typing Rules

- Incompatible assignment between boolean and numeric types (`int x = true;` or `bool flag = 10;`) raises an explicit `SemanticError: Type mismatch`.
- Narrowing conversions (e.g. assigning `double` to `int`) are explicitly rejected.
- `if` and `while` conditions must strictly evaluate to boolean expressions.
- Duplicate declarations in the same scope generate `SemanticError: Variable '<name>' is already declared`.

---

## 7. Explicitly Unsupported C++ Features

To maintain educational clarity and compiler pipeline integrity, the following features are rejected with line/column-accurate errors:
- Preprocessor directives (`#include`, `#define`, `#pragma`, macros)
- User-defined functions, multiple entry points
- Classes, structs, objects, constructors, destructors
- Inheritance, virtual functions, polymorphism, interfaces
- Templates, generic programming, operator overloading
- Pointers (`*`), references (`&`), address-of, dynamic allocation (`new`, `delete`)
- Arrays, vectors, STL containers, iterators, strings
- Iteration constructs: `for`, range-based for, `do...while`
- Jump statements: `switch`, `case`, `break`, `continue`, `goto`
- Exceptions: `try`, `catch`, `throw`
- Namespaces beyond the recognized `std::cout` / `std::endl`

---

## 8. Verification & End-to-End Examples

### Smoke Test 1: Arithmetic & Operator Precedence
```cpp
int main() {
    int x = 10;
    int y = 20;
    int z = x + y * 2;
    std::cout << z << std::endl;
}
```
**Execution Output**: `50`

### Smoke Test 2: If/Else Conditional (True Branch)
```cpp
int main() {
    int x = 15;
    if (x > 10) {
        std::cout << x << std::endl;
    } else {
        std::cout << 0 << std::endl;
    }
}
```
**Execution Output**: `15`

### Smoke Test 3: If/Else Conditional (False Branch)
```cpp
int main() {
    int x = 5;
    if (x > 20) {
        std::cout << x << std::endl;
    } else {
        std::cout << 0 << std::endl;
    }
}
```
**Execution Output**: `0`

### Smoke Test 4: While Loop Iteration
```cpp
int main() {
    int x = 0;
    while (x < 5) {
        std::cout << x << std::endl;
        x = x + 1;
    }
}
```
**Execution Output**: `0`, `1`, `2`, `3`, `4`

### Smoke Test 5: Optimizer Constant Folding
```cpp
int main() {
    int x = 10 + 20 * 2;
    std::cout << x << std::endl;
}
```
**Execution Output**: `50`
**Optimizer Actions**: Constant folds `20 * 2` -> `40` and `10 + 40` -> `50`, propagating constant values directly into target instructions.

### CodeFlow VM Execution Trace
For the while-loop program, execution produces genuine CodeFlow instructions:
`PUSH`, `LOAD`, `STORE`, `CMP_LT`, `JMP_IF_FALSE`, `JMP`, `PRINT`, `ADD`, `HALT`.
