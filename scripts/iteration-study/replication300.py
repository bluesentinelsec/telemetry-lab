"""Descriptive fresh-fleet replication; never pool the two studies' observations."""
import collections,json,sys
from pathlib import Path
import numpy as np

b,previous=map(Path,sys.argv[1:3]);out=b/'analysis'
def summarize(base):
 allocation=json.loads((base/'allocation.json').read_text());groups=collections.defaultdict(list)
 for p in (base/'normalized').glob('*-linux-primitives.jsonl'):
  for line in p.open():
   r=json.loads(line)
   if r['valid'] and r['repetition'] in allocation[r['host']]['development']+allocation[r['host']]['validation']:groups[(r['case'],r['config'])].append(r)
 result={}
 for key,rs in groups.items():
  byhost=collections.defaultdict(list)
  for r in rs:byhost[r['host']].append(r)
  types=sorted(set().union(*(r['event_counts'] for r in rs)));hostvol=[];hostcomp=[]
  for host,hrs in byhost.items():
   counts=np.array([[r['event_counts'].get(e,0) for e in types] for r in hrs],float);vol=counts.sum(axis=1)
   hostvol.append(float(vol.mean()));hostcomp.append((counts/vol[:,None]).mean(axis=0))
  result[key]=dict(n=len(rs),hosts=len(byhost),mean=float(np.mean(hostvol)),composition=dict(zip(types,np.mean(hostcomp,axis=0))))
 return result

old,new=summarize(previous),summarize(b);rows=[]
for key in sorted(old.keys()&new.keys()):
 x,y=old[key],new[key];events=x['composition'].keys()|y['composition'].keys()
 rows.append(dict(case=key[0],config=key[1],previous_n=x['n'],current_n=y['n'],previous_hosts=x['hosts'],current_hosts=y['hosts'],previous_mean=x['mean'],current_mean=y['mean'],mean_change_percent=(y['mean']/x['mean']-1)*100,composition_tv_pp=sum(abs(y['composition'].get(e,0)-x['composition'].get(e,0)) for e in events)*50))
(out/'cross-study-replication.json').write_text(json.dumps(dict(previous_study=str(previous),current_study=str(b),interpretation='Different fleets and collection times; descriptive replication, not an effect of repetition count and not pooled data.',cells=rows),indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(cells=len(rows),worst_volume_change_percent=max(abs(r['mean_change_percent']) for r in rows),worst_composition_tv_pp=max(r['composition_tv_pp'] for r in rows))))
