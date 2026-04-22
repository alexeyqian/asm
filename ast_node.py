"""
ast_nodes.py  –  AST node definitions for Tiny-C
==================================================
Every node carries (line, col) from the token that originated it so
downstream passes (semantic analysis, codegen) can emit precise errors.

Node hierarchy
--------------
  Node
  ├── Type nodes
  │   └── TypeNode
  ├── Declaration nodes
  │   ├── ParamDecl
  │   ├── VarDecl
  │   └── FuncDecl
  ├── Statement nodes
  │   ├── BlockStmt
  │   ├── IfStmt
  │   ├── WhileStmt
  │   ├── ForStmt
  │   ├── ReturnStmt
  │   ├── BreakStmt
  │   ├── ContinueStmt
  │   └── ExprStmt
  ├── Expression nodes
  │   ├── IntLiteral
  │   ├── CharLiteral
  │   ├── StringLiteral
  │   ├── Identifier
  │   ├── BinOp
  │   ├── UnaryOp
  │   ├── Assign
  │   ├── CompoundAssign
  │   ├── PostfixOp
  │   ├── CallExpr
  │   ├── IndexExpr
  │   └── TernaryExpr
  └── Program  (root)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class Node:
    line: int = field(repr=False)
    col:  int = field(repr=False)

    # Visitor Pattern: used to separate the data structure(the Node) 
    # from the operations performed on them (the visitor)
    # keep nodes clean, easy to extend, centralized logic
    def accept(self, visitor):
        """Visitor dispatch."""
        method = "visit_" + type(self).__name__
        return getattr(visitor, method)(self)


# ---------------------------------------------------------------------------
# Type  (int / char / void with optional pointer depth)
# ---------------------------------------------------------------------------

@dataclass
class TypeNode(Node):
    name:    str          # "int" | "char" | "void"
    pointer: int = 0     # number of '*' levels  (int** → 2)

    def __str__(self) -> str:
        return self.name + "*" * self.pointer


# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------

@dataclass
class ParamDecl(Node):
    type:  TypeNode
    name:  str


@dataclass
class VarDecl(Node):
    type:  TypeNode
    name:  str
    init:  Optional[Node] = None   # initialiser expression, may be None


@dataclass
class FuncDecl(Node):
    ret_type: TypeNode
    name:     str
    params:   list[ParamDecl]
    body:     Optional["BlockStmt"] = None   # None = forward declaration


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class BlockStmt(Node):
    stmts: list[Node]


@dataclass
class IfStmt(Node):
    cond:      Node
    then_body: Node
    else_body: Optional[Node] = None


@dataclass
class WhileStmt(Node):
    cond: Node
    body: Node


@dataclass
class ForStmt(Node):
    init:   Optional[Node]   # VarDecl or ExprStmt or None
    cond:   Optional[Node]   # expression or None
    post:   Optional[Node]   # expression or None
    body:   Node


@dataclass
class ReturnStmt(Node):
    value: Optional[Node] = None


@dataclass
class BreakStmt(Node):
    pass


@dataclass
class ContinueStmt(Node):
    pass


@dataclass
class ExprStmt(Node):
    expr: Node


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class IntLiteral(Node):
    raw:   str    # keep original text so codegen can handle 0xFF etc.
    value: int    # parsed integer value


@dataclass
class CharLiteral(Node):
    raw:   str    # e.g. "'\\n'"
    value: int    # numeric value of character


@dataclass
class StringLiteral(Node):
    raw:   str    # includes surrounding quotes
    value: str    # decoded string (escape sequences resolved)


@dataclass
class Identifier(Node):
    name: str


@dataclass
class BinOp(Node):
    op:    str    # "+", "-", "==", "&&", etc.
    left:  Node
    right: Node


@dataclass
class UnaryOp(Node):
    op:      str   # "-", "!", "~", "&" (addr-of), "*" (deref), "++" (pre), "--" (pre)
    operand: Node
    prefix:  bool = True


@dataclass
class PostfixOp(Node):
    op:      str   # "++" | "--"
    operand: Node


@dataclass
class Assign(Node):
    target: Node
    value:  Node


@dataclass
class CompoundAssign(Node):
    op:     str    # "+=", "-=", "*=", "/="
    target: Node
    value:  Node


@dataclass
class CallExpr(Node):
    callee: Node
    args:   list[Node]


@dataclass
class IndexExpr(Node):
    array: Node
    index: Node


@dataclass
class TernaryExpr(Node):
    cond:       Node
    then_value: Node
    else_value: Node


# ---------------------------------------------------------------------------
# Program root
# ---------------------------------------------------------------------------

@dataclass
class Program(Node):
    decls: list[Node]   # list of VarDecl / FuncDecl at top level


# ---------------------------------------------------------------------------
# Pretty-printer (AST → indented text)
# ---------------------------------------------------------------------------

class ASTPrinter:
    """Walk the AST and print a readable tree."""

    def __init__(self) -> None:
        self._depth = 0

    def _w(self, text: str) -> None:
        print("  " * self._depth + text)

# Example of how this code is likely used
#with obj._indent():
#   # Inside this block, obj._depth is increased by 1
#    obj.print_line("First level of indentation")

#    with obj._indent():
#        # Inside here, obj._depth is increased by another 1
#        obj.print_line("Second level of indentation")

# Outside the blocks, obj._depth automatically returns to its original value

    def _indent(self):
        class _CM: # context manager for indentation
            def __init__(s): pass
            # Automatically called when you start a with block
            def __enter__(s): self._depth += 1
            # Automatically called when the with block ends (even if an error occurs). 
            def __exit__(s, *_): self._depth -= 1
        return _CM()

    # ── helpers ──────────────────────────────────────────────────────────

    def _print_node(self, label: str, node: Optional[Node]) -> None:
        if node is None:
            self._w(f"{label}: <none>")
        else:
            self._w(f"{label}:")
            with self._indent():
                node.accept(self)

    def _print_list(self, label: str, nodes: list) -> None:
        self._w(f"{label}: [{len(nodes)}]")
        with self._indent():
            for n in nodes:
                n.accept(self)

    # ── visitors ─────────────────────────────────────────────────────────

    def visit_Program(self, n: Program):
        self._w(f"Program  ({len(n.decls)} top-level decls)")
        with self._indent():
            for d in n.decls:
                d.accept(self)

    def visit_TypeNode(self, n: TypeNode):
        self._w(f"Type: {n}")

    def visit_ParamDecl(self, n: ParamDecl):
        self._w(f"ParamDecl: {n.type} {n.name}")

    def visit_VarDecl(self, n: VarDecl):
        self._w(f"VarDecl: {n.type} {n.name}")
        if n.init:
            with self._indent():
                self._print_node("init", n.init)

    def visit_FuncDecl(self, n: FuncDecl):
        params = ", ".join(f"{p.type} {p.name}" for p in n.params)
        self._w(f"FuncDecl: {n.ret_type} {n.name}({params})")
        with self._indent():
            if n.body:
                n.body.accept(self)
            else:
                self._w("<forward declaration>")

    def visit_BlockStmt(self, n: BlockStmt):
        self._w(f"Block [{len(n.stmts)} stmts]")
        with self._indent():
            for s in n.stmts:
                s.accept(self)

    def visit_IfStmt(self, n: IfStmt):
        self._w("If")
        with self._indent():
            self._print_node("cond", n.cond)
            self._print_node("then", n.then_body)
            if n.else_body:
                self._print_node("else", n.else_body)

    def visit_WhileStmt(self, n: WhileStmt):
        self._w("While")
        with self._indent():
            self._print_node("cond", n.cond)
            self._print_node("body", n.body)

    def visit_ForStmt(self, n: ForStmt):
        self._w("For")
        with self._indent():
            self._print_node("init", n.init)
            self._print_node("cond", n.cond)
            self._print_node("post", n.post)
            self._print_node("body", n.body)

    def visit_ReturnStmt(self, n: ReturnStmt):
        self._w("Return")
        if n.value:
            with self._indent():
                n.value.accept(self)

    def visit_BreakStmt(self, _): self._w("Break")
    def visit_ContinueStmt(self, _): self._w("Continue")

    def visit_ExprStmt(self, n: ExprStmt):
        self._w("ExprStmt")
        with self._indent():
            n.expr.accept(self)

    def visit_IntLiteral(self, n: IntLiteral):
        self._w(f"IntLit({n.raw} = {n.value})")

    def visit_CharLiteral(self, n: CharLiteral):
        self._w(f"CharLit({n.raw} = {n.value})")

    def visit_StringLiteral(self, n: StringLiteral):
        self._w(f"StringLit({n.raw})")

    def visit_Identifier(self, n: Identifier):
        self._w(f"Ident({n.name})")

    def visit_BinOp(self, n: BinOp):
        self._w(f"BinOp({n.op})")
        with self._indent():
            n.left.accept(self)
            n.right.accept(self)

    def visit_UnaryOp(self, n: UnaryOp):
        pos = "pre" if n.prefix else "post"
        self._w(f"UnaryOp({n.op}, {pos}fix)")
        with self._indent():
            n.operand.accept(self)

    def visit_PostfixOp(self, n: PostfixOp):
        self._w(f"PostfixOp({n.op})")
        with self._indent():
            n.operand.accept(self)

    def visit_Assign(self, n: Assign):
        self._w("Assign")
        with self._indent():
            self._print_node("target", n.target)
            self._print_node("value",  n.value)

    def visit_CompoundAssign(self, n: CompoundAssign):
        self._w(f"CompoundAssign({n.op})")
        with self._indent():
            self._print_node("target", n.target)
            self._print_node("value",  n.value)

    def visit_CallExpr(self, n: CallExpr):
        self._w(f"Call")
        with self._indent():
            self._print_node("callee", n.callee)
            self._print_list("args", n.args)

    def visit_IndexExpr(self, n: IndexExpr):
        self._w("Index")
        with self._indent():
            self._print_node("array", n.array)
            self._print_node("index", n.index)

    def visit_TernaryExpr(self, n: TernaryExpr):
        self._w("Ternary")
        with self._indent():
            self._print_node("cond", n.cond)
            self._print_node("then", n.then_value)
            self._print_node("else", n.else_value)