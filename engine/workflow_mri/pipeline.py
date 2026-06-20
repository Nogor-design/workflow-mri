"""Orchestrate the engine: samples folder → Artifact Bundle.

ingest → mine process graph → detect risks → recommend → simulate → assemble Bundle.
Deterministic and offline by default; an optional LLM pass can enrich descriptions later.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from workflow_mri.extraction.event_log import parse_events
from workflow_mri.graph.mine import mine_edges, mine_steps
from workflow_mri.ingestion.loader import find_event_log, load_company
from workflow_mri.recommend.score import recommend
from workflow_mri.risk.rules import detect_risks
from workflow_mri.schema import (
    Artifact,
    Bundle,
    Company,
    EngineInfo,
    ExportFile,
    Manifest,
    ReviewTask,
)
from workflow_mri.simulate.estimate import simulate

_REVIEW_ROLE = {
    "pii": "Compliance",
    "missing_approval": "Claims Manager",
    "review_bypass": "Compliance",
    "low_confidence": "Adjuster",
}

_EXPORTS = [
    ExportFile(id="exp_map", label="Process Map", kind="pdf", path_in_bundle="exports/process-map.pdf", description="Swimlane diagram of the mined workflow."),
    ExportFile(id="exp_schema", label="Cleaned Data Schema", kind="json", path_in_bundle="exports/schema.json", description="Typed entities + validation rules inferred from the artifacts."),
    ExportFile(id="exp_reviews", label="Review Queue", kind="csv", path_in_bundle="exports/review-queue.csv", description="Items requiring human review, with reasons and roles."),
    ExportFile(id="exp_audit", label="Audit Log", kind="json", path_in_bundle="exports/audit.json", description="Decision/inference trail for the run."),
    ExportFile(id="exp_backlog", label="Implementation Backlog", kind="md", path_in_bundle="exports/backlog.md", description="Prioritized automation work items for engineering."),
]


def build_bundle(samples_dir: Path, *, run_id: str | None = None) -> Bundle:
    loaded = load_company(samples_dir)
    log = find_event_log(loaded)
    if log is None:
        raise ValueError(f"No event log found under {samples_dir}")
    log_id = log.artifact.id

    events = parse_events(log.rows)
    steps = mine_steps(events, log_id)
    edges = mine_edges(events, log_id)
    risks = detect_risks(events, loaded, steps, edges, log_id)
    automations = recommend(steps, edges, risks, log_id)
    simulation = simulate(steps, edges)

    reviews = [
        ReviewTask(
            id=f"rev_{i:03d}",
            reason=r.title,
            related_id=r.id,
            status="open",
            required_role=_REVIEW_ROLE.get(r.category, "Reviewer"),
            created_at=datetime.now().astimezone().replace(microsecond=0).isoformat(),
        )
        for i, r in enumerate((r for r in risks if r.severity == "high"), start=1)
    ]

    artifacts: list[Artifact] = [la.artifact for la in loaded]
    manifest = Manifest(
        run_id=run_id or f"meridian-{datetime.now():%Y-%m-%d}",
        company=Company(name="Meridian Claims Co.", fictional=True, domain="insurance-claims"),
        generated_at=datetime.now().astimezone().replace(microsecond=0).isoformat(),
        engine=EngineInfo(llm_backend="ollama", model="deterministic (process-mining + rules)", prompt_set="v1", temperature=0),
        counts={
            "artifacts": len(artifacts),
            "steps": len(steps),
            "edges": len(edges),
            "risks": len(risks),
            "automations": len(automations),
            "reviews": len(reviews),
        },
        safe_mode=True,
    )

    return Bundle(
        manifest=manifest,
        artifacts=artifacts,
        steps=steps,
        edges=edges,
        risks=risks,
        reviews=reviews,
        automations=automations,
        simulation=simulation,
        exports=_EXPORTS,
    )
