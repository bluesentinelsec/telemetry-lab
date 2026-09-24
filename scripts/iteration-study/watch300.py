"""Normalize verified Linux archives, audit exact execution coverage, then analyze."""
import json,subprocess,sys,time
from orchestrate300 import BASE,ROOT

seen={}
while True:
 receipts=sorted((BASE/'archives').glob('H??-linux-verified.json')) if (BASE/'archives').exists() else []
 new=[p for p in receipts if seen.get(p.name)!=json.loads(p.read_text())['sha256']]
 if new:
  subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/normalize.py'),str(BASE)],check=True)
  seen.update((p.name,json.loads(p.read_text())['sha256']) for p in new)
  print('NORMALIZED_ARCHIVES',len(seen),flush=True)
 if len(seen)==20:
  records=[json.loads(p.read_text()) for p in (BASE/'normalized').glob('H??-linux-verification.json')]
  if len(records)!=20 or not all(r['primitive_count']==3224 and r['composite_count']==15128 for r in records):
   raise RuntimeError('Incomplete collection: preserve archives and reconcile unexecuted slots')
  break
 time.sleep(30)
(BASE/'analysis').mkdir(exist_ok=True)
for name in ('audit.py','provenance.py','analyze.py','diagnostics.py','composite_diagnostics.py','plateau.py','dependence300.py','report300.py'):
 subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study'/name),str(BASE)],check=True)
audit=json.loads((BASE/'analysis/slot-audit.json').read_text())
assert audit['expected_slots']==audit['physical_records']==audit['unique_recorded_slots']==367040
assert not any(audit[k] for k in ('missing','unexpected','duplicates','duplicate_container_ids','unlaunched_slots'))
assert audit['native_attempt_states'].get('completed')==302560,audit['native_attempt_states']
subprocess.run(['/tmp/telemetry-pilot-analysis-venv/bin/python',str(ROOT/'scripts/iteration-study/plot300.py'),str(BASE)],check=True)
(BASE/'ANALYSIS300_READY').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())+'\n')
print('ANALYSIS300_READY',flush=True)
