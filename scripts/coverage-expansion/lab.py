#!/usr/bin/env python3
"""Stage CI-built composites and run frozen, retry-enabled CDK lab campaigns.

Deployment remains the existing lab-environment CDK app. All remote requests,
source archives, CI run metadata and results are retained under --evidence.
"""
import argparse,hashlib,json,subprocess,tarfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def call(argv):return subprocess.check_output(argv,text=True,timeout=900)
def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('action',choices=['stage','status','run','collect','refresh'])
 p.add_argument('--evidence',type=Path,required=True);p.add_argument('--outputs',type=Path,required=True);p.add_argument('--stack',required=True)
 p.add_argument('--ci-run');p.add_argument('--falco-archive',type=Path);p.add_argument('--os',choices=['linux','windows'],required=True)
 p.add_argument('--phase',default='qualification');p.add_argument('--repetitions',type=int,default=3);p.add_argument('--case',action='append',dest='cases');p.add_argument('--config',action='append',dest='configs')
 a=p.parse_args();a.evidence.mkdir(parents=True,exist_ok=True)
 infra=json.loads(a.outputs.read_text())[a.stack];bucket=infra['DataBucketName'];host=infra['DebianInstanceId' if a.os=='linux' else 'WindowsInstanceId'];region=infra['Region']
 def aws(*args):return call(['aws','--region',region,*args])
 def send(script,phase):
  dest=a.evidence/a.os/phase;dest.mkdir(parents=True,exist_ok=True)
  if (dest/'command.json').exists():raise ValueError('Phase already submitted; choose a new phase')
  (dest/('script.sh' if a.os=='linux' else 'script.ps1')).write_text(script)
  req=dict(InstanceIds=[host],DocumentName='AWS-RunShellScript' if a.os=='linux' else 'AWS-RunPowerShellScript',Parameters={'commands':[script],'executionTimeout':['14400']},OutputS3BucketName=bucket,OutputS3KeyPrefix=f'ssm/{a.os}/{phase}')
  (dest/'request.json').write_text(json.dumps(req,indent=2));result=json.loads(aws('ssm','send-command','--cli-input-json',json.dumps(req)));(dest/'command.json').write_text(json.dumps(result,indent=2));print(result['Command']['CommandId'])
 if a.action=='status':
  dest=a.evidence/a.os/a.phase;cmd=json.loads((dest/'command.json').read_text())['Command']['CommandId'];result=json.loads(aws('ssm','get-command-invocation','--command-id',cmd,'--instance-id',host));(dest/'status.json').write_text(json.dumps(result,indent=2));print(result['Status']);print(result.get('StandardOutputContent','')[-5000:]);print(result.get('StandardErrorContent','')[-1500:]);return
 if a.action=='collect':
  print(aws('s3','sync',f's3://{bucket}/results/{a.os}/',str(a.evidence/'raw'/a.os),'--only-show-errors'));print(aws('s3','sync',f's3://{bucket}/ssm/',str(a.evidence/'ssm'),'--only-show-errors'));return
 if a.action in ('stage','refresh'):
  if not a.ci_run: p.error('--ci-run required')
  artifact=a.evidence/'artifacts'/a.ci_run
  if len(list(artifact.glob('composite-'+a.os+'-*')))!=8:
   meta=json.loads(call(['gh','api',f'repos/bluesentinelsec/telemetry-lab/actions/runs/{a.ci_run}']));(a.evidence/f'ci-{a.ci_run}.json').write_text(json.dumps(meta,indent=2))
   artifact.mkdir(parents=True,exist_ok=True);call(['gh','run','download',a.ci_run,'--repo','bluesentinelsec/telemetry-lab','--pattern','composite-'+a.os+'-*','--dir',str(artifact)])
  stage=a.evidence/'stage'/a.os/a.phase;stage.mkdir(parents=True,exist_ok=False);bundle=stage/'bundle';bundle.mkdir()
  configs=[]
  for source in sorted(artifact.glob('composite-'+a.os+'-*')):
   config=source.name.removeprefix('composite-');configs.append(config);shutil.copytree(source,bundle/'ttp-composite'/config)
  if len(configs)!=8:raise ValueError('Require all eight CI configuration artifacts')
  shutil.copytree(ROOT/'ttp-composite'/a.os/'coverage',bundle/'ttp-composite/coverage',ignore=shutil.ignore_patterns('__pycache__','validation'))
  (bundle/'manifest.json').write_text(json.dumps(dict(os=a.os,composite_configs=configs,ci_run=a.ci_run),indent=2))
  (bundle/'files.sha256.json').write_text(json.dumps({f.relative_to(bundle).as_posix():digest(f) for f in bundle.rglob('*') if f.is_file()},indent=2))
  shutil.copytree(ROOT/'scripts/experiment',stage/'scripts/experiment',ignore=shutil.ignore_patterns('__pycache__'))
  with tarfile.open(stage/'payload.tgz','w:gz') as tar:
   tar.add(bundle,arcname='bundle');tar.add(stage/'scripts',arcname='scripts')
  prefix=f'stage/{a.os}/{a.phase}'
  aws('s3','cp',str(stage/'payload.tgz'),f's3://{bucket}/{prefix}/payload.tgz','--only-show-errors')
  receipt={'payload_sha256':digest(stage/'payload.tgz'),'ci_run':a.ci_run,'source_head':call(['git','-C',str(ROOT),'rev-parse','HEAD']).strip()}
  if a.os=='linux':
   if not a.falco_archive:p.error('--falco-archive required for Linux staging')
   receipt['falco_sha256']=digest(a.falco_archive);aws('s3','cp',str(a.falco_archive),f's3://{bucket}/{prefix}/falco.tgz','--only-show-errors')
  (stage/'receipt.json').write_text(json.dumps(receipt,indent=2))
  template=(ROOT/'scripts/coverage-expansion'/('stage-linux.sh' if a.os=='linux' else 'stage-windows.ps1')).read_text()
  script=template.replace('@BUCKET@',bucket).replace('@PREFIX@',prefix).replace('@PAYLOAD_SHA@',receipt['payload_sha256']).replace('@FALCO_SHA@',receipt.get('falco_sha256',''))
  send(script,a.phase);return
 if a.action=='run':
  if a.repetitions<1:p.error('positive repetitions required')
  # Only known catalog values may enter the remote command line.
  catalog=json.loads((ROOT/'ttp-composite'/a.os/'coverage'/('manifest.json' if a.os=='linux' else 'selection.json')).read_text())
  known={x['id'] for x in catalog['cases']}|{'negative'} if a.os=='linux' else {x['case_id'] for x in catalog['candidates']}
  if a.cases and not set(a.cases)<=known:p.error('Unknown cases')
  configs=json.loads((a.evidence/'stage'/a.os/'stage'/'bundle/manifest.json').read_text())['composite_configs']
  if a.configs and not set(a.configs)<=set(configs):p.error('Unknown configurations')
  extra=' '.join('--case '+x for x in a.cases or [])+' '+' '.join('--config '+x for x in a.configs or [])
  if not all(c.isalnum() or c in '-_' for c in a.phase):p.error('Unsafe phase name')
  if a.os=='linux':
   script=f'''set -eu
cd /opt/coverage-expansion
trap 'aws s3 sync evidence s3://{bucket}/results/linux/ --only-show-errors' EXIT
python3 scripts/experiment/run.py bundle evidence/{a.phase} --cohort composites --repetitions {a.repetitions} --batch-size 16 {extra} > evidence/{a.phase}.log 2>&1
'''
  else:
   script=f'''$ErrorActionPreference='Stop'
Set-Location C:\\lab\\coverage-expansion
try {{
 & C:\\lab\\python\\python.exe scripts/experiment/run.py bundle evidence/{a.phase} --cohort composites --repetitions {a.repetitions} --batch-size 48 {extra} > evidence/{a.phase}.log 2>&1
 if($LASTEXITCODE){{throw 'Campaign incomplete; inspect preserved evidence'}}
}} finally {{ & 'C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe' s3 sync evidence s3://{bucket}/results/windows/ --only-show-errors }}
'''
  send(script,a.phase)
if __name__=='__main__':main()
