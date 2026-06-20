# Workflow MRI — Design Document

> **Canonical build-against spec.** This is the spine. Detail lives in `docs/`:
> [architecture](docs/architecture.md) · [data model](docs/data-model.md) ·
> [roadmap](docs/roadmap.md) · [demo script](docs/demo-script.md) ·
> [public safety](docs/public-safety.md) · [portfolio integration](docs/portfolio-integration.md).
>
> Status: **Design complete, build not started.** Last updated 2026-06-20.

---

## 1. One-line pitch

**Workflow MRI ingests a chaotic company's operational artifacts — spreadsheets, PDFs,
emails, screenshots, notes — reconstructs how work actually flows, exposes bottlenecks,
duplicate work, and compliance risk, recommends automations with estimated time savings,
and exports a governed handoff package with an audit trail.**

It is an *operations diagnostician*: a hospital MRI for a business process.

## 2. Why this project, why now

Eric's portfolio (11 projects at `nogor-design.github.io/portfolio-showcase`) and GitHub
already prove **range** — local-first AI, multi-agent systems, RAG, ops dashboards,
trading sims. Three independent reviews converge on the same two gaps:

1. **No single flagship** that embodies the central claim — *"I turn messy real-world
   workflows into governed, measurable operating systems."*
2. **Low visual impact.** The portfolio is text-and-links; recruiters scan in 30 seconds.

Workflow MRI closes both. It is the one unforgettable artifact that ties the whole
narrative together, and its centerpiece — an interactive, before/after process graph with
a risk overlay — is the screenshot that wins interviews.

**Audience (in priority order):** hiring managers for AI / senior / platform / automation
engineering roles; founders & operators wanting workflow automation; enterprise
internal-tools teams that care about governance and auditability.

## 3. The single most important design decision

**The engine and the showcase are two artifacts joined by one contract: the Artifact Bundle.**

| | Engine (`engine/`) | Showcase (`web/`) |
|---|---|---|
| What | Local-first, multi-agent Python pipeline | React + Vite static SPA |
| Job | Turn messy inputs → a typed, JSON-safe **Artifact Bundle** | Render a Bundle beautifully and interactively |
| Runs | Locally / offline (Ollama or Claude, pluggable) | In any browser, **statically on GitHub Pages**, no server |
| LLM at demo time | **None** | **None** |

Why this split is non-negotiable for a *portfolio* piece:

- A public demo must **always work** in a 30-second scan — no API keys, no cold Ollama,
  no cost, no live-call flakiness during an interview.
- You cannot run Ollama on GitHub Pages. So the real local-first engine runs **offline**,
  produces a deterministic Bundle, and the Bundle is **committed** and replayed by the
  static UI.
- The separation is itself a strong engineering story and mirrors Eric's `ta_foundation`
  layer discipline: *the engine computes; the UI is a pure, deterministic renderer.*

> **Honesty contract:** the public demo is labeled as a replay of a pre-computed run over
> a **fictional** company. The engineering underneath is real and reproducible
> (`make bundle` regenerates it locally). Nothing is faked; it is *baked*.

See [docs/architecture.md](docs/architecture.md) for the full picture.

## 4. Locked decisions (2026-06-20)

| Decision | Choice | Rationale |
|---|---|---|
| Showcase UI stack | **React + Vite static SPA** | Free static deploy to GitHub Pages; highest visual ceiling for the interactive graph (React Flow); matches Next.js/React/TS already on the portfolio. |
| Engine LLM | **Hybrid pluggable backend** | One `LLMClient` interface; **default local Ollama** (reinforces the local-first narrative the reviews praised), optional **Claude** for higher-quality baked runs. Backend is swappable without touching pipeline code. |
| This deliverable | **Design doc + repo scaffold** | Folders, READMEs, stubs, and these docs so building can start immediately; no feature code yet. |

## 5. Design principles (non-negotiables)

1. **Public-safe by construction.** Only fictional/synthetic data ever enters the repo.
   No real customer data, no secrets, no proprietary IP. See [public-safety](docs/public-safety.md).
2. **Deterministic demo.** The committed Bundle fully determines what the public sees.
   Same Bundle → same pixels. No live inference on the critical path.
3. **Local-first engine.** Defaults to Ollama; runs with no cloud dependency.
4. **Layer separation.** Ingestion → Extraction → Graph → Risk → Recommend → Simulate →
   Export. Each layer consumes typed objects and emits typed objects. The UI reads only
   the Bundle — never files, never an LLM.
5. **Governance is a feature, not a footnote.** Confidence scores, "why this was flagged"
   evidence links, a human-review queue, and an audit log are first-class outputs. If
   scope is cut, cut AI polish before governance.
6. **Artifacts over summaries.** Every run yields downloadable, stakeholder-specific
   deliverables, not just prose.
7. **Evals prove it works.** Synthetic ground truth → measured extraction accuracy,
   risk recall, and hallucination rate. Numbers go on the case-study page.

## 6. System architecture (summary)

```
                         ┌──────────────────────────── ENGINE (Python, local-first) ────────────────────────────┐
  samples/                │                                                                                       │
  meridian-claims/  ──►  Ingestion ─► Extraction ─► Graph ─► Risk ─► Recommend ─► Simulate ─► Export ──► Artifact │
  (fictional inputs)      (normalize)  (LLM+rules)  (build) (rules+ (score      (before/    (assemble)   Bundle   │
                          │                                  LLM)   value/effort) after sim)            (JSON +   │
                          │                              ▲                                              assets)   │
                          │              LangGraph agents │  LLMClient ── Ollama | Claude (pluggable)             │
                          └──────────────────────────────┼────────────────────────────────────────────┬─────────┘
                                                          │                                             │
                                                   evals/ (synthetic ground truth)            committed to web/public/bundle/
                                                                                                        │
                         ┌──────────────────────── SHOWCASE (React + Vite, static) ◄─────────────────────┘
                         │  Landing ─► Ingest view ─► Process Graph ─► Risk panel ─► Automations ─► Before/After ─► Export
                         │  (pure renderer of the Bundle; zero IO, zero LLM, deploys to GitHub Pages)
                         └───────────────────────────────────────────────────────────────────────────────────────
```

Pipeline layers (each is a package under `engine/workflow_mri/`):

1. **Ingestion** — accept files, detect type, normalize into an artifact store with metadata.
2. **Extraction** — LLM + rules pull entities, dates, owners, steps, approvals, exceptions;
   every field carries a confidence score.
3. **Graph** — build a directed workflow graph; detect bottlenecks, loops, duplicate handoffs,
   missing fields, orphaned steps.
4. **Risk** — rules + LLM flag PII, missing-approval evidence, inconsistent status labels,
   ambiguous ownership, review-bypass, low-confidence extractions.
5. **Recommend** — score automation candidates by value (time saved) × effort × required oversight.
6. **Simulate** — before/after cycle-time & cost estimate (clearly labeled as simulated).
7. **Export** — assemble the typed **Artifact Bundle** (+ derived export files).

Full detail: [docs/architecture.md](docs/architecture.md).

## 7. The Artifact Bundle (the contract)

A single versioned, JSON-safe directory the engine writes and the UI reads. Top-level objects:
`Manifest, Artifact, Document, Entity, WorkflowStep, ProcessEdge, Exception, RiskFinding,
ReviewTask, AutomationCandidate, SimulationResult, AuditEvent, ExportFile`.

Every analytic object links back to the evidence (`Artifact`/`Document` ids) that produced it,
which powers the "why was this flagged" UX and the audit trail. The schema is the *single
source of truth* shared by engine (Pydantic) and UI (TypeScript types generated from it).

Full schema + JSON examples: [docs/data-model.md](docs/data-model.md).

## 8. The sample company

One fully-built fictional company ships in the MVP so the demo always works:
**"Meridian Claims Co."** — a small insurance-claims operation whose process is scattered
across inconsistent spreadsheets, PDF SOPs/forms, email approval threads, dashboard
screenshots, and employee notes. Claims chosen deliberately: a clear linear workflow
(intake → triage → review → approval → payment → exception → closure), rich PII surface,
and obvious compliance stakes — ideal to show governance. Inputs live in
`samples/meridian-claims/`. Later companies (onboarding, vendor mgmt, support) are additive.

## 9. Showcase UI spec (views)

A dark, enterprise-grade SPA. The interactive process graph is visually dominant.

1. **Landing** — the hook ("Upload your chaotic operations folder"), the fictional sample
   company tile, the one-claim narrative, a 20-second auto-playing teaser of the graph.
2. **Ingest** — file inventory: counts, detected types, extraction confidence, "items
   needing review." Feels magical but believable.
3. **Process Graph** *(centerpiece)* — React Flow swimlane graph: steps, owners, handoffs,
   cycle times; bottleneck heatmap; loops & duplicate handoffs highlighted. Click any node →
   evidence drawer.
4. **Risk & Quality** — findings list with severity chips, each with "why this was flagged"
   evidence links.
5. **Automations** — prioritized cards: time saved, confidence, required oversight,
   implementation complexity.
6. **Before / After** — side-by-side simulated cycle-time & cost, clearly labeled simulated.
7. **Export & Handoff** — the downloadable package (process map, schema JSON, review-queue
   CSV, audit log, backlog, tests).
8. **Case-study mode** — a portfolio overlay: problem → architecture → evals → "what I'd
   build next," for recruiters.

UX cues: status chips, confidence indicators, "needs review" states, a "regen with safer
mode" toggle to signal governance awareness.

## 10. Engine spec

- **`llm/`** — `LLMClient` protocol + `OllamaClient` and `ClaudeClient`; selected by config/env.
  All prompts versioned; all calls logged for the audit trail and evals.
- **`agents/`** — LangGraph orchestration: extraction agent → graph agent → risk agent →
  recommender, with a critic/review pass. Human-in-the-loop seams for the review queue.
- **`schema/`** — Pydantic models = the Bundle contract; a `make types` step emits matching
  TypeScript for the UI.
- **`export/`** — assembles the Bundle and the derived export files.
- **`evals/`** — synthetic ground truth for Meridian → extraction accuracy, risk recall,
  hallucination rate, simulated time-savings sanity.

When unsure about an LLM/provider detail, consult the `claude-api` skill before coding;
do not reason about model behavior from memory.

## 11. Public-safety contract

Every input is fictional and obviously so. A redaction/secret-scan pass runs before any
publish. No real names, accounts, PII, or proprietary logic. The simulation panel is
labeled "simulated." Details and the pre-publish checklist: [docs/public-safety.md](docs/public-safety.md).

## 12. Roadmap (sequenced for earliest "wow")

The build is ordered so the interview-winning screenshot — the interactive before/after
process graph — exists as early as possible, even before deep extraction is polished.

- **Phase 0** — Repo, contract, seeded sample, Bundle stub, UI shell. *(this scaffold)*
- **Phase 1** — Hand-authored "golden" Bundle for Meridian → render the full UI end-to-end.
  *The flagship screenshot exists here, decoupled from the engine.*
- **Phase 2** — Real engine: ingestion + extraction + graph builder produce the Bundle.
- **Phase 3** — Risk engine, review queue, automation recommender, before/after simulation.
- **Phase 4** — Evals, polish, case-study page, demo recording, portfolio link.

Full task-level plan: [docs/roadmap.md](docs/roadmap.md).

## 13. Definition of done

- Public static demo live at a GitHub Pages URL, linked from the portfolio.
- Loads instantly, always works, runs the full Meridian narrative with no setup.
- `make bundle` reproduces the committed Bundle locally from `samples/` (engine is real).
- Case-study page: problem, architecture diagram, eval numbers, governance model,
  "what I'd build next."
- A 2–3 min demo GIF/video embedded.
- Public-safety checklist passed.
- **The page makes a reviewer believe the central claim in under 5 minutes.**

## 14. Open questions / future

- Second sample company (onboarding or support) once the engine generalizes.
- Optional live "bring your own folder" mode behind a local run (never on the public path).
- "Research the domain while mapping the workflow" tie-in to `local-deep-research`.
- Deeper evals: red-teaming the extractor on adversarially messy inputs.
