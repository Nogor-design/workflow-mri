// TypeScript mirror of the Artifact Bundle contract (engine/workflow_mri/schema/models.py).
// Phase 1: hand-maintained. Phase 2 generates this from the Pydantic schema (`make types`).
// See docs/data-model.md.

export interface EvidenceRef {
  artifact_id: string;
  document_id?: string;
  page?: number;
  cell?: string;
  line?: number;
  quote?: string;
}

export interface Company {
  name: string;
  fictional: boolean;
  domain: string;
}

export interface EngineInfo {
  llm_backend: "ollama" | "claude";
  model: string;
  prompt_set: string;
  temperature: number;
}

export interface Manifest {
  bundle_version: string;
  run_id: string;
  company: Company;
  generated_at: string;
  engine: EngineInfo;
  counts: Record<string, number>;
  safe_mode: boolean;
  hashes: Record<string, string>;
}

export type ArtifactKind = "csv" | "xlsx" | "pdf" | "email" | "screenshot" | "note";

export interface Artifact {
  id: string;
  kind: ArtifactKind;
  source_name: string;
  detected_type: string;
  ingested_at: string;
  page_count: number;
  extraction_confidence: number;
  thumbnail_asset_id?: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  owner_role: string;
  sequence_index: number;
  cycle_time_hours?: number;
  inputs: string[];
  outputs: string[];
  is_review: boolean;
  is_approval: boolean;
  is_bottleneck?: boolean;
  confidence: number;
  evidence: EvidenceRef[];
}

export type EdgeKind = "normal" | "loop" | "duplicate" | "exception" | "bypass";

export interface ProcessEdge {
  id: string;
  from_step: string;
  to_step: string;
  owner_handoff?: string;
  kind: EdgeKind;
  frequency?: number;
  avg_delay_hours?: number;
  evidence: EvidenceRef[];
}

export type RiskCategory =
  | "pii"
  | "missing_approval"
  | "inconsistent_status"
  | "ambiguous_ownership"
  | "review_bypass"
  | "low_confidence";

export type Severity = "low" | "med" | "high";

export interface RiskFinding {
  id: string;
  category: RiskCategory;
  severity: Severity;
  title: string;
  description: string;
  step_id?: string;
  entity_id?: string;
  confidence: number;
  suggested_action?: string;
  evidence: EvidenceRef[];
}

export interface ReviewTask {
  id: string;
  reason: string;
  related_id: string;
  status: "open" | "approved" | "overridden" | "rejected";
  required_role?: string;
  created_at: string;
}

export interface AutomationCandidate {
  id: string;
  title: string;
  description: string;
  target_step_id?: string;
  est_time_saved_hours_per_week: number;
  confidence: number;
  required_oversight: "none" | "light" | "strict";
  implementation_complexity: "low" | "med" | "high";
  value_score: number;
  effort_score: number;
  priority_rank?: number;
  evidence: EvidenceRef[];
}

export interface SimStats {
  total_cycle_time_hours: number;
  handoffs: number;
  rework_rate: number;
  monthly_cost: number;
}

export interface SimulationResult {
  is_simulated: boolean;
  before: SimStats;
  after: SimStats;
  assumptions: string[];
  method: string;
}

export interface ExportFile {
  id: string;
  label: string;
  kind: "pdf" | "json" | "csv" | "md";
  path_in_bundle: string;
  description?: string;
}

export interface Bundle {
  manifest: Manifest;
  artifacts: Artifact[];
  steps: WorkflowStep[];
  edges: ProcessEdge[];
  risks: RiskFinding[];
  reviews: ReviewTask[];
  automations: AutomationCandidate[];
  simulation: SimulationResult | null;
  exports: ExportFile[];
}
