# MiniLang Grammar & Token Specification

## Token Categories
- `KEYWORD`: `let`, `if`, `else`, `while`, `print`, `true`, `false`
- `IDENTIFIER`: `[a-zA-Z_][a-zA-Z0-9_]*`
- `INTEGER`: `[0-9]+`
- `FLOAT`: `[0-9]+\.[0-9]+`
- `BOOLEAN`: `true` | `false`
- `OPERATOR`: `+`, `-`, `*`, `/`, `%`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!`
- `DELIMITER`: `(`, `)`, `{`, `}`, `;`
- `EOF`: End of file

## Grammar (EBNF)
```ebnf
Program -> Statement* EOF

Statement -> VariableDeclaration
           | Assignment
           | IfStatement
           | WhileStatement
           | PrintStatement
           | Block

VariableDeclaration -> "let" Identifier "=" Expression ";"
Assignment -> Identifier "=" Expression ";"
IfStatement -> "if" "(" Expression ")" Block ( "else" Block )?
WhileStatement -> "while" "(" Expression ")" Block
PrintStatement -> "print" "(" Expression ")" ";"
Block -> "{" Statement* "}"

Expression -> LogicalOr

LogicalOr -> LogicalAnd ( "||" LogicalAnd )*
LogicalAnd -> Equality ( "&&" Equality )*
Equality -> Relational ( ("==" | "!=") Relational )*
Relational -> Additive ( ("<" | "<=" | ">" | ">=") Additive )*
Additive -> Multiplicative ( ("+" | "-") Multiplicative )*
Multiplicative -> Unary ( ("*" | "/" | "%") Unary )*
Unary -> ("!" | "-") Unary | Primary

Primary -> Identifier
         | INTEGER
         | FLOAT
         | BOOLEAN
         | "(" Expression ")"
```
