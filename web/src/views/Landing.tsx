import { useEffect, useMemo, useState } from "react";
import type { Bundle } from "../bundle/types";
import { computeLayout } from "../graph/layout";
import { GraphSvg, type GraphMode } from "./ProcessGraph";

export function Landing({ bundle, onEnter }: { bundle: Bundle; onEnter: (view?: string) => void }) {
  const layout = useMemo(() => computeLayout(bundle.steps), [bundle.steps]);
  const [mode, setMode] = useState<GraphMode>("before");
  const co = bundle.manifest.company;
  const c = bundle.manifest.counts;

  // 20-second teaser: auto-morph the graph between the messy "before" and cleaned "after".
  useEffect(() => {
    const t = setInterval(() => setMode((m) => (m === "before" ? "after" : "before")), 2800);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="landing">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden>◐</span>
          <span className="brand-name">Workflow&nbsp;MRI</span>
        </div>
        <span className="status-chip">operations diagnostician</span>
      </header>

      <div className="landing-body">
        <section className="landing-copy">
          <p className="eyebrow">Messy artifacts → governed operating system</p>
          <h1>
            Turn a chaotic company's files into a
            <span className="accent"> process you can see, measure, and fix.</span>
          </h1>
          <p className="lede">
            Workflow MRI ingests spreadsheets, PDFs, emails, screenshots, and notes —
            reconstructs how work actually flows, exposes bottlenecks, duplicate work, and
            compliance risk, recommends automations, and exports a governed handoff package.
          </p>

          <div className="sample-card">
            <div className="sample-card-head">
              <span className="dot" aria-hidden />
              Loaded sample
              {co.fictional && <span className="fictional">FICTIONAL</span>}
            </div>
            <div className="sample-card-body">
              <strong>{co.name}</strong>
              <span>{c.artifacts} artifacts · {c.steps} steps · {c.risks} risk findings · {c.automations} automations</span>
            </div>
          </div>

          <div className="landing-cta">
            <button className="btn-primary" onClick={() => onEnter("graph")}>Open the workbench →</button>
            <button className="btn-ghost" onClick={() => onEnter("ingest")}>Start from ingest</button>
          </div>
          <p className="landing-note">Deterministic replay of a pre-computed local-first run. No live inference, no setup.</p>
        </section>

        <section className="landing-teaser">
          <div className="teaser-head">
            <span className={`teaser-tag ${mode}`}>{mode === "before" ? "Before — as-is" : "After — cleaned"}</span>
            <span className="teaser-sub">auto-preview</span>
          </div>
          <div className="teaser-frame">
            <GraphSvg bundle={bundle} layout={layout} mode={mode} />
          </div>
        </section>
      </div>
    </div>
  );
}
