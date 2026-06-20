# Workflow MRI — task runner. See docs/architecture.md "Build/run commands".
# Targets marked (Phase N) are stubs until that roadmap phase.

.PHONY: help install web web-build test test-web test-engine bundle promote types evals

help:
	@echo "install     - install engine (editable) + web deps"
	@echo "web         - vite dev server for the showcase"
	@echo "web-build   - static export of the showcase (-> web/dist)"
	@echo "test        - engine (pytest) + web (vitest)"
	@echo "bundle      - (Phase 2) samples/meridian-claims -> bundles/<run>/"
	@echo "promote     - (Phase 1) copy a verified bundle -> web/public/bundle/"
	@echo "types       - (Phase 2) Pydantic schema -> web/src TS types"
	@echo "evals       - (Phase 4) synthetic-ground-truth metrics"

install:
	cd engine && pip install -e ".[dev]"
	cd web && npm install

web:
	cd web && npm run dev

web-build:
	cd web && npm run build

test: test-engine test-web

test-engine:
	cd engine && python -m pytest

test-web:
	cd web && npm test

bundle:
	cd engine && python -m workflow_mri build

promote:
	cd engine && python -m workflow_mri build --promote

types:
	@echo "TODO (Phase 2): generate web/src TS types from engine Pydantic schema"

evals:
	@echo "TODO (Phase 4): run evals against synthetic ground truth"
