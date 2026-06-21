"""Phase 3: agent orchestration — audit trail, critic pass, and runner equivalence."""

from pathlib import Path

import pytest

from workflow_mri.agents.orchestrator import orchestrate

SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "meridian-claims"


@pytest.fixture(scope="module")
def bundle():
    return orchestrate(SAMPLES, run_id="agents-test", use_langgraph=False)


def test_audit_trail_records_every_agent(bundle):
    actors = [e.actor for e in bundle.audit]
    for expected in ("agent:ingest", "agent:graph", "agent:risk", "agent:recommender",
                     "agent:simulator", "agent:assembler", "agent:critic"):
        assert expected in actors


def test_audit_ids_are_ordered_and_unique(bundle):
    ids = [e.id for e in bundle.audit]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_critic_passes_on_the_clean_bundle(bundle):
    critic = [e for e in bundle.audit if e.actor == "agent:critic"]
    assert critic and "passed" in critic[-1].detail


def test_enrich_disabled_by_default_keeps_deterministic_text(bundle):
    skip = [e for e in bundle.audit if e.action == "skip_enrich"]
    assert skip, "enrichment should be skipped by default"


def test_sequential_and_langgraph_agree_on_shape():
    seq = orchestrate(SAMPLES, run_id="x", use_langgraph=False)
    lg = orchestrate(SAMPLES, run_id="x", use_langgraph=True)
    assert [s.id for s in seq.steps] == [s.id for s in lg.steps]
    assert {(e.from_step, e.to_step, e.kind) for e in seq.edges} == \
           {(e.from_step, e.to_step, e.kind) for e in lg.edges}
    assert {r.id for r in seq.risks} == {r.id for r in lg.risks}
