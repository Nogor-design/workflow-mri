import type { Bundle } from "../bundle/types";

export function Automations({ bundle }: { bundle: Bundle }) {
  const total = bundle.automations.reduce((s, a) => s + a.est_time_saved_hours_per_week, 0);
  const stepName = (id?: string) => bundle.steps.find((s) => s.id === id)?.name;

  return (
    <div className="view">
      <div className="view-head">
        <h2>Automation Recommendations</h2>
        <p>Ranked by value, effort, and required oversight — ~{total}h/week recoverable.</p>
      </div>

      <div className="auto-grid">
        {bundle.automations.map((a) => (
          <div key={a.id} className="auto-card">
            <div className="auto-rank">#{a.priority_rank}</div>
            <h3>{a.title}</h3>
            <p>{a.description}</p>
            <div className="auto-meta">
              <Tag k="saves" v={`${a.est_time_saved_hours_per_week}h/wk`} strong />
              {stepName(a.target_step_id) && <Tag k="step" v={stepName(a.target_step_id)!} />}
              <Tag k="oversight" v={a.required_oversight} />
              <Tag k="effort" v={a.implementation_complexity} />
            </div>
            <div className="auto-bars">
              <Meter label="value" v={a.value_score} />
              <Meter label="confidence" v={a.confidence} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Tag({ k, v, strong }: { k: string; v: string; strong?: boolean }) {
  return (
    <span className={`tag ${strong ? "tag-strong" : ""}`}>
      <span className="tag-k">{k}</span>
      {v}
    </span>
  );
}

function Meter({ label, v }: { label: string; v: number }) {
  return (
    <div className="meter">
      <span className="meter-l">{label}</span>
      <span className="meter-track">
        <span className="meter-fill" style={{ width: `${v * 100}%` }} />
      </span>
    </div>
  );
}
