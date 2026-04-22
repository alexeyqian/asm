import pytest
from lexer import Lexer, TT


def types(tokens):
    return [t.type for t in tokens]


def test_simple_tokens():
    src = "int x = 42;"
    toks = Lexer(src).tokenize()
    assert types(toks[:5]) == [TT.KW_INT, TT.IDENT, TT.EQ, TT.INT_LIT, TT.SEMI]
    assert toks[-1].type == TT.EOF


def test_literals_and_eof():
    src = "char c = '\\n'; char *s = \"hi\";"
    toks = Lexer(src).tokenize()
    # Expect: KW_CHAR IDENT EQ CHAR_LIT SEMI KW_CHAR STAR IDENT EQ STRING_LIT SEMI EOF
    expected_prefix = [TT.KW_CHAR, TT.IDENT, TT.EQ, TT.CHAR_LIT, TT.SEMI,
                       TT.KW_CHAR, TT.STAR, TT.IDENT, TT.EQ, TT.STRING_LIT, TT.SEMI]
    assert types(toks[:-1]) == expected_prefix
    assert toks[-1].type == TT.EOF


def test_comments_and_multiline_comments():
    src = """
    // line comment
    int a = 1; /* multi\nline \n comment */ a = a + 2;
    """
    toks = Lexer(src).tokenize()
    # tokens: KW_INT IDENT EQ INT_LIT SEMI IDENT EQ IDENT PLUS INT_LIT SEMI EOF
    expected = [TT.KW_INT, TT.IDENT, TT.EQ, TT.INT_LIT, TT.SEMI,
                TT.IDENT, TT.EQ, TT.IDENT, TT.PLUS, TT.INT_LIT, TT.SEMI, TT.EOF]
    assert types(toks) == expected


def test_for_loop_tokens():
    src = "for (int i = 0; i < 10; i++) { x = x + i; }"
    toks = Lexer(src).tokenize()
    expected = [
        TT.KW_FOR, TT.LPAREN, TT.KW_INT, TT.IDENT, TT.EQ, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.LT, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.PLUS_PLUS, TT.RPAREN,
        TT.LBRACE, TT.IDENT, TT.EQ, TT.IDENT, TT.PLUS, TT.IDENT, TT.SEMI, TT.RBRACE,
        TT.EOF,
    ]
    assert types(toks) == expected
