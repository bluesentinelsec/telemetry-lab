"""Verify that built artifacts exhibit the substrate their configuration claims.

Expectations attach to the *configuration*, not to the individual primitive.
Every primitive built under linux-c-musl must exhibit the same interpreter, the
same libc, and the same machine, so one expectation block covers all 16
primitives in that cell. 16 configurations x 16 primitives = 256 artifacts,
described by 16 blocks.
"""

import tomllib
from pathlib import Path

from . import facts, rules


class ManifestError(Exception):
    pass


def load_manifest(path):
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    return data.get("config", {})


def find_artifacts(paths):
    """Expand paths into the binaries to verify, in stable order."""
    found = []
    for path in paths:
        path = Path(path)
        if path.is_dir():
            found.extend(
                child for child in sorted(path.rglob("*"))
                if child.is_file() and facts.is_binary(child)
            )
        elif path.is_file():
            found.append(path)
        else:
            raise ManifestError(f"{path}: no such file or directory")
    return found


def verify(config_name, manifest, artifacts):
    """Check every artifact against one configuration's expectations."""
    if config_name not in manifest:
        known = ", ".join(sorted(manifest)) or "(none)"
        raise ManifestError(f"unknown config {config_name!r}; known: {known}")

    config = manifest[config_name]
    expectations = config.get("expect", {})
    if not expectations:
        raise ManifestError(f"config {config_name!r} declares no expectations")

    report = {
        "config": config_name,
        "substrate": {
            key: value for key, value in config.items() if key != "expect"
        },
        "artifacts": [],
        "passed": True,
    }

    for artifact in artifacts:
        observed = facts.extract(artifact)

        checks = []
        for fact, expected in expectations.items():
            for ok, detail in rules.check(fact, expected, observed.get(fact)):
                checks.append({"ok": ok, "detail": detail})

        passed = all(check["ok"] for check in checks)
        report["passed"] = report["passed"] and passed
        report["artifacts"].append(
            {
                "path": str(artifact),
                "name": Path(artifact).stem,
                "observed": observed,
                "checks": checks,
                "passed": passed,
            }
        )

    return report


def render(report):
    """Human-readable report. Observed facts are always printed, pass or fail,
    so CI logs carry the provenance evidence rather than just a green check."""
    lines = []
    substrate = report["substrate"]
    summary = ", ".join(f"{k}={v}" for k, v in substrate.items() if k != "description")
    lines.append(f"config: {report['config']}  ({summary})")

    for artifact in report["artifacts"]:
        status = "PASS" if artifact["passed"] else "FAIL"
        lines.append("")
        lines.append(f"  [{status}] {artifact['path']}")

        observed = artifact["observed"]
        for key in ("machine", "interpreter", "needed", "linkage", "libc", "comment"):
            if key in observed:
                lines.append(f"      {key:<12} {observed[key]!r}")

        for check in artifact["checks"]:
            mark = "ok  " if check["ok"] else "FAIL"
            lines.append(f"      {mark} {check['detail']}")

    lines.append("")
    total = len(report["artifacts"])
    failed = sum(1 for a in report["artifacts"] if not a["passed"])
    if report["passed"]:
        lines.append(f"all {total} artifact(s) match the {report['config']} substrate")
    else:
        lines.append(f"{failed} of {total} artifact(s) do NOT match the {report['config']} substrate")

    return "\n".join(lines)
