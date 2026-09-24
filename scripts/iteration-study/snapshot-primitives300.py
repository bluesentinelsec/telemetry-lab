"""Snapshot completed primitives during composite collection, without rerunning tests."""
import concurrent.futures,json,subprocess,sys,tempfile,time
from pathlib import Path
from orchestrate300 import BASE,ROOT,ssm,aws,write
import normalize

EARLY=BASE/'primitive-analysis';EARLY.mkdir(exist_ok=True);(EARLY/'normalized').mkdir(exist_ok=True)
for name in ('allocation.json','study.json','PROTOCOL.md'):(EARLY/name).write_bytes((BASE/name).read_bytes())
fleet=json.loads((BASE/'fleet.json').read_text())
while True:
 progress=BASE/'live-summary.json'
 if progress.exists() and json.loads(progress.read_text())['counts']['linux_primitive_hosts_complete']==20:break
 time.sleep(30)

def one(x):
 h,instance,bucket=x['host'],x['instance'],x['bucket'];key=f'primitive-snapshots/{h}-linux.tar.gz'
 receipt=EARLY/f'{h}-linux-snapshot-verified.json'
 if receipt.exists():return
 script=f'''set -eu
cd /opt/pilot/evidence
python3 -c 'import json; assert len(json.load(open("primitives/results.json")))==3224'
tar -czf ../primitives-snapshot.tar.gz primitives inventory.json packages.txt collection-started.txt
cd ..
sha256sum primitives-snapshot.tar.gz > primitives-snapshot.tar.gz.sha256
aws s3 cp primitives-snapshot.tar.gz s3://{bucket}/{key} --only-show-errors
aws s3 cp primitives-snapshot.tar.gz.sha256 s3://{bucket}/{key}.sha256 --only-show-errors
'''
 ssm(h,'linux',instance,bucket,'primitive-snapshot300',script)
 with tempfile.TemporaryDirectory(prefix=f'{h}-',dir=EARLY) as tmp:
  d=Path(tmp);archive=d/'snapshot.tar.gz';digest=d/'snapshot.sha256'
  aws('s3','cp',f's3://{bucket}/{key}',str(archive),'--only-show-errors')
  aws('s3','cp',f's3://{bucket}/{key}.sha256',str(digest),'--only-show-errors')
  actual=normalize.sha(archive);assert actual==digest.read_text().split()[0].lower()
  extract=d/'evidence';extract.mkdir();subprocess.run(['tar','-xzf',str(archive),'-C',str(extract)],check=True)
  normalize.normalize(extract,h,'linux',EARLY/'normalized')
  write(receipt,dict(sha256=actual,bytes=archive.stat().st_size,s3_key=key))
 print('PRIMITIVES_READY',h,flush=True)

with concurrent.futures.ThreadPoolExecutor(2) as pool:list(pool.map(one,fleet))
for name in ('analyze.py','diagnostics.py','plateau.py','dependence300.py','report300.py'):
 subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study'/name),str(EARLY)],check=True)
subprocess.run(['/tmp/telemetry-pilot-analysis-venv/bin/python',str(ROOT/'scripts/iteration-study/plot300.py'),str(EARLY)],check=True)
(EARLY/'ANALYSIS300_READY').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())+'\n')
print('PRIMITIVE_ANALYSIS300_READY',flush=True)
