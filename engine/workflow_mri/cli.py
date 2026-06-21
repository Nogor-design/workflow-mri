"""CLI: `python -m workflow_mri build` regenerates the Artifact Bundle from samples.

    python -m workflow_mri build                 # -> bundles/<run_id>/
    python -m workflow_mri build --promote        # also copy into web/public/bundle/
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from workflow_mri.export.bundle_io import write_bundle
from workflow_mri.pipeline import build_bundle

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLES = REPO_ROOT / "samples" / "meridian-claims"
WEB_BUNDLE = REPO_ROOT / "web" / "public" / "bundle"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workflow_mri")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build the Artifact Bundle from a samples folder")
    b.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    b.add_argument("--out", type=Path, default=None, help="output dir (default bundles/<run_id>/)")
    b.add_argument("--run-id", default=None)
    b.add_argument("--promote", action="store_true", help="also copy the bundle into web/public/bundle/")
    b.add_argument("--enrich", action="store_true", help="run the optional LLM enrichment pass (needs Ollama/Claude)")

    args = parser.parse_args(argv)
    if args.cmd == "build":
        bundle = build_bundle(args.samples, run_id=args.run_id, enrich=args.enrich)
        out = args.out or (REPO_ROOT / "bundles" / bundle.manifest.run_id)
        write_bundle(bundle, out)
        c = bundle.manifest.counts
        print(f"built bundle -> {out}")
        print(f"  {c['artifacts']} artifacts · {c['steps']} steps · {c['edges']} edges · "
              f"{c['risks']} risks · {c['automations']} automations · {c['reviews']} reviews")
        if args.promote:
            WEB_BUNDLE.mkdir(parents=True, exist_ok=True)
            for f in out.glob("*.json"):
                shutil.copy2(f, WEB_BUNDLE / f.name)
            print(f"  promoted -> {WEB_BUNDLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
