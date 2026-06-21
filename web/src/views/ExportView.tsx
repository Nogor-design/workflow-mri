import type { Bundle, ExportFile } from "../bundle/types";

const KIND_ICON: Record<ExportFile["kind"], string> = { pdf: "▤", json: "{}", csv: "▦", md: "≡" };

export function ExportView({ bundle }: { bundle: Bundle }) {
  return (
    <div className="view">
      <div className="view-head">
        <h2>Export &amp; Handoff</h2>
        <p>Everything an engineering team needs to pick this up tomorrow. (Downloads are stubbed in the Phase&nbsp;1 demo.)</p>
      </div>

      <div className="export-list">
        {bundle.exports.map((e) => (
          <div key={e.id} className="export-row">
            <span className="export-icon">{KIND_ICON[e.kind]}</span>
            <div className="export-body">
              <span className="export-label">
                {e.label} <span className="export-kind">.{e.kind}</span>
              </span>
              <span className="export-desc">{e.description}</span>
            </div>
            <button className="export-btn" disabled title="Stubbed in the public demo">
              download
            </button>
          </div>
        ))}
      </div>

      <div className="review-queue">
        <span className="k">Human review queue ({bundle.reviews.length})</span>
        {bundle.reviews.map((r) => (
          <div key={r.id} className="review-row">
            <span className={`rq-status rq-${r.status}`}>{r.status}</span>
            <span className="rq-reason">{r.reason}</span>
            {r.required_role && <span className="pill pill-dim">{r.required_role}</span>}
          </div>
        ))}
      </div>

      {bundle.audit.length > 0 && (
        <div className="audit-trail">
          <span className="k">Audit trail — {bundle.audit.length} agent decisions</span>
          <ol className="audit-list">
            {bundle.audit.map((e) => (
              <li key={e.id} className="audit-row">
                <span className="audit-actor">{e.actor.replace("agent:", "")}</span>
                <span className="audit-detail">{e.detail}</span>
                {e.llm_call && <span className="pill pill-dim">{e.llm_call.model}</span>}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
