"""Normalize completed, verified archives and produce analysis when all hosts finish."""
import json,subprocess,sys,time
from pathlib import Path
from orchestrate import BASE,ROOT,write
seen={}
while True:
 receipts=sorted((BASE/'archives').glob('H??-*-verified.json')) if (BASE/'archives').exists() else []
 new=[p for p in receipts if seen.get(p.name)!=json.loads(p.read_text())['sha256']]
 if new:
  result=subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/normalize.py'),str(BASE)])
  if result.returncode:raise SystemExit(result.returncode)
  seen.update((p.name,json.loads(p.read_text())['sha256']) for p in new)
  print('NORMALIZED_ARCHIVES',len(seen),flush=True)
 if len(seen)==20:
  records=[json.loads(p.read_text()) for p in (BASE/'normalized').glob('H??-*-verification.json')]
  if len(records)==20 and all(r['primitive_count']==(2184 if r['os']=='linux' else 378) and r['composite_count']==(10248 if r['os']=='linux' else 7728) for r in records):break
 time.sleep(30)
subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/analyze.py'),str(BASE)],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/audit.py'),str(BASE)],check=True)
subprocess.run(['/tmp/telemetry-pilot-analysis-venv/bin/python',str(ROOT/'scripts/iteration-study/plot.py'),str(BASE)],check=True)
print('ANALYSIS_READY',flush=True)
