# engine/

Local-first, multi-agent Python pipeline. Turns messy inputs in `samples/<company>/` into a
typed, JSON-safe **Artifact Bundle** (the contract consumed by `web/`).

See [`../docs/architecture.md`](../docs/architecture.md) for the full pipeline and
[`../docs/data-model.md`](../docs/data-model.md) for the Bundle schema.

## Build a bundle

```bash
pip install -e .
python -m workflow_mri build            # -> bundles/<run_id>/
python -m workflow_mri build --promote  # also copy into web/public/bundle/
# or: make bundle  /  make promote
```

The pipeline: **ingest** the sample folder → **mine** a directly-follows process graph from
the claims event log (steps, cycle times, bottleneck, loop/duplicate/bypass edges) →
**detect risks** with rules over structured + unstructured artifacts → **recommend** +
**simulate** → **export** a schema-valid Artifact Bundle. Deterministic and offline.

## Packages (`workflow_mri/`)

`llm/` (clients) · `ingestion/` (loader) · `extraction/` (event-log normalize) ·
`graph/` (process mining) · `risk/` (rules) · `recommend/` · `simulate/` · `export/` ·
`schema/` (Bundle contract) · `pipeline.py` · `cli.py`.

## LLM backend

Pluggable behind `llm.LLMClient`. Default **Ollama** (local-first); optional **Claude** for
higher-quality baked runs. Selected by env/config. Keys live in `.env` only (gitignored) —
never committed. Consult the `claude-api` skill before writing Claude-backed code; don't
reason about model behavior from memory.

## Status

Phase 2 complete — the engine mines a schema-valid Bundle from `samples/meridian-claims/`
that renders unchanged in the web app. 11 tests (`python -m pytest`). LLM enrichment
(Phase 3, optional) and evals (Phase 4) are next.
