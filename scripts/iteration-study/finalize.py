"""Audit and archive completed study, then destroy only its disposable stack.

May be launched while collection runs. Destruction is gated on twenty verified
archives, complete normalization, exact slot accounting and provenance checks.
"""
import hashlib,json,subprocess,sys,time
from pathlib import Path
from orchestrate import BASE,ROOT,STACK,aws,write
BUCKET='iterationstudy20260923-labdata46f5603f-jud5kcetktyy'
def run(args,**kwargs):
 print('RUN',args,flush=True);subprocess.run(args,check=True,**kwargs)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
while True:
 log=BASE/'analysis-watch.log'
 if log.exists() and 'ANALYSIS_READY' in log.read_text():break
 time.sleep(30)
assert len(list((BASE/'archives').glob('H??-*-verified.json')))==20
assert len(list((BASE/'normalized').glob('H??-*-verification.json')))==20
for name in ('audit.py','provenance.py','diagnostics.py','composite_diagnostics.py','render.py'):
 run([sys.executable,str(ROOT/'scripts/iteration-study'/name),str(BASE)])
audit=json.loads((BASE/'analysis/slot-audit.json').read_text())
assert audit['expected_slots']==audit['physical_records']==audit['unique_recorded_slots']==205380
assert not any(audit[k] for k in ('missing','unexpected','duplicates','duplicate_container_ids'))
# Confirm the early primitive report and final archives describe the same executions.
verified=0
for early in (BASE/'primitive-analysis/normalized').glob('*-primitives.jsonl'):
 def index(p):
  return {(r['host'],r['case'],r['config'],r['repetition']):(r['raw_sha256'],r['event_counts']) for line in p.read_text().splitlines() if (r:=json.loads(line))}
 x=index(early);y=index(BASE/'normalized'/early.name);assert x==y,early.name;verified+=len(x)
assert verified==25620
write(BASE/'analysis/early-final-primitive-verification.json',dict(matching_records=verified))
for receipt in (BASE/'archives').glob('H??-*-verified.json'):
 r=json.loads(receipt.read_text());archive=receipt.with_name(receipt.name.replace('-verified.json','.tar.gz'));assert sha(archive)==r['sha256']
# Preserve service output and the exact infrastructure before S3 auto-deletion.
run(['aws','--region','us-west-2','s3','sync',f's3://{BUCKET}/ssm/',str(BASE/'ssm-full-output'),'--only-show-errors'])
for op in ('describe-stacks','list-stack-resources','get-template'):
 write(BASE/'cleanup'/f'{op}.json',json.loads(aws('cloudformation',op,'--stack-name',STACK)))
fleet=json.loads((BASE/'fleet.json').read_text());ids=[r['instance'] for r in fleet]
write(BASE/'cleanup/instances-before.json',json.loads(aws('ec2','describe-instances','--instance-ids',*ids)))
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
run(['git','archive','--format=tar.gz',f'--output={BASE}/inputs/analysis-source-{commit[:8]}.tar.gz',commit],cwd=ROOT)
write(BASE/'analysis-source.json',dict(commit=commit,branch='research/iteration-threshold-study'))
files=list((BASE/'archives').glob('*'))+list((BASE/'inputs').glob('*'))
write(BASE/'final-evidence-sha256.json',{str(p.relative_to(BASE)):sha(p) for p in files if p.is_file()})
write(BASE/'cleanup/ready.json',dict(verified_archives=20,accounted_executions=205380,stack=STACK,time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
with (BASE/'cleanup/destroy.log').open('w') as f:
 run(['npx','cdk','destroy','-c',f'stackName={STACK}','-c','hostPairs=10','--force'],cwd=ROOT/'lab-environment',stdout=f,stderr=subprocess.STDOUT)
# EC2 termination can finish shortly after CloudFormation deletes the stack.
for _ in range(30):
 state=json.loads(aws('ec2','describe-instances','--instance-ids',*ids))
 instances=[x for r in state['Reservations'] for x in r['Instances']]
 if len(instances)==20 and all(x['State']['Name']=='terminated' for x in instances):break
 time.sleep(10)
else:raise RuntimeError('Some study instances have not terminated')
write(BASE/'cleanup/instances-after.json',state)
write(BASE/'cleanup/stack-history.json',json.loads(aws('cloudformation','list-stacks','--stack-status-filter','DELETE_COMPLETE')))
write(BASE/'cleanup/complete.json',dict(stack=STACK,terminated_instances=ids,time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
print('STUDY_ARCHIVED_AND_DESTROYED',flush=True)
