# web/

React + Vite static SPA. A **pure renderer** of the Artifact Bundle — no inference, no IO
beyond loading its own static Bundle. Deploys free to GitHub Pages.


See [`../DESIGN.md`](../DESIGN.md) §9 for the view spec and
[`../docs/data-model.md`](../docs/data-model.md) for the Bundle it consumes.

## Key choices

- **React Flow** for the centerpiece process graph (swimlanes, bottleneck heatmap, clickable
  evidence drawer).
- TypeScript types **generated** from the Pydantic schema (`make types`) so the UI can't
  drift from the contract.
- Static-export-safe routing (works under a GitHub Pages subpath).
- Loads the committed Bundle from `public/bundle/`.

## Layout (target)

```
web/
├── src/            # views, components, the Bundle store, generated types
└── public/
    └── bundle/     # the committed, published Artifact Bundle (the demo replays this)
```

## Status

Phase 0: scaffold an empty styled SPA that builds and deploys. Full UI is roadmap Phase 1.
