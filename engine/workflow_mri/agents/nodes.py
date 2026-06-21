"""Pipeline stages as agent nodes.

Each node takes the shared state dict, does one stage of work, appends an AuditEvent for the
decision it made, and returns the keys it set. Nodes run sequentially (LangGraph or the
deterministic fallback runner), so plain last-write-wins state semantics are correct.

State keys: samples_dir, run_id, enrich, now, loaded, events, log_id, steps, edges, risks,
automations, simulation, bundle, audit, critic_issues.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from workflow_mri.extraction.event_log import parse_events
from workflow_mri.graph.mine import mine_edges, mine_steps
from workflow_mri.ingestion.loader import find_event_log, load_company
from workflow_mri.recommend.score import recommend
from workflow_mri.risk.rules import detect_risks
from workflow_mri.schema import (
    Artifact,
    AuditEvent,
    Bundle,
    Company,
    EngineInfo,
    ExportFile,
    LLMCallInfo,
    Manifest,
    ReviewTask,
)
from workflow_mri.simulate.estimate import simulate

State = dict[str, Any]

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
    ExportFile(id="exp_audit", label="Audit Log", kind="json", path_in_bundle="audit.json", description="Decision/inference trail for the run."),
    ExportFile(id="exp_backlog", label="Implementation Backlog", kind="md", path_in_bundle="exports/backlog.md", description="Prioritized automation work items for engineering."),
]


def _event(state: State, actor: str, action: str, detail: str, *, target_id: str | None = None,
           llm_call: LLMCallInfo | None = None) -> list[AuditEvent]:
    audit = list(state.get("audit", []))
    now: datetime = state["now"]
    audit.append(AuditEvent(
        id=f"evt_{len(audit) + 1:03d}",
        at=now.isoformat(),
        actor=actor,
        action=action,
        target_id=target_id,
        detail=detail,
        llm_call=llm_call,
    ))
    return audit


def ingest_node(state: State) -> State:
    loaded = load_company(state["samples_dir"])
    log = find_event_log(loaded)
    if log is None:
        raise ValueError(f"No event log found under {state['samples_dir']}")
    events = parse_events(log.rows)
    return {
        "loaded": loaded,
        "events": events,
        "log_id": log.artifact.id,
        "audit": _event(state, "agent:ingest", "ingest",
                        f"loaded {len(loaded)} artifacts; parsed {len(events)} events from {log.artifact.source_name}"),
    }


def graph_node(state: State) -> State:
    steps = mine_steps(state["events"], state["log_id"])
    edges = mine_edges(state["events"], state["log_id"])
    hot = next((s.id for s in steps if s.is_bottleneck), None)
    kinds = sorted({e.kind for e in edges})
    return {
        "steps": steps,
        "edges": edges,
        "audit": _event(state, "agent:graph", "mine_process",
                        f"mined {len(steps)} steps, {len(edges)} edges ({', '.join(kinds)}); bottleneck={hot}",
                        target_id=hot),
    }


def risk_node(state: State) -> State:
    risks = detect_risks(state["events"], state["loaded"], state["steps"], state["edges"], state["log_id"])
    cats = sorted({r.category for r in risks})
    return {
        "risks": risks,
        "audit": _event(state, "agent:risk", "detect_risks",
                        f"detected {len(risks)} findings across {len(cats)} categories: {', '.join(cats)}"),
    }


def recommend_node(state: State) -> State:
    autos = recommend(state["steps"], state["edges"], state["risks"], state["log_id"])
    return {
        "automations": autos,
        "audit": _event(state, "agent:recommender", "recommend",
                        f"ranked {len(autos)} automation candidates by value/effort"),
    }


def simulate_node(state: State) -> State:
    sim = simulate(state["steps"], state["edges"])
    saved = sim.before.total_cycle_time_hours - sim.after.total_cycle_time_hours
    return {
        "simulation": sim,
        "audit": _event(state, "agent:simulator", "simulate",
                        f"before/after estimate: cycle time -{saved}h (simulated)"),
    }


def enrich_node(state: State) -> State:
    """Optional LLM pass: rewrite step/risk descriptions for readability. Off by default.

    Gated by state['enrich']; failures degrade gracefully (the deterministic text stands).
    """
    if not state.get("enrich"):
        return {"audit": _event(state, "agent:enricher", "skip_enrich",
                                "LLM enrichment disabled (deterministic descriptions kept)")}
    from workflow_mri.llm import get_client
    client = get_client(state.get("llm_backend"))
    audit = state.get("audit", [])
    enriched = 0
    for risk in state["risks"][:1]:  # one call to demonstrate; full pass is future work
        try:
            prompt = f"Rewrite this operations risk in one crisp sentence for an executive: {risk.description}"
            out = client.complete(prompt, system="You are an operations analyst. Be concise and concrete.")
            if out.strip():
                risk.description = out.strip()
                enriched += 1
                audit = _event({"now": state["now"], "audit": audit}, "agent:enricher", "enrich_risk",
                               f"rewrote description for {risk.id}", target_id=risk.id,
                               llm_call=LLMCallInfo(prompt_id="risk_rewrite_v1", model=getattr(client, "model", client.name)))
        except Exception as e:  # noqa: BLE001 — enrichment is best-effort
            audit = _event({"now": state["now"], "audit": audit}, "agent:enricher", "enrich_failed",
                           f"{client.name} enrichment unavailable: {type(e).__name__}; kept deterministic text")
            break
    return {"risks": state["risks"], "audit": audit}


def assemble_node(state: State) -> State:
    risks = state["risks"]
    reviews = [
        ReviewTask(
            id=f"rev_{i:03d}",
            reason=r.title,
            related_id=r.id,
            status="open",
            required_role=_REVIEW_ROLE.get(r.category, "Reviewer"),
            created_at=state["now"].isoformat(),
        )
        for i, r in enumerate((r for r in risks if r.severity == "high"), start=1)
    ]
    artifacts: list[Artifact] = [la.artifact for la in state["loaded"]]
    model = "deterministic (process-mining + rules)"
    if state.get("enrich"):
        model += " + LLM enrichment"
    manifest = Manifest(
        run_id=state["run_id"],
        company=Company(name="Meridian Claims Co.", fictional=True, domain="insurance-claims"),
        generated_at=state["now"].isoformat(),
        engine=EngineInfo(llm_backend=state.get("llm_backend", "ollama"), model=model, prompt_set="v1", temperature=0),
        counts={
            "artifacts": len(artifacts),
            "steps": len(state["steps"]),
            "edges": len(state["edges"]),
            "risks": len(risks),
            "automations": len(state["automations"]),
            "reviews": len(reviews),
        },
        safe_mode=True,
    )
    audit = _event(state, "agent:assembler", "assemble",
                   f"assembled bundle: {len(reviews)} review tasks from high-severity findings")
    bundle = Bundle(
        manifest=manifest,
        artifacts=artifacts,
        steps=state["steps"],
        edges=state["edges"],
        risks=risks,
        reviews=reviews,
        automations=state["automations"],
        simulation=state["simulation"],
        audit=audit,
        exports=_EXPORTS,
    )
    return {"bundle": bundle, "audit": audit}
