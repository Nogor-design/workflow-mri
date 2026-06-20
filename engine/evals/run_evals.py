"""Evaluate the engine against an independently-authored ground truth.

Builds the Meridian bundle, then scores process reconstruction, risk recall, PII recall, and
a hallucination check (does every finding trace to a real artifact / real PII?). Prints a
table and writes evals/report.md for the case-study page.

    python evals/run_evals.py      (from engine/, or: make evals)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from workflow_mri.pipeline import build_bundle
from workflow_mri.schema import Bundle

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parents[1]  # engine/evals -> engine -> repo root
SAMPLES = REPO_ROOT / "samples" / "meridian-claims"
_PII = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}-\d{2}-\d{2}\b")


@dataclass
class Metric:
    name: str
    value: float
    detail: str
    target: float
    higher_is_better: bool = True

    @property
    def passed(self) -> bool:
        return self.value >= self.target if self.higher_is_better else self.value <= self.target


def _recall(found: set, expected: set) -> float:
    return len(found & expected) / len(expected) if expected else 1.0


def evaluate(bundle: Bundle, gt: dict) -> list[Metric]:
    metrics: list[Metric] = []
    artifact_ids = {a.id for a in bundle.artifacts}

    # 1. process steps
    step_ids = {s.id for s in bundle.steps}
    exp_steps = set(gt["expected_steps"])
    metrics.append(Metric("Step reconstruction recall", _recall(step_ids, exp_steps),
                          f"{len(step_ids & exp_steps)}/{len(exp_steps)} canonical steps", 1.0))

    # 2. bottleneck
    hot = next((s.id for s in bundle.steps if s.is_bottleneck), None)
    metrics.append(Metric("Bottleneck identified", 1.0 if hot == gt["expected_bottleneck"] else 0.0,
                          f"got {hot}, expected {gt['expected_bottleneck']}", 1.0))

    # 3. edges (from,to,kind)
    found_edges = {(e.from_step, e.to_step, e.kind) for e in bundle.edges}
    exp_edges = {(e["from"], e["to"], e["kind"]) for e in gt["expected_edges"]}
    metrics.append(Metric("Edge + kind recall", _recall(found_edges, exp_edges),
                          f"{len(found_edges & exp_edges)}/{len(exp_edges)} directed edges with correct kind", 1.0))

    # 4. risk categories
    found_cats = {r.category for r in bundle.risks}
    exp_cats = set(gt["expected_risk_categories"])
    metrics.append(Metric("Risk-category recall", _recall(found_cats, exp_cats),
                          f"{len(found_cats & exp_cats)}/{len(exp_cats)} categories", 1.0))

    # 5. PII recall (every planted secret detected somewhere in the findings)
    pii_text = " ".join(ev.quote or "" for r in bundle.risks if r.category == "pii" for ev in r.evidence)
    planted = gt["planted_pii"]
    found_pii = [p for p in planted if p in pii_text]
    metrics.append(Metric("PII detection recall", len(found_pii) / len(planted),
                          f"{len(found_pii)}/{len(planted)} planted secrets surfaced", 1.0))

    # 6. hallucination: every finding's evidence must reference a real artifact, and every
    #    pii quote must actually contain a PII pattern (no fabricated sensitive strings)
    offenders = 0
    total = 0
    for r in bundle.risks:
        for ev in r.evidence:
            total += 1
            if ev.artifact_id not in artifact_ids:
                offenders += 1
            elif r.category == "pii" and ev.quote and not _PII.search(ev.quote):
                offenders += 1
    rate = offenders / total if total else 0.0
    metrics.append(Metric("Hallucination rate", rate, f"{offenders}/{total} findings with bad evidence",
                          0.0, higher_is_better=False))

    return metrics


def render_report(bundle: Bundle, metrics: list[Metric]) -> str:
    c = bundle.manifest.counts
    lines = [
        "# Workflow MRI — Evaluation Report",
        "",
        "Engine output scored against an independently-authored ground truth for the fictional",
        "**Meridian Claims Co.** sample (`engine/evals/ground_truth.json`). Deterministic;",
        "reproduce with `make evals`.",
        "",
        f"Bundle under test: {c['artifacts']} artifacts → {c['steps']} steps, {c['edges']} edges, "
        f"{c['risks']} risk findings, {c['automations']} automations.",
        "",
        "| Metric | Result | Detail | Target | Pass |",
        "|---|---|---|---|---|",
    ]
    for m in metrics:
        shown = f"{m.value * 100:.0f}%" if m.name != "Hallucination rate" else f"{m.value * 100:.1f}%"
        tgt = f"≥{m.target * 100:.0f}%" if m.higher_is_better else f"≤{m.target * 100:.0f}%"
        lines.append(f"| {m.name} | **{shown}** | {m.detail} | {tgt} | {'✅' if m.passed else '❌'} |")
    lines += ["", f"_All targets met: {'yes' if all(m.passed for m in metrics) else 'NO'}._", ""]
    return "\n".join(lines)


def main() -> int:
    gt = json.loads((EVALS_DIR / "ground_truth.json").read_text(encoding="utf-8"))
    bundle = build_bundle(SAMPLES, run_id="eval-run")
    metrics = evaluate(bundle, gt)
    report = render_report(bundle, metrics)
    (EVALS_DIR / "report.md").write_text(report, encoding="utf-8")

    print(report)
    return 0 if all(m.passed for m in metrics) else 1


if __name__ == "__main__":
    raise SystemExit(main())
