#!/usr/bin/env bash
# Run only on the disposable lab host. Leaves the original configuration intact.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$HERE/validate_manifest.py"
systemctl stop falco-modern-bpf.service
systemctl stop falco-coverage.service 2>/dev/null || true
systemd-run --unit=falco-coverage --collect /usr/bin/falco \
  -c /etc/falco/falco.yaml \
  -r "$HERE/rules/falco_rules.yaml" \
  -r "$HERE/rules/falco-incubating_rules.yaml" \
  -r "$HERE/rules/falco-sandbox_rules.yaml" \
  -o engine.kind=modern_ebpf -o rule_matching=all -o json_output=true \
  -o priority=debug -o buffered_outputs=false \
  -o webserver.prometheus_metrics_enabled=true -o metrics.enabled=true \
  -o metrics.interval=1s -o metrics.kernel_counters_enabled=true
for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8765/metrics | grep -q drops; then exit 0; fi
  sleep 1
done
journalctl -u falco-coverage --no-pager -n 50
exit 1
