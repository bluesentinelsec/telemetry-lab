"""Analyze completed Linux composites while Windows continues; stop the final Linux host."""
import json,shutil,subprocess,sys,time
from orchestrate import BASE,ROOT,aws,write
while True:
 records=[json.loads(p.read_text()) for p in (BASE/'normalized').glob('H??-linux-verification.json')]
 if len(records)==10 and all(r['composite_count']==10248 for r in records):break
 time.sleep(30)
b=BASE/'linux-complete-analysis';(b/'normalized').mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'allocation.json',b/'allocation.json')
for p in list((BASE/'primitive-analysis/normalized').glob('*-primitives.jsonl'))+list((BASE/'normalized').glob('*-linux-composites.jsonl'))+list((BASE/'normalized').glob('*-linux-verification.json')):
 target=b/'normalized'/p.name
 if not target.exists():target.symlink_to(p)
for name in ('analyze.py','composite_diagnostics.py','provenance.py'):
 subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study'/name),str(b)],check=True)
counts=json.loads((b/'analysis/counts.json').read_text());assert counts['composite_attempts']==102480
x=next(x for x in json.loads((BASE/'fleet.json').read_text()) if x['host']=='H10' and x['os']=='linux')
write(BASE/'cleanup/H10-linux-stop-request.json',json.loads(aws('ec2','stop-instances','--instance-ids',x['instance'])))
print('LINUX_ANALYSIS_READY_AND_HOST_STOPPED',flush=True)
