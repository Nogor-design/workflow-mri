"""Deterministic before/after estimate over the mined process graph.

"Before" is measured from the mined data (happy-path cycle time, handoff count, rework
frequency). "After" applies the modeled effect of the recommended automations. Clearly
labeled as a simulation; assumptions are stated for honesty.
"""

from __future__ import annotations

from workflow_mri.schema import (
    ProcessEdge,
    SimStats,
    SimulationResult,
    WorkflowStep,
)

HAPPY_PATH = ["step_intake", "step_triage", "step_review", "step_approval", "step_payment", "step_closure"]
BLENDED_RATE = 95.0  # fictional $/hr
CLAIMS_PER_MONTH = 320


def simulate(steps: list[WorkflowStep], edges: list[ProcessEdge]) -> SimulationResult:
    by_id = {s.id: s for s in steps}
    happy = [by_id[i].cycle_time_hours or 0 for i in HAPPY_PATH if i in by_id]
    base_cycle = round(sum(happy))

    problem_edges = [e for e in edges if e.kind in ("loop", "duplicate", "bypass", "exception")]
    rework_freq = sum(e.frequency or 0 for e in edges if e.kind == "loop")
    rework_before = round(min(0.4, max(0.05, rework_freq + 0.1)), 2)

    handoffs_before = len(edges)
    cycle_before = round(base_cycle * (1 + rework_before))

    # modeled "after": SLA alerts cut bottleneck dwell, routing removes problem edges,
    # enforcement cuts rework.
    bottleneck = next((s for s in steps if s.is_bottleneck), None)
    dwell_cut = round((bottleneck.cycle_time_hours or 0) * 0.5) if bottleneck else 0
    cycle_after = max(1, round((base_cycle - dwell_cut) * (1 + rework_before * 0.35)))
    handoffs_after = max(len(happy) - 1, handoffs_before - len(problem_edges))
    rework_after = round(rework_before * 0.35, 2)

    def cost(cycle_h: float) -> float:
        # crude: cost scales with labor-hours in flight per month
        return round(cycle_h * BLENDED_RATE * CLAIMS_PER_MONTH / 24.0 / 10, -2)

    return SimulationResult(
        is_simulated=True,
        before=SimStats(total_cycle_time_hours=cycle_before, handoffs=handoffs_before, rework_rate=rework_before, monthly_cost=cost(cycle_before)),
        after=SimStats(total_cycle_time_hours=cycle_after, handoffs=handoffs_after, rework_rate=rework_after, monthly_cost=cost(cycle_after)),
        assumptions=[
            f"Volume held constant at ~{CLAIMS_PER_MONTH} claims/month (fictional).",
            "Auto-routing removes the duplicated triage handoff.",
            "Review enforcement + duplicate checks cut the rework loop by ~65%.",
            "SLA alerts halve the bottleneck's average dwell.",
            f"Labor costed at a flat fictional ${BLENDED_RATE:.0f}/hr blended rate; illustrative only.",
        ],
        method="deterministic estimate over the mined directly-follows graph",
    )
