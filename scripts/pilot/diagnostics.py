#!/usr/bin/env python3
"""Prespecified repetition-count diagnostics plus labeled first-launch exploration."""
import argparse,collections,csv,json,math
from pathlib import Path
import numpy as np
from scipy.stats import t
from analyze import primitive_rows,metrics

p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
data=[r for r in primitive_rows(a.root) if r['valid']]
groups=collections.defaultdict(list)
for r in data:groups[(r['os'],r['case'],r['config'])].append(r)
trajectory=[];first_launch=[]
for key,rows in sorted(groups.items()):
 for rep in range(1,11):
  subset=[r for r in rows if r['repetition']<=rep]
  if len(subset)<2:continue
  stat=metrics([sum(r['event_counts'].values()) for r in subset],[r['host'] for r in subset])
  trajectory.append(dict(os=key[0],case=key[1],config=key[2],through_repetition=rep,n=stat['n'],mean=stat['mean'],relative_ci95_half=stat['relative_half']))
 for host in sorted({r['host'] for r in rows}):
  initial=[r for r in rows if r['host']==host and r['repetition']==1]
  later=[r for r in rows if r['host']==host and r['repetition']>1]
  if len(initial)!=1 or not later:continue
  f=sum(initial[0]['event_counts'].values());v=[sum(r['event_counts'].values()) for r in later]
  first_launch.append(dict(os=key[0],case=key[1],config=key[2],host=host,first_volume=f,later_n=len(v),later_mean=float(np.mean(v)),first_excess=f-float(np.mean(v)),first_relative_excess=f/float(np.mean(v))-1))
for name,rows in [('primitive-convergence',trajectory),('first-launch-diagnostic',first_launch)]:
 with (a.output/f'{name}.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Saved run-count trajectories and first-launch exploration. No observations removed from primary analysis.')
