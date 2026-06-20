"""workflow_mri.llm

Pluggable LLM backend. One `LLMClient` protocol; the engine never imports a vendor SDK
directly — it depends on this interface so Ollama (default, local-first) and Claude are
interchangeable per the hybrid decision (DESIGN.md §4).

Phase 0: protocol + factory signature only. Concrete OllamaClient / ClaudeClient land in
roadmap Phase 2. When implementing the Claude path, consult the `claude-api` skill for model
ids/params rather than reasoning from memory; keep keys in env only (never committed).
"""

from __future__ import annotations

import os
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Minimal surface the pipeline relies on. Concrete clients also emit AuditEvents."""

    name: str

    def complete(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.0) -> str:
        """Return a completion. Structured callers validate/constrain the result downstream."""
        ...


def get_client(backend: Optional[str] = None) -> "LLMClient":
    """Select a backend by arg, then $WORKFLOW_MRI_LLM, defaulting to local Ollama.

    Not yet implemented (Phase 2). Defined now so config wiring and types are stable.
    """
    backend = backend or os.environ.get("WORKFLOW_MRI_LLM", "ollama")
    raise NotImplementedError(
        f"LLM backend '{backend}' not implemented until roadmap Phase 2 "
        "(OllamaClient / ClaudeClient)."
    )


__all__ = ["LLMClient", "get_client"]
