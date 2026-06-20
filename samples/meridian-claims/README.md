# samples/meridian-claims/

Fictional input artifacts for **Meridian Claims Co.**, a small insurance-claims operation.
These are the messy inputs Workflow MRI ingests. **Everything here is invented** — no real
people, companies, or data (see [`../../docs/public-safety.md`](../../docs/public-safety.md)).

Chosen because claims processing has a clear linear workflow (intake → triage → review →
approval → payment → exception → closure), a rich PII surface, and obvious compliance stakes
— ideal for showing governance.

## Folders (populated in roadmap Phase 2)

| Folder | Messy-on-purpose contents |
|---|---|
| `spreadsheets/` | CSV/XLSX claim logs with inconsistent columns, mixed status labels |
| `pdfs/` | SOP docs and claim forms |
| `emails/` | approval threads, exceptions, escalations |
| `screenshots/` | dashboard/ticket screenshots (fictional) |
| `notes/` | free-text employee/manager notes (with planted PII to be flagged) |

The mess is intentional: inconsistent columns, duplicate handoffs, missing approvals, and
PII in free text are the exact things the engine should surface.
