"""Ingestion: walk a sample company folder, classify artifacts, load their text.

Dependency-light on purpose — stdlib only — so `make bundle` runs offline and in CI.
Each file becomes an Artifact (+ a Document holding its text/rows). Kind is inferred from
the subfolder and extension; confidence is a heuristic the rest of the pipeline can surface.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from workflow_mri.schema import Artifact

# folder -> default artifact kind
_FOLDER_KIND = {
    "spreadsheets": "csv",
    "pdfs": "pdf",
    "emails": "email",
    "screenshots": "screenshot",
    "notes": "note",
}
_EXT_KIND = {".csv": "csv", ".xlsx": "xlsx", ".eml": "email", ".txt": "note", ".md": "pdf"}

# heuristic extraction confidence by kind (screenshots/OCR are least reliable)
_KIND_CONF = {"csv": 0.92, "xlsx": 0.85, "pdf": 0.82, "email": 0.76, "note": 0.66, "screenshot": 0.57}


@dataclass
class LoadedArtifact:
    artifact: Artifact
    path: Path
    text: str = ""
    rows: list[dict] = field(default_factory=list)  # for tabular artifacts


def _now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _classify(path: Path) -> str:
    folder = path.parent.name
    if folder in _FOLDER_KIND:
        base = _FOLDER_KIND[folder]
        # an .ocr.txt inside screenshots/ is still a screenshot
        if folder == "screenshots":
            return "screenshot"
        if folder == "spreadsheets":
            return _EXT_KIND.get(path.suffix.lower(), "csv")
        return base
    return _EXT_KIND.get(path.suffix.lower(), "note")


def load_company(samples_dir: Path) -> list[LoadedArtifact]:
    """Load every file under samples_dir (excluding READMEs), deterministically ordered."""
    out: list[LoadedArtifact] = []
    files = sorted(p for p in samples_dir.rglob("*") if p.is_file() and p.name.lower() != "readme.md")
    for i, path in enumerate(files, start=1):
        kind = _classify(path)
        rows: list[dict] = []
        text = ""
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            text = path.read_text(encoding="utf-8")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        art = Artifact(
            id=f"art_{i:03d}",
            kind=kind,  # type: ignore[arg-type]
            source_name=path.name,
            detected_type=_detected_type(path, kind),
            ingested_at=_now_iso(),
            page_count=max(1, text.count("\f") + 1),
            extraction_confidence=_KIND_CONF.get(kind, 0.7),
        )
        out.append(LoadedArtifact(artifact=art, path=path, text=text, rows=rows))
    return out


def _detected_type(path: Path, kind: str) -> str:
    name = path.name.lower()
    if "event_log" in name:
        return "claim event log"
    if "payment" in name:
        return "payment ledger"
    if "sop" in name:
        return "standard operating procedure"
    if kind == "email":
        return "approval thread"
    if kind == "screenshot":
        return "dashboard screenshot"
    if kind == "note":
        return "employee notes"
    return kind


def find_event_log(loaded: list[LoadedArtifact]) -> Optional[LoadedArtifact]:
    for la in loaded:
        if "event_log" in la.path.name.lower():
            return la
    return None
