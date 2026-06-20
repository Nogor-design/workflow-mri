import { describe, expect, it } from "vitest";
import { maskQuote, piiArtifactIds } from "./redact";
import type { RiskFinding } from "./types";

describe("Safe Mode redaction", () => {
  it("collects only artifact ids tied to PII findings", () => {
    const risks: RiskFinding[] = [
      {
        id: "risk-pii",
        category: "pii",
        severity: "high",
        title: "Synthetic PII in free text",
        description: "A fictional email contains synthetic PII-like values.",
        confidence: 0.91,
        evidence: [{ artifact_id: "art-email", quote: "Jane Demo, 555-0101" }],
      },
      {
        id: "risk-approval",
        category: "missing_approval",
        severity: "med",
        title: "Approval missing evidence",
        description: "Approval was recorded without a linked document.",
        confidence: 0.82,
        evidence: [{ artifact_id: "art-approval", quote: "approved" }],
      },
    ];

    expect(Array.from(piiArtifactIds(risks))).toEqual(["art-email"]);
  });

  it("masks letters, digits, and placeholder characters when Safe Mode is on", () => {
    expect(maskQuote("Jane Demo 555-0101 *synthetic*", true)).toBe(
      "▒▒▒▒ ▒▒▒▒ ▒▒▒-▒▒▒▒ ▒▒▒▒▒▒▒▒▒▒▒",
    );
    expect(maskQuote("Jane Demo 555-0101", false)).toBe("Jane Demo 555-0101");
  });
});
