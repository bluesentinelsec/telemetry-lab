#!/usr/bin/env bash
# Runs ON the Debian lab host at the end of provisioning (invoked from EC2 user
# data). Writes /opt/lab/inventory.json -- version + SHA-256 + path for the
# detector (Falco), the telemetry-lab release and its binaries, and the OS.
#
# tap discovers this file co-located with telemetry data and stamps analysis
# output with it, so every result traces back to exact versions + hashes.
set -uo pipefail
OUT=/opt/lab/inventory.json

python3 - "$OUT" <<'PY'
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
base = ""
for d in sorted(os.listdir("/opt/lab")) if os.path.isdir("/opt/lab") else []:
    if d.startswith("telemetry-lab-") and d.endswith("-linux"):
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
if os.path.exists(falco):
    fm = re.search(r"\d+\.\d+\.\d+", stdout(falco, "--version"))
    comps.append({"name": "falco", "type": "detector",
                  "version": fm.group(0) if fm else None,
                  "sha256": sha256(falco), "path": falco})
tgz = "/opt/lab/telemetry-lab.tar.gz"
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
