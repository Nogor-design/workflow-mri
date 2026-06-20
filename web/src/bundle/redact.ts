import type { RiskFinding } from "./types";

// Safe mode is a governance control, not cosmetics: when on, evidence tied to PII findings
// is masked so the demo never displays sensitive-looking strings. The set of artifact ids
// that carry PII is derived from the bundle's own pii-category risk findings.
export function piiArtifactIds(risks: RiskFinding[]): Set<string> {
  const ids = new Set<string>();
  for (const r of risks) {
    if (r.category === "pii") for (const ev of r.evidence) ids.add(ev.artifact_id);
  }
  return ids;
}

export function maskQuote(quote: string | undefined, redact: boolean): string | undefined {
  if (!quote) return quote;
  if (!redact) return quote;
  return quote.replace(/[A-Za-z0-9*]/g, "▒");
}
