set -eu
cloud-init status --wait
mkdir -p /opt/coverage-expansion/evidence /opt/telemetry-lab
cd /opt/coverage-expansion
aws s3 cp s3://@BUCKET@/@PREFIX@/payload.tgz payload.tgz --only-show-errors
printf '%s  payload.tgz\n' '@PAYLOAD_SHA@' | sha256sum -c -
# Existing evidence is retained; stage only while no campaign is running.
tar xzf payload.tgz
aws s3 cp s3://@BUCKET@/@PREFIX@/falco.tgz falco.tgz --only-show-errors
printf '%s  falco.tgz\n' '@FALCO_SHA@' | sha256sum -c -
tar xzf falco.tgz -C /opt/telemetry-lab
mkdir -p /opt/telemetry-lab/falco-0.45.0-healthfix.1
cp -a /opt/telemetry-lab/final-install/. /opt/telemetry-lab/falco-0.45.0-healthfix.1/
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=600 install -y --no-install-recommends python3-yaml libtbb12 libjsoncpp26 libre2-11 libelf1t64 libcurl4t64 libssl3t64 zlib1g > evidence/dependencies.log 2>&1
python3 - <<'PY'
import json,hashlib,shutil
from pathlib import Path
b=Path('bundle');expected=json.loads((b/'files.sha256.json').read_text())
for name,digest in expected.items():
 p=b/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
 if p.read_bytes()[:4]==b'\x7fELF':p.chmod(0o755)
image=Path('image');image.mkdir(exist_ok=True)
for cfg in json.loads((b/'manifest.json').read_text())['composite_configs']:
 shutil.copytree(b/'ttp-composite'/cfg,image/cfg,dirs_exist_ok=True)
shutil.copy2(b/'ttp-composite/linux-c-glibc/falco_helper',image/'helper')
shutil.copy2(b/'ttp-composite/coverage/Dockerfile',image/'Dockerfile')
receipt=json.loads(Path('/opt/telemetry-lab/falco-0.45.0-healthfix.1/receipt.json').read_text())
assert receipt['binary_sha256']==hashlib.sha256(Path('/opt/telemetry-lab/falco-0.45.0-healthfix.1/bin/falco').read_bytes()).hexdigest()
PY
docker build -t lab-falco-coverage:local image > evidence/image-build.log 2>&1
FALCO_BIN=/opt/telemetry-lab/falco-0.45.0-healthfix.1/bin/falco bash bundle/ttp-composite/coverage/setup-detector.sh > evidence/falco-setup.log 2>&1
cp /opt/telemetry-lab/falco-0.45.0-healthfix.1/receipt.json evidence/falco-receipt.json
dpkg-query -W > evidence/packages.txt
uname -a > evidence/kernel.txt
aws s3 sync evidence s3://@BUCKET@/results/linux/ --only-show-errors
