"""Read completed primitive data while composite measurements continue; no test reruns."""
import concurrent.futures,hashlib,json,subprocess,sys,tarfile,tempfile
from pathlib import Path
from orchestrate import BASE,ROOT,ssm,aws,write
import normalize
EARLY=BASE/'primitive-analysis';EARLY.mkdir(exist_ok=True);(EARLY/'normalized').mkdir(exist_ok=True)
(EARLY/'allocation.json').write_bytes((BASE/'allocation.json').read_bytes())
fleet=json.loads((BASE/'fleet.json').read_text())
def one(x):
 h,os,instance,bucket=x['host'],x['os'],x['instance'],x['bucket'];key=f'primitive-snapshots/{h}-{os}.tar'
 if os=='linux':
  script=f'''set -eu
cd /opt/pilot/evidence
test -f primitives/results.json
python3 -c 'import json; assert len(json.load(open("primitives/results.json")))==2184'
tar -cf ../primitives-snapshot.tar primitives inventory.json collection-started.txt
cd ..
sha256sum primitives-snapshot.tar > primitives-snapshot.tar.sha256
aws s3 cp primitives-snapshot.tar s3://{bucket}/{key} --only-show-errors
aws s3 cp primitives-snapshot.tar.sha256 s3://{bucket}/{key}.sha256 --only-show-errors
'''
 else:
  script=f'''$p='C:\\lab\\pilot';$rows=Get-Content "$p\\evidence\\primitives\\results.json" -Raw | ConvertFrom-Json
if($rows.Count -ne 378 -or !(Test-Path "$p\\evidence\\composites\\plan.json")){{throw 'Primitive collection incomplete'}}
& tar.exe -cf "$p\\primitives-snapshot.tar" -C "$p\\evidence" primitives inventory.json collection-started.txt
if($LASTEXITCODE){{throw 'Snapshot failed'}}
(Get-FileHash "$p\\primitives-snapshot.tar").Hash.ToLower() | Set-Content "$p\\primitives-snapshot.tar.sha256" -Encoding ASCII
$aws='C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe'
& $aws s3 cp "$p\\primitives-snapshot.tar" s3://{bucket}/{key} --only-show-errors
if($LASTEXITCODE){{throw 'Snapshot upload failed'}}
& $aws s3 cp "$p\\primitives-snapshot.tar.sha256" s3://{bucket}/{key}.sha256 --only-show-errors
if($LASTEXITCODE){{throw 'Digest upload failed'}}
'''
 ssm(h,os,instance,bucket,'primitive-snapshot',script)
 # Two downloads at once limit local temporary disk space; raw originals remain on hosts.
 with tempfile.TemporaryDirectory(prefix=f'{h}-{os}-',dir=EARLY) as tmp:
  d=Path(tmp);archive=d/'snapshot.tar';digest=d/'snapshot.sha256'
  aws('s3','cp',f's3://{bucket}/{key}',str(archive),'--only-show-errors');aws('s3','cp',f's3://{bucket}/{key}.sha256',str(digest),'--only-show-errors')
  actual=normalize.sha(archive);assert actual==digest.read_text().split()[0].lower()
  extract=d/'evidence';extract.mkdir();subprocess.run(['tar','-xf',str(archive),'-C',str(extract)],check=True)
  normalize.normalize(extract,h,os,EARLY/'normalized')
  write(EARLY/f'{h}-{os}-snapshot-verified.json',dict(sha256=actual,bytes=archive.stat().st_size,s3_key=key))
 print('PRIMITIVES_READY',h,os,flush=True)
with concurrent.futures.ThreadPoolExecutor(2) as pool:list(pool.map(one,fleet))
subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/analyze.py'),str(EARLY)],check=True)
subprocess.run(['/tmp/telemetry-pilot-analysis-venv/bin/python',str(ROOT/'scripts/iteration-study/plot.py'),str(EARLY)],check=True)
print('PRIMITIVE_ANALYSIS_READY',flush=True)
