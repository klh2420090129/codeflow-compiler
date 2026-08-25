# CodeFlow — Project Report Screenshot Checklist

Use this checklist when taking screenshots of the running CodeFlow Web IDE (`http://127.0.0.1:5000`) for the final written report and presentation slides.

---

## Required Report Screenshots

- [ ] **1. Master CodeFlow IDE Overview**: Full browser window showing Source Editor (left), Pipeline Stage Bar (top right), and Phase Inspector (bottom right).
- [ ] **2. Source Editor & Controls**: Close-up of editor with line numbers, code highlighting, and the *Compile & Run* / *Clear* buttons.
- [ ] **3. Terminal Execution Output**: Bottom left output console displaying executed `print()` results (e.g. `50` or loop iterations `0, 1, 2`).
- [ ] **4. Lexer Token Table Inspector**: `LEXER` tab selected, showing columns for `TYPE`, `VALUE`, `LINE`, and `COL`.
- [ ] **5. AST Tree Inspector**: `PARSER` tab selected, showing the expandable nested node hierarchy (`Program` $\rightarrow$ `VariableDeclaration` $\rightarrow$ `BinaryExpression`).
- [ ] **6. Semantic Analysis & Symbol Table**: `SEMANTIC` tab selected, showing Scope tables (`Global`), variable identifiers, type signatures, and initialization status (`✓`).
- [ ] **7. Intermediate Representation (TAC)**: `TAC GEN` tab selected, showing two-digit indexed Three-Address Code instructions (`00: x = 10`, `01: t1 = y * 2`).
- [ ] **8. Control Flow Graph (CFG) Viewer**: `CFG` tab selected for a `while` loop program, showing Basic Blocks (`B0`, `B1`, `B2`, `B3`), `ENTRY`/`EXIT` badges, and color-coded branch tags (`➔ B1 (JUMP)`, `➔ B3 (FALSE)`).
- [ ] **9. Optimizer Split Comparison**: `OPTIMIZER` tab selected, showing side-by-side `BEFORE OPTIMIZATION` and `AFTER OPTIMIZATION` panes.
- [ ] **10. Optimization Explanation Trace**: Close-up of the Optimization Trace section showing step badges (`CONSTANT PROPAGATION`, `CONSTANT FOLDING`, `DEAD CODE ELIMINATION`), crossed-out before/after values, and pedagogical explanations.
- [ ] **11. Target Bytecode Inspector**: `CODEGEN` tab selected, showing linear stack instructions (`PUSH 10`, `STORE x`, `LOAD y`, `MUL`, `HALT`).
- [ ] **12. Virtual Machine State Trace**: `VM EXEC` tab selected with *Enable VM Trace* checked, showing step-by-step table with `IP`, `INSTRUCTION`, `STACK` snapshot (`[10, 20]`), and `MEMORY` heap (`{x: 10, y: 20}`).
- [ ] **13. Structured Compiler Error Card**: Triggering a semantic error (e.g. undeclared variable) showing the red error box with exact line/column tracking.
- [ ] **14. Automated Test Suite Terminal Output**: Command prompt showing `python -m pytest` executing with `193 passed in 0.36s`.
