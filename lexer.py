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
 
 