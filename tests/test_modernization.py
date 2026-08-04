"""Behavioral tests for static decomposition.

The stub split lines on the word "import", so the assertions that matter here are the ones it would
have failed: an import inside a string is not a dependency, `from x import y` names the module and not
the symbol, service count is a property of the dependency graph rather than of the import count, and
unparseable source yields no decomposition at all instead of a confident one.

One test exists for the threat model rather than for the feature: submitting source with a side effect
must not run it.
"""

from eads.modernization.analysis import MODULE_UNIT, analyze_source
from eads.modernization.modernization import ModernizationPipeline

MONOLITH = '''
import os
from collections import defaultdict


def read_config():
    return os.environ


def build_index():
    return defaultdict(list)


def report():
    return build_index()


def serve():
    return read_config()
'''


def test_a_dependency_is_the_module_not_the_symbol() -> None:
    result = ModernizationPipeline().analyze(MONOLITH)
    assert result["dependencies"] == ["collections", "os"]


def test_the_word_import_in_a_string_or_comment_is_not_a_dependency() -> None:
    """The old line-splitting heuristic counted both."""
    result = ModernizationPipeline().analyze(
        'MESSAGE = "please import the ledger"\n# import legacy_billing\n'
    )
    assert result["dependencies"] == []


def test_services_are_units_that_reference_each_other() -> None:
    services = ModernizationPipeline().analyze(MONOLITH)["proposed_services"]
    groups = {tuple(service["units"]) for service in services}
    assert ("build_index", "report") in groups
    assert ("read_config", "serve") in groups


def test_service_count_follows_the_graph_not_the_import_count() -> None:
    """The stub returned one service per dependency, up to three -- a property of nothing."""
    one_component = ModernizationPipeline().analyze(
        "import os\nimport sys\nimport json\nimport csv\n\n\ndef a():\n    return os\n"
    )
    assert len(one_component["dependencies"]) == 4
    assert len(one_component["proposed_services"]) == 2


def test_a_service_is_named_after_its_largest_unit() -> None:
    for service in ModernizationPipeline().analyze(MONOLITH)["proposed_services"]:
        stripped = [unit.strip("<>") for unit in service["units"]]
        assert service["name"].removeprefix("service_") in stripped
    big = ModernizationPipeline().analyze(
        "def small():\n    return 1\n\n\ndef large():\n    x = small()\n    y = x\n    z = y\n"
        "    return z\n"
    )["proposed_services"]
    assert big[0]["name"] == "service_large"


def test_edges_that_would_be_cut_are_reported_rather_than_assumed_away() -> None:
    result = ModernizationPipeline().analyze(MONOLITH)
    assert result["cross_service_edges"] == []
    connected = ModernizationPipeline().analyze(
        "def a():\n    return b()\n\n\ndef b():\n    return 1\n"
    )
    assert len(connected["proposed_services"]) == 1


def test_a_cycle_is_reported_because_it_is_what_makes_decomposition_hard() -> None:
    result = ModernizationPipeline().analyze(
        "def a():\n    return b()\n\n\ndef b():\n    return a()\n"
    )
    assert result["cycles"] == [["a", "b"]]


def test_module_level_statements_are_their_own_unit() -> None:
    analysis = analyze_source("import os\nprint(os.getcwd())\n")
    assert [unit.name for unit in analysis.units] == [MODULE_UNIT]


def test_entry_points_are_discovered_rather_than_asserted() -> None:
    """The stub always returned ["main"], whether or not one existed."""
    assert ModernizationPipeline().analyze(MONOLITH)["entry_points"] == []
    guarded = ModernizationPipeline().analyze(
        "def main():\n    return 1\n\n\nif __name__ == '__main__':\n    main()\n"
    )
    assert guarded["entry_points"] == ["__main__", "main"]


def test_unparseable_source_yields_no_decomposition() -> None:
    """A decomposition of source that could not be read would be an invented answer."""
    result = ModernizationPipeline().analyze("def broken(:\n")
    assert result["parsed"] is False
    assert result["error"] == "SyntaxError"
    assert result["proposed_services"] == []


def test_submitted_source_is_parsed_and_never_executed() -> None:
    """T5: legacy source is attacker-supplied. `ast.parse` reads it; nothing runs it."""
    marker: list[str] = []
    globals()["_modernization_marker"] = marker
    ModernizationPipeline().analyze(
        "_modernization_marker.append('executed')\nraise SystemExit(1)\n"
    )
    assert marker == []


def test_classes_are_units_too() -> None:
    result = ModernizationPipeline().analyze(
        "class Ledger:\n    def post(self):\n        return 1\n"
    )
    assert result["units"] == [{"name": "Ledger", "kind": "class", "lines": 3}]
