"""workflow_mri.schema

Pydantic models = the Artifact Bundle contract (source of truth for `make types`).

Changelog:
- 1.0  initial schema (Phase 0 stubs): Manifest, Artifact, Document, Entity, WorkflowStep,
       ProcessEdge, Exception, RiskFinding, ReviewTask, AutomationCandidate,
       SimulationResult, AuditEvent, ExportFile, Bundle.
"""

from workflow_mri.schema.models import (
    BUNDLE_VERSION,
    Artifact,
    AuditEvent,
    AutomationCandidate,
    Bundle,
    Company,
    Document,
    EngineInfo,
    Entity,
    EvidenceRef,
    Exception,
    ExportFile,
    LLMCallInfo,
    Manifest,
    ProcessEdge,
    ReviewTask,
    RiskFinding,
    SimStats,
    SimulationResult,
    WorkflowStep,
)

__all__ = [
    "BUNDLE_VERSION",
    "Artifact",
    "AuditEvent",
    "AutomationCandidate",
    "Bundle",
    "Company",
    "Document",
    "EngineInfo",
    "Entity",
    "EvidenceRef",
    "Exception",
    "ExportFile",
    "LLMCallInfo",
    "Manifest",
    "ProcessEdge",
    "ReviewTask",
    "RiskFinding",
    "SimStats",
    "SimulationResult",
    "WorkflowStep",
]
