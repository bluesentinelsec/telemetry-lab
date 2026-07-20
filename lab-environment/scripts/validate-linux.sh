#!/usr/bin/env bash
# validate-linux.sh — post-deploy validation for the Debian lab host.
#
# Two jobs, matching the study's rigor model (consume latest, record exactly what
# ran):
#   1. Provenance: capture the installed Falco version + binary/rule SHA-256s and
#      host facts into a JSON manifest (printed, saved, and uploaded to S3).
#   2. Fire test: prove the detection pipeline (modern-eBPF driver -> event ->
#      rule eval -> alert) actually fires, end to end, with a deterministic
#      canary rule, and also exercise a real shipped rule (read /etc/shadow).
#
# Usage:  sudo bash validate-linux.sh [s3-bucket-name]
# Exit 0 only if the pipeline fired.
set -uo pipefail

BUCKET="${1:-}"
MANIFEST=/var/log/lab-provision-linux.json
CANARY=/etc/falco/rules.d/zz-lab-firetest-canary.yaml
CANARY_BIN=/usr/local/bin/lab_canary_xyz
SERVICE=falco-modern-bpf.service

say() { printf '\n=== %s ===\n' "$*"; }

# ---------------------------------------------------------------- provenance ---
say "PROVENANCE"
FALCO_VERSION="$(falco --version 2>/dev/null | tr -d '\r')"
FALCO_BIN="$(command -v falco || echo /usr/bin/falco)"
FALCO_BIN_SHA="$(sha256sum "$FALCO_BIN" 2>/dev/null | awk '{print $1}')"
KERNEL="$(uname -r)"
OS_PRETTY="$(. /etc/os-release && echo "$PRETTY_NAME")"

# Per-rule-file hashes (default + any incubating/sandbox feeds falcoctl pulled).
RULE_ROWS=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  h="$(sha256sum "$f" | awk '{print $1}')"
  RULE_ROWS="${RULE_ROWS}    {\"file\": \"${f}\", \"sha256\": \"${h}\"},\n"
done < <(find /etc/falco -maxdepth 2 -name '*.yaml' 2>/dev/null | sort)
RULE_ROWS="$(printf '%b' "$RULE_ROWS" | sed '$ s/,$//')"

DRIVER_STATE="$(systemctl is-active "$SERVICE" 2>/dev/null)"

printf 'falco: %s\nbinary: %s\nsha256: %s\nkernel: %s\nos: %s\nservice(%s): %s\n' \
  "$FALCO_VERSION" "$FALCO_BIN" "$FALCO_BIN_SHA" "$KERNEL" "$OS_PRETTY" "$SERVICE" "$DRIVER_STATE"

# ------------------------------------------------------------------ firetest ---
say "FIRE TEST"
# (a) deterministic canary rule — proves the engine+driver+eval path unambiguously
cat > "$CANARY" <<'YAML'
- rule: Lab Firetest Canary
  desc: Deterministic validation that the Falco detection pipeline fires end to end.
  condition: spawned_process and proc.name = "lab_canary_xyz"
  output: "LAB_FIRETEST_CANARY pid=%proc.pid exe=%proc.exepath"
  priority: WARNING
  tags: [lab, firetest]
YAML
cp /bin/true "$CANARY_BIN"
systemctl restart "$SERVICE"
sleep 8   # let the driver attach and rules load

MARK="$(date --iso-8601=seconds)"
"$CANARY_BIN" || true                        # trip the canary
cat /etc/shadow >/dev/null 2>&1 || true      # trip a real shipped rule
sleep 5

LOG="$(journalctl -u "$SERVICE" --since "$MARK" --no-pager 2>/dev/null)"
CANARY_HIT=no; SHADOW_HIT=no
echo "$LOG" | grep -q "LAB_FIRETEST_CANARY" && CANARY_HIT=yes
echo "$LOG" | grep -qi "sensitive file" && SHADOW_HIT=yes
echo "canary_fired=$CANARY_HIT  shadow_rule_fired=$SHADOW_HIT"
echo "--- falco alert lines ---"
echo "$LOG" | grep -iE "Warning|Notice|Critical|Error|LAB_FIRETEST" | tail -20

# canary is the authoritative pipeline check; clean it up afterwards
rm -f "$CANARY" "$CANARY_BIN"; systemctl restart "$SERVICE" || true

PASS=fail
[ "$CANARY_HIT" = yes ] && PASS=pass

# ------------------------------------------------------------------ manifest ---
{
  printf '{\n'
  printf '  "host": "debian",\n'
  printf '  "falco_version": "%s",\n' "$FALCO_VERSION"
  printf '  "falco_binary": "%s",\n' "$FALCO_BIN"
  printf '  "falco_binary_sha256": "%s",\n' "$FALCO_BIN_SHA"
  printf '  "kernel": "%s",\n' "$KERNEL"
  printf '  "os": "%s",\n' "$OS_PRETTY"
  printf '  "service": "%s",\n' "$DRIVER_STATE"
  printf '  "rule_files": [\n%s\n  ],\n' "$RULE_ROWS"
  printf '  "firetest": {"canary_fired": "%s", "shadow_rule_fired": "%s"},\n' "$CANARY_HIT" "$SHADOW_HIT"
  printf '  "result": "%s"\n' "$PASS"
  printf '}\n'
} | tee "$MANIFEST"

if [ -n "$BUCKET" ]; then
  aws s3 cp "$MANIFEST" "s3://$BUCKET/provenance/linux-provision.json" --only-show-errors \
    && echo "uploaded to s3://$BUCKET/provenance/linux-provision.json"
fi

say "RESULT: $PASS"
[ "$PASS" = pass ]
