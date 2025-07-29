import ast
import sys
from typing import List, Union

BRANCH_NAME = "_slipcover_branches"

if sys.version_info[0:2] >= (3,12):
    def is_branch(line):
        return (line & (1<<30)) != 0

    def encode_branch(from_line, to_line):
        # FIXME anything bigger, and we get an overflow... encode to_line as relative number?
        assert from_line <= 0x7FFF, f"Line number {from_line} too high, unable to add branch tracking"
        assert to_line <= 0x7FFF, f"Line number {to_line} too high, unable to add branch tracking"
        return (1<<30)|((from_line & 0x7FFF)<<15)|(to_line&0x7FFF)

    def decode_branch(line):
        return ((line>>15)&0x7FFF, line&0x7FFF)

EXIT = 0

def preinstrument(tree: ast.Module) -> ast.Module:
    """Prepares an AST for Slipcover instrumentation, inserting assignments indicating where branches happen."""

    class SlipcoverTransformer(ast.NodeTransformer):
        def __init__(self):
            pass

        def _mark_branch(self, from_line: int, to_line: int) -> List[ast.stmt]:
            if sys.version_info[0:2] >= (3,12):
                # Using a constant Expr allows the compiler to optimize this to a NOP
                mark = ast.Expr(ast.Constant(None))
                for node in ast.walk(mark):
                    node.lineno = node.end_lineno = encode_branch(from_line, to_line) # type: ignore[attr-defined]
                    # Leaving the columns unitialized can lead to invalid positions despite
                    # our use of ast.fix_missing_locations
                    node.col_offset = node.end_col_offset = -1 # type: ignore[attr-defined]
            else:
                mark = ast.Assign([ast.Name(BRANCH_NAME, ast.Store())],
                                   ast.Tuple([ast.Constant(from_line), ast.Constant(to_line)], ast.Load()))
                if sys.version_info[0:2] == (3,11):
                    for node in ast.walk(mark):
                        node.lineno = 0 # we ignore line 0, so this avoids generating extra line probes
                else:
                    for node in ast.walk(mark):
                        node.lineno = from_line # type: ignore[attr-defined]

            return [mark]

        if sys.version_info[0:2] < (3,12):
            def visit_FunctionDef(self, node: Union[ast.AsyncFunctionDef, ast.FunctionDef]) -> ast.AST:
                # Mark BRANCH_NAME global, so that our assignments are easier to find (only STORE_NAME/STORE_GLOBAL,
                # but not STORE_FAST, etc.)
                has_docstring = ast.get_docstring(node, clean=False) is not None
                node.body.insert(1 if has_docstring else 0, ast.Global([BRANCH_NAME]))
                super().generic_visit(node)
                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
                return self.visit_FunctionDef(node)

        def _mark_branches(self, node: Union[ast.If, ast.For, ast.AsyncFor, ast.While]) -> ast.AST:
            node.body = self._mark_branch(node.lineno, node.body[0].lineno) + node.body

            if node.orelse:
                node.orelse = self._mark_branch(node.lineno, node.orelse[0].lineno) + node.orelse
            else:
                to_line = node.next_node.lineno if node.next_node else EXIT # type: ignore[union-attr]
                node.orelse = self._mark_branch(node.lineno, to_line)

            super().generic_visit(node)
            return node

        def visit_If(self, node: ast.If) -> ast.AST:
            return self._mark_branches(node)

        def visit_For(self, node: ast.For) -> ast.AST:
            return self._mark_branches(node)

        def visit_AsyncFor(self, node: ast.AsyncFor) -> ast.AST:
            return self._mark_branches(node)

        def visit_While(self, node: ast.While) -> ast.AST:
            return self._mark_branches(node)

        if sys.version_info >= (3,10): # new in Python 3.10
            def visit_Match(self, node: ast.Match) -> ast.Match:
                for case in node.cases:
                    case.body = self._mark_branch(node.lineno, case.body[0].lineno) + case.body

                last_pattern = case.pattern  # case is node.cases[-1]
                while isinstance(last_pattern, ast.MatchOr):
                    last_pattern = last_pattern.patterns[-1]

                has_wildcard = case.guard is None and isinstance(last_pattern, ast.MatchAs) and last_pattern.pattern is None
                if not has_wildcard:
                    to_line = node.next_node.lineno if node.next_node else EXIT # type: ignore[attr-defined]
                    node.cases.append(ast.match_case(ast.MatchAs(),
                                                     body=self._mark_branch(node.lineno, to_line)))

                super().generic_visit(node)
                return node


    if sys.version_info >= (3,10):
        match_type = ast.Match
    else:
        match_type = tuple() # matches nothing

    if sys.version_info >= (3,11):
        try_type = (ast.Try, ast.TryStar)
    else:
        try_type = ast.Try

    # Compute the "next" statement in case a branch flows control out of a node.
    # We need a parent node's "next" computed before its siblings, so we compute it here, in BFS;
    # note that visit() doesn't guarantee any specific order.
    tree.next_node = None  # type: ignore[attr-defined]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # no next node, yields (..., 0), i.e., "->exit" branch
            node.next_node = None  # type: ignore[union-attr]

        for name, field in ast.iter_fields(node):
            if isinstance(field, ast.AST):
                # if a field is just a node, any execution continues after our node
                field.next_node = node.next_node  # type: ignore[attr-defined]
            elif isinstance(node, match_type) and name == 'cases':
                # each case continues after the 'match'
                for item in field:
                    item.next_node = node.next_node  # type: ignore[attr-defined]
            elif isinstance(node, try_type) and name == 'handlers':
                # each 'except' continues either in 'finally', or after the 'try'
                for h in field:
                    h.next_node = node.finalbody[0] if node.finalbody else node.next_node # type: ignore[attr-defined,union-attr]
            elif isinstance(field, list):
                # if a field is a list, each item but the last one continues with the next item
                prev = None
                for item in field:
                    if isinstance(item, ast.AST):
                        if prev:
                            prev.next_node = item  # type: ignore[attr-defined]
                        prev = item

                if prev:
                    if isinstance(node, (ast.For, ast.While)):
                        # loops back
                        prev.next_node = node   # type: ignore[attr-defined]
                    elif isinstance(node, try_type) and (name in ('body', 'orelse')):
                        if name == 'body' and node.orelse:
                            prev.next_node = node.orelse[0] # type: ignore[attr-defined]
                        elif node.finalbody:
                            prev.next_node = node.finalbody[0] # type: ignore[attr-defined]
                        else:
                            prev.next_node = node.next_node  # type: ignore[attr-defined, union-attr]
                    else:
                        prev.next_node = node.next_node  # type: ignore[attr-defined]

    tree = SlipcoverTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return tree
