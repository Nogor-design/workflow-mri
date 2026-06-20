"""Phase 4: the engine meets every eval target against the independent ground truth.

Guards regressions in process reconstruction, risk recall, PII recall, and hallucination.
"""

import json
from pathlib import Path

import pytest

import sys

EVALS_DIR = Path(__file__).resolve().parents[1] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from run_evals import SAMPLES, evaluate  # noqa: E402
from workflow_mri.pipeline import build_bundle  # noqa: E402


@pytest.fixture(scope="module")
def metrics():
    gt = json.loads((EVALS_DIR / "ground_truth.json").read_text(encoding="utf-8"))
    bundle = build_bundle(SAMPLES, run_id="eval-test")
    return evaluate(bundle, gt)


def test_every_metric_passes_its_target(metrics):
    failing = [m.name for m in metrics if not m.passed]
    assert not failing, f"eval targets missed: {failing}"


def test_no_hallucinated_evidence(metrics):
    hall = next(m for m in metrics if m.name == "Hallucination rate")
    assert hall.value == 0.0, hall.detail


def test_full_recall_on_process_and_risk(metrics):
    by_name = {m.name: m.value for m in metrics}
    assert by_name["Step reconstruction recall"] == 1.0
    assert by_name["Edge + kind recall"] == 1.0
    assert by_name["Risk-category recall"] == 1.0
    assert by_name["PII detection recall"] == 1.0
