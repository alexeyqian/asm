import pytest
from lexer import Lexer, TT, LexError


def types(tokens):
    return [t.type for t in tokens]


def test_nested_for_loops():
    src = 'for (int i = 0; i < 3; i++) { for (int j = 0; j < 2; j++) { x = x + i * j; } }'
    toks = Lexer(src).tokenize()
    expected = [
        TT.KW_FOR, TT.LPAREN, TT.KW_INT, TT.IDENT, TT.EQ, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.LT, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.PLUS_PLUS, TT.RPAREN,
        TT.LBRACE,

        TT.KW_FOR, TT.LPAREN, TT.KW_INT, TT.IDENT, TT.EQ, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.LT, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.PLUS_PLUS, TT.RPAREN,
        TT.LBRACE,

        TT.IDENT, TT.EQ, TT.IDENT, TT.PLUS, TT.IDENT, TT.STAR, TT.IDENT, TT.SEMI,
        TT.RBRACE, TT.RBRACE,
        TT.EOF,
    ]
    assert types(toks) == expected


def test_unterminated_string_raises():
    with pytest.raises(LexError):
        Lexer('"unterminated').tokenize()


def test_complex_bitwise_expression():
    src = 'a = b << 2 | c & ~d;'
    toks = Lexer(src).tokenize()
    expected = [TT.IDENT, TT.EQ, TT.IDENT, TT.LSHIFT, TT.INT_LIT, TT.PIPE, TT.IDENT, TT.AMP, TT.TILDE, TT.IDENT, TT.SEMI, TT.EOF]
    assert types(toks) == expected


def test_escape_in_string():
    src = 'char *s = "She said \\\"hi\\\"";'
    toks = Lexer(src).tokenize()
    expected = [TT.KW_CHAR, TT.STAR, TT.IDENT, TT.EQ, TT.STRING_LIT, TT.SEMI, TT.EOF]
    assert types(toks) == expected


def test_compound_and_increments():
    src = 'x += 1; y--; z *= 2;'
    toks = Lexer(src).tokenize()
    expected = [
        TT.IDENT, TT.PLUS_EQ, TT.INT_LIT, TT.SEMI,
        TT.IDENT, TT.MINUS_MINUS, TT.SEMI,
        TT.IDENT, TT.STAR_EQ, TT.INT_LIT, TT.SEMI,
        TT.EOF,
    ]
    assert types(toks) == expected
