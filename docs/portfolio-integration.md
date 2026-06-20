# Portfolio Integration

How Workflow MRI plugs into `nogor-design.github.io/portfolio-showcase` as the new flagship.
Companion to [`../DESIGN.md`](../DESIGN.md) §2.

## Positioning

Workflow MRI becomes the **lead** project — promoted above the current top five
(Trades Resource Command Center, Job Application Factory, Agentic Idea Validation Engine,
TA Foundation, Empire of Drawdown). It is the one piece that states the portfolio's central
claim directly:

> *"Give me an ugly business process and I'll turn it into a governed, measurable operating system."*

It also fixes the two weaknesses every review named: **no unifying flagship** and **low
visual impact**.

## Where it lives

- **Code:** its own public GitHub repo (`workflow-mri`), pinned on the `Nogor-design` profile.
- **Live demo:** GitHub Pages static deploy of `web/` (e.g. `nogor-design.github.io/workflow-mri`).
- **Portfolio card:** a new top entry on the showcase site linking to the live demo, the
  repo, and the case-study page.

## Portfolio card copy (draft)

> **Workflow MRI** — *Operations diagnostician*
> Upload a chaotic company's spreadsheets, PDFs, emails, screenshots, and notes; get back a
> governed operating system: reconstructed process map, risk & PII findings, human-review
> queue, ranked automations, before/after simulation, and an exportable handoff package.
> Local-first multi-agent engine (Ollama/Claude, LangGraph) with evals; deterministic
> public demo. **[Live demo] · [Case study] · [Code]**
> *Tags: Multi-agent · Governance · RAG/Extraction · React · Python · Evals*

## Case-study page structure

Reuse the portfolio's existing case-study format, with these sections (from the idea docs):
Problem → Why it matters → System architecture (diagram) → Live demo (embed) →
Representative outputs → Evaluation criteria & numbers → Governance & safety model →
What I'd build next.

## Cross-links to amplify the narrative

- Link the engine's local-first + agentic angle to `ei-local-deep-research` and
  `Job Application Factory` (shared LangGraph / local-LLM DNA).
- Link the governance/review-queue angle to `Trades Resource Command Center` and the
  redaction discipline in `a1-program-manager`.
- This makes Workflow MRI read as the *synthesis* of the existing portfolio, not a one-off.

## Quick wins on the existing site (independent of the build)

Per the portfolio reviews, these can ship before the demo is done:
- Add a "Flagship (in build)" teaser card pointing at the repo.
- Add more visuals (screenshots, architecture diagram) to the landing page generally.
- Add a "For AI Engineering Roles" subsection highlighting agents, evals, tool-use, governance.
- Re-pin GitHub repos to prioritize the flagship + local-deep-research + Trades + Agentic.
