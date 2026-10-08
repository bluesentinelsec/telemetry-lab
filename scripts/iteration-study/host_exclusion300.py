"""Secondary host-exclusion sensitivity; the primary dataset is never modified."""
import collections,json,sys
from pathlib import Path
import numpy as np

b=Path(sys.argv[1]);excluded=sys.argv[2];out=b/'analysis';allocation=json.loads((b/'allocation.json').read_text());hosts=sorted(allocation);H=len(hosts);D=len(allocation[hosts[0]]['development'])
assert excluded in hosts
groups=collections.defaultdict(list)
for p in (b/'normalized').glob('*-primitives.jsonl'):
 for line in p.open():
  r=json.loads(line);groups[(r['case'],r['config'])].append(r)
byk=collections.defaultdict(list);profiles={}
for key,rs in sorted(groups.items()):
 lookup={(r['host'],r['repetition']):r for r in rs if r['valid']};types=sorted(set().union(*(r['event_counts'] for r in rs)))
 arrays={kind:np.array([[[lookup[h,rep]['event_counts'].get(e,0) for e in types] for rep in allocation[h][kind]] for h in hosts],float) for kind in ('development','validation')}
 keep=np.array([h!=excluded for h in hosts]);dev=arrays['development'];val=arrays['validation'][keep];reference=val.sum(axis=2).mean();refcomp=(val/val.sum(axis=2)[:,:,None]).mean(axis=(0,1))
 profiles[key]={}
 for k in range(1,D+1):
  full=dev[:,:k];x=full[keep];fm=full.sum(axis=2).mean();mean=x.sum(axis=2).mean()
  fc=(full/full.sum(axis=2)[:,:,None]).mean(axis=(0,1));comp=(x/x.sum(axis=2)[:,:,None]).mean(axis=(0,1));profiles[key][k]=(float(mean),comp)
  byk[k].append(dict(case=key[0],config=key[1],volume_change_from_full_fleet_percent=float(abs(mean-fm)/fm*100),composition_change_from_full_fleet_pp=float(abs(comp-fc).sum()*50),validation_volume_difference_percent=float(abs(mean-reference)/reference*100),validation_composition_difference_pp=float(abs(comp-refcomp).sum()*50)))
summary=[];passing=[]
for k,rs in sorted(byk.items()):
 later=[(abs(vm-profiles[key][k][0])/profiles[key][k][0]*100,float(abs(cp-profiles[key][k][1]).sum()*50)) for key,values in profiles.items() for m,(vm,cp) in values.items() if m>k]
 summary.append(dict(blocks_per_host=k,full_fleet_n=H*k,excluded_fleet_n=(H-1)*k,
  max_volume_change_from_full_fleet_percent=max(r['volume_change_from_full_fleet_percent'] for r in rs),max_composition_change_from_full_fleet_pp=max(r['composition_change_from_full_fleet_pp'] for r in rs),
  max_validation_volume_difference_percent=max(r['validation_volume_difference_percent'] for r in rs),max_validation_composition_difference_pp=max(r['validation_composition_difference_pp'] for r in rs),
  max_later_volume_change_percent=max((v for v,c in later),default=None),max_later_composition_change_pp=max((c for v,c in later),default=None)))
 agreement=all(r['validation_volume_difference_percent']<=2 and r['validation_composition_difference_pp']<=1 for m,rr in byk.items() if m>=k for r in rr)
 if D-k>=5 and agreement and all(v<=.5 and c<=.5 for v,c in later):passing.append(k)
result=dict(excluded_host=excluded,retained_hosts=H-1,validation_n=(H-1)*D,primary_dataset_unchanged=True,
 interpretation='Secondary sensitivity, using the same per-host block counts. The smaller fleet has 95/190/285 rather than 100/200/300 observations. The secondary block criterion requires five later blocks per retained host, not the primary protocol’s 100 later observations.',
 first_passing_blocks_per_host=min(passing) if passing else None,curves=summary)
(out/f'host-exclusion-{excluded}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(excluded_host=excluded,first_passing_blocks_per_host=result['first_passing_blocks_per_host'],checkpoints=[r for r in summary if r['full_fleet_n'] in (100,200,300)]),indent=2))
