# Data Model — The Artifact Bundle

Companion to [`../DESIGN.md`](../DESIGN.md) §7. The Bundle is the **contract** between the
engine (writes it) and the showcase (reads it). It is versioned and JSON-safe — no
DataFrames, callables, or runtime objects, ever.

Source of truth: Pydantic models in `engine/workflow_mri/schema/`. TypeScript types for the
UI are **generated** from these (`make types`) so the two sides cannot drift.

## Bundle on disk

```
bundle/
├── manifest.json          # Manifest: version, run id, company, model config, counts, hashes
├── artifacts.json         # Artifact[]            (the raw input files, normalized)
├── documents.json         # Document[]            (parsed text + page refs)
├── entities.json          # Entity[]              (people, dates, systems, ...)
├── steps.json             # WorkflowStep[]
├── edges.json             # ProcessEdge[]
├── exceptions.json        # Exception[]
├── risks.json             # RiskFinding[]
├── reviews.json           # ReviewTask[]
├── automations.json       # AutomationCandidate[]
├── simulation.json        # SimulationResult
├── audit.json             # AuditEvent[]
├── exports/               # derived downloadable files (process-map.pdf, schema.json, ...)
└── assets/                # sanitized thumbnails/screenshots referenced by id
```

The UI loads `manifest.json` first, then the arrays it needs per view.

## Core principles

1. **Everything analytic links to evidence.** `RiskFinding`, `WorkflowStep`,
   `AutomationCandidate`, etc. each carry `evidence: EvidenceRef[]` pointing at the
   `Artifact`/`Document` (and page/cell/line) that produced them. This powers the "why was
   this flagged" drawer and the audit trail.
2. **Everything uncertain carries `confidence: float (0–1)`** and may spawn a `ReviewTask`.
3. **IDs are stable strings** (`art_001`, `step_intake`, `risk_pii_004`) so the Bundle is
   diffable and the UI can deep-link.
4. **All datetimes are ISO-8601 strings with timezone.** No naive datetimes.

## Object reference

### Manifest
```jsonc
{
  "bundle_version": "1.0",
  "run_id": "meridian-2026-06-20",
  "company": { "name": "Meridian Claims Co.", "fictional": true, "domain": "insurance-claims" },
  "generated_at": "2026-06-20T08:00:00-06:00",
  "engine": { "llm_backend": "ollama", "model": "llama3.1:8b", "prompt_set": "v1", "temperature": 0 },
  "counts": { "artifacts": 23, "steps": 7, "risks": 11, "automations": 6 },
  "safe_mode": true,
  "hashes": { "...": "sha256" }
}
```

### Artifact  — a normalized input file
`id, kind (csv|xlsx|pdf|email|screenshot|note), source_name, detected_type,
ingested_at, page_count, extraction_confidence, thumbnail_asset_id`

### Document — parsed content of an Artifact
`id, artifact_id, text, pages: [{page, text}], language`

### Entity — extracted noun
`id, type (person|role|org|system|date|amount|status|policy), value, normalized_value,
confidence, evidence: EvidenceRef[]`

### WorkflowStep — a node in the process
`id, name, swimlane/owner_role, sequence_index, cycle_time_hours, inputs[], outputs[],
is_review, is_approval, confidence, evidence[]`

### ProcessEdge — a directed handoff
`id, from_step, to_step, owner_handoff, kind (normal|loop|duplicate|exception|bypass),
frequency, avg_delay_hours, evidence[]`

### Exception — a deviation from the happy path
`id, step_id, description, frequency, evidence[]`

### RiskFinding — a governance flag
`id, category (pii|missing_approval|inconsistent_status|ambiguous_ownership|review_bypass|
low_confidence), severity (low|med|high), title, description, step_id?, entity_id?,
confidence, evidence[], suggested_action`

### ReviewTask — a human-in-the-loop queue item
`id, reason, related_id (risk/step/entity), status (open|approved|overridden|rejected),
required_role, created_at`

### AutomationCandidate — a scored opportunity
`id, title, description, target_step_id, est_time_saved_hours_per_week, confidence,
required_oversight (none|light|strict), implementation_complexity (low|med|high),
value_score, effort_score, priority_rank, evidence[]`

### SimulationResult — before/after (labeled simulated)
```jsonc
{
  "is_simulated": true,
  "before": { "total_cycle_time_hours": 92, "handoffs": 14, "rework_rate": 0.22, "monthly_cost": 41000 },
  "after":  { "total_cycle_time_hours": 51, "handoffs": 9,  "rework_rate": 0.08, "monthly_cost": 24500 },
  "assumptions": ["...clearly stated, plausible, fictional..."],
  "method": "deterministic queueing estimate over the process graph"
}
```

### AuditEvent — decision/override/inference trail
`id, at, actor (engine|agent:<name>|reviewer), action, target_id, detail,
llm_call?: { prompt_id, model, tokens, latency_ms }`

### ExportFile — a derived downloadable
`id, label, kind (pdf|json|csv|md), path_in_bundle, description`

### EvidenceRef (embedded)
`artifact_id, document_id?, page?, cell?, line?, quote?`

## Versioning

`bundle_version` is bumped on any breaking schema change. The UI checks it on load and
refuses (with a clear message) to render a Bundle it doesn't understand. Keep a short
changelog at the top of `engine/workflow_mri/schema/__init__.py`.
