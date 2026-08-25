# CodeFlow — Comprehensive Viva Questions & Answers

A curated collection of 45 Compiler Design viva examination questions grouped by phase, providing textbook theory along with project-specific implementation details.

---

## Group A: General Compiler Architecture

### Q1: What is a compiler, and how does it differ from an interpreter?
- **Short Answer**: A compiler translates an entire source program into an intermediate representation or target code before execution, while an interpreter translates and executes source statements line-by-line.
- **CodeFlow Implementation**: CodeFlow uses a hybrid approach: it compiles MiniLang into optimized TAC and then target bytecode, which is executed by an emulated stack-based Virtual Machine.

### Q2: What are the primary phases of a compiler?
- **Short Answer**: Lexical Analysis, Syntax Analysis, Semantic Analysis, Intermediate Code Generation, Code Optimization, Target Code Generation, and Runtime Execution.
- **CodeFlow Implementation**: Implements all 7 classical phases plus Basic Block/CFG analysis, an Optimization Explanation Engine, and VM state tracing.

### Q3: What is the purpose of decoupling the compiler frontend from the backend?
- **Short Answer**: It enables modularity, allowing multiple source frontends to target a single intermediate representation (IR), and multiple backend code generators to emit code for different target architectures from the same IR.
- **CodeFlow Implementation**: Frontend passes (Lexer, Parser, Semantic Analyzer) emit AST/Symbol Table; the middle-end works on Three-Address Code (TAC); the backend generates stack machine bytecode for the VM.

---

## Group B: Lexical Analysis

### Q4: What is the main responsibility of a Lexical Analyzer (Scanner)?
- **Short Answer**: To convert a raw character stream into a structured sequence of atomic tokens, stripping whitespace and comments while tracking line and column numbers.
- **CodeFlow Implementation**: Implemented in `compiler/lexer/lexer.py`, returning typed `Token` objects (`type`, `lexeme`, `line`, `column`).

### Q5: How does the Lexer distinguish between identifiers and keywords?
- **Short Answer**: When an alphanumeric word is scanned, it is looked up in a reserved keyword dictionary; if found, a keyword token is emitted, otherwise an identifier token is generated.
- **CodeFlow Implementation**: Uses a `KEYWORDS` dictionary mapping `'let'`, `'if'`, `'else'`, `'while'`, `'print'`, `'true'`, `'false'` to their respective `TokenType`.

### Q6: How does the Lexer handle multi-character operators like `==` and `<=`?
- **Short Answer**: Using lookahead: upon encountering a character like `=`, it inspects the next character (`=`) to decide whether to emit `EQUAL_EQUAL` or `ASSIGN`.
- **CodeFlow Implementation**: `Lexer.peek()` and `Lexer.advance()` handle 2-character tokens (`==`, `!=`, `<=`, `>=`, `&&`, `||`).

---

## Group C: Syntax Analysis & AST

### Q7: What is an LL(1) parser?
- **Short Answer**: A top-down parser that parses input from **L**eft-to-right, constructing a **L**eftmost derivation, using **1** token of lookahead without backtracking.
- **CodeFlow Implementation**: Implemented as a hand-crafted recursive-descent parser in `compiler/parser/parser.py`.

### Q8: What is the difference between a Parse Tree (Concrete Syntax Tree) and an Abstract Syntax Tree (AST)?
- **Short Answer**: A Parse Tree contains all grammatical tokens (parentheses, semicolons, keywords), whereas an AST retains only the semantic operators and operand nodes necessary for compilation.
- **CodeFlow Implementation**: AST nodes in `compiler/ast/nodes.py` store structural semantics (e.g. `BinaryExpression(left, op, right)`) without syntactic punctuation.

### Q9: How is operator precedence enforced in a recursive descent parser?
- **Short Answer**: By nesting grammar production rules in order of increasing precedence, so that higher precedence operators (multiplication) are parsed deeper in the recursion tree than lower precedence operators (addition).
- **CodeFlow Implementation**: `parse_expression()` calls `parse_logical_or()`, which cascades through `logical_and`, `equality`, `relational`, `additive`, `multiplicative`, `unary`, and `primary`.

### Q10: How does a recursive descent parser eliminate left recursion?
- **Short Answer**: Left recursion ($A \rightarrow A \alpha \mid \beta$) is rewritten into right recursion or parsed iteratively using `while` loops over the operator tokens.
- **CodeFlow Implementation**: Expressions use `while self.current_token.type in (PLUS, MINUS): ...` to iteratively bind operands without recursion loops.

---

## Group D: Semantic Analysis & Symbol Tables

### Q11: What is the role of Semantic Analysis?
- **Short Answer**: To verify context-sensitive requirements that cannot be captured by context-free grammars, including variable declaration checks, type checking, and scope resolution.
- **CodeFlow Implementation**: `compiler/semantic/analyzer.py` walks the AST, checking symbol scopes and validating operand types.

### Q12: How does a Symbol Table handle nested scopes?
- **Short Answer**: Using a tree or stack of `Scope` objects where each inner scope holds a pointer to its parent enclosing scope.
- **CodeFlow Implementation**: `SymbolTable` in `compiler/semantic/symbol_table.py` maintains `current_scope` with parent pointers, searching outward from local to global scope.

### Q13: What semantic error checks are performed in CodeFlow?
- **Short Answer**:
  1. Use of undeclared variables.
  2. Duplicate variable declarations within the same scope.
  3. Non-boolean condition expressions in `if` and `while` statements.
  4. Type mismatches in arithmetic and logical expressions.

---

## Group E: Intermediate Code Generation (TAC)

### Q14: What is Three-Address Code (TAC)?
- **Short Answer**: An intermediate representation where every instruction has at most one operator and at most three operand addresses (two sources, one destination).
- **CodeFlow Implementation**: Instructions in `compiler/intermediate/tac.py` represent `Assignment` ($x = y$), `Binary` ($t1 = a + b$), `Unary` ($t1 = -a$), `Label` ($L1:$), `Goto`, `ConditionalJump`, and `Print`.

### Q15: Why generate TAC instead of emitting machine code directly from the AST?
- **Short Answer**: TAC linearizes complex expression trees into simple instructions, making machine-independent optimizations (DCE, constant folding, CFG analysis) vastly simpler to implement.
- **CodeFlow Implementation**: TAC decouples AST traversal from target VM bytecode generation.

### Q16: How are boolean conditions translated in TAC?
- **Short Answer**: By emitting a comparison instruction followed by a conditional jump (`IF_FALSE condition GOTO label`) to skip the then-block or exit the loop.
- **CodeFlow Implementation**: `TACGenerator.visit_if_statement()` emits `ConditionalJump(cond, l_false, jump_if_false=True)`.

---

## Group F: Basic Blocks & Control Flow Graphs (CFG)

### Q17: What is a Basic Block?
- **Short Answer**: A maximal sequence of consecutive instructions that has a single entry point (the first instruction) and a single exit point (the last instruction), with no jumps into the middle.
- **CodeFlow Implementation**: `BasicBlock` in `compiler/analysis/basic_blocks.py` contains `id`, `instructions`, `start_index`, `end_index`, and predecessor/successor lists.

### Q18: What are the three standard leader rules for Basic Block identification?
- **Short Answer**:
  1. The first instruction of the program is a leader.
  2. Any target of a jump (`Goto` or `ConditionalJump`) is a leader.
  3. Any instruction immediately following a jump is a leader.
- **CodeFlow Implementation**: `BasicBlockAnalyzer.identify_leaders()` implements these three rules deterministically.

### Q19: What is a Control Flow Graph (CFG)?
- **Short Answer**: A directed graph where nodes represent Basic Blocks and edges represent possible control flow transitions between blocks.
- **CodeFlow Implementation**: `ControlFlowGraph` in `compiler/analysis/cfg.py` stores blocks and typed `CFGEdge` objects (`jump`, `true`, `false`, `fallthrough`).

### Q20: What is a loop back-edge in a CFG?
- **Short Answer**: An edge in a CFG that points from a downstream block back to a loop header block that dominates it.
- **CodeFlow Implementation**: In `while` loops, the unconditional jump at the end of the body emits a `jump` edge back to the condition header block (e.g. `B2 -> B1`).

---

## Group G: Code Optimization & Explanation Engine

### Q21: What is Constant Propagation?
- **Short Answer**: The process of replacing variable uses with their known compile-time constant values.
- **CodeFlow Implementation**: `Optimizer.constant_propagation()` tracks known constants and substitutes them into variable references.

### Q22: What is Constant Folding?
- **Short Answer**: The compile-time evaluation of operations whose operands are known constants (e.g. $10 + 40 \rightarrow 50$).
- **CodeFlow Implementation**: `Optimizer.constant_folding_and_algebraic()` calculates arithmetic and logical operations on literal operands at compile time.

### Q23: What is Algebraic Simplification?
- **Short Answer**: Using mathematical identities to eliminate redundant operations (e.g. $x + 0 \rightarrow x$, $x \cdot 1 \rightarrow x$, $x \cdot 0 \rightarrow 0$).
- **CodeFlow Implementation**: Pattern-matches identities on `Binary` TAC instructions.

### Q24: What is Dead Code Elimination (DCE)?
- **Short Answer**: The removal of instructions whose computed results are never read or used by any subsequent instruction.
- **CodeFlow Implementation**: `Optimizer.dead_code_elimination()` scans instruction uses and drops unused temporary variables (`t1`, `t2`).

### Q25: What is the Optimization Explanation Engine in CodeFlow?
- **Short Answer**: An event-driven subsystem that records an `OptimizationStep` at the moment an optimization rule fires, capturing the rule name, before/after values, and pedagogical rationale.
- **CodeFlow Implementation**: Populates `PipelineResult.optimization_steps` and `optimization_summary`, rendered in the web IDE.

---

## Group H: Target Code & Virtual Machine

### Q26: What is the difference between a stack-based machine and a register-based machine?
- **Short Answer**: A stack-based machine uses a LIFO operand stack for intermediate calculations (e.g. `PUSH`, `ADD`), while a register-based machine explicitly names source and destination registers (e.g. `ADD R1, R2, R3`).
- **CodeFlow Implementation**: Uses a stack-based target architecture modeled in `compiler/codegen/codegen.py` and `compiler/vm/virtual_machine.py`.

### Q27: How does CodeFlow's Virtual Machine prevent host environment pollution?
- **Short Answer**: The VM runs inside an isolated memory dictionary and stack array, executing only its explicit instruction set without invoking Python's native `exec()` or `eval()`.
- **CodeFlow Implementation**: `VirtualMachine` manages its own `ip`, `stack = []`, and `memory = {}`.

### Q28: What is an Instruction Pointer (IP)?
- **Short Answer**: A register or index that points to the memory address of the next instruction to be executed.
- **CodeFlow Implementation**: `VirtualMachine.ip` is an integer index pointing into `TargetProgram.instructions`.

---

## Group I: Software Engineering & Testing

### Q29: How many automated tests does CodeFlow have?
- **Short Answer**: 193 automated tests across all compiler modules, with 100% passing rate.

### Q30: How does the Unified Pipeline handle compiler errors gracefully?
- **Short Answer**: When an exception occurs, the orchestrator catches it, populates a structured `CompilerError` dict in `PipelineResult`, and returns the partial results accumulated up to that phase.
