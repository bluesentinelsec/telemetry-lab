"""Archive/audit the Linux study and destroy its disposable infrastructure only.

Run after analysis review. Invalid measurements remain in the evidence; completion
means every planned native attempt is accounted for, not every detection passed.
"""
import hashlib,json,subprocess,sys,time
from orchestrate300 import BASE,ROOT,STACK,aws,write

def run(args,**kwargs):
 print('RUN',args,flush=True);subprocess.run(args,check=True,**kwargs)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

assert (BASE/'ANALYSIS300_READY').exists()
assert (BASE/'ANALYSIS_REVIEWED').exists(),'Review results before finalization'
fleet=json.loads((BASE/'fleet.json').read_text());ids=[r['instance'] for r in fleet]
assert len(set(ids))==20 and all(r['os']=='linux' for r in fleet)
buckets={r['bucket'] for r in fleet};assert len(buckets)==1;bucket=buckets.pop()
assert len(list((BASE/'archives').glob('H??-linux-verified.json')))==20
assert len(list((BASE/'normalized').glob('H??-linux-verification.json')))==20
for name in ('audit.py','provenance.py'):
 run([sys.executable,str(ROOT/'scripts/iteration-study'/name),str(BASE)])
audit=json.loads((BASE/'analysis/slot-audit.json').read_text())
assert audit['expected_slots']==audit['physical_records']==audit['unique_recorded_slots']==367040
assert not any(audit[k] for k in ('missing','unexpected','duplicates','duplicate_container_ids','unlaunched_slots'))
assert audit['native_attempt_states']=={'completed':302560}
verified=0
for early in (BASE/'primitive-analysis/normalized').glob('*-primitives.jsonl'):
 def index(p):
  return {(r['host'],r['case'],r['config'],r['repetition']):(r['raw_sha256'],r['event_counts']) for line in p.read_text().splitlines() if (r:=json.loads(line))}
 x=index(early);y=index(BASE/'normalized'/early.name);assert x==y,early.name;verified+=len(x)
if (BASE/'primitive-analysis/ANALYSIS300_READY').exists():assert verified==64480
write(BASE/'analysis/early-final-primitive-verification.json',dict(matching_records=verified))
for receipt in (BASE/'archives').glob('H??-linux-verified.json'):
 r=json.loads(receipt.read_text());archive=receipt.with_name(receipt.name.replace('-verified.json','.tar.gz'))
 assert sha(archive)==r['sha256']
 remote=aws('s3','cp',f's3://{bucket}/archives/{archive.name}.sha256','-','--only-show-errors').split()[0].lower()
 assert remote==r['sha256']
run([sys.executable,str(ROOT/'scripts/iteration-study/postflight300.py')])
run(['aws','--region','us-west-2','s3','sync',f's3://{bucket}/ssm/',str(BASE/'ssm-full-output'),'--only-show-errors'])
for op in ('describe-stacks','list-stack-resources','get-template'):
 write(BASE/'cleanup'/f'{op}.json',json.loads(aws('cloudformation',op,'--stack-name',STACK)))
resources=json.loads((BASE/'cleanup/list-stack-resources.json').read_text())['StackResourceSummaries']
assert {x['PhysicalResourceId'] for x in resources if x['ResourceType']=='AWS::EC2::Instance'}==set(ids)
before=json.loads(aws('ec2','describe-instances','--instance-ids',*ids));write(BASE/'cleanup/instances-before.json',before)
volumes=[m['Ebs']['VolumeId'] for r in before['Reservations'] for i in r['Instances'] for m in i['BlockDeviceMappings'] if 'Ebs' in m]
assert len(volumes)==20
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),'Commit final source before archival'
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
run(['git','archive','--format=tar.gz',f'--output={BASE}/inputs/analysis-source-{commit[:8]}.tar.gz',commit],cwd=ROOT)
write(BASE/'analysis-source.json',dict(commit=commit,branch='research/linux-300-iterations'))
write(BASE/'final-evidence-sha256.json',{str(p.relative_to(BASE)):sha(p) for folder in ('archives','inputs') for p in (BASE/folder).glob('*') if p.is_file()})
write(BASE/'cleanup/ready.json',dict(verified_archives=20,accounted_executions=367040,stack=STACK,time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
with (BASE/'cleanup/destroy.log').open('w') as f:
 run(['npx','cdk','destroy','-c',f'stackName={STACK}','-c','linuxOnly=true','-c','hostPairs=20','-c','debianAmiId=ami-0c605b75e3a75e872','-c','availabilityZones=us-west-2b,us-west-2c','--force'],cwd=ROOT/'lab-environment',stdout=f,stderr=subprocess.STDOUT)
for _ in range(30):
 state=json.loads(aws('ec2','describe-instances','--instance-ids',*ids))
 instances=[x for r in state['Reservations'] for x in r['Instances']]
 if len(instances)==20 and all(x['State']['Name']=='terminated' for x in instances):break
 time.sleep(10)
else:raise RuntimeError('Some study instances have not terminated')
write(BASE/'cleanup/instances-after.json',state)
for _ in range(30):
 remaining=json.loads(aws('ec2','describe-volumes','--filters',json.dumps([dict(Name='volume-id',Values=volumes)])))
 if not remaining['Volumes']:break
 time.sleep(10)
else:raise RuntimeError('Study volumes remain')
write(BASE/'cleanup/volumes-after.json',remaining)
history=json.loads(aws('cloudformation','list-stacks','--stack-status-filter','DELETE_COMPLETE'))
stack_id=json.loads((BASE/'cleanup/describe-stacks.json').read_text())['Stacks'][0]['StackId']
assert any(s['StackId']==stack_id and s['StackName']==STACK for s in history['StackSummaries'])
write(BASE/'cleanup/stack-history.json',history)
write(BASE/'cleanup/complete.json',dict(stack=STACK,terminated_instances=ids,deleted_volumes=volumes,time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
print('STUDY300_ARCHIVED_AND_DESTROYED',flush=True)
