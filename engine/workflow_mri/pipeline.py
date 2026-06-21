"""Pipeline entry point.

`build_bundle` delegates to the agent orchestrator (ingest -> graph -> risk -> recommend ->
simulate -> optional enrich -> assemble -> critic), which runs as a LangGraph state graph
when available and a deterministic sequential runner otherwise. Deterministic and offline by
default; LLM enrichment is opt-in via `enrich=True`.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from workflow_mri.agents import orchestrate
from workflow_mri.schema import Bundle


def build_bundle(
    samples_dir: Path,
    *,
    run_id: str | None = None,
    enrich: bool = False,
    llm_backend: str | None = None,
) -> Bundle:
    return orchestrate(
        samples_dir,
        run_id=run_id or f"meridian-{datetime.now():%Y-%m-%d}",
        enrich=enrich,
        llm_backend=llm_backend,
    )
