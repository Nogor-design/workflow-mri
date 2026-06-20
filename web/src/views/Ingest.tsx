import type { Artifact, Bundle } from "../bundle/types";

const KIND_ICON: Record<Artifact["kind"], string> = {
  csv: "▦",
  xlsx: "▦",
  pdf: "▤",
  email: "✉",
  screenshot: "▭",
  note: "✎",
};

export function Ingest({ bundle }: { bundle: Bundle }) {
  const needsReview = bundle.reviews.length;
  const avgConf =
    bundle.artifacts.reduce((s, a) => s + a.extraction_confidence, 0) /
    Math.max(1, bundle.artifacts.length);

  return (
    <div className="view">
      <div className="view-head">
        <h2>Ingest</h2>
        <p>Chaotic inputs, normalized. Governance starts at intake — low-confidence items are flagged for review.</p>
      </div>

      <div className="stat-row">
        <Stat n={bundle.manifest.counts.artifacts} label="artifacts" />
        <Stat n={new Set(bundle.artifacts.map((a) => a.kind)).size} label="formats" />
        <Stat n={`${(avgConf * 100) | 0}%`} label="avg confidence" />
        <Stat n={needsReview} label="need review" warn />
      </div>

      <div className="artifact-list">
        {bundle.artifacts.map((a) => (
          <div key={a.id} className="artifact-row">
            <span className="art-icon">{KIND_ICON[a.kind]}</span>
            <span className="art-name">{a.source_name}</span>
            <span className="art-type">{a.detected_type}</span>
            <span className={`art-conf ${a.extraction_confidence < 0.7 ? "low" : ""}`}>
              <span className="bar" style={{ width: `${a.extraction_confidence * 60}px` }} />
              {(a.extraction_confidence * 100) | 0}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ n, label, warn }: { n: number | string; label: string; warn?: boolean }) {
  return (
    <div className={`stat ${warn ? "stat-warn" : ""}`}>
      <span className="stat-n">{n}</span>
      <span className="stat-l">{label}</span>
    </div>
  );
}
