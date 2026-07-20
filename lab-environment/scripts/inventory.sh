#!/usr/bin/env bash
# inventory.sh — after the lab deploys, record what's actually installed.
#
# Asks each host (over SSM) for the versions + SHA-256s of the lab release
# package and the external detection dependencies, and writes a single
# lab-inventory.md file. That file is the reproducibility record for the
# dissertation: the lab consumes latest deps, so what establishes rigor is a
# per-run note of exactly what ran.
#
# Usage:  ./inventory.sh                 # writes ./lab-inventory.md
#         LAB_RELEASE=0.2.0 ./inventory.sh
set -uo pipefail

REGION=us-west-2
STACK=LabEnvironmentStack
LAB_RELEASE="${LAB_RELEASE:-0.1.0}"     # version of the telemetry-lab release bundle we deploy
OUT="${1:-lab-inventory.md}"
TMP="$(mktemp -d)"

out() { aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }
DEB="$(out DebianInstanceId)"; WIN="$(out WindowsInstanceId)"; BUCKET="$(out DataBucketName)"

# Run a script on a host over SSM and print its stdout.
run_ssm() { # $1=instance $2=doc $3=local-script-file
  local iid=$1 doc=$2 file=$3 cid st
  printf '{"commands":[%s]}' "$(python3 -c 'import json,sys;print(json.dumps(open(sys.argv[1]).read()))' "$file")" > "$TMP/p.json"
  cid=$(aws ssm send-command --region "$REGION" --instance-ids "$iid" --document-name "$doc" \
        --parameters "file://$TMP/p.json" --query 'Command.CommandId' --output text 2>/dev/null) || return 1
  for _ in $(seq 1 45); do
    sleep 4
    st=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$iid" \
         --query 'Status' --output text 2>/dev/null)
    [ "$st" = Success ] && { aws ssm get-command-invocation --region "$REGION" --command-id "$cid" \
        --instance-id "$iid" --query 'StandardOutputContent' --output text; return 0; }
    case "$st" in Failed|Cancelled|TimedOut) return 1;; esac
  done
  return 1
}

# --- Debian probe: emits Markdown table rows ---
cat > "$TMP/probe-linux.sh" <<EOF
REL="$LAB_RELEASE"
row(){ printf '| %s | %s | %s | %s | %s |\n' "\$1" "\$2" "\$3" "\$4" "\$5"; }
FB="\$(command -v falco)"
FV="\$(falco --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
row falco detector "\$FV" "\$(sha256sum "\$FB" 2>/dev/null | cut -c1-64)" "\$FB"
row os platform "\$(. /etc/os-release; echo "\$PRETTY_NAME") (kernel \$(uname -r))" "-" "-"
# telemetry-lab release package: version comes from the extracted dir name
# (telemetry-lab-<ver>-linux); the tarball hash is the release's byte identity.
BASE="\$(ls -d /opt/lab/telemetry-lab-*-linux 2>/dev/null | head -1)"
VER="\$(basename "\$BASE" 2>/dev/null | sed -e 's/^telemetry-lab-//' -e 's/-linux\$//')"
[ -n "\$VER" ] || VER="\$REL"
[ -f /opt/lab/telemetry-lab.tar.gz ] && row telemetry-lab release "\$VER" "\$(sha256sum /opt/lab/telemetry-lab.tar.gz | cut -c1-64)" "\$BASE"
[ -f "\$BASE/tmon/tmon" ] && row tmon project "\$VER" "\$(sha256sum "\$BASE/tmon/tmon" | cut -c1-64)" "\$BASE/tmon/tmon"
[ -f "\$BASE/tap/tap" ]   && row tap  project "\$VER" "\$(sha256sum "\$BASE/tap/tap"  | cut -c1-64)" "\$BASE/tap/tap"
[ -d "\$BASE/ttp-primitives" ] && row ttp_primitives project "\$VER" "(dir)" "\$BASE/ttp-primitives"
[ -d "\$BASE/ttp-composite" ]  && row ttp_composite  project "\$VER" "(dir)" "\$BASE/ttp-composite"
true   # never let a false test above be the script's exit code (SSM marks non-zero as Failed)
EOF

# --- Windows probe: emits Markdown table rows ---
cat > "$TMP/probe-win.ps1" <<EOF
\$rel = "$LAB_RELEASE"
function Row(\$n,\$t,\$v,\$h,\$p){ "| \$n | \$t | \$v | \$h | \$p |" }
\$sm = "C:\\lab\\sysmon\\Sysmon64.exe"; \$hb = "C:\\lab\\hayabusa\\hayabusa.exe"
Row "sysmon" "detector" ((Get-Item \$sm -EA SilentlyContinue).VersionInfo.FileVersion) ((Get-FileHash \$sm -EA SilentlyContinue).Hash) \$sm
\$hv = (& \$hb help 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+' | Select-Object -First 1).Matches.Value
Row "hayabusa" "detector" \$hv ((Get-FileHash \$hb -EA SilentlyContinue).Hash) \$hb
Row "os" "platform" ((Get-CimInstance Win32_OperatingSystem).Caption + " (" + [Environment]::OSVersion.Version + ")") "-" "-"
# telemetry-lab release package: version from the extracted dir name (telemetry-lab-<ver>-windows)
\$base = Get-ChildItem C:\\lab\\telemetry-lab -Directory -Filter 'telemetry-lab-*-windows' -EA SilentlyContinue | Select-Object -First 1
\$ver = if (\$base) { (\$base.Name -replace '^telemetry-lab-','' -replace '-windows\$','') } else { \$rel }
if (Test-Path C:\\lab\\telemetry-lab.zip) { Row "telemetry-lab" "release" \$ver ((Get-FileHash C:\\lab\\telemetry-lab.zip).Hash) (\$(if(\$base){\$base.FullName}else{"C:\\lab\\telemetry-lab"})) }
if (\$base) {
  foreach(\$c in @("tmon\\tmon.exe","tap\\tap.exe")){ \$p = Join-Path \$base.FullName \$c; if(Test-Path \$p){ Row ([IO.Path]::GetFileNameWithoutExtension(\$p)) "project" \$ver ((Get-FileHash \$p).Hash) \$p } }
  foreach(\$d in @("ttp-primitives","ttp-composite")){ \$p = Join-Path \$base.FullName \$d; if(Test-Path \$p){ Row (\$d -replace '-','_') "project" \$ver "(dir)" \$p } }
}
EOF

echo "Querying Debian ($DEB)..."   >&2; LINUX_ROWS="$(run_ssm "$DEB" AWS-RunShellScript   "$TMP/probe-linux.sh")" || LINUX_ROWS="| (debian probe failed) | | | | |"
echo "Querying Windows ($WIN)..."  >&2; WIN_ROWS="$(run_ssm "$WIN" AWS-RunPowerShellScript "$TMP/probe-win.ps1")"  || WIN_ROWS="| (windows probe failed) | | | | |"

{
  echo "# Lab Inventory"
  echo
  echo "- Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "- Stack: \`$STACK\` (region $REGION)"
  echo "- Lab release package: \`$LAB_RELEASE\`"
  echo "- Hosts: debian \`$DEB\`, windows \`$WIN\`"
  echo
  echo "| Component | Type | Version | SHA-256 | Path |"
  echo "|---|---|---|---|---|"
  echo "$LINUX_ROWS"
  echo "$WIN_ROWS"
} > "$OUT"

rm -rf "$TMP"
echo "wrote $OUT"; echo; cat "$OUT"

# Best-effort copy alongside the run's data.
[ -n "$BUCKET" ] && aws s3 cp "$OUT" "s3://$BUCKET/provenance/$(basename "$OUT")" --only-show-errors \
  && echo "uploaded to s3://$BUCKET/provenance/$(basename "$OUT")"
