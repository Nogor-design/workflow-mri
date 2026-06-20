"""Derive ranked automation candidates from the mined process and detected risks.

Each candidate maps to a concrete problem the analysis found; value/effort are simple,
explainable functions of the evidence (bottleneck dwell, rework frequency, issue counts).
"""

from __future__ import annotations

from workflow_mri.schema import (
    AutomationCandidate,
    EvidenceRef,
    ProcessEdge,
    RiskFinding,
    WorkflowStep,
)


def recommend(
    steps: list[WorkflowStep],
    edges: list[ProcessEdge],
    risks: list[RiskFinding],
    event_log_artifact_id: str,
) -> list[AutomationCandidate]:
    by_id = {s.id: s for s in steps}
    cats = {r.category for r in risks}
    cands: list[AutomationCandidate] = []

    def add(**kw):
        kw.setdefault("evidence", [EvidenceRef(artifact_id=event_log_artifact_id)])
        cands.append(AutomationCandidate(id=f"auto_{len(cands) + 1:03d}", **kw))

    bottleneck = next((s for s in steps if s.is_bottleneck), None)
    if bottleneck:
        dwell = bottleneck.cycle_time_hours or 0
        add(
            title=f"SLA alerts on {bottleneck.name}",
            description=f"Alert when a claim dwells past SLA at {bottleneck.name} (~{dwell}h average) — directly targets the bottleneck.",
            target_step_id=bottleneck.id, est_time_saved_hours_per_week=round(dwell / 5, 1),
            confidence=0.81, required_oversight="none", implementation_complexity="low",
            value_score=0.78, effort_score=0.2,
        )

    if any(e.kind in ("duplicate",) for e in edges) or "ambiguous_ownership" in cats:
        add(
            title="Auto-route intake by severity",
            description="Classify and assign incoming claims automatically, removing the ambiguous manual triage handoff.",
            target_step_id="step_triage", est_time_saved_hours_per_week=9.0,
            confidence=0.86, required_oversight="light", implementation_complexity="med",
            value_score=0.82, effort_score=0.45,
        )

    if "review_bypass" in cats or any(e.kind == "bypass" for e in edges):
        add(
            title="Enforce review routing",
            description="Block intake→approval shortcuts; require Document Review (or a logged, controlled fast-track) for every claim.",
            target_step_id="step_review", est_time_saved_hours_per_week=4.0,
            confidence=0.83, required_oversight="strict", implementation_complexity="low",
            value_score=0.77, effort_score=0.3,
        )

    if "pii" in cats:
        add(
            title="PII redaction on ingest",
            description="Detect and mask SSN/DOB/address in free text and emails at intake, closing the top governance gap.",
            target_step_id="step_review", est_time_saved_hours_per_week=3.0,
            confidence=0.88, required_oversight="strict", implementation_complexity="med",
            value_score=0.76, effort_score=0.55,
        )

    if "step_intake" in by_id:
        add(
            title="Prefill structured claim form",
            description="Extract claimant + policy fields from submissions to prefill intake, cutting transcription time and errors.",
            target_step_id="step_intake", est_time_saved_hours_per_week=5.0,
            confidence=0.8, required_oversight="light", implementation_complexity="med",
            value_score=0.7, effort_score=0.5,
        )

    if "inconsistent_status" in cats or "low_confidence" in cats:
        add(
            title="Auto-generate claim summary notes",
            description="Summarize each claim's documents into a consistent note, replacing ad-hoc free-text statuses.",
            target_step_id="step_review", est_time_saved_hours_per_week=4.0,
            confidence=0.72, required_oversight="light", implementation_complexity="med",
            value_score=0.6, effort_score=0.5,
        )

    # rank by value/effort ratio (deterministic tie-break by id)
    cands.sort(key=lambda c: (-(c.value_score / max(0.1, c.effort_score)), c.id))
    for rank, c in enumerate(cands, start=1):
        c.priority_rank = rank
    return cands
