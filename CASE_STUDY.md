# Workflow MRI — Case Study

> *"Give me an ugly business process and I'll turn it into a governed, measurable operating
> system."*

Workflow MRI ingests a chaotic company's operational artifacts — spreadsheets, PDFs, emails,
screenshots, notes — reconstructs how work actually flows, exposes bottlenecks, duplicate
work, and compliance risk, recommends automations, and exports a governed handoff package
with an audit trail. The public demo runs on a fictional insurance-claims company,
**Meridian Claims Co.**

**[Live demo](#) · [Repo](https://github.com/Nogor-design/workflow-mri) · [Design doc](DESIGN.md)**

---

## Problem

Most companies already have the raw material for better operations — but it's trapped across
inconsistent spreadsheets, PDF SOPs, email approval threads, dashboard screenshots, and
free-text notes. The result is duplicated work, unclear ownership, missed handoffs,
compliance risk, and no reliable way to measure performance. There's no single view of how
work *actually* happens versus how the SOP says it should.

## Why it matters

This is the shift the industry is making: AI is most valuable when it works **inside real
workflows**, not just in chat. Workflow MRI proves the full arc — messy ingestion → a typed,
auditable operating model → governance controls → measurable before/after — not a toy
chatbot.

## System architecture

Two artifacts joined by one contract — **the Artifact Bundle**:

```
  samples/meridian-claims/        ENGINE (Python, local-first, offline)
  (fictional messy inputs)  ─►  ingest → mine process graph → detect risk
                                  → recommend → simulate → export
                                          │
                                   Artifact Bundle (typed JSON + evidence)
                                          │  committed
                                          ▼
  SHOWCASE (React + Vite, static)  ◄── pure renderer, no inference, no IO
  landing → ingest → process graph → risk → automations → before/after → export
```

- The **engine** does the real work and is allowed to be slow, call models, read files.
- The **showcase** is a *pure function of the Bundle* (`UI = render(bundle)`) — it performs
  no inference and no IO, so it deploys as static files and **always works in a 30-second
  scan**, with no keys and no cost.
- The committed Bundle makes the public demo a **deterministic replay** of a pre-computed
  run. It's **baked, not faked**: `make bundle` regenerates it locally.

This mirrors a discipline I use elsewhere: *compute in the analysis layer; render in a
deterministic view layer that consumes a typed context object and nothing else.*

### The analytical core: process mining (not a prompt)

The engine reconstructs the workflow by **mining a directly-follows graph from a claims
event log** — a real technique, fully deterministic. It computes per-activity cycle times
from timestamps, flags the bottleneck, and classifies every handoff as
`normal / exception / loop / duplicate / bypass`. Risk detection is rule-based over both
structured events and unstructured text (PII regex, missing-approval, review-bypass,
ambiguous-ownership, inconsistent-status, low-confidence). The LLM (pluggable **Ollama** or
**Claude**) is **optional enrichment** — the core pipeline needs neither, which is exactly
why the demo is reproducible and runs offline / in CI.

## Representative outputs

From 6 fictional artifacts, the engine reconstructs a 7-step claims process and surfaces:

- **Bottleneck** at Manager Approval (~40h average dwell).
- A **duplicate handoff** (triage performed by two roles), a **rework loop**
  (exception → review), and a **review bypass** (intake → approval, skipping the control).
- **8 risk findings** across all 6 governance categories — including SSN/DOB in free text and
  approvals recorded without sign-off — each linked to the exact evidence that triggered it.
- **6 ranked automations** with estimated time saved, required oversight, and effort.
- A **simulated before/after** (cycle time, handoffs, rework, cost), clearly labeled.

## Evaluation

Scored against an **independently-authored ground truth**
(`engine/evals/ground_truth.json`, written from the scenario design — not derived from engine
code), reproducible with `make evals`:

| Metric | Result | Detail |
|---|---|---|
| Step reconstruction recall | **100%** | 7/7 canonical steps |
| Bottleneck identified | **100%** | Manager Approval |
| Edge + kind recall | **100%** | 8/8 directed edges, correct kind |
| Risk-category recall | **100%** | 6/6 governance categories |
| PII detection recall | **100%** | every planted secret surfaced |
| Hallucination rate | **0.0%** | every finding traces to real evidence |

The hallucination check is the one I care about most: every risk/step/edge must reference a
real source artifact, and every PII finding's quote must actually contain a PII pattern — no
fabricated sensitive strings. Guarded in CI (`engine/tests/test_evals.py`).

## Governance & safety model

Governance is a **first-class feature, not a footnote**:

- **Evidence everywhere** — every analytic object links to the artifact (and line/cell) that
  produced it, powering a "why was this flagged" drawer and the audit trail.
- **Confidence + human review** — uncertain extractions carry confidence scores and spawn
  review tasks; high-severity risks become an open review queue with required roles.
- **Safe mode** — a toggle that redacts detected PII from displayed evidence (a real control,
  not cosmetics).
- **Public-safe by construction** — the only data that ever exists is fictional, so there's
  nothing to leak; no secrets in the repo; the simulation is labeled simulated. See
  [docs/public-safety.md](docs/public-safety.md).

The pipeline is wired as a **LangGraph multi-agent graph** (ingest → graph → risk →
recommend → simulate → enrich → assemble → critic) with a **critic/review pass** that audits
the assembled bundle, and an **audit trail** emitting an event per agent decision (shown in
the demo's Export view). It falls back to a deterministic sequential runner when LangGraph
isn't installed — so the same output is reproducible offline and in CI.

## What I'd build next

- A second sample company (onboarding or support) to prove the engine generalizes beyond
  claims.
- Promote the optional LLM enrichment node to a full extraction path graded against the
  deterministic miner.
- An optional, local-only "bring your own folder" mode (never on the public path).
- Adversarial evals: red-team the extractor on deliberately degraded inputs.

## Stack

Python (Pydantic, stdlib process-mining) · React + Vite + TypeScript · custom SVG process
graph · pluggable Ollama / Claude · pytest + vitest · GitHub Actions.
