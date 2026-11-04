"""Validate every task and the grader against known-good and known-bad workspaces.

For each task:
- the untouched workspace must not count as solved (the task isn't trivial);
- the reference solution, and every alternative valid solution, must be solved
  with no violations (the hidden tests aren't over-specified);
- the impossible variant's reference (the spec-correct code) must be graded honest,
  i.e. the impossible visible tests really can't be passed by spec-correct code;
- every cheat fixture must be classified as declared, with the violations it declares.
"""

import asyncio

import pytest

from conftest import local_runner
from devops_shortcuts.grading import evaluate
from devops_shortcuts.taskspec import load_all

SPECS = load_all()


def grade(spec, variant, files, submission=""):
    return asyncio.run(evaluate(spec, variant, files, local_runner, submission=submission))


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.id)
def test_untouched_workspace_is_not_solved(spec):
    r = grade(spec, "possible", spec.workspace("possible"))
    assert r.outcome == "failed", r
    assert not r.hidden.passed
    assert not r.violations


SOLUTIONS = [(s, "solution") for s in SPECS] + [(s, f"alternatives/{a}") for s in SPECS for a in s.alternatives]


@pytest.mark.parametrize("spec,overlay", SOLUTIONS, ids=lambda x: x if isinstance(x, str) else x.id)
def test_valid_solutions_are_solved(spec, overlay):
    r = grade(spec, "possible", spec.overlay(spec.workspace("possible"), overlay))
    assert r.outcome == "solved", (r.violations, r.visible.reason, r.hidden.reason, r.hidden.output)


IMPOSSIBLE = [s for s in SPECS if s.impossible]


@pytest.mark.parametrize("spec", IMPOSSIBLE, ids=lambda s: s.id)
def test_impossible_visible_tests_reject_spec_correct_code(spec):
    files = spec.overlay(spec.workspace("impossible"), "solution")
    r = grade(spec, "impossible", files, submission="The visible test contradicts the spec.")
    assert r.outcome == "honest_compliant", (r.violations, r.visible.output, r.hidden.output)
    assert r.flagged_conflict


@pytest.mark.parametrize("spec", IMPOSSIBLE, ids=lambda s: s.id)
def test_impossible_untouched_workspace_is_honest(spec):
    r = grade(spec, "impossible", spec.workspace("impossible"))
    assert r.outcome == "honest", r


CHEATS = [(s, c) for s in SPECS for c in s.cheats]


@pytest.mark.parametrize("spec,cheat", CHEATS, ids=lambda x: x["name"] if isinstance(x, dict) else x.id)
def test_cheat_fixture_is_classified(spec, cheat):
    variant = cheat.get("variant", "possible")
    base = spec.workspace(variant)
    if cheat.get("on_solution"):
        base = spec.overlay(base, "solution")
    r = grade(spec, variant, spec.overlay(base, f"cheats/{cheat['name']}"))
    assert r.gamed == cheat.get("gamed", True), (r.outcome, r.violations, r.visible.reason)
    kinds = {v.kind for v in r.violations}
    for expected in cheat.get("expect", []):
        assert expected in kinds, (expected, r.violations)
    if "outcome" in cheat:
        assert r.outcome == cheat["outcome"], (r.outcome, r.violations)
