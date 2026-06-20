# Workflow MRI

> An operations diagnostician — an MRI for a business process.

Upload a chaotic company's operational artifacts (spreadsheets, PDFs, emails, screenshots,
notes) and Workflow MRI reconstructs how work actually flows, exposes bottlenecks, duplicate
work, and compliance risk, recommends automations with estimated time savings, and exports a
governed handoff package with an audit trail.

**Status:** Phase 1 static demo is live locally and ready for portfolio packaging.
The hand-authored Meridian Claims bundle renders the full React workbench: landing,
ingest summary, process graph, risk panel, automation recommendations, before/after
simulation, Safe Mode redaction, and export handoff view. The engine remains in
Phase 0/2 scaffold state; `make bundle` is still the next implementation milestone.
See [`DESIGN.md`](DESIGN.md) and [`docs/roadmap.md`](docs/roadmap.md).

## How it's built

Two artifacts joined by one contract:

- **`engine/`** — a local-first, multi-agent Python pipeline (pluggable Ollama/Claude,
  LangGraph) that turns messy inputs into a typed, JSON-safe **Artifact Bundle**.
- **`web/`** — a React + Vite static SPA that renders a Bundle into an interactive
  before/after process graph, risk panel, automation recommendations, and handoff export.
  It performs **no inference and no IO** — it's a pure renderer, so the public demo always
  works and deploys free to GitHub Pages.

The Bundle is committed, so the public demo is a deterministic replay of a baked run over a
**fictional** company (Meridian Claims Co.). The engine is real and reproducible:
`make bundle` regenerates the Bundle locally.

## Documentation

| Doc | What |
|---|---|
| [`DESIGN.md`](DESIGN.md) | Canonical build-against spec (start here) |
| [docs/architecture.md](docs/architecture.md) | Two-artifact model, pipeline, repo layout, commands |
| [docs/data-model.md](docs/data-model.md) | The Artifact Bundle contract (schema + examples) |
| [docs/roadmap.md](docs/roadmap.md) | Phased build plan (sequenced for earliest "wow") |
| [docs/demo-script.md](docs/demo-script.md) | Narrated walkthrough for the demo recording |
| [docs/public-safety.md](docs/public-safety.md) | Public-safe contract + pre-publish checklist |
| [docs/portfolio-integration.md](docs/portfolio-integration.md) | How it links from the portfolio |
| [docs/ideas/](docs/ideas/) | Original idea/brief docs (archived) |

## Quick start

```bash
make bundle      # engine: samples/meridian-claims → bundles/<run>/
make promote     # publish a verified bundle → web/public/bundle/
make web         # vite dev server for the showcase
make web-build   # static export for GitHub Pages
make evals       # synthetic-ground-truth metrics
make test        # engine (pytest) + web (vitest)
```

Current verification:

- `cd web && npm run build` builds the GitHub Pages-ready static app.
- `cd web && npm test` runs the web safety/unit checks.
- `cd engine && python -m pytest` runs the schema smoke tests.
