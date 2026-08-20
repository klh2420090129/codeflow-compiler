# Target Machine Architecture

The CodeFlow virtual machine represents an educational stack-based architecture designed for executing target instructions generated from MiniLang code. 

## Memory Model
1. **Instruction Memory:** A sequential list of `TargetInstruction` objects containing the executable code.
2. **Instruction Pointer (IP):** Tracks the current execution index.
3. **Operand Stack:** A Last-In-First-Out (LIFO) stack primarily used to temporarily hold literals, evaluated conditions, and numeric operators during expression calculations.
4. **Variable Storage:** A dictionary mapping identifiers (variable names) to their respective evaluated runtime values. Both user variables (`x`, `y`) and TAC temporaries (`t1`, `t2`) exist here.

## Data Types
The architecture natively manipulates dynamically typed data corresponding directly to MiniLang variables:
- `Integer` (represented as standard numbers)
- `Float` (represented as standard numbers)
- `Boolean` (represented intrinsically as python booleans)

## Instruction Set Architecture (ISA)

### Memory Operations
- `PUSH <value>`: Pushes a literal value onto the operand stack.
- `LOAD <var>`: Fetches the value of the variable `<var>` from storage and pushes it onto the operand stack.
- `STORE <var>`: Pops the top value from the operand stack and saves it in the variable `<var>`.

### Arithmetic Operations
Pops the top two values (Right, then Left), performs the operation, and pushes the result.
- `ADD`: (Left + Right)
- `SUB`: (Left - Right)
- `MUL`: (Left * Right)
- `DIV`: (Left / Right)
- `MOD`: (Left % Right)

### Unary Operations
Pops the top value, performs the operation, and pushes the result.
- `NEG`: (-Value)
- `NOT`: (!Value)

### Comparison Operations
Pops the top two values (Right, then Left), performs the comparison, and pushes the resulting boolean.
- `CMP_LT`: (Left < Right)
- `CMP_GT`: (Left > Right)
- `CMP_LE`: (Left <= Right)
- `CMP_GE`: (Left >= Right)
- `CMP_EQ`: (Left == Right)
- `CMP_NE`: (Left != Right)

### Logical Operations
Pops the top two values, performs logic, and pushes the resulting boolean.
- `AND`: (Left && Right)
- `OR`: (Left || Right)

### Control Flow
- `LABEL <name>`: A non-operational pseudo-instruction marking a destination offset for jump instructions.
- `JMP <label>`: Unconditionally sets the Instruction Pointer (IP) to the offset of `<label>`.
- `JMP_IF_FALSE <label>`: Pops the top value from the operand stack. If it is `False`, jumps to `<label>`.
- `JMP_IF_TRUE <label>`: Pops the top value from the operand stack. If it is `True`, jumps to `<label>`.

### System
- `PRINT`: Pops the top value from the operand stack and logs it to output.
- `HALT`: Terminate execution immediately.
