"""Normalize completed, verified archives and produce analysis when all hosts finish."""
import json,subprocess,sys,time
from pathlib import Path
from orchestrate import BASE,ROOT,write
seen=set()
while True:
 receipts=sorted((BASE/'archives').glob('H??-*-verified.json')) if (BASE/'archives').exists() else []
 new=[p for p in receipts if p.name not in seen]
 if new:
  result=subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/normalize.py'),str(BASE)])
  if result.returncode:raise SystemExit(result.returncode)
  seen.update(p.name for p in new)
  print('NORMALIZED_ARCHIVES',len(seen),flush=True)
 if len(seen)==20:break
 time.sleep(30)
subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/analyze.py'),str(BASE)],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/audit.py'),str(BASE)],check=True)
subprocess.run(['/tmp/telemetry-pilot-analysis-venv/bin/python',str(ROOT/'scripts/iteration-study/plot.py'),str(BASE)],check=True)
print('ANALYSIS_READY',flush=True)
