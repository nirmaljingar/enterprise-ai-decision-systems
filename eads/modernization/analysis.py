"""Static analysis of legacy Python source, using the standard-library parser.

Only `ast.parse` is used: the submitted source is never imported, `eval`-ed, or executed. That is the
control behind T5 in the threat model, and it is why this module can be handed attacker-supplied text.

The unit of analysis is a top-level function or class, plus a synthetic ``<module>`` unit for
statements at module level. Edges between units come from names a unit references, which is a
call-graph approximation: it follows direct references and attribute roots, and it does not resolve
aliases, dynamic dispatch, or names reached through a variable.
"""

import ast
from dataclasses import dataclass, field

MODULE_UNIT = "<module>"


@dataclass(frozen=True)
class Unit:
    """One top-level definition and the names it references."""

    name: str
    kind: str
    lineno: int
    end_lineno: int
    references: frozenset[str] = field(default_factory=frozenset)
    imports: frozenset[str] = field(default_factory=frozenset)

    @property
    def lines(self) -> int:
        return max(1, self.end_lineno - self.lineno + 1)


@dataclass(frozen=True)
class Analysis:
    """The parsed shape of a module. ``parsed`` is false when the source did not parse."""

    parsed: bool
    units: tuple[Unit, ...] = ()
    imports: tuple[str, ...] = ()
    edges: tuple[tuple[str, str], ...] = ()
    entry_points: tuple[str, ...] = ()
    error: str = ""


class _References(ast.NodeVisitor):
    """Collects the names a subtree refers to, and the modules it imports."""

    def __init__(self) -> None:
        self.names: set[str] = set()
        self.imports: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        self.names.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        root = node
        while isinstance(root, ast.Attribute):
            root = root.value  # type: ignore[assignment]
        if isinstance(root, ast.Name):
            self.names.add(root.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])
            self.names.add((alias.asname or alias.name).split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and not node.level:
            self.imports.add(node.module.split(".")[0])
        for alias in node.names:
            self.names.add(alias.asname or alias.name)


def analyze_source(code: str) -> Analysis:
    """Parse *code* into units, imports, unit-to-unit edges, and entry points.

    Unparseable source yields ``parsed=False`` with the syntax error and no units. Reporting a
    decomposition of source that could not be read would be an invented answer, so nothing is
    reported at all.
    """
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError) as error:
        return Analysis(parsed=False, error=type(error).__name__)

    units: list[Unit] = []
    module_level: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            units.append(_unit(node))
        else:
            module_level.append(node)

    if module_level:
        collector = _References()
        for node in module_level:
            collector.visit(node)
        units.append(
            Unit(
                name=MODULE_UNIT,
                kind="module",
                lineno=module_level[0].lineno,
                end_lineno=module_level[-1].end_lineno or module_level[-1].lineno,
                references=frozenset(collector.names),
                imports=frozenset(collector.imports),
            )
        )

    imports = sorted({name for unit in units for name in unit.imports})
    defined = {unit.name for unit in units}
    edges = tuple(
        sorted(
            (unit.name, reference)
            for unit in units
            for reference in unit.references
            if reference in defined and reference != unit.name
        )
    )
    return Analysis(
        parsed=True,
        units=tuple(units),
        imports=tuple(imports),
        edges=edges,
        entry_points=_entry_points(tree, units),
    )


def _unit(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> Unit:
    collector = _References()
    for child in node.body:
        collector.visit(child)
    kind = "class" if isinstance(node, ast.ClassDef) else "function"
    return Unit(
        name=node.name,
        kind=kind,
        lineno=node.lineno,
        end_lineno=node.end_lineno or node.lineno,
        references=frozenset(collector.names),
        imports=frozenset(collector.imports),
    )


def _entry_points(tree: ast.Module, units: list[Unit]) -> tuple[str, ...]:
    """Names a caller can plausibly start from: ``__main__`` guards, ``main``, and top-level calls."""
    found: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.If) and _is_main_guard(node.test):
            found.append("__main__")
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            called = node.value.func
            if isinstance(called, ast.Name):
                found.append(called.id)
    found.extend(unit.name for unit in units if unit.name in {"main", "run"})
    return tuple(sorted(set(found)))


def _is_main_guard(test: ast.expr) -> bool:
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
    )


__all__ = ["MODULE_UNIT", "Analysis", "Unit", "analyze_source"]
