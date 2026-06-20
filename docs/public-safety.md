# Public-Safety Contract

Workflow MRI is a **public** portfolio artifact. Everything in the repo and the deployed
demo must be safe to show the entire internet, forever. Companion to
[`../DESIGN.md`](../DESIGN.md) §5 & §11.

## Principles

1. **Fictional by construction.** The only company is invented (Meridian Claims Co.). All
   names, policy numbers, amounts, emails, and dates are synthetic and obviously so. The
   `Manifest` and UI both label the company `fictional: true`.
2. **No secrets in the repo, ever.** No API keys, tokens, account numbers, local absolute
   paths, broker filenames, or model credentials. LLM keys live only in local env vars,
   never committed.
3. **No real personal data.** Even synthetic data avoids resembling a real person or company.
4. **Simulation is labeled.** The before/after panel is explicitly marked simulated, with
   its assumptions stated.
5. **The demo path runs no inference.** No live model calls from the public site → no way to
   leak a key or rack up cost.

## What lives where

| Sensitive? | Allowed in repo / public demo? |
|---|---|
| Fictional sample inputs (`samples/meridian-claims/`) | ✅ yes |
| Committed Bundle (`web/public/bundle/`) | ✅ yes — verify it contains only fictional data |
| Engine code, prompts, schema | ✅ yes |
| LLM API keys / Ollama host config | ❌ env vars only, never committed (`.env` gitignored) |
| Any real customer/trading/account data | ❌ never — wrong repo entirely |

## Pre-publish checklist (run before any deploy)

- [ ] Secret scan passes (e.g. `gitleaks detect`) — no keys/tokens.
- [ ] No absolute local paths (`D:\...`, `C:\Users\...`) in committed files or the Bundle.
- [ ] `Manifest.company.fictional == true`; UI shows the fictional banner.
- [ ] Simulation panel renders the "simulated" label and assumptions.
- [ ] No real person/company names anywhere (grep the Bundle + samples).
- [ ] `.env` and any local config are gitignored and absent from the tree.
- [ ] Thumbnails/screenshots in `assets/` are of the fictional company only.
- [ ] README and case-study copy contain no private context.

## Relationship to Eric's existing redaction policy

This mirrors the redaction discipline already used across the portfolio (`a1-program-manager`
REDACTION_POLICY / PUBLIC_REDACTION_REVIEW). The difference: Workflow MRI is **born public**
— there is no private original to redact, because the only data that ever exists is fictional.
That is the cleanest possible safety posture and is worth saying on the case-study page.
