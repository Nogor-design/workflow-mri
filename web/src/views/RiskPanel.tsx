import { useState } from "react";
import type { Bundle, RiskCategory, Severity } from "../bundle/types";
import { maskQuote } from "../bundle/redact";

const CAT_LABEL: Record<RiskCategory, string> = {
  pii: "PII exposure",
  missing_approval: "Missing approval",
  inconsistent_status: "Inconsistent status",
  ambiguous_ownership: "Ambiguous ownership",
  review_bypass: "Review bypass",
  low_confidence: "Low confidence",
};

const SEV_RANK: Record<Severity, number> = { high: 0, med: 1, low: 2 };

export function RiskPanel({ bundle, safeMode }: { bundle: Bundle; safeMode: boolean }) {
  const [open, setOpen] = useState<string | null>(null);
  const risks = [...bundle.risks].sort((a, b) => SEV_RANK[a.severity] - SEV_RANK[b.severity]);
  const stepName = (id?: string) => bundle.steps.find((s) => s.id === id)?.name;

  return (
    <div className="view">
      <div className="view-head">
        <h2>Risk &amp; Quality</h2>
        <p>Each finding links back to the evidence that triggered it. {bundle.reviews.length} are queued for human review.</p>
      </div>

      <div className="risk-list">
        {risks.map((r) => {
          const isOpen = open === r.id;
          return (
            <div key={r.id} className={`risk-row ${isOpen ? "open" : ""}`} onClick={() => setOpen(isOpen ? null : r.id)}>
              <div className="risk-top">
                <span className={`sev sev-${r.severity}`}>{r.severity}</span>
                <span className="risk-cat">{CAT_LABEL[r.category]}</span>
                <span className="risk-title">{r.title}</span>
                {stepName(r.step_id) && <span className="pill pill-dim">{stepName(r.step_id)}</span>}
                <span className="risk-conf">{(r.confidence * 100) | 0}%</span>
              </div>
              {isOpen && (
                <div className="risk-detail">
                  <p>{r.description}</p>
                  {r.suggested_action && (
                    <p className="risk-action">→ {r.suggested_action}</p>
                  )}
                  {r.evidence.map((ev, i) => {
                    const redact = safeMode && r.category === "pii";
                    return (
                      <div key={i} className="evidence-row">
                        <code>{ev.artifact_id}{ev.page ? ` p${ev.page}` : ""}{ev.line ? ` L${ev.line}` : ""}{ev.cell ? ` ${ev.cell}` : ""}</code>
                        {ev.quote && <span className={`quote${redact ? " redacted" : ""}`}>“{maskQuote(ev.quote, redact)}”</span>}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
