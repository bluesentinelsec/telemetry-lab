"""Durable attempt evidence and conservative recovery of the same collector."""
import json,os,time
from pathlib import Path

def write_json(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
 with tmp.open('w') as f:
  json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 tmp.replace(path)

def snapshot(collector):
 try:return collector.detector_state()
 except Exception as error:return dict(service='unavailable',counters={},error=repr(error))

def healthy(collector,before,after):
 return not before.get('error') and not after.get('error') and collector.health_ok(before,after)

def ensure_ready(collector,expected,output,offset):
 state=snapshot(collector)
 if not state.get('error'):return state
 path=Path(output)/f'collector-restart-{offset:06d}.json'
 evidence=dict(offset=offset,started_ns=time.time_ns(),before=state,expected_provenance=expected)
 write_json(path,evidence)
 # The transient --collect unit can disappear after an abort. Recreate it
 # with the same setup script and an explicit frozen detector binary.
 setup=Path(collector.__file__).with_name('setup-detector.sh')
 collector.command(['env','FALCO_BIN='+expected['path'],'bash',str(setup)])
 for _ in range(15):
  time.sleep(1);state=snapshot(collector)
  if not state.get('error'):break
 evidence.update(after=state,ended_ns=time.time_ns());write_json(path,evidence)
 if state.get('error'):raise RuntimeError('Collector recovery failed; no new batch launched')
 actual=collector.detector_provenance();evidence['actual_provenance']=actual;write_json(path,evidence)
 if actual!=expected:raise RuntimeError('Collector provenance changed; no new batch launched')
 return state
