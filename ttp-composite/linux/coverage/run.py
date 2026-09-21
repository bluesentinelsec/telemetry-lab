#!/usr/bin/env python3
"""Run the C matrix on the Linux lab host; preserve exact-rule evidence.

Each measured process runs in a fresh, network-isolated disposable container.
Fixture preparation completes before the journal cursor is captured. Missing
alerts remain valid outcomes; failed behavior or collector health never does.
"""
import argparse
import datetime
import hashlib
import json
import random
import re
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path
from validate_manifest import validate

SERVICE = 'falco-coverage.service'

def command(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, timeout=60, **kwargs).stdout.strip()

def detector_state():
    state = command(['systemctl', 'show', SERVICE, '-p', 'ActiveState', '-p', 'MainPID'])
    if 'ActiveState=active' not in state or 'MainPID=0' in state:
        raise RuntimeError('Falco is not healthy: ' + state)
    with urllib.request.urlopen('http://127.0.0.1:8765/metrics', timeout=5) as response:
        metrics = response.read().decode()
    counters = {}
    for line in metrics.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        name, value, *_ = line.split()
        if 'drops' in name or 'n_evts' in name:
            counters[name] = float(value)
    if not any('drops' in name for name in counters):
        raise RuntimeError('No kernel-drop counters available; cannot certify collection')
    return {'service': state, 'counters': counters, 'metrics': metrics}

def health_ok(before, after):
    if before['service'] != after['service']:
        return False
    if before['counters'].keys() != after['counters'].keys():
        return False
    for name, value in before['counters'].items():
        new = after['counters'][name]
        if new < value or ('drops' in name and new != value):
            return False
    return True

def attributed_alerts(log, container_id):
    alerts = []
    for line in log.splitlines():
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(event, dict) or not event.get('rule'):
            continue
        cid = str(event.get('output_fields', {}).get('container.id', ''))
        # Falco normally emits the first 12 hex characters. No substring matching.
        if len(cid) >= 12 and container_id.startswith(cid):
            alerts.append(event)
    return alerts

def score(case, execution, alerts, collection_ok, selected):
    marker = ('CONTROL_OK ' if case.get('control') else 'CASE_OK ') + case['id']
    behavior_ok = execution.returncode == 0 and marker in execution.stdout.splitlines()
    matches = sorted({a['rule'] for a in alerts})
    target = None if case.get('control') else case.get('rule')
    return {'behavior_ok': behavior_ok, 'collection_ok': collection_ok,
            'valid': behavior_ok and collection_ok, 'target_fired': target in matches if target else None,
            'negative_control_ok': not (set(matches) & selected) if not target else None,
            'matched_rules': matches}

def execute(case, config, output, image, functional_only=False):
    name = 'labcov-' + uuid.uuid4().hex[:16]
    exe = '/opt/coverage/' + config + '/coverage/' + case['id']
    cid = command(['docker', 'create', '--name', name, '--network', 'none',
                   '--cap-add', 'SYS_PTRACE', '--cap-add', 'NET_ADMIN',
                   '--security-opt', 'seccomp=unconfined',
                   '--tmpfs', '/dev/shm:rw,exec,nosuid,size=16m', image])
    output.mkdir(parents=True)
    try:
        command(['docker', 'start', cid])
        command(['docker', 'exec', cid, 'ip', 'addr', 'add', '169.254.169.254/32', 'dev', 'lo'])
        command(['docker', 'exec', cid, 'ip', 'addr', 'add', '198.18.0.1/32', 'dev', 'lo'])
        command(['docker', 'exec', cid, '/opt/coverage/' + config + '/coverage/fixture_prepare'])
        # Flush preparation events. No fixture processes remain running.
        time.sleep(2 if not functional_only else 0)
        before = detector_state() if not functional_only else None
        cursor = None
        if not functional_only:
            latest = command(['journalctl', '-u', SERVICE, '-n', '1', '--show-cursor', '--no-pager'])
            cursor = re.search(r'-- cursor: (.+)', latest).group(1)
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        execution = subprocess.run(['docker', 'exec', cid, exe] + (['--control'] if case.get('control') else []),
                                   text=True, capture_output=True, timeout=20)
        time.sleep(3 if not functional_only else 0)
        after = detector_state() if not functional_only else None
        log = command(['journalctl', '-u', SERVICE, '--after-cursor', cursor, '-o', 'cat', '--no-pager']) if cursor else ''
        alerts = attributed_alerts(log, cid)
        (output / 'journal.jsonl').write_text(log + '\n')
        (output / 'stdout.txt').write_text(execution.stdout)
        (output / 'stderr.txt').write_text(execution.stderr)
        (output / 'alerts.json').write_text(json.dumps(alerts, indent=2) + '\n')
        (output / 'health.json').write_text(json.dumps({'before':before, 'after':after}, indent=2) + '\n')
        record = {'case': case['id'], 'target_rule': case.get('rule'), 'config': config,
                  'container_id': cid, 'started': started, 'exit_code':execution.returncode,
                  'functional_only':functional_only, 'control':bool(case.get('control')), 'executable':exe}
        record.update(score(case, execution, alerts, health_ok(before,after) if before else False,
                            {c['rule'] for c in validate()['cases']}))
        (output / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
        return record
    finally:
        subprocess.run(['docker', 'rm', '-f', cid], capture_output=True, timeout=30)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--image',default='lab-falco-coverage:local')
    parser.add_argument('--repetitions',type=int,default=3)
    parser.add_argument('--seed',type=int,default=20260921)
    parser.add_argument('--case',action='append',dest='cases')
    parser.add_argument('--functional-only',action='store_true')
    args=parser.parse_args()
    if args.repetitions < 1: parser.error('repetitions must be positive')
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=validate()
    image_id=command(['docker','image','inspect',args.image,'--format','{{.Id}}'])
    cases=manifest['cases']
    if args.cases:
        if not set(args.cases) <= {c['id'] for c in cases}: parser.error('unknown case')
        cases=[c for c in cases if c['id'] in args.cases]
    target_cases=cases
    cases=cases + [{**c, 'control':True} for c in cases] + [{'id':'negative'}]
    plan=[];rng=random.Random(args.seed)
    for rep in range(1,args.repetitions+1):
        block=[{'repetition':rep,'case':c,'config':cfg} for c in cases for cfg in manifest['configs']]
        rng.shuffle(block);plan.extend(block)
    provenance={'manifest':manifest,'image_id':image_id,'seed':args.seed,'plan':plan,
                'kernel':command(['uname','-r']),'architecture':command(['uname','-m']),
                'docker':command(['docker','--version']),
                'falco':command(['falco','--version']) if not args.functional_only else None}
    here=Path(__file__).resolve().parent
    provenance['suite_files_sha256']={
        str(p.relative_to(here)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in here.rglob('*') if p.is_file() and '__pycache__' not in p.parts
    }
    provenance['binary_sha256']=command(['docker','run','--rm','--network','none',image_id,
        'sha256sum',*['/opt/coverage/'+cfg+'/coverage/'+name for cfg in manifest['configs']
                       for name in [c['id'] for c in manifest['cases']]+['negative','fixture_prepare']],
        '/opt/coverage/helper'])
    (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    records=[]
    for index,item in enumerate(plan):
        dest=args.output/f"{index:04d}-{item['config']}-{item['case']['id']}"
        try:
            record=execute(item['case'],item['config'],dest,image_id,args.functional_only)
        except Exception as error:
            dest.mkdir(parents=True,exist_ok=True)
            record={'case':item['case']['id'],'config':item['config'],'valid':False,
                    'behavior_ok':False,'error':str(error),'control':bool(item['case'].get('control'))}
            (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        record['repetition']=item['repetition'];records.append(record)
        print(json.dumps(record),flush=True)
    qualified={r['target_rule'] for r in records if r.get('valid') and r.get('target_fired')}
    positives={(r['case'],r['config']) for r in records if r.get('valid') and r.get('target_fired')}
    controls={(r['case'],r['config']) for r in records if r.get('valid') and r.get('control') and r.get('negative_control_ok')}
    paired=sorted(positives & controls)
    summary={'executions':len(records),'valid':sum(r['valid'] for r in records),
             'behavior_successes':sum(r['behavior_ok'] for r in records),
             'qualified_rules':len(qualified),'qualified_rule_names':sorted(qualified),
             'negative_controls_pass':all(r.get('valid') and r.get('negative_control_ok') for r in records if r['case']=='negative' or r.get('control')),
             'qualified_case_configurations':len(paired),'paired_qualification':paired,
             'functional_only':args.functional_only,'records':records}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))
    if args.functional_only:
        return 0 if all(r['behavior_ok'] for r in records) else 1
    return 0 if all(r['valid'] for r in records) and summary['negative_controls_pass'] and len(paired)==len(target_cases)*len(manifest['configs']) else 1

if __name__ == '__main__':
    raise SystemExit(main())
