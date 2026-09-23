#!/usr/bin/env bash
# Runs ON the Debian lab host at the end of provisioning (invoked from EC2 user
# data). Writes /opt/lab/inventory.json -- version + SHA-256 + path for the
# detector (Falco), the telemetry-lab release and its binaries, and the OS.
#
# tap discovers this file co-located with telemetry data and stamps analysis
# output with it, so every result traces back to exact versions + hashes.
set -uo pipefail
OUT="${1:-/opt/lab/inventory.json}"
BUNDLE="${2:-}"
ARCHIVE="${3:-/opt/lab/telemetry-lab.tar.gz}"

python3 - "$OUT" "$BUNDLE" "$ARCHIVE" <<'PY'
import hashlib, json, os, platform, re, subprocess, sys
from datetime import datetime, timezone

out = sys.argv[1]

def sha256(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None

def stdout(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout
    except OSError:
        return ""

# telemetry-lab release: version comes from the extracted dir name.
base = sys.argv[2]
for d in sorted(os.listdir("/opt/lab")) if os.path.isdir("/opt/lab") else []:
    if not base and d.startswith("telemetry-lab-") and d.endswith("-linux"):
        base = os.path.join("/opt/lab", d)
        break
m = re.match(r"telemetry-lab-(.+)-linux$", os.path.basename(base)) if base else None
ver = m.group(1) if m else ""

pretty = ""
try:
    for line in open("/etc/os-release"):
        if line.startswith("PRETTY_NAME="):
            pretty = line.split("=", 1)[1].strip().strip('"')
except OSError:
    pass

comps = []
falco = "/usr/bin/falco"
# Inventory the running detector, including a locally patched coverage build.
# The distribution binary remains installed but may not be the measured one.
for service in ("falco-coverage.service", "falco-modern-bpf.service"):
    pid = stdout("systemctl", "show", service, "-p", "MainPID", "--value").strip()
    if pid.isdigit() and int(pid) > 0:
        candidate = os.path.realpath(f"/proc/{pid}/exe")
        if os.path.isfile(candidate):
            falco = candidate
            break
if os.path.exists(falco):
    version_output = stdout(falco, "--version")
    try:
        falco_version = json.loads(version_output)["falco_version"]
    except (ValueError, KeyError, TypeError):
        fm = re.search(r"(?im)^Falco version:\s*(\d+\.\d+\.\d+)", version_output)
        falco_version = fm.group(1) if fm else None
    comps.append({"name": "falco", "type": "detector",
                  "version": falco_version,
                  "sha256": sha256(falco), "path": falco})
    receipt = os.path.join(os.path.dirname(os.path.dirname(falco)), "receipt.json")
    if os.path.isfile(receipt):
        comps.append({"name": "falco-build-receipt", "type": "provenance",
                      "version": falco_version, "sha256": sha256(receipt), "path": receipt})

# Container detonation runtime: Docker daemon + the constant substrate base image.
docker = "/usr/bin/docker"
if os.path.exists(docker):
    dm = re.search(r"\d+\.\d+\.\d+", stdout(docker, "--version"))
    comps.append({"name": "docker", "type": "runtime",
                  "version": dm.group(0) if dm else None,
                  "sha256": None, "path": docker})
    img = stdout(docker, "image", "inspect", "--format", "{{.Id}}", "lab-substrate:13").strip()
    if img:
        comps.append({"name": "lab-substrate-image", "type": "container",
                      "version": "debian:13", "sha256": img.replace("sha256:", ""),
                      "path": "lab-substrate:13"})
tgz = sys.argv[3]
if os.path.exists(tgz):
    comps.append({"name": "telemetry-lab", "type": "release", "version": ver,
                  "sha256": sha256(tgz), "path": base})
for name, rel in (("tmon", "tmon/tmon"), ("tap", "tap/tap")):
    p = os.path.join(base, rel) if base else ""
    if p and os.path.isfile(p):
        comps.append({"name": name, "type": "project", "version": ver,
                      "sha256": sha256(p), "path": p})
for name, rel in (("ttp_primitives", "ttp-primitives"), ("ttp_composite", "ttp-composite")):
    p = os.path.join(base, rel) if base else ""
    if p and os.path.isdir(p):
        comps.append({"name": name, "type": "project", "version": ver,
                      "sha256": None, "path": p})

doc = {
    "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "host": "linux",
    "os": pretty,
    "kernel": platform.release(),
    "telemetry_lab_release": ver,
    "components": comps,
}
with open(out, "w") as f:
    json.dump(doc, f, indent=2)
    f.write("\n")
print(open(out).read())
PY
