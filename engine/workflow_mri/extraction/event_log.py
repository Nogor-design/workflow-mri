"""Normalize a messy claim event log into canonical events.

Real-world event logs use inconsistent activity labels; we map every variant to a canonical
activity so the miner sees a clean signal. This is the deterministic extraction step.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# canonical activity -> (display name, default owner, sequence index, is_review, is_approval)
CANON = {
    "intake": ("Claim Intake", "Intake Clerk", 0, False, False),
    "triage": ("Triage & Assignment", "Triage Specialist", 1, False, False),
    "review": ("Document Review", "Adjuster", 2, True, False),
    "approval": ("Manager Approval", "Claims Manager", 3, False, True),
    "payment": ("Payment", "Finance", 4, False, False),
    "exception": ("Exception Handling", "Adjuster", 5, False, False),
    "closure": ("Closure", "Intake Clerk", 6, False, False),
}

# label variant (lowercased) -> canonical
_LABELS = {
    "claim intake": "intake", "intake": "intake",
    "triage & assignment": "triage", "triage": "triage", "assign": "triage",
    "document review": "review", "doc review": "review", "review": "review",
    "manager approval": "approval", "approval": "approval", "mgr approval": "approval",
    "payment": "payment", "disbursement": "payment", "pay": "payment",
    "exception handling": "exception", "exception": "exception",
    "closure": "closure", "close": "closure",
}


@dataclass
class Event:
    case_id: str
    activity: str  # canonical key
    role: str
    ts: datetime
    status: str
    approver: str
    notes: str


def normalize_activity(raw: str) -> Optional[str]:
    return _LABELS.get(raw.strip().lower())


def parse_events(rows: list[dict]) -> list[Event]:
    events: list[Event] = []
    for r in rows:
        canon = normalize_activity(r.get("activity", ""))
        if not canon:
            continue
        try:
            ts = datetime.fromisoformat(r["ts"])
        except (KeyError, ValueError):
            continue
        events.append(
            Event(
                case_id=r.get("case_id", "").strip(),
                activity=canon,
                role=r.get("role", "").strip(),
                ts=ts,
                status=r.get("status", "").strip(),
                approver=r.get("approver", "").strip(),
                notes=r.get("notes", "").strip(),
            )
        )
    return events


def by_case(events: list[Event]) -> dict[str, list[Event]]:
    cases: dict[str, list[Event]] = {}
    for e in events:
        cases.setdefault(e.case_id, []).append(e)
    for evs in cases.values():
        evs.sort(key=lambda e: e.ts)
    return cases
