#!/usr/bin/env bash
# Run only on the disposable lab host. Leaves the original configuration intact.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$HERE/validate_manifest.py"
systemctl stop falco-modern-bpf.service
systemctl stop falco-coverage.service 2>/dev/null || true
# Falco 0.45.0/libsinsp 0.26.0 discards live entry events when only their
# pathname is unreadable. Use the pinned parser fix; keep rules and the strict
# health gate unchanged. FALCO_BIN is an explicit override for diagnostics.
if [[ -z ${FALCO_BIN:-} ]]; then
  FALCO_BIN=/usr/bin/falco
  version=$("$FALCO_BIN" --version -o json_output=true | python3 -c 'import json,sys; print(json.load(sys.stdin)["falco_version"])')
  if [[ "$version" == 0.45.0 ]]; then
    FALCO_BIN=$(bash "$HERE/falco-health-fix/install.sh")
  fi
fi
systemd-run --unit=falco-coverage --collect "$FALCO_BIN" \
  -c /etc/falco/falco.yaml \
  -r "$HERE/rules/falco_rules.yaml" \
  -r "$HERE/rules/falco-incubating_rules.yaml" \
  -r "$HERE/rules/falco-sandbox_rules.yaml" \
  -o engine.kind=modern_ebpf -o rule_matching=all -o json_output=true \
  -o priority=debug -o buffered_outputs=false -o watch_config_files=false \
  -o stdout_output.enabled=true -o syslog_output.enabled=false \
  -o webserver.prometheus_metrics_enabled=true -o metrics.enabled=true \
  -o metrics.interval=1s -o metrics.kernel_counters_enabled=true
for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8765/metrics | grep -q drops; then exit 0; fi
  sleep 1
done
journalctl -u falco-coverage --no-pager -n 50
exit 1
