# Roadmap

Companion to [`../DESIGN.md`](../DESIGN.md) §12. Sequenced so the **interview-winning
screenshot** (interactive before/after process graph) exists as early as possible —
decoupled from, and ahead of, the deep engine work.

Each phase ends in a **demoable or verifiable** state. Don't start a phase before the
previous one's "done" check passes.

---

## Phase 0 — Foundation *(this scaffold)*

**Goal:** a real repo with the contract and structure in place.

- [x] Repo skeleton, git init, idea docs archived to `docs/ideas/`.
- [x] Design docs (`DESIGN.md` + `docs/`).
- [x] `engine/pyproject.toml`, package stubs, `Makefile` targets.
- [x] `web/` Vite + React + TypeScript app scaffold.
- [x] Pydantic schema stubs for the Bundle objects.
- [x] CI: build the static web app; deploy to GitHub Pages on push to `main`.

**Done when:** an empty styled SPA deploys to a GitHub Pages URL and the repo reads like a
serious project at first glance.

---

## Phase 1 — Golden Bundle + full UI *(the flagship screenshot)*

**Goal:** the complete narrative renders end-to-end from a **hand-authored** Bundle, before
the engine can generate one. This front-loads the visual payoff and de-risks the contract.

- [x] Hand-author a realistic `web/public/bundle/` for Meridian Claims (all object types).
- [x] Build the core views (DESIGN §9), centerpiece first: **Process Graph** (custom SVG
      swimlanes, bottleneck glow, edge-kind styling, clickable evidence panel).
- [x] Before/After view + Risk panel + Automations cards + Ingest view.
- [x] Dark enterprise theme, status/confidence chips, "needs review" states.
- [x] Export & Handoff view (download buttons present; wired to real files in Phase 2).
- [x] Polish pass: landing/hero entry with auto-cycling before/after teaser; safe-mode
      toggle (real PII redaction of evidence); animated before→after graph morph (segmented
      control on the Process Graph).
- [ ] Capture the flagship screenshot/GIF (needs a browser session — extension not connected
      in this environment; run `npm run dev` and capture manually).

**Done when:** a reviewer can click through the entire Meridian story and it looks like a
finished product. **Capture the flagship screenshot/GIF here.**

> Core views landed 2026-06-20; build is green (`npm run build`). The landing entry,
> Safe Mode toggle, before/after process graph mode, and deterministic replay bundle are
> in place. Remaining: capture the flagship screenshot/GIF and publish the portfolio
> case-study integration.

---

## Phase 2 — Real engine (ingest → extract → graph)

**Goal:** `make bundle` regenerates the Meridian Bundle from `samples/` for real.

- [x] Author the fictional `samples/meridian-claims/` inputs (messy on purpose): a claims
      **event log** CSV (variant labels, mixed status vocab, planted PII, loop/bypass/dup
      cases), a second payment register, SOP, notes, email, and a screenshot OCR sidecar.
- [x] `llm/` — `LLMClient` protocol + Ollama (default) + Claude clients; `WORKFLOW_MRI_LLM`
      switch. Optional enrichment only; the core pipeline is deterministic and offline.
- [x] Ingestion: folder walk, kind detection, text/row loading → `Artifact` records.
- [x] Extraction + graph: **process-mining** a directly-follows graph from the event log →
      `WorkflowStep`/`ProcessEdge` with cycle times, bottleneck, loop/duplicate/bypass.
- [x] Risk rules (PII regex, missing-approval, review-bypass, ambiguous-ownership,
      inconsistent-status, low-confidence), recommender, and before/after simulation.
- [x] `export/` writes a schema-valid Bundle; `python -m workflow_mri build [--promote]` +
      `make bundle` / `make promote`. 9 pipeline tests assert the golden shape.

**Done when:** the generated Bundle renders in the existing UI with no UI changes, and
matches the golden Bundle's shape. ✅ **Met 2026-06-20** — promoted bundle drives the web app
(7 steps, all 5 edge kinds, 8 risks across all 6 categories); web build + 11 engine tests green.

> Note: the deterministic engine reconstructs the process by **mining the event log** (a real
> analytic technique), with the LLM as optional enrichment — chosen so `make bundle` is
> reproducible and runs offline/in CI. See [architecture](architecture.md).

---

## Phase 3 — Governance + recommendations + simulation

**Goal:** the parts that make it memorable rather than just a graph.

- [ ] Risk engine: rules + LLM → `RiskFinding`s (PII, missing approvals, inconsistent
      status, ambiguous ownership, review-bypass, low-confidence) with evidence links.
- [ ] Review queue: `ReviewTask`s + approve/override/reject state in the audit log.
- [ ] Automation recommender: value × effort × oversight scoring → ranked `AutomationCandidate`s.
- [ ] Simulation: deterministic before/after cycle-time & cost over the graph (labeled simulated).
- [ ] LangGraph agent wiring with a critic/review pass; emit `AuditEvent`s for every decision.

**Done when:** the full Bundle is engine-generated end-to-end and governance objects are real.

---

## Phase 4 — Evals, polish, publish

**Goal:** prove it works and make it land.

- [ ] `evals/` synthetic ground truth → extraction accuracy, risk recall, hallucination rate.
- [ ] Case-study page: problem, architecture diagram, **eval numbers**, governance model,
      "what I'd build next."
- [ ] 2–3 min demo GIF/video, embedded.
- [ ] Public-safety checklist pass ([public-safety.md](public-safety.md)).
- [ ] Link from `nogor-design.github.io/portfolio-showcase` ([portfolio-integration.md](portfolio-integration.md)).

**Done when:** DESIGN §13 Definition of Done is fully met.

---

## Sequencing rationale

- **UI before engine (Phase 1 before 2)** is deliberate: the portfolio value is the visible
  artifact, and a hand-authored Bundle locks the contract and surfaces UI needs before
  expensive engine work. It also means you *always* have a working demo to show.
- **Governance after the happy path (Phase 3)** but **never cut**: if time runs short, ship
  Phases 0–2 + a partial Phase 3, but keep risk findings + review queue — they are the
  differentiator.
- **Evals last but mandatory (Phase 4):** the numbers are what separate this from a polished
  toy on the case-study page.

## Effort note

The original idea docs framed this as a 4-week plan. That maps cleanly onto Phases 1–4
(~one week each) with Phase 0 as a setup day. Adjust to actual availability; the phase
gates matter more than the calendar.
