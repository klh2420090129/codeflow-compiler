# CodeFlow — Live Project Demonstration Script

**Estimated Duration**: 5–7 Minutes  
**Target Audience**: Academic Evaluators, Project Reviewers, and Viva Examiners.

---

### Phase 1: Introduction (0:00 – 0:45)
1. **Action**: Open browser at `http://127.0.0.1:5000`.
2. **Presenter Statement**:  
   > *"Good morning. This is **CodeFlow**, an interactive compiler design laboratory and execution system. It takes source code written in a custom strongly typed language, MiniLang, and processes it through every classical phase of compiler engineering: from lexical scanning to AST construction, semantic analysis, intermediate TAC generation, basic block & CFG analysis, multi-pass optimization with real-time reasoning explanations, target bytecode generation, and virtual machine execution."*

---

### Phase 2: Compiling a Program (0:45 – 1:30)
1. **Action**: Select **Basic Setup** from the dropdown (`let x = 10; let y = 20; let z = x + y * 2; print(z);`).
2. **Action**: Check **Enable VM Trace** and click **Compile & Run**.
3. **Presenter Statement**:  
   > *"When we click 'Compile & Run', the source code is sent to the Flask backend. Notice the execution output in the terminal below shows `50`. Across the top, all 8 pipeline stages have lit up green, indicating successful end-to-end compilation."*

---

### Phase 3: Inspecting Frontend Stages (1:30 – 2:30)
1. **Action**: Click on the **LEXER** stage.
   - *Show*: Token table showing types (`LET`, `IDENTIFIER`, `ASSIGN`, `INTEGER`, `STAR`, `SEMICOLON`), values, lines, and columns.
   - *Statement*: *"The Lexer performs deterministic character scanning with exact coordinate tracking."*
2. **Action**: Click on the **PARSER** stage.
   - *Show*: Expandable visual AST tree showing `VariableDeclaration`, `BinaryExpression`, and `PrintStatement` nodes.
   - *Statement*: *"Our recursive-descent parser validates syntax and builds this typed AST enforcing operator precedence."*
3. **Action**: Click on the **SEMANTIC** stage.
   - *Show*: Symbol Table scope table listing variables (`x`, `y`, `z`), types (`int`), and initialization status (`✓`).
   - *Statement*: *"Semantic analysis validates variable declarations and type safety before any code generation occurs."*

---

### Phase 4: TAC & Control Flow Graph (2:30 – 3:30)
1. **Action**: Click on the **TAC GEN** stage.
   - *Show*: Linear Three-Address Code with generated temporaries (`t1 = y * 2`, `t2 = x + t1`, `z = t2`).
   - *Statement*: *"The intermediate representation linearizes nested expressions into atomic 3-address instructions."*
2. **Action**: Click on the **CFG** stage.
   - *Show*: Basic blocks and directed edges with entry/exit tags.
3. **Action**: Change example to **Loops (While)** and click **Compile & Run**, then click **CFG**.
   - *Show*: Blocks `B0`, `B1` (loop header), `B2` (body), `B3` (exit), and highlight the back edge `B2 -> B1 (JUMP)`.
   - *Statement*: *"The CFG engine uses 3 standard leader rules to partition TAC into Basic Blocks and construct a control flow graph, explicitly identifying the loop header, true/false branches, and the back-edge."*

---

### Phase 5: Optimization & Explanation Engine (3:30 – 4:45)
1. **Action**: Switch back to **Basic Setup**, click **Compile & Run**, then click **OPTIMIZER**.
   - *Show*: Summary Card (9 steps, 6 $\rightarrow$ 4 instructions, 33.33% reduction), side-by-side BEFORE/AFTER panes, and the **Optimization Explanation Trace**.
2. **Presenter Statement**:  
   > *"Here is one of our key features: the Optimization Explanation Engine. On the left is the unoptimized TAC; on the right is the optimized TAC. Below, the compiler generates a real-time explanation trace for every transformation. For example, Step 1 shows Constant Propagation replacing variable `y` with `20`, followed by Constant Folding evaluating `20 * 2` to `40`, and Dead Code Elimination pruning the temporary `t1` because it is no longer referenced downstream."*

---

### Phase 6: Bytecode & Virtual Machine Execution (4:45 – 5:45)
1. **Action**: Click on the **CODEGEN** stage.
   - *Show*: Target bytecode instructions (`PUSH 10`, `STORE x`, `PUSH 20`, `STORE y`, `LOAD y`, `MUL`, etc.).
   - *Statement*: *"Target code generation emits stack-based bytecode instructions ready for execution."*
2. **Action**: Click on the **VM EXEC** stage.
   - *Show*: Step-by-step trace table showing Instruction Pointer (IP), Instruction, Operand Stack snapshot `[10, 20]`, and Memory Heap state `{x: 10, y: 20}`.
   - *Statement*: *"Our custom Virtual Machine executes the target bytecode within an isolated stack and memory environment, recording an exact execution trace for debugging."*

---

### Phase 7: Error Handling Demonstration (5:45 – 6:30)
1. **Action**: Select **Semantic Error** from the dropdown (`let a = 10; let b = c + 5; print(b);`) and click **Compile & Run**.
   - *Show*: Pipeline stops at `SEMANTIC` (red ✗), downstream stages (`TAC`, `CFG`, `OPTIMIZER`, `CODEGEN`, `VM`) marked as skipped (—).
   - *Show*: Inspector displaying a clear red error card: *"Semantic Error: Variable 'c' is not declared. Line 2, Column 9"*.
   - *Statement*: *"When an error occurs, CodeFlow gracefully catches it, halts invalid downstream phases while preserving previous results, and reports exact line and column locations without exposing Python tracebacks."*

---

### Phase 8: Conclusion (6:30 – 7:00)
1. **Presenter Statement**:  
   > *"In summary, CodeFlow represents a complete, transparent, and academically defensible compiler laboratory. All 193 automated tests in our suite pass with zero regressions. Thank you, and we welcome any questions or live code tests you would like to run."*
