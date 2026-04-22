from __future__ import annotations
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import Iterator

class TT(Enum):
    # ── Literals ──────────────────────────────────────────────────────────
    INT_LIT    = auto()   # 42  0xFF  0b1010  0777
    CHAR_LIT   = auto()   # 'a'  '\n'
    STRING_LIT = auto()   # "hello"
 
    # ── Identifiers & keywords ────────────────────────────────────────────
    IDENT      = auto()
 
    # Types
    KW_INT     = auto()
    KW_CHAR    = auto()
    KW_VOID    = auto()
 
    # Control flow
    KW_IF      = auto()
    KW_ELSE    = auto()
    KW_WHILE   = auto()
    KW_FOR     = auto()
    KW_RETURN  = auto()
    KW_BREAK   = auto()
    KW_CONTINUE= auto()
 
    # ── Operators ─────────────────────────────────────────────────────────
    PLUS       = auto()   # +
    MINUS      = auto()   # -
    STAR       = auto()   # *
    SLASH      = auto()   # /
    PERCENT    = auto()   # %
 
    AMP        = auto()   # &
    PIPE       = auto()   # |
    CARET      = auto()   # ^
    TILDE      = auto()   # ~
    LSHIFT     = auto()   # <<
    RSHIFT     = auto()   # >>
 
    AMP_AMP    = auto()   # &&
    PIPE_PIPE  = auto()   # ||
    BANG       = auto()   # !
 
    EQ         = auto()   # =
    EQ_EQ      = auto()   # ==
    BANG_EQ    = auto()   # !=
    LT         = auto()   # <
    LT_EQ      = auto()   # <=
    GT         = auto()   # >
    GT_EQ      = auto()   # >=
 
    PLUS_EQ    = auto()   # +=
    MINUS_EQ   = auto()   # -=
    STAR_EQ    = auto()   # *=
    SLASH_EQ   = auto()   # /=
    PLUS_PLUS  = auto()   # ++
    MINUS_MINUS= auto()   # --
 
    # ── Delimiters ────────────────────────────────────────────────────────
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACE     = auto()   # {
    RBRACE     = auto()   # }
    LBRACKET   = auto()   # [
    RBRACKET   = auto()   # ]
    SEMI       = auto()   # ;
    COMMA      = auto()   # ,
    DOT        = auto()   # .
    ARROW      = auto()   # ->
 
    # ── Special ───────────────────────────────────────────────────────────
    EOF        = auto()
    UNKNOWN    = auto()   # anything we didn't recognise
 
KEYWORDS: dict[str, TT] = {
    "int":      TT.KW_INT,
    "char":     TT.KW_CHAR,
    "void":     TT.KW_VOID,
    "if":       TT.KW_IF,
    "else":     TT.KW_ELSE,
    "while":    TT.KW_WHILE,
    "for":      TT.KW_FOR,
    "return":   TT.KW_RETURN,
    "break":    TT.KW_BREAK,
    "continue": TT.KW_CONTINUE,
}

@dataclass
class Token:
    type:   TT
    value:  str
    line:   int
    col:    int
 
    def __repr__(self) -> str:
        return f"Token({self.type.name:<15} {self.value!r:<20} line={self.line} col={self.col})"

class LexError(Exception):
    def __init__(self, msg: str, line: int, col: int):
        super().__init__(f"[line {line}, col {col}] LexError: {msg}")
        self.line = line
        self.col  = col
        
class Lexer:
    # Compiled regex for integer literals (hex / binary / octal / decimal)
    _INT_RE = re.compile(r'0[xX][0-9a-fA-F]+|0[bB][01]+|0[0-7]*|[1-9][0-9]*')
    
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0 # current character index
        self.line = 1
        self.col = 1
        
    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else "\0"
    
    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch
    
    def _current_pos(self) -> tuple[int, int]:
        return self.line, self.col
    
    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            ch = self._peek()
            # white space
            if ch in " \t\r\n":
                self._advance()
            # line comment
            elif ch == '/' and self._peek(1) == '/':
                while self.pos < len(self.source) and self._peek() != "\n":
                    self._advance()
            # Multi-line comment
            elif ch == '/' and self._peek(1) == '*':
                start_line, start_col = self._current_pos()
                self._advance()  # consume '/'
                self._advance()  # consume '*'
                while self.pos < len(self.source):
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()  # consume '*'
                        self._advance()  # consume '/'
                        break
                    else:
                        self._advance()
                else:
                    raise LexError("Unterminated multi-line comment", start_line, start_col)
            else:
                break
            
    def _read_integer(self, line: int, col: int) -> Token:
        # Example 1: Decimal "42"
        # Before: self.pos = 0
        # m = <Match object; span=(0, 2), match='42'>
        # m.group() = "42"
        # value = "42"
        # After: self.pos = 2

        # Example 2: Hexadecimal "0xFF"
        # Before: self.pos = 5
        # m = <Match object; span=(5, 9), match='0xFF'>
        # m.group() = "0xFF"
        # value = "0xFF"
        # After: self.pos = 9

        # Example 3: Binary "0b1010"
        # Before: self.pos = 10
        # m = <Match object; span=(10, 16), match='0b1010'>
        # m.group() = "0b1010"
        # value = "0b1010"
        # After: self.pos = 16

        # Example 4: Octal "0777"
        # Before: self.pos = 20
        # m = <Match object; span=(20, 24), match='0777'>
        # m.group() = "0777"
        # value = "0777"
        # After: self.pos = 24

        # Example 5: "123abc" (only matches integer part)
        # Before: self.pos = 30
        # m = <Match object; span=(30, 33), match='123'>
        # m.group() = "123"
        # value = "123"
        # After: self.pos = 33
        m = self._INT_RE.match(self.source, self.pos)
        if not m:
            raise LexError("Invalid integer literal", line, col)

        value = m.group()
        token = Token(TT.INT_LIT, value, line, col)
        self.pos += len(value) # move past the matched integer
        self.col += len(value) # update column number
        return token
    
    def _read_char_literal(self, line: int, col: int) -> Token:
        self._advance()   # consume opening '
        value = "'"
        if self._peek() == "\\":
            value += self._advance()   # backslash
            if self._peek() == "\0":
                raise LexError("Unterminated char literal", line, col)
            value += self._advance()   # escape char
        elif self._peek() == "'":
            raise LexError("Empty char literal", line, col)
        else:
            value += self._advance()
        if self._peek() != "'":
            raise LexError("Unterminated char literal (expected closing ')", line, col)
        value += self._advance()   # closing '
        return Token(TT.CHAR_LIT, value, line, col)
    
    def _read_string_literal(self, line: int, col: int) -> Token:
        self._advance()   # consume opening "
        value = '"'
        while True:
            ch = self._peek()
            if ch == "\0" or ch == "\n":
                raise LexError("Unterminated string literal", line, col)
            if ch == '"':
                value += self._advance()
                break
            if ch == "\\":
                value += self._advance()   # backslash
                value += self._advance()   # escaped char
            else:
                value += self._advance()
        return Token(TT.STRING_LIT, value, line, col)
    
    def _read_ident_or_keyword(self, line: int, col: int) -> Token:
        start = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        value = self.source[start:self.pos]
        tt    = KEYWORDS.get(value, TT.IDENT)
        return Token(tt, value, line, col)
    
    def tokens(self) -> Iterator[Token]:
        """Lazily yield tokens one at a time."""
        while True:
            self._skip_whitespace_and_comments()
 
            if self.pos >= len(self.source):
                yield Token(TT.EOF, "", self.line, self.col)
                return
 
            line, col = self._current_pos()
            ch        = self._peek()
 
            # ── literals ──────────────────────────────────────────────────
            if ch.isdigit():
                yield self._read_integer(line, col)
                continue
 
            if ch == "'":
                yield self._read_char_literal(line, col)
                continue
 
            if ch == '"':
                yield self._read_string_literal(line, col)
                continue
 
            # ── identifier / keyword ──────────────────────────────────────
            if ch.isalpha() or ch == "_":
                yield self._read_ident_or_keyword(line, col)
                continue
 
            # ── operators & punctuation  (longest-match, manual) ──────────
            self._advance()   # consume first char
 
            # Two-char look-ahead table
            nch = self._peek()
 
            if ch == "+":
                if nch == "+":  self._advance(); yield Token(TT.PLUS_PLUS,   "++", line, col)
                elif nch == "=": self._advance(); yield Token(TT.PLUS_EQ,    "+=", line, col)
                else:            yield Token(TT.PLUS,   "+",  line, col)
            elif ch == "-":
                if nch == "-":  self._advance(); yield Token(TT.MINUS_MINUS, "--", line, col)
                elif nch == "=": self._advance(); yield Token(TT.MINUS_EQ,   "-=", line, col)
                elif nch == ">": self._advance(); yield Token(TT.ARROW,      "->", line, col)
                else:            yield Token(TT.MINUS,  "-",  line, col)
            elif ch == "*":
                if nch == "=":  self._advance(); yield Token(TT.STAR_EQ,    "*=", line, col)
                else:            yield Token(TT.STAR,   "*",  line, col)
            elif ch == "/":
                if nch == "=":  self._advance(); yield Token(TT.SLASH_EQ,   "/=", line, col)
                else:            yield Token(TT.SLASH,  "/",  line, col)
            elif ch == "%":     yield Token(TT.PERCENT, "%",  line, col)
            elif ch == "=":
                if nch == "=":  self._advance(); yield Token(TT.EQ_EQ,      "==", line, col)
                else:            yield Token(TT.EQ,     "=",  line, col)
            elif ch == "!":
                if nch == "=":  self._advance(); yield Token(TT.BANG_EQ,    "!=", line, col)
                else:            yield Token(TT.BANG,   "!",  line, col)
            elif ch == "<":
                if nch == "=":  self._advance(); yield Token(TT.LT_EQ,      "<=", line, col)
                elif nch == "<": self._advance(); yield Token(TT.LSHIFT,    "<<", line, col)
                else:            yield Token(TT.LT,     "<",  line, col)
            elif ch == ">":
                if nch == "=":  self._advance(); yield Token(TT.GT_EQ,      ">=", line, col)
                elif nch == ">": self._advance(); yield Token(TT.RSHIFT,    ">>", line, col)
                else:            yield Token(TT.GT,     ">",  line, col)
            elif ch == "&":
                if nch == "&":  self._advance(); yield Token(TT.AMP_AMP,    "&&", line, col)
                else:            yield Token(TT.AMP,    "&",  line, col)
            elif ch == "|":
                if nch == "|":  self._advance(); yield Token(TT.PIPE_PIPE,  "||", line, col)
                else:            yield Token(TT.PIPE,   "|",  line, col)
            elif ch == "^":     yield Token(TT.CARET,   "^",  line, col)
            elif ch == "~":     yield Token(TT.TILDE,   "~",  line, col)
            elif ch == "(":     yield Token(TT.LPAREN,  "(",  line, col)
            elif ch == ")":     yield Token(TT.RPAREN,  ")",  line, col)
            elif ch == "{":     yield Token(TT.LBRACE,  "{",  line, col)
            elif ch == "}":     yield Token(TT.RBRACE,  "}",  line, col)
            elif ch == "[":     yield Token(TT.LBRACKET,"[",  line, col)
            elif ch == "]":     yield Token(TT.RBRACKET,"]",  line, col)
            elif ch == ";":     yield Token(TT.SEMI,    ";",  line, col)
            elif ch == ",":     yield Token(TT.COMMA,   ",",  line, col)
            elif ch == ".":     yield Token(TT.DOT,     ".",  line, col)
            else:
                yield Token(TT.UNKNOWN, ch, line, col)
 
    def tokenize(self) -> list[Token]:
        """Return all tokens (including EOF) as a list."""
        return list(self.tokens())

def print_tokens(tokens: list[Token]) -> None:
    for tok in tokens:
        marker = "  *** UNKNOWN ***" if tok.type == TT.UNKNOWN else ""
        print(f"  {tok.type.name:<18} {tok.value!r:<22} (line {tok.line}, col {tok.col}){marker}")

# Quick demo / smoke test           
SAMPLE = r"""
// Tiny-C sample program
int add(int a, int b) {
    return a + b;
}
 
int main(void) {
    int x = 10;
    int y = 0xFF;
    char c = '\n';
    char *msg = "hello, world";
 
    if (x > 5) {
        x += 1;
    } else {
        x--;
    }
 
    for (int i = 0; i < 3; i++) {
        y = y + add(x, i);
    }
 
    /* block comment */
    while (x != 0) {
        x = x >> 1;
    }
 
    return 0;
}
"""
 
if __name__ == "__main__":
    print("=" * 60)
    print("  Tiny-C Lexer  –  token stream")
    print("=" * 60)
    try:
        lex    = Lexer(SAMPLE)
        tokens = lex.tokenize()
        print_tokens(tokens)
        print(f"\n  Total tokens: {len(tokens)}")
    except LexError as e:
        print(f"ERROR: {e}")