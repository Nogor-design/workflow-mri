import { useEffect, useState } from "react";
import type { Bundle } from "./bundle/types";
import { loadBundle } from "./bundle/load";
import { Landing } from "./views/Landing";
import { ProcessGraph } from "./views/ProcessGraph";
import { Ingest } from "./views/Ingest";
import { RiskPanel } from "./views/RiskPanel";
import { Automations } from "./views/Automations";
import { BeforeAfter } from "./views/BeforeAfter";
import { ExportView } from "./views/ExportView";

const NAV = [
  { key: "ingest", label: "Ingest" },
  { key: "graph", label: "Process Graph", center: true },
  { key: "risk", label: "Risk & Quality" },
  { key: "automations", label: "Automations" },
  { key: "beforeafter", label: "Before / After" },
  { key: "export", label: "Export & Handoff" },
];

export function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [entered, setEntered] = useState(false);
  const [active, setActive] = useState("graph");
  const [safeMode, setSafeMode] = useState(true);

  useEffect(() => {
    loadBundle().then(setBundle).catch((e) => setError(String(e)));
  }, []);

  if (error) return <Centered>Failed to load bundle: {error}</Centered>;
  if (!bundle) return <Centered>Loading Workflow MRI…</Centered>;

  if (!entered) {
    return <Landing bundle={bundle} onEnter={(view) => { setActive(view ?? "graph"); setEntered(true); }} />;
  }

  const co = bundle.manifest.company;

  return (
    <div className="app">
      <header className="topbar">
        <button className="brand brand-btn" onClick={() => setEntered(false)} title="Back to overview">
          <span className="brand-mark" aria-hidden>◐</span>
          <span className="brand-name">Workflow&nbsp;MRI</span>
        </button>
        <div className="topbar-right">
          <button
            className={`safe-toggle${safeMode ? " on" : ""}`}
            onClick={() => setSafeMode((s) => !s)}
            title="When on, detected PII is redacted from evidence — a governance control."
          >
            <span className="safe-dot" />
            Safe mode {safeMode ? "ON" : "OFF"}
          </button>
          <div className="topbar-co">
            <span className="co-name">{co.name}</span>
            {co.fictional && <span className="fictional">FICTIONAL</span>}
          </div>
        </div>
      </header>

      <div className="layout">
        <nav className="nav">
          {NAV.map((n) => (
            <button
              key={n.key}
              className={`nav-item${active === n.key ? " on" : ""}${n.center ? " center" : ""}`}
              onClick={() => setActive(n.key)}
            >
              {n.label}
              {n.center && <span className="nav-badge">core</span>}
            </button>
          ))}
          <div className="nav-foot">
            <span>engine: {bundle.manifest.engine.llm_backend} · {bundle.manifest.engine.model}</span>
            <span>deterministic replay · no live inference</span>
          </div>
        </nav>

        <main className="content">
          {active === "ingest" && <Ingest bundle={bundle} />}
          {active === "graph" && <ProcessGraph bundle={bundle} safeMode={safeMode} />}
          {active === "risk" && <RiskPanel bundle={bundle} safeMode={safeMode} />}
          {active === "automations" && <Automations bundle={bundle} />}
          {active === "beforeafter" && <BeforeAfter bundle={bundle} />}
          {active === "export" && <ExportView bundle={bundle} />}
        </main>
      </div>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="centered">{children}</div>;
}
