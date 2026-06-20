import type {
  Artifact,
  AutomationCandidate,
  Bundle,
  ExportFile,
  Manifest,
  ProcessEdge,
  ReviewTask,
  RiskFinding,
  SimulationResult,
  WorkflowStep,
} from "./types";

// Loads the committed Artifact Bundle from /bundle/. Pure fetch of static JSON — no
// inference, no secrets. import.meta.env.BASE_URL respects the GitHub Pages subpath.
async function getJson<T>(name: string): Promise<T> {
  const res = await fetch(`${import.meta.env.BASE_URL}bundle/${name}`);
  if (!res.ok) throw new Error(`Failed to load bundle/${name}: ${res.status}`);
  return (await res.json()) as T;
}

export async function loadBundle(): Promise<Bundle> {
  const [manifest, artifacts, steps, edges, risks, reviews, automations, simulation, exports] =
    await Promise.all([
      getJson<Manifest>("manifest.json"),
      getJson<Artifact[]>("artifacts.json"),
      getJson<WorkflowStep[]>("steps.json"),
      getJson<ProcessEdge[]>("edges.json"),
      getJson<RiskFinding[]>("risks.json"),
      getJson<ReviewTask[]>("reviews.json"),
      getJson<AutomationCandidate[]>("automations.json"),
      getJson<SimulationResult>("simulation.json"),
      getJson<ExportFile[]>("exports.json"),
    ]);

  return {
    manifest,
    artifacts,
    steps: [...steps].sort((a, b) => a.sequence_index - b.sequence_index),
    edges,
    risks,
    reviews,
    automations: [...automations].sort(
      (a, b) => (a.priority_rank ?? 99) - (b.priority_rank ?? 99),
    ),
    simulation,
    exports,
  };
}
