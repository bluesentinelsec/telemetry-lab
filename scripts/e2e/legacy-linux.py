#!/usr/bin/env python3
"""Exercise the retained Linux pilot programs with container-attributed Falco evidence.

These pilot cases lack the independent behavior contracts of coverage/run.py;
exit success and observed alerts are reported without claiming qualification.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
p.add_argument('--image',default='lab-falco-coverage:release030')
p.add_argument('--config',action='append');p.add_argument('--case',action='append')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(a.bundle/'ttp-composite/coverage'))
import run as coverage
manifest=json.loads((a.bundle/'manifest.json').read_text());rows=[]
configs=a.config or manifest['composite_configs'];cases=a.case or manifest['composites']
if not set(configs)<=set(manifest['composite_configs']) or not set(cases)<=set(manifest['composites']):
 raise SystemExit('Unknown pilot configuration/case')
for config in configs:
 for case in cases:
  dest=a.output/f'{config}-{case}';dest.mkdir()
  exe=f'/opt/coverage/{config}/{case}'
  cid=coverage.command(['docker','create','--name','legacy-'+uuid.uuid4().hex[:12],'--network','none','--cap-add','SYS_PTRACE','--cap-add','NET_ADMIN','--security-opt','seccomp=unconfined',a.image])
  row=dict(config=config,case=case,container_id=cid,valid=False,
           binary_sha256=hashlib.sha256((a.bundle/'ttp-composite'/config/case).read_bytes()).hexdigest())
  try:
   coverage.command(['docker','start',cid])
   coverage.command(['docker','exec',cid,'ip','addr','add','169.254.169.254/32','dev','lo'])
   coverage.command(['docker','exec',cid,f'/opt/coverage/{config}/coverage/fixture_prepare'])
   time.sleep(2)
   before=coverage.detector_state()
   latest=coverage.command(['journalctl','-u',coverage.SERVICE,'-n','1','--show-cursor','--no-pager'])
   cursor=re.search(r'-- cursor: (.+)',latest).group(1)
   result=subprocess.run(['docker','exec',cid,exe],capture_output=True,text=True,timeout=30)
   time.sleep(3);after=coverage.detector_state()
   journal=coverage.command(['journalctl','-u',coverage.SERVICE,'--after-cursor',cursor,'-o','cat','--no-pager'])
   alerts=coverage.attributed_alerts(journal,cid)
   for name,data in [('stdout.txt',result.stdout),('stderr.txt',result.stderr),('journal.jsonl',journal),('alerts.json',json.dumps(alerts,indent=2)),('health.json',json.dumps(dict(before=before,after=after),indent=2))]:
    (dest/name).write_text(data)
   row.update(exit_code=result.returncode,collection_ok=coverage.health_ok(before,after),matched_rules=sorted({r['rule'] for r in alerts}))
   row['valid']=result.returncode==0 and row['collection_ok']
  except Exception as error:row['error']=str(error)
  finally:subprocess.run(['docker','rm','-f',cid],capture_output=True,timeout=30)
  (dest/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
  (a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
raise SystemExit(0 if all(r['valid'] for r in rows) else 1)
