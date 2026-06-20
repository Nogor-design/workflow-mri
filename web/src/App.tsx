import { useState } from "react";

/**
 * Phase 0 shell. This is the static showcase front door — a pure renderer with no IO and
 * no inference. The real views (DESIGN.md §9) render an Artifact Bundle loaded from
 * /bundle/ and arrive in roadmap Phase 1. For now it states the project intent and the
 * planned surfaces so the deploy reads as a serious work-in-progress, not an empty Vite app.
 */

type ViewDef = { key: string; label: string; blurb: string; center?: boolean };

const VIEWS: ViewDef[] = [
  { key: "ingest", label: "Ingest", blurb: "File inventory, detected types, extraction confidence." },
  { key: "graph", label: "Process Graph", blurb: "Reconstructed workflow: owners, cycle times, bottlenecks.", center: true },
  { key: "risk", label: "Risk & Quality", blurb: "PII, missing approvals, review-bypass — with evidence." },
  { key: "automations", label: "Automations", blurb: "Ranked opportunities: time saved × effort × oversight." },
  { key: "beforeafter", label: "Before / After", blurb: "Simulated cycle-time & cost improvement." },
  { key: "export", label: "Export & Handoff", blurb: "Process map, schema, review queue, audit log, backlog." },
];

export function App() {
  const [active, setActive] = useState<string>("graph");
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden>◐</span>
          <span className="brand-name">Workflow&nbsp;MRI</span>
        </div>
        <span className="status-chip">Phase&nbsp;0 · shell</span>
      </header>

      <main className="hero">
        <p className="eyebrow">An operations diagnostician</p>
        <h1>
          Turn a chaotic company's artifacts into a
          <span className="accent"> governed operating system.</span>
        </h1>
        <p className="lede">
          Workflow MRI ingests spreadsheets, PDFs, emails, screenshots, and notes —
          reconstructs how work actually flows, exposes bottlenecks, duplicate work, and
          compliance risk, recommends automations, and exports a governed handoff package.
        </p>

        <div className="sample-card">
          <div className="sample-card-head">
            <span className="dot" aria-hidden />
            Sample company
            <span className="fictional">FICTIONAL</span>
          </div>
          <div className="sample-card-body">
            <strong>Meridian Claims Co.</strong>
            <span>23 artifacts · 7 workflow steps · 11 risk findings</span>
          </div>
          <p className="sample-note">Demo data loads here in Phase&nbsp;1.</p>
        </div>

        <section className="views">
          <h2>Planned surfaces</h2>
          <div className="view-grid">
            {VIEWS.map((v) => (
              <button
                key={v.key}
                className={`view-tile${v.center ? " center" : ""}${active === v.key ? " on" : ""}`}
                onClick={() => setActive(v.key)}
              >
                <span className="view-label">
                  {v.label}
                  {v.center && <span className="badge">centerpiece</span>}
                </span>
                <span className="view-blurb">{v.blurb}</span>
              </button>
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        Local-first multi-agent engine (Ollama / Claude) · deterministic public demo ·{" "}
        <a href="https://github.com/Nogor-design" target="_blank" rel="noreferrer">
          Nogor-design
        </a>
      </footer>
    </div>
  );
}
