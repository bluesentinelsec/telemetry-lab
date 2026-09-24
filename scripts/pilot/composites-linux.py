#!/usr/bin/env python3
"""Batched Falco collection with fresh per-execution containers and strict group health.

Only collector draining is amortized. Each program still has its own container,
behavior result and event-time boundary. A health failure invalidates the entire
batch; no counter is ignored. Containers remain alive until delivery is drained.
"""
import argparse, datetime, hashlib, json, random, re, subprocess, sys, time, uuid
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
p.add_argument('--image',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--host-id',required=True)
p.add_argument('--repetitions',type=int,default=10);p.add_argument('--batch-size',type=int,default=16)
p.add_argument('--case',action='append',dest='cases')
p.add_argument('--resume',action='store_true',help='Resume only unexecuted slots after reconciling preserved prior attempts')
a=p.parse_args();sys.path.insert(0,str(a.bundle/'ttp-composite/coverage'))
import run as cov
m=cov.validate();selected={c['rule'] for c in m['cases']};cases=[c for c in m['cases'] if not a.cases or c['id'] in a.cases]
if a.cases and set(a.cases)-{c['id'] for c in cases}:raise SystemExit('Unknown case')
a.output.mkdir(parents=True,exist_ok=a.resume);rng=random.Random(a.seed);plan=[]
for rep in range(1,a.repetitions+1):
 block=[dict(config=cfg,case=c,repetition=rep) for cfg in m['configs'] for c in cases+[{**c,'control':True} for c in cases]+[{'id':'negative'}]]
 rng.shuffle(block);plan+=block
image_id=cov.command(['docker','image','inspect',a.image,'--format','{{.Id}}'])
provenance=dict(seed=a.seed,host=a.host_id,plan=plan,batch_size=a.batch_size,image_id=image_id,falco=cov.detector_provenance(),
 rules_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (a.bundle/'ttp-composite/coverage/rules').glob('*.yaml')},
 binaries=cov.command(['docker','run','--rm','--network','none',image_id,'sha256sum',*['/opt/coverage/'+cfg+'/coverage/'+c for cfg in m['configs'] for c in [x['id'] for x in cases]+['negative','fixture_prepare']]]))
rows=[]
if a.resume:
 assert json.loads((a.output/'provenance.json').read_text())==provenance,'Frozen provenance changed'
 rows=[json.loads(line) for line in (a.output/'results.jsonl').read_text().splitlines()]
 assert len(rows)%a.batch_size==0 and len(rows)<len(plan),'Resume requires reconciled complete batch boundaries'
 for row,item in zip(rows,plan):
  assert (row['config'],row['case'],row['control'],row['repetition'])==(item['config'],item['case']['id'],bool(item['case'].get('control')),item['repetition'])
 (a.output/f'resume-provenance-{len(rows):05d}.json').write_text(json.dumps(dict(resume_offset=len(rows),provenance=provenance),indent=2)+'\n')
else:(a.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
def time_ns(event):
 value=event['time'];match=re.fullmatch(r'(.*?)(?:\.(\d+))?Z',value)
 if not match:raise ValueError('Unexpected Falco event time: '+value)
 return int(datetime.datetime.fromisoformat(match[1]+'+00:00').timestamp())*10**9+int((match[2] or '').ljust(9,'0')[:9])
for offset in range(len(rows),len(plan),a.batch_size):
 batch=plan[offset:offset+a.batch_size];folder=a.output/f'batch-{offset:05d}';folder.mkdir();containers=[];pending=[]
 time.sleep(1) # settle previous batch teardown before the strict group snapshot
 before=cov.detector_state();latest=cov.command(['journalctl','-u',cov.SERVICE,'-n','1','--show-cursor','--no-pager']);cursor=re.search(r'-- cursor: (.+)',latest).group(1)
 try:
  for index,item in enumerate(batch,offset):
   cfg,case=item['config'],item['case'];dest=folder/f'{index:05d}-{cfg}-{case["id"]}';dest.mkdir()
   cid=cov.command(['docker','create','--name','pilot-'+uuid.uuid4().hex[:16],'--network','none','--cap-add','SYS_PTRACE','--cap-add','NET_ADMIN','--security-opt','seccomp=unconfined','--tmpfs','/dev/shm:rw,exec,nosuid,size=16m',image_id]);containers.append(cid)
   row=dict(host=a.host_id,os='linux',config=cfg,case=case['id'],control=bool(case.get('control')),repetition=item['repetition'],target_rule=case.get('rule'),container_id=cid,valid=False)
   try:
    cov.command(['docker','start',cid])
    for address in ('169.254.169.254/32','198.18.0.1/32'):cov.command(['docker','exec',cid,'ip','addr','add',address,'dev','lo'])
    cov.command(['docker','exec',cid,f'/opt/coverage/{cfg}/coverage/fixture_prepare'])
    exe=f'/opt/coverage/{cfg}/coverage/{case["id"]}';row['started_ns']=time.time_ns()
    result=subprocess.run(['docker','exec',cid,exe]+(['--control'] if case.get('control') else []),capture_output=True,text=True,timeout=20)
    row.update(ended_ns=time.time_ns(),exit_code=result.returncode,executable=exe)
    (dest/'stdout.txt').write_text(result.stdout);(dest/'stderr.txt').write_text(result.stderr)
    pending.append((row,case,result,dest))
   except Exception as error:
    row['error']=str(error);pending.append((row,case,None,dest))
  time.sleep(3)
  after=cov.detector_state();healthy=cov.health_ok(before,after)
  log=cov.command(['journalctl','-u',cov.SERVICE,'--after-cursor',cursor,'-o','cat','--no-pager'])
  (folder/'journal.jsonl').write_text(log+'\n');(folder/'health.json').write_text(json.dumps(dict(before=before,after=after),indent=2)+'\n')
  for row,case,result,dest in pending:
   alerts=[e for e in cov.attributed_alerts(log,row['container_id']) if time_ns(e)>=row.get('started_ns',2**64)]
   (dest/'alerts.json').write_text(json.dumps(alerts,indent=2)+'\n')
   if result:row.update(cov.score(case,result,alerts,healthy,selected))
   else:row.update(behavior_ok=False,collection_ok=healthy)
   row['batch']=folder.name;(dest/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
   with (a.output/'results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(dict(host=a.host_id,completed=len(rows),planned=len(plan),valid=sum(r['valid'] for r in rows),last_batch_health=healthy)),flush=True)
 finally:
  for cid in containers:subprocess.run(['docker','rm','-f',cid],capture_output=True,timeout=30)
(a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(0 if cov.suite_ok(rows,{c['rule'] for c in cases}) else 1)
