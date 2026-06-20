import { useMemo, useState } from "react";
import type { Bundle, EdgeKind, WorkflowStep } from "../bundle/types";
import { computeLayout, edgePath, GraphLayout, NODE_H, NODE_W } from "../graph/layout";
import { maskQuote, piiArtifactIds } from "../bundle/redact";

export const EDGE_STYLE: Record<EdgeKind, { stroke: string; dash?: string; label: string }> = {
  normal: { stroke: "#3a6f93", label: "Normal flow" },
  duplicate: { stroke: "#ffb454", dash: "6 5", label: "Duplicate handoff" },
  exception: { stroke: "#e0884a", label: "Exception branch" },
  loop: { stroke: "#ef5e7a", dash: "6 5", label: "Rework loop" },
  bypass: { stroke: "#ef5e7a", dash: "2 6", label: "Control bypass" },
};

// Problem edges that the "after" (cleaned) process removes.
const PROBLEM: EdgeKind[] = ["duplicate", "loop", "bypass"];

export type GraphMode = "before" | "after";

/** Reusable SVG graph. Drives the centerpiece view and the landing teaser. */
export function GraphSvg({
  bundle,
  layout,
  mode,
  selected,
  onSelect,
}: {
  bundle: Bundle;
  layout: GraphLayout;
  mode: GraphMode;
  selected?: string | null;
  onSelect?: (id: string) => void;
}) {
  const risksFor = (id: string) => bundle.risks.filter((r) => r.step_id === id);
  return (
    <svg viewBox={`0 0 ${layout.width} ${layout.height}`} className="graph" role="img">
      <defs>
        {Object.entries(EDGE_STYLE).map(([k, v]) => (
          <marker key={k} id={`arrow-${k}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={v.stroke} />
          </marker>
        ))}
      </defs>

      {layout.lanes.map((lane) => (
        <g key={lane.role}>
          <rect x={0} y={lane.y} width={layout.width} height={112} className={`lane ${lane.index % 2 ? "lane-alt" : ""}`} />
          <text x={16} y={lane.y + 56} className="lane-label">{lane.role}</text>
        </g>
      ))}

      {bundle.edges.map((e) => {
        const style = EDGE_STYLE[e.kind];
        const removed = mode === "after" && PROBLEM.includes(e.kind);
        return (
          <path
            key={e.id}
            className="edge"
            d={edgePath(e, layout)}
            fill="none"
            stroke={style.stroke}
            strokeWidth={e.kind === "normal" ? 2 : 2.4}
            strokeDasharray={style.dash}
            markerEnd={`url(#arrow-${e.kind})`}
            style={{ opacity: removed ? 0 : 0.92 }}
          />
        );
      })}

      {bundle.steps.map((s: WorkflowStep) => {
        const n = layout.nodes.get(s.id)!;
        const isSel = s.id === selected;
        const nRisk = risksFor(s.id).length;
        const hot = s.is_bottleneck && mode === "before";
        return (
          <g
            key={s.id}
            transform={`translate(${n.x},${n.y})`}
            className={`node ${isSel ? "node-sel" : ""} ${hot ? "node-hot" : ""} ${onSelect ? "" : "node-static"}`}
            onClick={onSelect ? () => onSelect(s.id) : undefined}
          >
            <rect width={NODE_W} height={NODE_H} rx={10} />
            <text x={14} y={26} className="node-title">{s.name}</text>
            <text x={14} y={46} className="node-meta">{s.cycle_time_hours}h cycle</text>
            {s.is_review && <NodeBadge x={NODE_W - 30} label="R" title="Review" />}
            {s.is_approval && <NodeBadge x={NODE_W - 30} label="A" title="Approval" />}
            {nRisk > 0 && mode === "before" && (
              <g transform={`translate(${NODE_W - 24},${NODE_H - 22})`}>
                <circle r={10} className="node-risk" />
                <text className="node-risk-n" textAnchor="middle" y={4}>{nRisk}</text>
              </g>
            )}
            {hot && <text x={14} y={NODE_H - 10} className="node-hot-label">⚠ bottleneck</text>}
          </g>
        );
      })}
    </svg>
  );
}

export function ProcessGraph({ bundle, safeMode }: { bundle: Bundle; safeMode: boolean }) {
  const layout = useMemo(() => computeLayout(bundle.steps), [bundle.steps]);
  const [selected, setSelected] = useState<string | null>("step_approval");
  const [mode, setMode] = useState<GraphMode>("before");
  const sel = bundle.steps.find((s) => s.id === selected) ?? null;
  const risksFor = (id: string) => bundle.risks.filter((r) => r.step_id === id);
  const piiArts = useMemo(() => piiArtifactIds(bundle.risks), [bundle.risks]);

  return (
    <div className="view">
      <div className="view-head">
        <h2>Process Graph</h2>
        <p>Reconstructed from {bundle.manifest.counts.artifacts} artifacts — owners, cycle times, and the problems hiding in the handoffs. Click any step.</p>
      </div>

      <div className="seg" role="tablist">
        <button className={mode === "before" ? "on" : ""} onClick={() => setMode("before")}>Before — as-is</button>
        <button className={mode === "after" ? "on" : ""} onClick={() => setMode("after")}>After — cleaned</button>
        <span className="seg-note">{mode === "before" ? "duplicate handoffs, rework loop, and a review bypass" : "problem paths removed, bottleneck relieved"}</span>
      </div>

      <div className="graph-wrap">
        <GraphSvg bundle={bundle} layout={layout} mode={mode} selected={selected} onSelect={setSelected} />
      </div>

      <div className="legend">
        {Object.values(EDGE_STYLE).map((v) => (
          <span key={v.label} className="legend-item">
            <svg width="26" height="10"><line x1="0" y1="5" x2="26" y2="5" stroke={v.stroke} strokeWidth="2.4" strokeDasharray={v.dash} /></svg>
            {v.label}
          </span>
        ))}
      </div>

      {sel && (
        <div className="detail">
          <div className="detail-head">
            <h3>{sel.name}</h3>
            <span className="pill">{sel.owner_role}</span>
            <span className="pill pill-dim">conf {(sel.confidence * 100) | 0}%</span>
          </div>
          <div className="detail-grid">
            <div><span className="k">Cycle time</span><span className="v">{sel.cycle_time_hours} h</span></div>
            <div><span className="k">Inputs</span><span className="v">{sel.inputs.join(", ") || "—"}</span></div>
            <div><span className="k">Outputs</span><span className="v">{sel.outputs.join(", ") || "—"}</span></div>
          </div>
          {sel.evidence.length > 0 && (
            <div className="evidence">
              <span className="k">Why we know this</span>
              {sel.evidence.map((ev, i) => {
                const redact = safeMode && piiArts.has(ev.artifact_id);
                return (
                  <div key={i} className="evidence-row">
                    <code>{ev.artifact_id}{ev.page ? ` p${ev.page}` : ""}{ev.line ? ` L${ev.line}` : ""}{ev.cell ? ` ${ev.cell}` : ""}</code>
                    {ev.quote && <span className={`quote${redact ? " redacted" : ""}`}>“{maskQuote(ev.quote, redact)}”</span>}
                  </div>
                );
              })}
            </div>
          )}
          {risksFor(sel.id).length > 0 && (
            <div className="evidence">
              <span className="k">Risks at this step</span>
              {risksFor(sel.id).map((r) => (
                <div key={r.id} className="evidence-row">
                  <span className={`sev sev-${r.severity}`}>{r.severity}</span>
                  <span className="quote">{r.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function NodeBadge({ x, label, title }: { x: number; label: string; title: string }) {
  return (
    <g transform={`translate(${x},10)`}>
      <title>{title}</title>
      <rect width={18} height={18} rx={4} className="node-flag" />
      <text x={9} y={13} textAnchor="middle" className="node-flag-t">{label}</text>
    </g>
  );
}
