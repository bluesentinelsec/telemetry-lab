#!/usr/bin/env python3
"""Randomized blocked repetitions of immutable Linux primitive artifacts."""
import argparse, collections, hashlib, json, platform, random, subprocess, time
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
p.add_argument('--repetitions',type=int,default=10);p.add_argument('--seed',type=int,required=True);p.add_argument('--host-id',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);(a.output/'raw').mkdir()
m=json.loads((a.bundle/'manifest.json').read_text());rng=random.Random(a.seed)
plan=[]
for rep in range(1,a.repetitions+1):
 cells=[dict(config=cfg,case=case,repetition=rep) for cfg in m['configs'] for case in m['primitives']]
 rng.shuffle(cells);plan+=cells
(a.output/'plan.json').write_text(json.dumps(dict(seed=a.seed,host=a.host_id,plan=plan),indent=2)+'\n')
rows=[]
for index,cell in enumerate(plan):
 cfg,case,rep=cell['config'],cell['case'],cell['repetition'];exe=a.bundle/'ttp-primitives'/cfg/case
 raw=a.output/'raw'/f'{index:05d}-{cfg}-{case}.jsonl'
 cmd=[str(a.bundle/'tmon/tmon'),'--format','json','-o',str(raw)]
 for k,v in dict(os='linux',config=cfg,primitive=case,iteration=rep,host=a.host_id).items():cmd+=['--meta',f'{k}={v}']
 cmd+=['--',str(exe)];start=time.time();error=None
 try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);code=r.returncode;out=r.stdout;err=r.stderr
 except subprocess.TimeoutExpired as e:code=None;out=str(e.stdout);err=str(e.stderr);error='timeout'
 raw.with_suffix('.stdout').write_text(out);raw.with_suffix('.stderr').write_text(err)
 records=[json.loads(line) for line in raw.read_text().splitlines()] if raw.exists() else []
 summaries=[r for r in records if r.get('record')=='summary'];events=[r for r in records if r.get('record')=='event']
 good=code==0 and len(summaries)==1 and summaries[0]['target_exit_code']==0 and summaries[0]['dropped']==0 and summaries[0]['total_events']>0
 counts=collections.Counter((e.get('syscall','unknown') if e['kind']=='syscall' else '@'+e['kind']) for e in events)
 row=dict(**cell,host=a.host_id,os='linux',valid=good,exit_code=code,error=error,started_epoch=start,seconds=time.time()-start,
          binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),summary=summaries,event_counts=dict(counts),raw_events=len(events),raw=str(raw.relative_to(a.output)))
 rows.append(row)
 with (a.output/'results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps({k:row[k] for k in ('host','config','case','repetition','valid','seconds')}),flush=True)
(a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(0 if all(r['valid'] for r in rows) else 1)
