#!/usr/bin/env python3
"""Resume-safe stage/run/archive driver. Never deletes infrastructure."""
import concurrent.futures,hashlib,json,subprocess,time,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('/Users/michaellong/telemetry-lab-data/iteration-study-2026-09-23')
OLD=Path('/Users/michaellong/telemetry-lab-data/repeatability-pilot-2026-09-23/inputs')
STACK='IterationStudy20260923'

def aws(*args):
 p=subprocess.run(['aws','--region','us-west-2',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout

def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(v,indent=2));q.replace(p)

def ssm(host,os,instance,bucket,phase,script):
 d=BASE/'ssm'/f'{host}-{os}-{phase}';d.mkdir(parents=True,exist_ok=True)
 (d/('script.ps1' if os=='windows' else 'script.sh')).write_text(script)
 meta=d/'command.json'
 if meta.exists():cmd=json.loads(meta.read_text())['Command']['CommandId']
 else:
  args=dict(InstanceIds=[instance],DocumentName='AWS-RunPowerShellScript' if os=='windows' else 'AWS-RunShellScript',Parameters={'commands':[("$ErrorActionPreference='Stop'\n" if os=='windows' else '')+script],'executionTimeout':['172800']},OutputS3BucketName=bucket,OutputS3KeyPrefix=f'ssm/{host}/{os}/{phase}')
  result=json.loads(aws('ssm','send-command','--cli-input-json',json.dumps(args)));write(meta,result);cmd=result['Command']['CommandId']
  print(host,os,phase,cmd,flush=True)
 while True:
  try:state=json.loads(aws('ssm','get-command-invocation','--command-id',cmd,'--instance-id',instance))
  except RuntimeError:time.sleep(10);continue
  write(d/'status.json',state)
  if state['Status'] not in ('Pending','InProgress','Delayed'):break
  time.sleep(20)
 print(host,os,phase,state['Status'],flush=True)
 if state['Status']!='Success':raise RuntimeError(f'{host} {os} {phase}: {state}')
 return state

def one(host,os,instance,bucket,index):
 # Wait for registration and completed Windows bootstrap/reboot, without executing tests.
 start=time.time();attempt=0
 while True:
  infos=json.loads(aws('ssm','describe-instance-information','--filters',json.dumps([dict(Key='InstanceIds',Values=[instance])])) )['InstanceInformationList']
  if infos and infos[0]['PingStatus']=='Online':
   if os=='linux':break
   attempt+=1
   try:
    ssm(host,os,instance,bucket,f'ready-{attempt}',"if(!(Test-Path C:\\lab\\inventory.json) -or (Get-WindowsFeature Windows-Defender).Installed -or (Get-Process MsMpEng -ErrorAction SilentlyContinue)){throw 'Bootstrap not finished'}\nGet-Service Sysmon64")
    break
   except RuntimeError:pass
  if time.time()-start>3600:raise RuntimeError('Host readiness timed out '+host+os)
  time.sleep(30)
 template=(BASE/f'stage-{os}-template.txt').read_text().replace('BUCKET',bucket)
 ssm(host,os,instance,bucket,'stage',template)
 if os=='linux':
  run=f'''set -eu
cd /opt/pilot
aws s3 cp s3://{bucket}/stage/frozen-image.tar.gz frozen-image.tar.gz --only-show-errors
aws s3 cp s3://{bucket}/stage/frozen-image.sha256 frozen-image.sha256 --only-show-errors
sha256sum -c frozen-image.sha256
gunzip -c frozen-image.tar.gz | docker load
docker image inspect lab-falco-coverage:pilot > evidence/container-image.json
date -u +%FT%TZ > evidence/collection-started.txt
set +e
python3 -u scripts/pilot/primitives.py /opt/pilot/telemetry-lab-0.3.0-linux /opt/pilot/evidence/primitives --repetitions 21 --seed {940000+index} --host-id {host} > evidence/primitives.log 2>&1
prim_status=$?
printf '%s\\n' "$prim_status" > evidence/primitives.exit
python3 -u scripts/pilot/composites-linux.py /opt/pilot/telemetry-lab-0.3.0-linux /opt/pilot/evidence/composites --image lab-falco-coverage:pilot --repetitions 21 --seed {950000+index} --host-id {host} > evidence/composites.log 2>&1
comp_status=$?
printf '%s\\n' "$comp_status" > evidence/composites.exit
set -e
date -u +%FT%TZ > evidence/collection-ended.txt
printf 'STUDY_FINISHED primitives=%s composites=%s\\n' "$prim_status" "$comp_status"
'''
  archive=f'''set -eu
cd /opt/pilot
tar -czf evidence-final.tar.gz -C evidence .
sha256sum evidence-final.tar.gz > evidence-final.tar.gz.sha256
aws s3 cp evidence-final.tar.gz s3://{bucket}/archives/{host}-linux.tar.gz --only-show-errors
aws s3 cp evidence-final.tar.gz.sha256 s3://{bucket}/archives/{host}-linux.tar.gz.sha256 --only-show-errors
'''
 else:
  run=f'''$base='C:\\lab\\pilot';$bundle="$base\\telemetry-lab-0.3.0-windows"
[DateTime]::UtcNow.ToString('o') | Set-Content "$base\\evidence\\collection-started.txt"
try {{ & "$base\\scripts\\pilot\\primitives.ps1" -Bundle $bundle -Output "$base\\evidence\\primitives" -Inventory "$base\\evidence\\inventory.json" -Repetitions 21 -Seed {940000+index} -HostId {host} *> "$base\\evidence\\primitives.log" }} catch {{$_ | Out-String | Set-Content "$base\\evidence\\primitives-error.txt"}}
try {{ & "$base\\scripts\\pilot\\composites-windows.ps1" -Bundle $bundle -Output "$base\\evidence\\composites" -Repetitions 21 -Seed {950000+index} -HostId {host} *> "$base\\evidence\\composites.log" }} catch {{$_ | Out-String | Set-Content "$base\\evidence\\composites-error.txt"}}
[DateTime]::UtcNow.ToString('o') | Set-Content "$base\\evidence\\collection-ended.txt"
Get-Content "$base\\evidence\\composites.log" -Tail 3
'''
  archive=f'''$base='C:\\lab\\pilot'
& tar.exe -czf "$base\\evidence-final.tar.gz" -C "$base\\evidence" .
if($LASTEXITCODE){{throw 'Archive creation failed'}}
(Get-FileHash "$base\\evidence-final.tar.gz").Hash.ToLower() | Set-Content "$base\\evidence-final.tar.gz.sha256" -Encoding ASCII
$aws='C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe'
& $aws s3 cp "$base\\evidence-final.tar.gz" s3://{bucket}/archives/{host}-windows.tar.gz --only-show-errors
if($LASTEXITCODE){{throw 'Archive upload failed'}}
& $aws s3 cp "$base\\evidence-final.tar.gz.sha256" s3://{bucket}/archives/{host}-windows.tar.gz.sha256 --only-show-errors
if($LASTEXITCODE){{throw 'Checksum upload failed'}}
'''
 ssm(host,os,instance,bucket,'run',run)
 ssm(host,os,instance,bucket,'archive',archive)
 dest=BASE/'archives';dest.mkdir(exist_ok=True)
 for suffix in ('.tar.gz','.tar.gz.sha256'):aws('s3','cp',f's3://{bucket}/archives/{host}-{os}{suffix}',str(dest/f'{host}-{os}{suffix}'),'--only-show-errors')
 file=dest/f'{host}-{os}.tar.gz';expected=(dest/f'{host}-{os}.tar.gz.sha256').read_text().split()[0].lower()
 with file.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 if actual!=expected:raise RuntimeError('Archive checksum mismatch')
 write(dest/f'{host}-{os}-verified.json',dict(host=host,os=os,sha256=actual,bytes=file.stat().st_size,instance=instance))
 print('VERIFIED',host,os,file.stat().st_size,flush=True)

if __name__=='__main__':
 while not (BASE/'stack.json').exists():time.sleep(10)
 stack=json.loads((BASE/'stack.json').read_text())[STACK];bucket=stack['DataBucketName']
 files=[(OLD/'telemetry-lab-0.3.0-linux.tar.gz','linux.tar.gz'),(OLD/'telemetry-lab-0.3.0-windows.zip','windows.zip'),(OLD/'pilot-falco.tgz','falco.tgz'),(OLD/'frozen-image.tar.gz','frozen-image.tar.gz'),(OLD/'frozen-image.sha256','frozen-image.sha256'),(BASE/'inputs/support.tgz','support.tgz')]
 for file,name in files:aws('s3','cp',str(file),f's3://{bucket}/stage/{name}','--only-show-errors')
 fleet=[]
 for i in range(1,11):
  suffix='' if i==1 else f'Pair{i:02}'
  for os,key in [('linux','DebianInstanceId'),('windows','WindowsInstanceId')]:fleet.append((f'H{i:02}',os,stack[key+suffix],bucket,i))
 write(BASE/'fleet.json',[dict(zip(('host','os','instance','bucket','index'),x)) for x in fleet])
 with concurrent.futures.ThreadPoolExecutor(20) as pool:
  futures={pool.submit(one,*x):x for x in fleet}
  errors=[]
  for f in concurrent.futures.as_completed(futures):
   try:f.result()
   except Exception as e:
    message=dict(host=futures[f][0],os=futures[f][1],error=str(e));errors.append(message);print('ERROR',message,flush=True);write(BASE/'orchestration-errors.json',errors)
 if errors:sys.exit(1)
 print('ALL 20 HOST ARCHIVES VERIFIED',flush=True)
