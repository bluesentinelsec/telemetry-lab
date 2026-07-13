#!/usr/bin/env python3
"""Verify that built primitives have the runtime their configuration claims.

    verify_substrate.py --config linux-c-musl dist/linux-c-musl
    verify_substrate.py --config linux-c-glibc --json report.json dist/...

Exits nonzero if any artifact does not match, so CI fails on a mislabeled
build rather than shipping it to the lab.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from substrate import verify  # noqa: E402

DEFAULT_MANIFEST = Path(__file__).resolve().parent / "substrate.toml"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="artifacts, or directories of them")
    parser.add_argument("--config", required=True, help="configuration to verify against")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--json", type=Path, help="write the report as JSON")
    args = parser.parse_args(argv)

    try:
        manifest = verify.load_manifest(args.manifest)
        artifacts = verify.find_artifacts(args.paths)
    except (verify.ManifestError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if not artifacts:
        print(f"error: no binaries found in {args.paths}", file=sys.stderr)
        return 2

    try:
        report = verify.verify(args.config, manifest, artifacts)
    except verify.ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(verify.render(report))

    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
