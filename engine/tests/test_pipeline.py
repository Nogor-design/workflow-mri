"""Phase 2: the engine mines a schema-valid Bundle from the sample company.

Verifies the generated Bundle matches the golden Bundle's *shape* (object types and the
diagnostic structure the UI relies on), not exact values.
"""

from pathlib import Path

import pytest

from workflow_mri.pipeline import build_bundle

SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "meridian-claims"


@pytest.fixture(scope="module")
def bundle():
    return build_bundle(SAMPLES, run_id="test-run")


def test_reconstructs_seven_canonical_steps(bundle):
    assert len(bundle.steps) == 7
    assert [s.id for s in sorted(bundle.steps, key=lambda s: s.sequence_index)] == [
        "step_intake", "step_triage", "step_review", "step_approval",
        "step_payment", "step_exception", "step_closure",
    ]


def test_bottleneck_is_manager_approval(bundle):
    hot = [s for s in bundle.steps if s.is_bottleneck]
    assert len(hot) == 1 and hot[0].id == "step_approval"


def test_mines_every_edge_kind(bundle):
    kinds = {e.kind for e in bundle.edges}
    assert {"normal", "loop", "exception", "bypass", "duplicate"} <= kinds


def test_bypass_skips_the_review_control(bundle):
    bypass = [e for e in bundle.edges if e.kind == "bypass"]
    assert bypass and bypass[0].from_step == "step_intake" and bypass[0].to_step == "step_approval"


def test_detects_all_risk_categories(bundle):
    cats = {r.category for r in bundle.risks}
    assert {"pii", "missing_approval", "review_bypass", "ambiguous_ownership",
            "inconsistent_status", "low_confidence"} <= cats


def test_pii_evidence_links_to_a_real_artifact(bundle):
    pii = [r for r in bundle.risks if r.category == "pii"]
    assert pii
    art_ids = {a.id for a in bundle.artifacts}
    for r in pii:
        assert r.evidence and r.evidence[0].artifact_id in art_ids


def test_recommendations_are_ranked(bundle):
    ranks = [a.priority_rank for a in bundle.automations]
    assert ranks == sorted(ranks) and ranks[0] == 1


def test_simulation_improves_and_is_labeled(bundle):
    sim = bundle.simulation
    assert sim and sim.is_simulated
    assert sim.after.total_cycle_time_hours < sim.before.total_cycle_time_hours


def test_high_severity_risks_become_review_tasks(bundle):
    highs = [r for r in bundle.risks if r.severity == "high"]
    assert len(bundle.reviews) == len(highs)
