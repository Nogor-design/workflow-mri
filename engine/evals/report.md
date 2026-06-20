# Workflow MRI — Evaluation Report

Engine output scored against an independently-authored ground truth for the fictional
**Meridian Claims Co.** sample (`engine/evals/ground_truth.json`). Deterministic;
reproduce with `make evals`.

Bundle under test: 6 artifacts → 7 steps, 8 edges, 8 risk findings, 6 automations.

| Metric | Result | Detail | Target | Pass |
|---|---|---|---|---|
| Step reconstruction recall | **100%** | 7/7 canonical steps | ≥100% | ✅ |
| Bottleneck identified | **100%** | got step_approval, expected step_approval | ≥100% | ✅ |
| Edge + kind recall | **100%** | 8/8 directed edges with correct kind | ≥100% | ✅ |
| Risk-category recall | **100%** | 6/6 categories | ≥100% | ✅ |
| PII detection recall | **100%** | 2/2 planted secrets surfaced | ≥100% | ✅ |
| Hallucination rate | **0.0%** | 0/8 findings with bad evidence | ≤0% | ✅ |

_All targets met: yes._
