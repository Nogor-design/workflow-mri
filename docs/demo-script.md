# Demo Script

The narrated walkthrough for the recorded GIF/video and live interview demos. Tight,
high-signal, ~2–3 minutes. Companion to [`../DESIGN.md`](../DESIGN.md) §9.

## The 20-second hook (auto-plays on landing)

The process graph animates from a tangled, red-flagged "before" into a clean "after." No
narration needed — it states the whole value proposition visually.

## The full walkthrough

1. **Landing.**
   > "This is Meridian Claims — a fictional insurance company whose process lives in
   > spreadsheets, PDFs, emails, screenshots, and sticky notes. Watch Workflow MRI turn
   > that mess into a governed operating system."

2. **Ingest.**
   > "It ingests 23 chaotic artifacts, detects each type, and scores extraction confidence.
   > Eleven items are already flagged as needing human review — governance starts at intake."

3. **Process Graph** *(spend the most time here).*
   > "It reconstructs how work *actually* flows — intake, triage, review, approval, payment,
   > exception handling, closure — with owners and cycle times. The heatmap surfaces the
   > bottleneck at manual review; these two edges are duplicate handoffs; this loop is rework."
   > *(click a node)* "Every element links back to the evidence that produced it."

4. **Risk & Quality.**
   > "It flags PII sitting in free-text fields, approvals missing evidence, inconsistent
   > status labels, and tasks that bypass review — each with a 'why this was flagged' link."

5. **Automations.**
   > "Then it recommends automations, ranked by value, effort, and required oversight —
   > auto-routing intake, prefilling forms, deduping cases — with estimated time saved."

6. **Before / After.**
   > "A simulated before/after: cycle time drops from 92 to 51 hours, rework from 22% to 8%.
   > Clearly labeled as a simulation over the process graph."

7. **Export & Handoff.**
   > "Finally it exports a handoff package an engineering team could pick up tomorrow: process
   > map, cleaned schema, review-queue CSV, audit log, implementation backlog, and tests."

8. **Close (case-study mode).**
   > "Real local-first engine — pluggable Ollama or Claude, LangGraph agents with a critic
   > pass, evals on synthetic ground truth. The public demo is a deterministic replay of a
   > baked run, so it always works. This is the claim, proven: messy inputs become a governed,
   > measurable system."

## Recording notes

- Capture extra idle frames before/after each click for smooth GIF playback.
- Name the file meaningfully (e.g. `workflow-mri-walkthrough.gif`).
- Keep one fictional company preloaded so the demo can never fail live.
- Avoid any browser dialogs/alerts during capture.
