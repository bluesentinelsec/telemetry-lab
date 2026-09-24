"""Descriptive rare-event, later-estimate-change, and measured-duration diagnostics."""
import collections,csv,datetime,json,sys
from pathlib import Path
import numpy as np
b=Path(sys.argv[1]);out=b/'analysis';alloc=json.loads((b/'allocation.json').read_text())
def write(name,x):(out/name).write_text(json.dumps(x,indent=2)+'\n')
with (out/'primitive-cells.csv').open() as f:rows=list(csv.DictReader(f))
groups=collections.defaultdict(dict)
for r in rows:groups[(r['os'],r['case'],r['config'])][int(r['n'])]=float(r['development_mean'])
changes=[]
for n in range(10,101,10):
 values=[(abs(v[n]-v[m])/v[100]*100,key,m) for key,v in groups.items() for m in range(n,101,10)]
 if values:
  worst=max(values);changes.append(dict(n=n,max_change_from_any_later_mean_percent=worst[0],cell=worst[1],later_n=worst[2]))
write('later-mean-change-diagnostic.json',changes)
bycell=collections.defaultdict(list);byhost=collections.defaultdict(list)
for p in (b/'normalized').glob('*-primitives.jsonl'):
 for line in p.read_text().splitlines():
  r=json.loads(line);bycell[(r['os'],r['case'],r['config'])].append(r);byhost[(r['host'],r['os'])].append(r)
rare=[];ranges=[]
for key,rs in sorted(bycell.items()):
 d=[r for r in rs if r['valid'] and r['repetition'] in alloc[r['host']]['development']]
 v=[r for r in rs if r['valid'] and r['repetition'] in alloc[r['host']]['validation']]
 if not d or not v:continue
 dt=set().union(*(r['event_counts'] for r in d));vt=set().union(*(r['event_counts'] for r in v))
 for event in sorted(vt-dt):rare.append(dict(os=key[0],case=key[1],config=key[2],event=event,development_occurrences=0,development_n=len(d),validation_occurrences=sum(r['event_counts'].get(event,0)>0 for r in v),validation_n=len(v)))
 values=np.array([sum(r['event_counts'].values()) for r in d+v]);ranges.append(dict(os=key[0],case=key[1],config=key[2],n=len(values),min=int(values.min()),max=int(values.max()),median=float(np.median(values)),mean=float(values.mean()),sd=float(values.std(ddof=1)),cv_percent=float(values.std(ddof=1)/values.mean()*100)))
write('rare-validation-only-events.json',rare);write('subsequent-run-ranges.json',ranges)
timings=[]
for p in (b/'normalized').glob('*-verification.json'):
 x=json.loads(p.read_text());rs=byhost[x['host'],x['os']]
 timed=[r for r in rs if r.get('started_epoch') is not None and r.get('seconds') is not None]
 if not timed:continue
 start=min(r['started_epoch'] for r in timed);end=max(r['started_epoch']+r['seconds'] for r in timed)
 row=dict(host=x['host'],os=x['os'],primitive_wall_seconds=end-start,primitive_records=len(rs),collector_interruption=bool(x.get('interruption_reconciliation') or x.get('windows_resumption_complete')))
 if x.get('collection_ended'):
  totalend=datetime.datetime.fromisoformat(x['collection_ended'].replace('Z','+00:00')).timestamp()
  row['composite_wall_seconds_including_fixture_and_evaluation']=totalend-end;row['composite_records']=x['composite_count']
 timings.append(row)
write('collection-durations.json',timings)
print(json.dumps(dict(rare_validation_only_events=len(rare),timed_hosts=len(timings))))
