"""Phase 0 smoke test: the Bundle contract imports and a minimal Bundle validates."""

from workflow_mri.schema import (
    BUNDLE_VERSION,
    Bundle,
    Company,
    EngineInfo,
    Manifest,
)


def test_minimal_bundle_validates():
    bundle = Bundle(
        manifest=Manifest(
            run_id="smoke",
            company=Company(name="Meridian Claims Co.", domain="insurance-claims"),
            generated_at="2026-06-20T08:00:00-06:00",
            engine=EngineInfo(llm_backend="ollama", model="llama3.1:8b", prompt_set="v1"),
        )
    )
    assert bundle.manifest.bundle_version == BUNDLE_VERSION
    assert bundle.manifest.company.fictional is True
    assert bundle.artifacts == []


def test_bundle_round_trips_json():
    bundle = Bundle(
        manifest=Manifest(
            run_id="smoke",
            company=Company(name="Meridian Claims Co.", domain="insurance-claims"),
            generated_at="2026-06-20T08:00:00-06:00",
            engine=EngineInfo(llm_backend="claude", model="claude-opus-4-8", prompt_set="v1"),
        )
    )
    restored = Bundle.model_validate_json(bundle.model_dump_json())
    assert restored.manifest.engine.llm_backend == "claude"
