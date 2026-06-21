"""Serialize a Bundle to the on-disk Artifact Bundle the showcase consumes.

One JSON file per object array, matching web/src/bundle/load.ts. JSON-safe by construction
(Pydantic model_dump mode="json").
"""

from __future__ import annotations

import json
from pathlib import Path

from workflow_mri.schema import Bundle

_FILES = {
    "manifest.json": "manifest",
    "artifacts.json": "artifacts",
    "steps.json": "steps",
    "edges.json": "edges",
    "risks.json": "risks",
    "reviews.json": "reviews",
    "automations.json": "automations",
    "simulation.json": "simulation",
    "audit.json": "audit",
    "exports.json": "exports",
}


def write_bundle(bundle: Bundle, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    data = bundle.model_dump(mode="json")
    for filename, key in _FILES.items():
        (out_dir / filename).write_text(
            json.dumps(data[key], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return out_dir
