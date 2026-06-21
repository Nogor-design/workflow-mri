# Architecture

Companion to [`../DESIGN.md`](../DESIGN.md). This is the detailed view of *how the system
is built*. Read DESIGN §3 and §6 first.

## The two-artifact model

Workflow MRI is **two programs joined by one file format**.

```
engine/   →  produces  →  Artifact Bundle (JSON + assets)  →  consumed by  →  web/
(Python)                  (versioned, deterministic)                          (React/Vite)
```

- The **engine** is where the AI/engineering substance lives. It runs locally, offline,
  with a pluggable LLM backend. It is allowed to be slow, to call models, to read files.
- The **showcase** is a pure function of the Bundle: `UI = render(bundle)`. It performs
  **no IO and no inference**. It deploys as static files to GitHub Pages.
- The **Bundle** is the contract. Change the contract in one place (`engine/.../schema/`),
  regenerate TypeScript types, and both sides stay in sync.

This mirrors the `ta_foundation` discipline: *compute in the analysis layer, render in the
section layer; the renderer consumes a context object and nothing else.*

## Why not a live backend?

A hosted, live-inference demo was rejected for a portfolio piece because it: costs money,
needs secrets in CI, has cold-start/latency flakiness, and can break mid-interview. A
deterministic baked Bundle is free, instant, reproducible, and honest (it is *baked*, not
*faked* — `make bundle` regenerates it). If a live "bring your own folder" mode is ever
added, it runs **locally**, never on the public critical path.

## Engine pipeline

Each stage is a package under `engine/workflow_mri/`. Each consumes typed objects and emits
typed objects; no stage reaches across layers or mutates a previous stage's outputs.

| Stage | Package | Input | Output | LLM? |
|---|---|---|---|---|
| 1. Ingestion | `ingestion/` | raw files in `samples/<co>/` | `Artifact` + `Document` records, normalized text | OCR/text only |
| 2. Extraction | `extraction/` | `Document`s | `Entity`, `WorkflowStep` (with confidence) | yes (+ rules) |
| 3. Graph | `graph/` | steps + entities | `ProcessEdge`s, bottleneck/loop/duplicate diagnostics | no (deterministic) |
| 4. Risk | `risk/` | all of the above | `RiskFinding`s, `ReviewTask`s | rules + LLM |
| 5. Recommend | `recommend/` | graph + risks | `AutomationCandidate`s (value × effort × oversight) | LLM-assisted |
| 6. Simulate | `simulate/` | graph + automations | `SimulationResult` (before/after) | no (deterministic) |
| 7. Export | `export/` | everything | the **Artifact Bundle** + derived export files | no |

Cross-cutting:

- **`llm/`** — `LLMClient` protocol; `OllamaClient` (default) and `ClaudeClient`. Chosen by
  config/env. Prompts are versioned; every call is recorded as an `AuditEvent` and fed to evals.
- **`agents/`** — orchestration wiring every stage as a node (ingest → graph → risk →
  recommend → simulate → enrich → assemble → **critic**). Runs as a **LangGraph StateGraph**
  when `langgraph` is installed, else a deterministic sequential runner over the same nodes —
  identical output either way, so the pipeline stays offline-reproducible (CI installs
  neither LangGraph nor an LLM). Every node emits an `AuditEvent`; the critic validates the
  assembled bundle (edge/step integrity, review-task coverage, evidence references real
  artifacts, PII quotes contain real PII, manifest counts) and records its verdict. The
  optional `enrich` node (opt-in `--enrich`) is the first-class LLM seam.
- **`schema/`** — Pydantic models; the source of truth for the Bundle. `make types` emits
  matching TypeScript into `web/src/`.
- **`evals/`** — synthetic ground truth for the sample company; reports accuracy/recall/hallucination.

## Determinism

The pipeline must produce a stable Bundle for a fixed sample + fixed model config:

- LLM calls use temperature 0 (or a fixed seed where supported).
- Any LLM output that feeds structure is **constrained** (typed/JSON-schema-validated) and
  **rule-reconciled**, never trusted raw.
- The committed Bundle is the published truth; regeneration is for development, not the demo.

## Showcase rendering

`web/` is a React + Vite SPA. It loads the Bundle from `web/public/bundle/` at startup into
a typed store and renders the views in DESIGN §9. Key choices:

- **Custom SVG swimlane graph** for the process map (deterministic layout in
  `src/graph/layout.ts`; lanes = owner roles, columns = sequence index; edges styled by
  kind: normal / duplicate / exception / loop / bypass). Chosen over React Flow for full
  control of the distinctive look, zero heavy dependency, and exact determinism. (DESIGN
  originally named React Flow as the means; the end — an interactive, clickable graph — is
  what matters, and the custom renderer delivers it with a more bespoke visual.)
- TypeScript types are generated from the Pydantic schema, so the UI cannot drift from the
  contract.
- Routing is hash-based or static-export-safe so it works under a GitHub Pages subpath.
- Zero runtime secrets, zero network calls beyond loading its own static Bundle.

## Repository layout

```
workflow-mri/
├── DESIGN.md                  # canonical spec (spine)
├── README.md                  # repo front door
├── docs/                      # this folder
│   ├── architecture.md  data-model.md  roadmap.md
│   ├── demo-script.md  public-safety.md  portfolio-integration.md
│   └── ideas/                 # original idea docs (archived, read-only)
├── engine/                    # Python local-first engine
│   ├── workflow_mri/
│   │   ├── llm/ ingestion/ extraction/ graph/ risk/
│   │   ├── recommend/ simulate/ export/ agents/ schema/
│   ├── tests/
│   └── pyproject.toml
├── samples/
│   └── meridian-claims/       # fictional inputs (spreadsheets/pdfs/emails/screenshots/notes)
├── web/                       # React + Vite static showcase
│   ├── src/
│   └── public/bundle/         # committed Artifact Bundle the demo replays
└── bundles/                   # dev output of `make bundle` before promotion to web/public/bundle
```

## Build/run commands (target)

```
make bundle     # engine: samples/meridian-claims → bundles/<run>/ (dev artifact)
make promote    # copy a verified bundle → web/public/bundle/ (the published one)
make types      # Pydantic schema → web/src TypeScript types
make evals      # run synthetic-ground-truth evals, print metrics
make web        # vite dev server
make web-build  # static export for GitHub Pages
make test       # pytest (engine) + vitest (web)
```
