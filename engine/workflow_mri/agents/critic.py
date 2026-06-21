"""Critic / review pass.

A separate agent that audits the assembled bundle for internal consistency and governance
completeness — the kind of self-check a reliable pipeline needs. It records every check in
the audit trail (governance: issues are surfaced, never hidden) and returns the list of
problems found. It does not silently mutate results.
"""

from __future__ import annotations

import re
from typing import Any

from workflow_mri.agents.nodes import _event

State = dict[str, Any]
_PII = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}-\d{2}-\d{2}\b")


def critic_node(state: State) -> State:
    bundle = state["bundle"]
    issues: list[str] = []
    step_ids = {s.id for s in bundle.steps}
    artifact_ids = {a.id for a in bundle.artifacts}

    # 1. edges reference real steps
    for e in bundle.edges:
        if e.from_step not in step_ids or e.to_step not in step_ids:
            issues.append(f"edge {e.id} references a missing step")

    # 2. a bottleneck was identified
    if not any(s.is_bottleneck for s in bundle.steps):
        issues.append("no bottleneck identified")

    # 3. every high-severity risk has a review task
    reviewed = {r.related_id for r in bundle.reviews}
    for r in bundle.risks:
        if r.severity == "high" and r.id not in reviewed:
            issues.append(f"high-severity risk {r.id} has no review task")

    # 4. every finding's evidence references a real artifact; PII quotes contain real PII
    for r in bundle.risks:
        for ev in r.evidence:
            if ev.artifact_id not in artifact_ids:
                issues.append(f"risk {r.id} cites unknown artifact {ev.artifact_id}")
            elif r.category == "pii" and ev.quote and not _PII.search(ev.quote):
                issues.append(f"pii risk {r.id} evidence lacks a PII pattern")

    # 5. manifest counts match the arrays
    c = bundle.manifest.counts
    for key, n in (("steps", len(bundle.steps)), ("edges", len(bundle.edges)),
                   ("risks", len(bundle.risks)), ("automations", len(bundle.automations))):
        if c.get(key) != n:
            issues.append(f"manifest count '{key}'={c.get(key)} != {n}")

    verdict = "passed" if not issues else f"{len(issues)} issue(s): " + "; ".join(issues[:3])
    audit = _event(state, "agent:critic", "review", f"critic {verdict}")
    bundle.audit = audit  # the bundle carries the full trail incl. this verdict
    return {"bundle": bundle, "audit": audit, "critic_issues": issues}
