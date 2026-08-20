# Compiler Phases

## Lexical Analysis
**Implemented.**
Uses deterministic character-by-character scanning to convert the character stream into meaningful tokens.
- **Tokenization:** Groups characters into `Token` objects (containing type, lexeme, line, column).
- **Longest-Match Principle:** Handled explicitly (e.g., `==` is matched instead of `=` followed by `=`).
- **Line & Column Tracking:** Accurately maintained for precise error reporting.
- **Lexical Errors:** Encountering an unrecognized character (e.g. `@`) throws a structured `LexicalError`.
- **Comments:** Omitted as they are not defined in the MiniLang grammar, avoiding undocumented behavior.

## Syntax Analysis
**Implemented.**
Uses Recursive Descent Parsing (LL(1) approach) to avoid left recursion. Generates a Parse Tree mapped into an Abstract Syntax Tree (AST).
- **Operator Precedence:** Enforced structurally through the call stack (Logical OR -> Logical AND -> Equality -> Relational -> Additive -> Multiplicative -> Unary -> Primary).
- **AST Construction:** Uses strongly typed dataclasses representing each node type (`Program`, `VariableDeclaration`, `BinaryExpression`, etc.) retaining the structure instead of a flat list.
- **Syntax Errors:** Reports precise line/column where unexpected tokens are found and throws `ParserError`.

## Semantic Analysis
**Implemented.**
Traverses the AST to ensure the logical correctness of the program through a formal Symbol Table and Type System.
- **Symbol Table & Scopes:** Tracks variable declarations and types, utilizing lexical scoping. Inner blocks correctly shadow outer blocks, and out-of-scope variables raise `SemanticError`.
- **Type Checking:** Ensures arithmetic operations are only performed on numeric types (`int`, `float`), logical operators only on `bool`, and `if`/`while` conditions strictly evaluate to `bool`.
- **Declaration Checking:** Enforces that variables are declared before assignment/use, and rejects duplicate declarations within the exact same scope.

## Intermediate Representation / TAC Generation
**Implemented.**
Generates structured Three-Address Code (TAC), breaking down complex expressions into simple instructions.
- **Why IR:** Decouples the frontend (syntax/semantics) from the backend (optimization/target generation), simplifying optimizations like constant folding and making target code translation a 1:1 map.
- **Temporaries (`t1`, `t2`):** Generated dynamically to hold partial results of nested expressions.
- **Labels (`L1`, `L2`):** Generated dynamically to represent jump destinations for control flow (`if`, `while`).
- **Conditional Jumps (`IF_FALSE`):** Explicitly evaluates conditions and branches around code blocks.

## Optimization
**Implemented.**
Accepts the generated TAC and runs robust analytical transformations to improve efficiency without modifying semantics.
- **Constant Folding:** Statically evaluates expressions where both operands are constants (`10 + 20` -> `30`). Safely defers operations like division-by-zero to runtime.
- **Constant Propagation:** Tracks known constant values and substitutes them into subsequent variable references, avoiding unnecessary variable accesses.
- **Algebraic Simplification:** Applies safe mathematical identities (e.g. `x * 0` -> `0`, `x + 0` -> `x`) eliminating useless ops.
- **Dead Code Elimination (DCE):** Analyzes unused intermediate temporaries (like `t1` that was folded away) and prunes them from the instruction list.
- **Safety:** Optimization explicitly tracks boundaries around labels and branches to preserve control-flow states. Original TAC is completely isolated from the Optimized TAC.

## Target Code Generation
**Implemented.**
Translates the Optimized TAC into linear instructions targeted for a custom stack-based Virtual Machine.
- **Push/Load/Store Architecture:** Translates three-address concepts (`t1 = x + y`) into stack manipulations (`LOAD x`, `LOAD y`, `ADD`, `STORE t1`).
- **Literal Identification:** Automatically discriminates between variable loads (`LOAD x`) and literal assignments (`PUSH 10`).
- **Instruction Set Expansion:** Flattens structured boolean branches and comparators into their raw instruction set counterparts (`CMP_LT`, `JMP_IF_FALSE`, etc).
- **HALT Instruction:** Appends an explicit termination signal required by the downstream VM interpreter.

## Virtual Machine
**Implemented.**
Executes the output of Target Code Generation natively.
- **Why a VM:** Allows simulating realistic memory, register, stack, and machine pointer mechanics in an isolated, safe memory enclosure rather than passing off output to system binaries or python's `eval`.
- **Memory & Stack Emulation:** Maintains an isolated heap map for storage arrays alongside a stack mapping for mathematical resolving.
- **Instruction Pointer:** Steps through the opcodes in sequence, correctly skipping labels as non-operational index markers and modifying the index safely during jump events (`JMP`, `JMP_IF_FALSE`).
- **Runtime Errors:** Catches mathematical collisions naturally (div-by-zero) wrapping Python's environment leaks cleanly into `VMRuntimeError`.
- **Execution Tracing:** Optional debugging hooks log real-time stack shifts and pointer values instruction-by-instruction, which is critical for visual rendering later.
