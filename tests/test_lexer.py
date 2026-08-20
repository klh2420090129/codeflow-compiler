import pytest
from compiler.lexer.lexer import Lexer, TokenType
from compiler.errors import LexicalError

def get_tokens(source):
    lexer = Lexer(source)
    return lexer.tokenize()

def test_keywords():
    source = "let if else while print true false"
    tokens = get_tokens(source)
    expected_types = [
        TokenType.LET, TokenType.IF, TokenType.ELSE, 
        TokenType.WHILE, TokenType.PRINT, 
        TokenType.TRUE, TokenType.FALSE, TokenType.EOF
    ]
    assert len(tokens) == len(expected_types)
    for i, t_type in enumerate(expected_types):
        assert tokens[i].type == t_type

def test_identifiers():
    source = "x counter myVariable value123 _hidden"
    tokens = get_tokens(source)
    assert len(tokens) == 6 # 5 idents + EOF
    for i in range(5):
        assert tokens[i].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "x"
    assert tokens[4].lexeme == "_hidden"

def test_integers():
    source = "0 1 10 999"
    tokens = get_tokens(source)
    assert len(tokens) == 5
    for i in range(4):
        assert tokens[i].type == TokenType.INTEGER

def test_floats():
    source = "0.5 10.25 123.456"
    tokens = get_tokens(source)
    assert len(tokens) == 4
    for i in range(3):
        assert tokens[i].type == TokenType.FLOAT
    assert tokens[0].lexeme == "0.5"

def test_arithmetic_operators():
    source = "+ - * / %"
    tokens = get_tokens(source)
    expected = [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.MOD, TokenType.EOF]
    assert [t.type for t in tokens] == expected

def test_assignment_comparison_operators():
    source = "= == != < > <= >="
    tokens = get_tokens(source)
    expected = [
        TokenType.ASSIGN, TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL,
        TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, 
        TokenType.GREATER_EQUAL, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected

def test_logical_operators():
    source = "&& || !"
    tokens = get_tokens(source)
    expected = [TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.EOF]
    assert [t.type for t in tokens] == expected

def test_delimiters():
    source = "( ) { } ;"
    tokens = get_tokens(source)
    expected = [TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE, TokenType.SEMICOLON, TokenType.EOF]
    assert [t.type for t in tokens] == expected

def test_whitespace():
    source = "   \t\t\n \nlet  x\n="
    tokens = get_tokens(source)
    assert len(tokens) == 4 # let, x, =, EOF
    assert tokens[0].type == TokenType.LET
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[2].type == TokenType.ASSIGN

def test_line_column_tracking():
    source = "let x = 10;\nprint(x);"
    tokens = get_tokens(source)
    # let
    assert tokens[0].line == 1 and tokens[0].column == 1
    # x
    assert tokens[1].line == 1 and tokens[1].column == 5
    # =
    assert tokens[2].line == 1 and tokens[2].column == 7
    # 10
    assert tokens[3].line == 1 and tokens[3].column == 9
    # ;
    assert tokens[4].line == 1 and tokens[4].column == 11
    # print
    assert tokens[5].line == 2 and tokens[5].column == 1
    # EOF
    assert tokens[-1].line == 2 and tokens[-1].column == 10

def test_multi_character_longest_match():
    source = "> >= < <= = == ! !="
    tokens = get_tokens(source)
    expected = [
        TokenType.GREATER, TokenType.GREATER_EQUAL,
        TokenType.LESS, TokenType.LESS_EQUAL,
        TokenType.ASSIGN, TokenType.EQUAL_EQUAL,
        TokenType.NOT, TokenType.NOT_EQUAL,
        TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected

def test_keyword_vs_identifier():
    source = "let letx letter ifValue true falsey"
    tokens = get_tokens(source)
    expected = [
        TokenType.LET, TokenType.IDENTIFIER, TokenType.IDENTIFIER,
        TokenType.IDENTIFIER, TokenType.TRUE, TokenType.IDENTIFIER,
        TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected

def test_invalid_character():
    source = "let x = 10 @ 20;"
    with pytest.raises(LexicalError) as exc_info:
        get_tokens(source)
    assert "Unexpected character '@'" in str(exc_info.value)
    assert exc_info.value.line == 1
    assert exc_info.value.column == 12

def test_empty_source():
    source = ""
    tokens = get_tokens(source)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].line == 1
    assert tokens[0].column == 1

def test_eof_generation():
    source = "let x;"
    tokens = get_tokens(source)
    assert tokens[-1].type == TokenType.EOF
    assert tokens[-1].line == 1
    assert tokens[-1].column == 7
