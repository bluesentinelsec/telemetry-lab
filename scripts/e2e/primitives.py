#!/usr/bin/env python3
"""Run each shipped Linux primitive once under the shipped tmon, then tap."""
import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('bundle', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
a.bundle = a.bundle.resolve()
a.output.mkdir(parents=True, exist_ok=False)
raw = a.output / 'raw'
raw.mkdir()
m = json.loads((a.bundle / 'manifest.json').read_text())
rows = []
for config in m['configs']:
    for case in m['primitives']:
        exe = a.bundle / 'ttp-primitives' / config / case
        output = raw / f'{config}-{case}.jsonl'
        meta = dict(os='linux', config=config, primitive=case, iteration='1',
                    host=platform.node(), language=config.split('-')[1], runtime='-'.join(config.split('-')[2:]))
        cmd = [str(a.bundle / 'tmon/tmon'), '--format', 'json', '-o', str(output)]
        for k, v in meta.items():
            cmd += ['--meta', f'{k}={v}']
        cmd += ['--', str(exe)]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            stdout, stderr, code = run.stdout, run.stderr, run.returncode
        except subprocess.TimeoutExpired as e:
            stdout, stderr, code = str(e.stdout), str(e.stderr), 'timeout'
        output.with_suffix('.stdout').write_text(stdout)
        output.with_suffix('.stderr').write_text(stderr)
        records = [json.loads(line) for line in output.read_text().splitlines()] if output.exists() else []
        summaries = [r for r in records if r.get('record') == 'summary']
        good = (code == 0 and len(summaries) == 1 and summaries[0]['target_exit_code'] == 0
                and summaries[0]['dropped'] == 0 and summaries[0]['total_events'] > 0)
        row = dict(config=config, case=case, exit_code=code, valid=good,
                   binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(), summary=summaries)
        rows.append(row)
        (a.output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps(row), flush=True)
with (a.output / 'tap.log').open('w') as log:
    tap = subprocess.run([str(a.bundle / 'tap/tap'), 'run', str(raw), '-o', str(a.output / 'tap')], stdout=log, stderr=subprocess.STDOUT)
raise SystemExit(0 if all(r['valid'] for r in rows) and tap.returncode == 0 else 1)
