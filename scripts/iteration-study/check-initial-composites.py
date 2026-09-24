"""Read-only attribution check of each Windows host's first completed batch."""
import concurrent.futures,contextlib,io,json,subprocess,sys
from pathlib import Path
from orchestrate import BASE,ssm,aws,write
import normalize
D=BASE/'initial-composite-check';D.mkdir(exist_ok=True)
fleet=[x for x in json.loads((BASE/'fleet.json').read_text()) if x['os']=='windows']
def one(x):
 h=x['host'];bucket=x['bucket']
 script=f'''$p='C:\\lab\\pilot';$campaigns=Get-Content "$p\\evidence\\composites\\campaigns.json" -Raw | ConvertFrom-Json
$batch=@($campaigns)[0].campaign
if(!$batch -or $batch -notmatch '^01-windows-[a-z0-9-]+$'){{throw 'No unambiguous first batch'}}
& tar.exe -cf "$p\\first-composite.tar" -C "$p\\evidence\\composites" $batch
if($LASTEXITCODE){{throw 'Archive failed'}}
(Get-FileHash "$p\\first-composite.tar").Hash.ToLower() | Set-Content "$p\\first-composite.sha256" -Encoding ASCII
$aws='C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe'
& $aws s3 cp "$p\\first-composite.tar" s3://{bucket}/initial-composite-check/{h}.tar --only-show-errors
if($LASTEXITCODE){{throw 'Upload failed'}}
& $aws s3 cp "$p\\first-composite.sha256" s3://{bucket}/initial-composite-check/{h}.sha256 --only-show-errors
if($LASTEXITCODE){{throw 'Hash upload failed'}}
'''
 ssm(h,'windows',x['instance'],bucket,'first-composite-check',script)
 for suffix in ['tar','sha256']:aws('s3','cp',f's3://{bucket}/initial-composite-check/{h}.{suffix}',str(D/f'{h}.{suffix}'),'--only-show-errors')
 assert normalize.sha(D/f'{h}.tar')==(D/f'{h}.sha256').read_text().split()[0].lower()
 dest=D/h;dest.mkdir(exist_ok=True);subprocess.run(['tar','-xf',str(D/f'{h}.tar'),'-C',str(dest)],check=True)
 batch=next(dest.glob('01-*'))
 with contextlib.redirect_stdout(io.StringIO()):result=normalize.wc.analyze(batch)
 write(D/f'{h}-result.json',dict(host=h,campaign=batch.name,**result));print(h,batch.name,result['counts'],flush=True)
with concurrent.futures.ThreadPoolExecutor(2) as pool:list(pool.map(one,fleet))
