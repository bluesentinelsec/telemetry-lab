#!/usr/bin/env python3
"""Refresh source fixtures without rebuilding or changing any native CI executable.

Use only between campaigns. Captures original native hashes and verifies all
of them remotely before/after the refresh. The original payload and each small
refresh archive are retained, avoiding duplicate local native artifact copies.
"""
import argparse,hashlib,json,shutil,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--evidence',type=Path,required=True);p.add_argument('--outputs',type=Path,required=True);p.add_argument('--stack',required=True);p.add_argument('--phase',required=True)
a=p.parse_args();assert all(c.isalnum() or c in '-_' for c in a.phase)
i=json.loads(a.outputs.read_text())[a.stack];b=a.evidence
out=b/'fixture-refresh'/a.phase;out.mkdir(parents=True,exist_ok=False)
for name,source in [('coverage',ROOT/'ttp-composite/linux/coverage'),('experiment',ROOT/'scripts/experiment')]:
 shutil.copytree(source,out/name,ignore=shutil.ignore_patterns('__pycache__','validation'))
old=json.loads((b/'stage/linux/stage/bundle/files.sha256.json').read_text())
native={name:sha for name,sha in old.items() if name.startswith('ttp-composite/linux-')}
(out/'native-sha256.json').write_text(json.dumps(native,indent=2))
(out/'source-head.txt').write_text(subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True))
with tarfile.open(out/'patch.tgz','w:gz') as tar:
 for name in ['coverage','experiment','native-sha256.json','source-head.txt']:tar.add(out/name,arcname=name)
with (out/'patch.tgz').open('rb') as stream:
 sha=hashlib.file_digest(stream,'sha256').hexdigest()
prefix='fixture-refresh/'+a.phase
subprocess.run(['aws','--region',i['Region'],'s3','cp',str(out/'patch.tgz'),f"s3://{i['DataBucketName']}/{prefix}/patch.tgz",'--only-show-errors'],check=True)
script=f'''set -eu
exec 9>/tmp/telemetry-lab-experiment.lock
flock -n 9
cd /opt/coverage-expansion
mkdir -p refresh/{a.phase}
cd refresh/{a.phase}
aws s3 cp s3://{i['DataBucketName']}/{prefix}/patch.tgz patch.tgz --only-show-errors
printf '%s  patch.tgz\\n' '{sha}' | sha256sum -c -
tar xzf patch.tgz
cd /opt/coverage-expansion
python3 - <<'CHECK'
import json,hashlib,shutil
from pathlib import Path
r=Path('refresh/{a.phase}');bundle=Path('bundle')
expected=json.loads((r/'native-sha256.json').read_text())
for name,sha in expected.items():assert hashlib.sha256((bundle/name).read_bytes()).hexdigest()==sha,name
shutil.rmtree(bundle/'ttp-composite/coverage');shutil.copytree(r/'coverage',bundle/'ttp-composite/coverage')
shutil.rmtree('scripts/experiment');shutil.copytree(r/'experiment','scripts/experiment')
shutil.copy2(r/'coverage/Dockerfile','image/Dockerfile')
shutil.rmtree('image/fixtures');shutil.copytree(r/'coverage/fixtures','image/fixtures')
for name,sha in expected.items():assert hashlib.sha256((bundle/name).read_bytes()).hexdigest()==sha,name
(bundle/'files.sha256.json').write_text(json.dumps({{str(f.relative_to(bundle)):hashlib.sha256(f.read_bytes()).hexdigest() for f in bundle.rglob('*') if f.is_file() and f.name!='files.sha256.json' and '__pycache__' not in f.parts}},indent=2))
CHECK
docker build -t lab-falco-coverage:local image > evidence/{a.phase}-image.log 2>&1
FALCO_BIN=/opt/telemetry-lab/falco-0.45.0-healthfix.1/bin/falco bash bundle/ttp-composite/coverage/setup-detector.sh > evidence/{a.phase}-falco.log 2>&1
docker image inspect lab-falco-coverage:local > evidence/{a.phase}-image.json
docker run --rm --network none lab-falco-coverage:local dpkg-query -W > evidence/{a.phase}-packages.txt
docker run --rm --network none lab-falco-coverage:local sha256sum /usr/local/bin/bun > evidence/{a.phase}-bun.sha256
cp bundle/files.sha256.json evidence/{a.phase}-bundle-files.json
aws s3 sync evidence s3://{i['DataBucketName']}/results/linux/ --only-show-errors
'''
(out/'script.sh').write_text(script)
req=dict(InstanceIds=[i['DebianInstanceId']],DocumentName='AWS-RunShellScript',Parameters={'commands':[script],'executionTimeout':['7200']},OutputS3BucketName=i['DataBucketName'],OutputS3KeyPrefix='ssm/refresh/'+a.phase)
(out/'request.json').write_text(json.dumps(req,indent=2))
r=subprocess.check_output(['aws','--region',i['Region'],'ssm','send-command','--cli-input-json',json.dumps(req)],text=True)
(out/'command.json').write_text(r);print(json.loads(r)['Command']['CommandId'])
