"""Monolith-to-service decomposition from a static dependency graph.

The stub split each line on the word ``import``, took whatever followed, and named one service per
dependency up to three. "import" inside a comment or string counted, `from x import y` produced the
string ``y``, and the service count was a function of the import count -- a property of nothing.

Decomposition now groups units that reference each other. Services are the connected components of
the internal dependency graph, so a candidate boundary is one that can be cut with the fewest edges
crossing it, and the cut edges are reported by name rather than assumed away. Cycles are reported
too, because a cycle is the thing that makes a decomposition hard and it must not be hidden.

Nothing here refactors code or claims a decomposition is correct. It reports what the graph supports:
the boundaries, what crosses them, and what would have to be untangled first.
"""

from dataclasses import dataclass
from typing import Any

from .analysis import Analysis, Unit, analyze_source


@dataclass(frozen=True)
class Service:
    """A proposed service boundary: units that reference each other."""

    name: str
    units: tuple[str, ...]
    lines: int
    internal_edges: int


@dataclass
class ModernizationPipeline:
    """Legacy-code analysis and decomposition over a static dependency graph.

    Parses the submitted source with `ast` -- never importing, `eval`-ing, or executing it -- then
    reports the dependency graph between its top-level units and the service boundaries that graph
    supports.

    The call graph is an approximation: edges follow direct name references and attribute roots, and
    it does not resolve aliases, dynamic dispatch, or calls reached through a variable. Boundaries are
    therefore candidates for a human to weigh, not a refactoring plan, and the module reports the
    edges that would be cut so a reader can judge the cost.
    """

    def analyze(self, code: str) -> dict[str, Any]:
        analysis = analyze_source(code)
        if not analysis.parsed:
            # Reporting a decomposition of source that could not be read would be an invented
            # answer, and the caller cannot tell an invented one from a real one.
            return {
                "parsed": False,
                "error": analysis.error,
                "dependencies": [],
                "proposed_services": [],
                "entry_points": [],
                "cycles": [],
                "cross_service_edges": [],
            }

        services = self._services(analysis)
        return {
            "parsed": True,
            "dependencies": list(analysis.imports),
            "units": [
                {"name": unit.name, "kind": unit.kind, "lines": unit.lines}
                for unit in analysis.units
            ],
            "proposed_services": [
                {
                    "name": service.name,
                    "units": list(service.units),
                    "lines": service.lines,
                    "internal_edges": service.internal_edges,
                }
                for service in services
            ],
            "entry_points": list(analysis.entry_points),
            "cycles": [list(cycle) for cycle in self._cycles(analysis)],
            "cross_service_edges": [
                list(edge) for edge in self._crossing(analysis, services)
            ],
        }

    def _services(self, analysis: Analysis) -> list[Service]:
        """Connected components of the internal graph, largest first."""
        by_name = {unit.name: unit for unit in analysis.units}
        parent = {name: name for name in by_name}

        def root(name: str) -> str:
            while parent[name] != name:
                parent[name] = parent[parent[name]]
                name = parent[name]
            return name

        for source, target in analysis.edges:
            parent[root(source)] = root(target)

        groups: dict[str, list[str]] = {}
        for name in by_name:
            groups.setdefault(root(name), []).append(name)

        services = [
            Service(
                name=f"service_{self._label(sorted(members), by_name)}",
                units=tuple(sorted(members)),
                lines=sum(by_name[member].lines for member in members),
                internal_edges=sum(
                    1
                    for source, target in analysis.edges
                    if source in members and target in members
                ),
            )
            for members in groups.values()
        ]
        return sorted(services, key=lambda service: (-service.lines, service.name))

    @staticmethod
    def _label(members: list[str], by_name: dict[str, Unit]) -> str:
        """Name a service after its largest unit, so the name says what is inside it."""
        largest = max(members, key=lambda member: (by_name[member].lines, member))
        return largest.strip("<>")

    @staticmethod
    def _cycles(analysis: Analysis) -> list[tuple[str, ...]]:
        """Mutually referencing unit pairs. Longer cycles are not searched for."""
        edges = set(analysis.edges)
        return sorted(
            {
                tuple(sorted((source, target)))
                for source, target in edges
                if (target, source) in edges
            }
        )

    @staticmethod
    def _crossing(
        analysis: Analysis, services: list[Service]
    ) -> list[tuple[str, str]]:
        owner = {
            unit: service.name for service in services for unit in service.units
        }
        return sorted(
            (source, target)
            for source, target in analysis.edges
            if owner.get(source) != owner.get(target)
        )


__all__ = ["ModernizationPipeline", "Service"]
