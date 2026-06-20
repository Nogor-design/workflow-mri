"""Process mining: reconstruct the workflow graph from a normalized event log.

Builds steps (one per canonical activity actually seen), a directly-follows graph of edges,
and classifies each edge as normal / exception / loop / duplicate / bypass. Cycle times and
the bottleneck come from inter-event timestamps. Fully deterministic.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean

from workflow_mri.extraction.event_log import CANON, Event, by_case
from workflow_mri.schema import EvidenceRef, ProcessEdge, WorkflowStep

CONTROL_ACTIVITIES = {"review"}  # skipping these is a control bypass


def mine_steps(events: list[Event], event_log_artifact_id: str) -> list[WorkflowStep]:
    seen = {e.activity for e in events}
    roles: dict[str, Counter] = defaultdict(Counter)
    durations: dict[str, list[float]] = defaultdict(list)

    for evs in by_case(events).values():
        for i, e in enumerate(evs):
            roles[e.activity][e.role] += 1
            if i + 1 < len(evs):
                hrs = (evs[i + 1].ts - e.ts).total_seconds() / 3600.0
                if hrs > 0:
                    durations[e.activity].append(hrs)

    steps: list[WorkflowStep] = []
    for canon, (name, default_owner, seq, is_review, is_approval) in CANON.items():
        if canon not in seen:
            continue
        owner = roles[canon].most_common(1)[0][0] if roles[canon] else default_owner
        n_roles = len(roles[canon])
        cycle = round(mean(durations[canon]), 1) if durations[canon] else 3.0
        steps.append(
            WorkflowStep(
                id=f"step_{canon}",
                name=name,
                owner_role=owner,
                sequence_index=seq,
                cycle_time_hours=cycle,
                inputs=[],
                outputs=[],
                is_review=is_review,
                is_approval=is_approval,
                confidence=round(min(0.97, 0.6 + 0.05 * len(durations[canon])), 2),
                evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=f"{name} mined from event log")],
            )
        )

    # bottleneck = step with the largest mean cycle time
    if steps:
        hot = max(steps, key=lambda s: s.cycle_time_hours or 0)
        hot.is_bottleneck = True
    return steps


def mine_edges(events: list[Event], event_log_artifact_id: str) -> list[ProcessEdge]:
    pair_count: Counter = Counter()
    pair_delays: dict[tuple[str, str], list[float]] = defaultdict(list)
    pair_from_roles: dict[tuple[str, str], set[str]] = defaultdict(set)
    n_cases = 0

    cases = by_case(events)
    n_cases = len(cases)
    for evs in cases.values():
        for a, b in zip(evs, evs[1:]):
            key = (a.activity, b.activity)
            pair_count[key] += 1
            pair_delays[key].append(max(0.0, (b.ts - a.ts).total_seconds() / 3600.0))
            pair_from_roles[key].add(a.role)

    edges: list[ProcessEdge] = []
    for i, ((fa, ta), count) in enumerate(sorted(pair_count.items()), start=1):
        kind = _classify_edge(fa, ta, pair_from_roles[(fa, ta)])
        edges.append(
            ProcessEdge(
                id=f"e{i}",
                from_step=f"step_{fa}",
                to_step=f"step_{ta}",
                owner_handoff=" / ".join(sorted(pair_from_roles[(fa, ta)])),
                kind=kind,  # type: ignore[arg-type]
                frequency=round(count / n_cases, 2) if n_cases else None,
                avg_delay_hours=round(mean(pair_delays[(fa, ta)]), 1),
                evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=f"{fa}→{ta} ×{count} cases")],
            )
        )
    return edges


def _classify_edge(fa: str, ta: str, from_roles: set[str]) -> str:
    fi, ti = CANON[fa][2], CANON[ta][2]
    if fa == "exception" or ta == "exception":
        return "exception" if ti > fi else "loop"
    if ti < fi:
        return "loop"
    # bypass: the jump skips a control activity that sits between the two steps
    skipped_controls = {c for c in CONTROL_ACTIVITIES if fi < CANON[c][2] < ti}
    if skipped_controls:
        return "bypass"
    if len(from_roles) > 1:
        return "duplicate"
    return "normal"
