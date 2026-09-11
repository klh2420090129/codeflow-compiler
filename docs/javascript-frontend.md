# CodeFlow — Experimental JavaScript Frontend Documentation

## 1. Overview & Positioning

**JavaScript (Experimental)** — a controlled JavaScript subset frontend mapped into the CodeFlow compiler pipeline.

> [!NOTE]
> **Academic & Architectural Scope**:
> CodeFlow does **not** implement a full ECMAScript engine, nor does it delegate execution to Node.js, Deno, Bun, browser JavaScript runtimes, or any external interpreters. Instead, it demonstrates CodeFlow's multi-language compiler capability by accepting a controlled JavaScript subset, translating it into the canonical CodeFlow AST/IR, and reusing 100% of the downstream compiler pipeline:
> - Semantic Analysis (symbol table, scopes, type checking)
> - Three-Address Code (TAC) Generation
> - Basic Block Partitioning (leader analysis)
> - Control Flow Graph (CFG) Construction
> - Multi-Pass Optimizer (constant folding, constant propagation, dead code elimination)
> - Target Code Generator
> - CodeFlow Stack-Based Virtual Machine (VM) and Execution Trace

---

## 2. Architecture & Pipeline Flow

```text
JavaScript Source Code
       ↓
compiler.frontends.javascript.JSLexer
       ↓ (JavaScript Tokens: keywords, identifiers, numbers, operators)
compiler.frontends.javascript.JSParser
       ↓ (Recursive-Descent Parsing & Const Reassignment Enforcement)
CodeFlow AST / IR (nodes.Program, nodes.VariableDeclaration, nodes.Assignment, etc.)
       ↓
Existing CodeFlow Semantic Analysis (Symbol Table, Scopes, Type Checking)
       ↓
Existing CodeFlow TAC Generation (Three-Address Code)
       ↓
Existing Basic Block Partitioning & CFG Builder
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

## 3. Supported JavaScript Subset

| Category | Supported Constructs | Syntax Example | CodeFlow AST Representation |
| :--- | :--- | :--- | :--- |
| **Variable Declarations** | `let`, `const`, `var` | `let x = 10;`<br>`const MAX = 100;` | `nodes.VariableDeclaration` |
| **Variable Assignment** | Single identifier reassignment | `x = 25;` | `nodes.Assignment` |
| **Arithmetic Operators** | `+`, `-`, `*`, `/`, `%` | `let z = (x + y) * 2 % 5;` | `nodes.BinaryExpression` |
| **Unary Operators** | `-`, `!` | `let y = -x;`<br>`let notOk = !flag;` | `nodes.UnaryExpression` |
| **Comparison Operators** | `<`, `>`, `<=`, `>=`, `==`, `!=` | `if (x >= 18) { ... }` | `nodes.BinaryExpression` |
| **Logical Operators** | `&&`, `\|\|`, `!` | `let ok = isValid && !hasError;` | `nodes.BinaryExpression` |
| **Conditionals** | `if`, `if/else`, `else if` | `if (x > 0) { ... } else { ... }` | `nodes.IfStatement` |
| **Loops** | `while` loop | `while (count < 5) { count = count + 1; }` | `nodes.WhileStatement` |
| **Output / Logging** | `console.log(expr)` | `console.log(z);` | `nodes.PrintStatement` |
| **Literals** | Integers, Floats, Booleans (`true`, `false`) | `42`, `3.14`, `true`, `false` | `nodes.Literal` |
| **Compound Blocks** | `{ ... }` | `{ let local = 1; }` | `nodes.Block` |
| **Comments** | Single-line `//`, Multi-line `/* ... */` | `// comment`<br>`/* block */` | Skipped during lexical analysis |

---

## 4. Semantic Validation & `const` Enforcement

- **`const` Invariant**: Variables declared with `const` require an initializer at declaration and are tracked by the frontend parser. Attempting to reassign a `const` variable generates an explicit `SemanticError`:
  `TypeError: Assignment to constant variable '<identifier>'`
- **Undeclared Variables**: Referencing identifiers not present in the active symbol table scope is detected by CodeFlow's semantic analyzer.
- **Type Checking**: Conditions in `if` and `while` must evaluate to boolean types; invalid operand types generate semantic errors.

---

## 5. Explicitly Unsupported Constructs

CodeFlow purposefully restricts the JavaScript frontend to a verifiable subset. The following constructs are explicitly detected and rejected with informative, line/column-precise compiler errors:

- **Functions & Closures**: `function`, arrow functions (`=>`), callbacks, generators, `async`/`await`
- **Classes & Prototypes**: `class`, `new`, `this`, `super`, `extends`, `constructor`
- **Objects & Arrays**: Object literals `{ key: value }`, array literals `[...]`, indexing `a[i]`, property access `obj.prop`
- **Modules**: `import`, `export`, `require`, `default`
- **Exceptions**: `try`, `catch`, `finally`, `throw`
- **Control Flow**: `for`, `for...in`, `for...of`, `do/while`, `switch`, `case`, `break`, `continue`
- **Strict Equality (`===`, `!==`)**: Rejected explicitly with recommendation to use `==` or `!=` to maintain fidelity with CodeFlow's type system
- **Strings & Runtime Values**: General string manipulation, template literals, `null`, `undefined`
- **Dynamic Operators**: `typeof`, `instanceof`, `delete`, `eval`, `void`
- **DOM & Platform APIs**: `window`, `document`, Node.js modules, network APIs

---

## 6. Verification & End-to-End Examples

### Smoke Test 1: Arithmetic & Operator Precedence
```javascript
let x = 10;
let y = 20;
let z = x + y * 2;
console.log(z);
```
**Execution Output**: `50`

### Smoke Test 2: If/Else Conditional
```javascript
let x = 15;
if (x > 10) {
    console.log(x);
} else {
    console.log(0);
}
```
**Execution Output**: `15`

### Smoke Test 3: False Branch Execution
```javascript
let x = 5;
if (x > 20) {
    console.log(x);
} else {
    console.log(0);
}
```
**Execution Output**: `0`

### Smoke Test 4: While Loop Iteration
```javascript
let x = 0;
while (x < 5) {
    console.log(x);
    x = x + 1;
}
```
**Execution Output**: `0`, `1`, `2`, `3`, `4`

### Smoke Test 5: Multi-Pass Optimizer Constant Folding
```javascript
let x = 10 + 20 * 2;
console.log(x);
```
**Execution Output**: `50`
**Optimizer Actions**: Constant folds `20 * 2` -> `40`, `10 + 40` -> `50`, and constant propagates `50` directly into target instructions.

### CodeFlow VM Stack Execution Trace
For the while loop above, instructions genuinely executed by CodeFlow VM include:
`PUSH`, `LOAD`, `STORE`, `CMP_LT`, `JMP_IF_FALSE`, `JMP`, `PRINT`, `ADD`, `HALT`.
