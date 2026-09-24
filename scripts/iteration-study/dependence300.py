"""Exploratory host/time diagnostics; not additional independent observations."""
import collections,json,sys
from pathlib import Path
import numpy as np

b=Path(sys.argv[1]);out=b/'analysis';allocation=json.loads((b/'allocation.json').read_text());hosts=sorted(allocation)
groups=collections.defaultdict(list)
for p in (b/'normalized').glob('*-primitives.jsonl'):
 for line in p.open():
  r=json.loads(line);groups[(r['case'],r['config'])].append(r)
rows=[]
for key,rs in sorted(groups.items()):
 lookup={(r['host'],r['repetition']):r for r in rs if r['valid']}
 reps={h:sorted(allocation[h]['development']+allocation[h]['validation']) for h in hosts}
 if any((h,rep) not in lookup for h in hosts for rep in reps[h]):continue
 x=np.array([[sum(lookup[h,rep]['event_counts'].values()) for rep in reps[h]] for h in hosts],float)
 h,m=x.shape;mean=x.mean();hostmeans=x.mean(axis=1);centered=x-hostmeans[:,None]
 within=float(np.mean(np.var(x,axis=1,ddof=1)));between=float(m*np.var(hostmeans,ddof=1))
 denominator=between+(m-1)*within
 rho=float((between-within)/denominator) if denominator else None
 denom=float(np.sum(centered**2));lag1=float(np.sum(centered[:,1:]*centered[:,:-1])/denom) if denom else None
 rows.append(dict(case=key[0],config=key[1],hosts=h,subsequent_repetitions_per_host=m,
  host_mean_min=float(hostmeans.min()),host_mean_max=float(hostmeans.max()),grand_mean=float(mean),
  host_mean_range_percent=float((hostmeans.max()-hostmeans.min())/mean*100),
  within_host_variance=within,between_host_mean_square=between,
  exploratory_random_intercept_icc=rho,pooled_within_host_lag1=lag1,
  constant_volume=bool(np.all(x==x[0,0]))))
(out/'host-time-dependence.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(cells=len(rows),constant_volume_cells=sum(r['constant_volume'] for r in rows))))
