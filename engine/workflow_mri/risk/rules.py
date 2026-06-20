"""Deterministic risk detection over structured events and unstructured artifacts.

Each finding links to the evidence that triggered it. No LLM required — these are auditable
rules. (An optional LLM pass can later add softer, judgment-based findings.)
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from workflow_mri.extraction.event_log import Event
from workflow_mri.ingestion.loader import LoadedArtifact
from workflow_mri.schema import EvidenceRef, ProcessEdge, RiskFinding, WorkflowStep

_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_DOB = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b")


def detect_risks(
    events: list[Event],
    loaded: list[LoadedArtifact],
    steps: list[WorkflowStep],
    edges: list[ProcessEdge],
    event_log_artifact_id: str,
) -> list[RiskFinding]:
    risks: list[RiskFinding] = []
    n = 0

    def nid(p: str) -> str:
        nonlocal n
        n += 1
        return f"risk_{p}_{n:03d}"

    # 1. PII in unstructured artifacts (notes / emails) + event-log notes
    for la in loaded:
        if la.artifact.kind in ("note", "email") and (_SSN.search(la.text) or _DOB.search(la.text)):
            quote = _first_pii_line(la.text)
            risks.append(RiskFinding(
                id=nid("pii"), category="pii", severity="high",
                title=f"PII in {la.artifact.detected_type}",
                description="Claimant identifiers (SSN/DOB/address) appear in free text outside any access-controlled field.",
                step_id="step_review", confidence=0.94,
                suggested_action="Mask/relocate PII to a controlled field; redact from free text.",
                evidence=[EvidenceRef(artifact_id=la.artifact.id, quote=quote)],
            ))
    if any(_SSN.search(e.notes) or _DOB.search(e.notes) for e in events):
        e = next(e for e in events if _SSN.search(e.notes) or _DOB.search(e.notes))
        risks.append(RiskFinding(
            id=nid("pii"), category="pii", severity="high",
            title="PII in event-log notes",
            description="Synthetic SSN/DOB recorded in the claim event log's free-text notes column.",
            step_id="step_review", confidence=0.92,
            suggested_action="Drop PII from operational logs; capture identifiers only in the secured record.",
            evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=e.notes)],
        ))

    # 2. Approvals recorded without evidence (blank approver)
    blank = [e for e in events if e.activity == "approval" and not e.approver]
    if blank:
        risks.append(RiskFinding(
            id=nid("appr"), category="missing_approval", severity="high",
            title="Approvals recorded without sign-off evidence",
            description=f"{len(blank)} approval event(s) have no approver/sign-off attached — approval is asserted but not evidenced.",
            step_id="step_approval", confidence=0.88,
            suggested_action="Require a sign-off artifact before status can move to Approved.",
            evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=f"{blank[0].case_id}: approver column blank")],
        ))

    # 3. Review bypass (a mined bypass edge)
    bypass = [e for e in edges if e.kind == "bypass"]
    if bypass:
        risks.append(RiskFinding(
            id=nid("bypass"), category="review_bypass", severity="high",
            title="Claims skip Document Review",
            description="A directly-follows path jumps from intake to approval, bypassing the mandatory Document Review control.",
            step_id="step_review", confidence=0.86,
            suggested_action="Route all claims through review; log fast-tracks as explicit, controlled exceptions.",
            evidence=bypass[0].evidence,
        ))

    # 4. Ambiguous ownership (an activity performed by >1 role)
    roles: dict[str, set[str]] = defaultdict(set)
    for e in events:
        roles[e.activity].add(e.role)
    for activity, rs in roles.items():
        if len(rs) > 1:
            risks.append(RiskFinding(
                id=nid("owner"), category="ambiguous_ownership", severity="med",
                title=f"Ambiguous ownership at {activity.title()}",
                description=f"{activity.title()} was performed by multiple roles ({', '.join(sorted(rs))}), creating duplicate handoffs and unclear accountability.",
                step_id=f"step_{activity}", confidence=0.78,
                suggested_action="Assign a single owner per claim with a documented tie-break rule.",
                evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=f"{activity} roles: {', '.join(sorted(rs))}")],
            ))

    # 5. Inconsistent status vocabulary across registers
    statuses = Counter(e.status for e in events if e.status)
    ledger_states: set[str] = set()
    for la in loaded:
        if "payment" in la.path.name.lower():
            ledger_states = {r.get("state", "").strip() for r in la.rows if r.get("state")}
    closed_like = {s for s in list(statuses) + list(ledger_states) if any(w in s.lower() for w in ("paid", "closed", "disbursed"))}
    if len(closed_like) > 1:
        risks.append(RiskFinding(
            id=nid("status"), category="inconsistent_status", severity="med",
            title="Conflicting status vocabularies",
            description=f"The same terminal state is recorded under {len(closed_like)} different labels ({', '.join(sorted(closed_like))}), breaking reconciliation.",
            confidence=0.8,
            suggested_action="Adopt a single canonical status enum across registers.",
            evidence=[EvidenceRef(artifact_id=event_log_artifact_id, quote=", ".join(sorted(closed_like)))],
        ))

    # 6. Low-confidence extraction from a screenshot
    for la in loaded:
        if la.artifact.kind == "screenshot":
            risks.append(RiskFinding(
                id=nid("lowconf"), category="low_confidence", severity="low",
                title="Low-confidence extraction from dashboard screenshot",
                description=f"Counts were OCR'd from a screenshot at {int(la.artifact.extraction_confidence * 100)}% confidence; confirm against the source system.",
                confidence=la.artifact.extraction_confidence,
                suggested_action="Pull counts from the source system rather than a screenshot.",
                evidence=[EvidenceRef(artifact_id=la.artifact.id, quote="OCR of dashboard tiles")],
            ))
            break

    return risks


def _first_pii_line(text: str) -> str:
    for line in text.splitlines():
        if _SSN.search(line) or _DOB.search(line):
            return line.strip()[:160]
    return ""
