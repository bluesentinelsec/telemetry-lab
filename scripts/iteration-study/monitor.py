"""Compact live progress; raw observations are retained by progress.py."""
import collections,json,subprocess,sys,time
from orchestrate import BASE,ROOT
while True:
 p=subprocess.run([sys.executable,str(ROOT/'scripts/iteration-study/progress.py')],capture_output=True,text=True)
 with (BASE/'monitor-raw.log').open('a') as f:f.write(p.stdout+p.stderr)
 total=collections.Counter();failures=[]
 for line in p.stdout.splitlines():
  try:r=json.loads(line);data=json.loads(r['output'])
  except (ValueError,KeyError):continue
  os=r['os'];prim=data.get('primitives',{});comp=data.get('composites',{})
  total[os+'_primitive_records']+=prim.get('count',0);total[os+'_primitive_invalid']+=prim.get('invalid',0)
  total[os+'_primitive_hosts_complete']+=int(prim.get('count')==(2184 if os=='linux' else 378))
  if os=='linux':total['linux_composite_records']+=comp.get('count',0);total['linux_composite_invalid']+=comp.get('invalid',0)
  else:total['windows_composite_batches']+=comp.get('batches',0);total['windows_composite_batch_errors']+=comp.get('errors',0)
  if data.get('error'):failures.append(dict(host=r['host'],os=os,error=data['error']))
 record=dict(time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),counts=dict(total),errors=failures)
 (BASE/'live-summary.json').write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)
 if len(list((BASE/'archives').glob('*-verified.json')))==20:break
 time.sleep(60)
