import type { Bundle, SimStats } from "../bundle/types";

type Metric = { key: keyof SimStats; label: string; fmt: (n: number) => string; better: "lower" };

const METRICS: Metric[] = [
  { key: "total_cycle_time_hours", label: "Cycle time", fmt: (n) => `${n}h`, better: "lower" },
  { key: "handoffs", label: "Handoffs", fmt: (n) => `${n}`, better: "lower" },
  { key: "rework_rate", label: "Rework rate", fmt: (n) => `${(n * 100) | 0}%`, better: "lower" },
  { key: "monthly_cost", label: "Monthly cost", fmt: (n) => `$${(n / 1000).toFixed(1)}k`, better: "lower" },
];

export function BeforeAfter({ bundle }: { bundle: Bundle }) {
  const sim = bundle.simulation;
  if (!sim) return <div className="view">No simulation in this bundle.</div>;

  return (
    <div className="view">
      <div className="view-head">
        <h2>
          Before / After <span className="sim-flag">SIMULATED</span>
        </h2>
        <p>{sim.method}.</p>
      </div>

      <div className="ba-grid">
        {METRICS.map((m) => {
          const before = sim.before[m.key];
          const after = sim.after[m.key];
          const delta = before === 0 ? 0 : Math.round(((after - before) / before) * 100);
          const max = Math.max(before, after) || 1;
          return (
            <div key={m.key} className="ba-card">
              <span className="ba-label">{m.label}</span>
              <div className="ba-bars">
                <Bar label="before" value={before} text={m.fmt(before)} pct={before / max} tone="before" />
                <Bar label="after" value={after} text={m.fmt(after)} pct={after / max} tone="after" />
              </div>
              <span className={`ba-delta ${delta < 0 ? "good" : "bad"}`}>
                {delta > 0 ? "+" : ""}
                {delta}%
              </span>
            </div>
          );
        })}
      </div>

      <div className="assumptions">
        <span className="k">Assumptions (fictional, stated for honesty)</span>
        <ul>
          {sim.assumptions.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Bar({ label, text, pct, tone }: { label: string; value: number; text: string; pct: number; tone: "before" | "after" }) {
  return (
    <div className="ba-bar-row">
      <span className="ba-bar-label">{label}</span>
      <span className="ba-track">
        <span className={`ba-fill ba-${tone}`} style={{ width: `${Math.max(6, pct * 100)}%` }} />
      </span>
      <span className="ba-val">{text}</span>
    </div>
  );
}
