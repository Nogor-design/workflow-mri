"""Artifact Bundle schema — the contract between engine and showcase.

Source of truth for both sides. See docs/data-model.md for the on-disk layout and field
notes. TypeScript types for the UI are generated from these models (`make types`), so the
two sides cannot drift.

Phase 0: shapes only, no business logic. Fields may be refined as the engine is built; bump
BUNDLE_VERSION on any breaking change.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

BUNDLE_VERSION = "1.0"


class EvidenceRef(BaseModel):
    """Pointer back to the input that produced an analytic object."""

    artifact_id: str
    document_id: Optional[str] = None
    page: Optional[int] = None
    cell: Optional[str] = None
    line: Optional[int] = None
    quote: Optional[str] = None


class Company(BaseModel):
    name: str
    fictional: bool = True
    domain: str


class EngineInfo(BaseModel):
    llm_backend: Literal["ollama", "claude"]
    model: str
    prompt_set: str
    temperature: float = 0.0


class Manifest(BaseModel):
    bundle_version: str = BUNDLE_VERSION
    run_id: str
    company: Company
    generated_at: str  # ISO-8601 with timezone
    engine: EngineInfo
    counts: dict[str, int] = Field(default_factory=dict)
    safe_mode: bool = True
    hashes: dict[str, str] = Field(default_factory=dict)


class Artifact(BaseModel):
    id: str
    kind: Literal["csv", "xlsx", "pdf", "email", "screenshot", "note"]
    source_name: str
    detected_type: str
    ingested_at: str
    page_count: int = 1
    extraction_confidence: float = 0.0
    thumbnail_asset_id: Optional[str] = None


class Document(BaseModel):
    id: str
    artifact_id: str
    text: str = ""
    pages: list[dict] = Field(default_factory=list)  # [{page, text}]
    language: str = "en"


class Entity(BaseModel):
    id: str
    type: Literal["person", "role", "org", "system", "date", "amount", "status", "policy"]
    value: str
    normalized_value: Optional[str] = None
    confidence: float = 0.0
    evidence: list[EvidenceRef] = Field(default_factory=list)


class WorkflowStep(BaseModel):
    id: str
    name: str
    owner_role: str
    sequence_index: int
    cycle_time_hours: Optional[float] = None
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    is_review: bool = False
    is_approval: bool = False
    is_bottleneck: bool = False
    confidence: float = 0.0
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ProcessEdge(BaseModel):
    id: str
    from_step: str
    to_step: str
    owner_handoff: Optional[str] = None
    kind: Literal["normal", "loop", "duplicate", "exception", "bypass"] = "normal"
    frequency: Optional[float] = None
    avg_delay_hours: Optional[float] = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class Exception(BaseModel):
    id: str
    step_id: str
    description: str
    frequency: Optional[float] = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class RiskFinding(BaseModel):
    id: str
    category: Literal[
        "pii", "missing_approval", "inconsistent_status",
        "ambiguous_ownership", "review_bypass", "low_confidence",
    ]
    severity: Literal["low", "med", "high"]
    title: str
    description: str
    step_id: Optional[str] = None
    entity_id: Optional[str] = None
    confidence: float = 0.0
    suggested_action: Optional[str] = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ReviewTask(BaseModel):
    id: str
    reason: str
    related_id: str
    status: Literal["open", "approved", "overridden", "rejected"] = "open"
    required_role: Optional[str] = None
    created_at: str


class AutomationCandidate(BaseModel):
    id: str
    title: str
    description: str
    target_step_id: Optional[str] = None
    est_time_saved_hours_per_week: float = 0.0
    confidence: float = 0.0
    required_oversight: Literal["none", "light", "strict"] = "light"
    implementation_complexity: Literal["low", "med", "high"] = "med"
    value_score: float = 0.0
    effort_score: float = 0.0
    priority_rank: Optional[int] = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class SimStats(BaseModel):
    total_cycle_time_hours: float
    handoffs: int
    rework_rate: float
    monthly_cost: float


class SimulationResult(BaseModel):
    is_simulated: bool = True
    before: SimStats
    after: SimStats
    assumptions: list[str] = Field(default_factory=list)
    method: str = "deterministic queueing estimate over the process graph"


class LLMCallInfo(BaseModel):
    prompt_id: str
    model: str
    tokens: Optional[int] = None
    latency_ms: Optional[int] = None


class AuditEvent(BaseModel):
    id: str
    at: str
    actor: str  # "engine" | "agent:<name>" | "reviewer"
    action: str
    target_id: Optional[str] = None
    detail: Optional[str] = None
    llm_call: Optional[LLMCallInfo] = None


class ExportFile(BaseModel):
    id: str
    label: str
    kind: Literal["pdf", "json", "csv", "md"]
    path_in_bundle: str
    description: Optional[str] = None


class Bundle(BaseModel):
    """In-memory view of a full Artifact Bundle (serialized as separate JSON files on disk)."""

    manifest: Manifest
    artifacts: list[Artifact] = Field(default_factory=list)
    documents: list[Document] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    steps: list[WorkflowStep] = Field(default_factory=list)
    edges: list[ProcessEdge] = Field(default_factory=list)
    exceptions: list[Exception] = Field(default_factory=list)
    risks: list[RiskFinding] = Field(default_factory=list)
    reviews: list[ReviewTask] = Field(default_factory=list)
    automations: list[AutomationCandidate] = Field(default_factory=list)
    simulation: Optional[SimulationResult] = None
    audit: list[AuditEvent] = Field(default_factory=list)
    exports: list[ExportFile] = Field(default_factory=list)
