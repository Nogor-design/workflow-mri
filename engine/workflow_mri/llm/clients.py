"""Concrete LLM backends behind the `LLMClient` protocol.

Optional enrichment only — the core pipeline (process-mining + rules) is deterministic and
never calls these, so `make bundle` runs offline with no model or key. When enabled, both
clients implement the same `complete()` surface so they are interchangeable per config/env.

Vendor SDKs are imported lazily so neither is a hard dependency of the engine.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional


class OllamaClient:
    """Local-first default. Talks to a running Ollama server over HTTP (stdlib only)."""

    def __init__(self, model: Optional[str] = None, host: Optional[str] = None) -> None:
        self.name = "ollama"
        self.model = model or os.environ.get("WORKFLOW_MRI_OLLAMA_MODEL", "llama3.1:8b")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def complete(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.0) -> str:
        body = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {"temperature": temperature},
        }
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310 (localhost)
            return json.loads(resp.read()).get("response", "")


class ClaudeClient:
    """Higher-quality enrichment via the Anthropic API. Key from env only (never committed)."""

    def __init__(self, model: str = "claude-opus-4-8") -> None:
        self.name = "claude"
        self.model = model
        try:
            import anthropic  # lazy: optional dependency
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("ClaudeClient requires the 'anthropic' package (pip install -e '.[llm]')") from e
        self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    def complete(self, prompt: str, *, system: Optional[str] = None, temperature: float = 0.0) -> str:
        # Opus 4.8: adaptive thinking is the default; sampling params are not sent.
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
