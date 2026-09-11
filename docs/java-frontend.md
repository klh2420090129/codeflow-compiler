# CodeFlow — Experimental Java Frontend Documentation

## 1. Overview & Positioning

**Java (Experimental)** — a controlled Java subset frontend mapped into the CodeFlow compiler pipeline.

> [!NOTE]
> **Academic & Architectural Scope**:
> CodeFlow does **not** implement a complete Java virtual machine or language specification, nor does it rely on `javac`, JVM bytecode execution, `jshell`, or any external Java runtime. Instead, it demonstrates CodeFlow's multi-language compiler design by translating a controlled Java program subset into canonical CodeFlow AST/IR nodes and reusing 100% of the downstream compiler phases:
> - Semantic Analysis (symbol table, scopes, type checking)
> - Three-Address Code (TAC) Generation
> - Basic Block Partitioning (leader analysis)
> - Control Flow Graph (CFG) Construction
> - Multi-Pass Optimizer (constant folding, constant propagation, dead code elimination)
> - Target Code Generator (stack bytecode)
> - CodeFlow Stack Virtual Machine (VM) and Execution Trace

---

## 2. Java Program Wrapper Architecture

Java source code in CodeFlow is organized under a standard canonical educational entry-point wrapper:

```java
public class Main {
    public static void main(String[] args) {
        int x = 10;
        int y = 20;
        System.out.println(x + y);
    }
}
```

The frontend verifies this structural contract:
- The top-level class must be `public class Main`.
- The entry method must be `public static void main(String[] args)`.
- Statements inside `main` are extracted and compiled into CodeFlow AST statements.
- Additional classes, additional methods, fields, constructors, inheritance, and interfaces are rejected with clear compiler errors.

---

## 3. Pipeline Flow

```text
Java Source Code
       ↓
compiler.frontends.java.JavaLexer
       ↓ (Java Tokens: keywords, primitive types, operators, delimiters)
compiler.frontends.java.JavaParser
       ↓ (Class Wrapper Extraction, Static Type Validation & Const/Final Enforcement)
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

## 4. Supported Java Subset

| Construct | Syntax | CodeFlow Mapping |
| :--- | :--- | :--- |
| **Class Wrapper** | `public class Main { public static void main(String[] args) { ... } }` | Extracted into `nodes.Program` |
| **Integer Types** | `int x;`<br>`int x = 10;` | `nodes.VariableDeclaration` (`INTEGER`) |
| **Floating Types**| `double y;`<br>`double y = 2.5;` | `nodes.VariableDeclaration` (`FLOAT`) |
| **Boolean Types** | `boolean flag;`<br>`boolean flag = true;` | `nodes.VariableDeclaration` (`BOOLEAN`) |
| **Final Variables**| `final int MAX = 100;` | Enforced immutable in frontend parser |
| **Assignments**   | `x = 20;`<br>`y = y + 1.5;` | `nodes.Assignment` |
| **Arithmetic**    | `+`, `-`, `*`, `/`, `%` | `nodes.BinaryExpression` |
| **Unary**         | `-x`, `!flag` | `nodes.UnaryExpression` |
| **Comparisons**   | `<`, `>`, `<=`, `>=`, `==`, `!=` | `nodes.BinaryExpression` |
| **Logical**       | `&&`, `\|\|`, `!` | `nodes.BinaryExpression` |
| **Conditionals**  | `if (cond) { ... } else { ... }`<br>`else if (cond) { ... }` | `nodes.IfStatement` |
| **Loops**         | `while (condition) { ... }` | `nodes.WhileStatement` |
| **Console Output**| `System.out.println(expr);` | `nodes.PrintStatement` |
| **Compound Blocks**| `{ ... }` | `nodes.Block` |
| **Comments**      | `// comment`, `/* block comment */` | Ignored during lexing |

---

## 5. Static Typing Rules

The Java frontend enforces static typing:
1. **Type Incompatibility**: Assigning boolean expressions to numeric variables (`int x = true;`) or numeric expressions to boolean variables (`boolean b = 10;`) produces explicit `SemanticError`: `Type mismatch`.
2. **Precision Loss**: Assigning `double` expressions to `int` variables without casting is rejected.
3. **Condition Typing**: `if` and `while` conditions must strictly evaluate to boolean types.
4. **Final Immobility**: Reassigning a `final` variable produces a `SemanticError: Cannot assign a value to final variable`.

---

## 6. Explicitly Unsupported Constructs

The following Java features are explicitly out of scope for this subset and rejected with line/column-accurate errors:
- Multiple classes or non-Main class names
- User-defined methods, constructors, instance variables
- Inheritance (`extends`), interfaces (`implements`), abstract classes
- Object instantiation (`new`), arrays beyond `String[] args`, generics
- Control flow statements: `for`, `do-while`, `switch`, `case`, `break`, `continue`
- Exceptions: `try`, `catch`, `finally`, `throw`, `throws`
- Packages (`package`), imports (`import`), modules
- Strings as runtime values (only permitted in the wrapper signature)
- Dynamic reflection, annotations, lambdas, streams

---

## 7. Verification & End-to-End Examples

### Smoke Test 1: Arithmetic & Operator Precedence
```java
public class Main {
    public static void main(String[] args) {
        int x = 10;
        int y = 20;
        int z = x + y * 2;
        System.out.println(z);
    }
}
```
**Execution Output**: `50`

### Smoke Test 2: If/Else Conditional (True Branch)
```java
public class Main {
    public static void main(String[] args) {
        int x = 15;
        if (x > 10) {
            System.out.println(x);
        } else {
            System.out.println(0);
        }
    }
}
```
**Execution Output**: `15`

### Smoke Test 3: If/Else Conditional (False Branch)
```java
public class Main {
    public static void main(String[] args) {
        int x = 5;
        if (x > 20) {
            System.out.println(x);
        } else {
            System.out.println(0);
        }
    }
}
```
**Execution Output**: `0`

### Smoke Test 4: While Loop Iteration
```java
public class Main {
    public static void main(String[] args) {
        int x = 0;
        while (x < 5) {
            System.out.println(x);
            x = x + 1;
        }
    }
}
```
**Execution Output**: `0`, `1`, `2`, `3`, `4`

### Smoke Test 5: Optimizer Constant Folding
```java
public class Main {
    public static void main(String[] args) {
        int x = 10 + 20 * 2;
        System.out.println(x);
    }
}
```
**Execution Output**: `50`
**Optimizer Actions**: Constant folds `20 * 2` -> `40` and `10 + 40` -> `50`, propagating the constant value directly.

### CodeFlow VM Stack Execution Trace
For the while-loop program, execution produces real CodeFlow instructions:
`PUSH`, `LOAD`, `STORE`, `CMP_LT`, `JMP_IF_FALSE`, `JMP`, `PRINT`, `ADD`, `HALT`.
