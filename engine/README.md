# engine/

Local-first, multi-agent Python pipeline. Turns messy inputs in `samples/<company>/` into a
typed, JSON-safe **Artifact Bundle** (the contract consumed by `web/`).

See [`../docs/architecture.md`](../docs/architecture.md) for the full pipeline and
[`../docs/data-model.md`](../docs/data-model.md) for the Bundle schema.

## Packages (`workflow_mri/`)

`llm/` · `ingestion/` · `extraction/` · `graph/` · `risk/` · `recommend/` · `simulate/` ·
`export/` · `agents/` · `schema/` — each carries a one-line docstring describing its job.

## LLM backend

Pluggable behind `llm.LLMClient`. Default **Ollama** (local-first); optional **Claude** for
higher-quality baked runs. Selected by env/config. Keys live in `.env` only (gitignored) —
never committed. Consult the `claude-api` skill before writing Claude-backed code; don't
reason about model behavior from memory.

## Status

Phase 0 stubs only. Implementation begins in roadmap Phase 2.
