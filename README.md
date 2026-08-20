# CodeFlow

**Subtitle: Interactive Compiler Design Laboratory**

CodeFlow is a fully working, academically defensible compiler-based source code processing system designed to demonstrate the major phases of compiler design. It accepts source code written in a custom minimal programming language and processes it through a strict pipeline, finishing with execution on a custom Python-backed Virtual Machine.

CodeFlow is accompanied by a sophisticated developer-tool interface that visually communicates the inner workings of every compiler phase.

---

## 🛠 Supported Language (MiniLang)
MiniLang is a strongly typed, minimal educational programming language featuring:
- **Variable Declarations**: `let x = 10;`, `let y = 15.5;`
- **Control Flow**: `if/else`, `while`
- **Data Types**: Integers, Floats, Booleans (`true`, `false`)
- **Arithmetic & Logic**: `+`, `-`, `*`, `/`, `%`, `>`, `<`, `==`, `!=`, `&&`, `||`, `!`
- **I/O**: `print(x);`

---

## 🔄 Compiler Pipeline
CodeFlow avoids simulation and executes a genuine multi-pass compiler architecture:

1. **Lexical Analysis (Lexer)**: Transforms raw source code into structured `Token` streams.
2. **Syntax Analysis (Parser)**: Recursive descent (LL(1)) algorithm to build an Abstract Syntax Tree (AST).
3. **Semantic Analysis**: Type checking, scope resolution, and Symbol Table generation.
4. **Intermediate Representation**: Translation into Three-Address Code (TAC).
5. **Optimization**: Applies Constant Folding, Constant Propagation, Algebraic Simplification, and Dead Code Elimination over the TAC.
6. **Target Code Generation**: Maps optimized TAC to stack-based Virtual Machine instructions (`PUSH`, `LOAD`, `STORE`, `ADD`, `CMP_LT`, `JMP`, etc).
7. **Virtual Machine (VM)**: A custom bytecode interpreter that executes the target instructions within a sandboxed memory and stack structure.

---

## 🚀 Installation

Ensure you have **Python 3.10+** installed.

1. Clone or download the repository.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

---

## 🖥 How to Run (Web Interface)

The primary way to use CodeFlow is through its interactive laboratory frontend. 

Start the server:
```bash
python app.py
```

1. Open your browser and navigate to `http://127.0.0.1:5000`.
2. Use the **Source Editor** on the left to write MiniLang code. Alternatively, select an example from the top dropdown.
3. Check **Enable VM Trace** if you wish to see step-by-step memory mutations.
4. Click **Compile & Run**.
5. Click on the **Pipeline Stages** (`LEXER`, `PARSER`, etc.) to inspect the exact data generated at each phase!

---

## 💻 CLI Usage

You can bypass the web interface and compile directly from the terminal to see structured JSON pipeline output:
```bash
python -m compiler.pipeline examples/basic.cf
```

To run only the VM (if you want to test bytecode manually):
```bash
python -m compiler.vm.virtual_machine examples/basic.cf
```

---

## 🧪 Testing

CodeFlow maintains rigorous test-driven compliance. All compiler phases are individually verified.

To run the full test suite (173 passing tests):
```bash
python -m pytest
```
