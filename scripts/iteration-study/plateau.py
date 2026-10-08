"""Prespecified agreement and incremental-gain criteria; never call the endpoint a plateau."""
import collections,csv,json,sys
from pathlib import Path
import numpy as np
b=Path(sys.argv[1]);out=b/'analysis';allocation=json.loads((b/'allocation.json').read_text());hosts=sorted(allocation);H=len(hosts);D=len(allocation[hosts[0]]['development']);ns=list(range(H,H*D+1,H))
def save(n,x):(out/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def readcsv(n):
 if not (out/n).exists():return []
 with (out/n).open() as f:return list(csv.DictReader(f))
curves=readcsv('primitive-cells.csv');bykey=collections.defaultdict(dict)
for r in curves:bykey[(r['os'],r['case'],r['config'])][int(r['n'])]=r
groups=collections.defaultdict(list)
for p in (b/'normalized').glob('*-primitives.jsonl'):
 for line in p.open():
  r=json.loads(line);groups[(r['os'],r['case'],r['config'])].append(r)
profiles={};drift=[]
for key,rs in groups.items():
 if key not in bykey:continue
 lookup={(r['host'],r['repetition']):r for r in rs if r['valid']};types=sorted(set().union(*(r['event_counts'] for r in rs)))
 x=np.array([[[lookup[h,rep]['event_counts'].get(e,0) for e in types] for rep in allocation[h]['development']] for h in hosts],float)
 vol=x.sum(axis=2);comp=x/vol[:,:,None]
 profiles[key]={n:(float(vol[:,:n//H].mean()),comp[:,:n//H].mean(axis=(0,1))) for n in ns}
 chrono=[sorted(allocation[h]['development']+allocation[h]['validation']) for h in hosts]
 z=np.array([[[lookup[h,rep]['event_counts'].get(e,0) for e in types] for rep in reps] for h,reps in zip(hosts,chrono)],float)
 total=z.sum(axis=2);c=z/total[:,:,None];half=total.shape[1]//2
 early=total[:,:half].mean();late=total[:,half:].mean()
 drift.append(dict(os=key[0],case=key[1],config=key[2],early_mean=float(early),late_mean=float(late),relative_change_percent=float((late/early-1)*100),composition_tv_pp=float(abs(c[:,:half].mean(axis=(0,1))-c[:,half:].mean(axis=(0,1))).sum()*50)))
if not profiles:raise SystemExit('No complete primitive cells; plateau cannot be estimated')
comparisons=[]
for key,values in sorted(profiles.items()):
 for n in ns:
  for later in ns:
   if later<=n:continue
   vm,cp=values[n];vl,cl=values[later]
   comparisons.append(dict(os=key[0],case=key[1],config=key[2],n=n,later_n=later,volume_change_percent=abs(vl-vm)/vm*100,composition_change_pp=float(abs(cl-cp).sum()*50)))
bycomparison=collections.defaultdict(list)
for r in comparisons:bycomparison[r['n']].append(r)
summary=[]
for n in ns:
 rs=bycomparison[n];current=[r for values in bykey.values() for k,r in values.items() if k==n]
 summary.append(dict(n=n,cells=len(current),later_observations_available=max(ns)-n,eligible_for_plateau_claim=max(ns)-n>=100,
  worst_validation_volume_percent=max(float(r['relative_volume_error_percent']) for r in current),worst_validation_composition_pp=max(float(r['composition_tv_pp']) for r in current),
  worst_later_volume_change_percent=max((r['volume_change_percent'] for r in rs),default=None),worst_later_composition_change_pp=max((r['composition_change_pp'] for r in rs),default=None)))
thresholds=[];expected=len(groups)
for vt in (1.,2.,5.):
 for ct in (.5,1.,2.):
  for dv in (.25,.5,1.):
   for dc in (.25,.5,1.):
    for fraction in (.95,1.):
     passing=[]
     for n in ns:
      if max(ns)-n<100:continue
      good=0
      for key,values in bykey.items():
       agreement=all(float(r['relative_volume_error_percent'])<=vt and float(r['composition_tv_pp'])<=ct for m,r in values.items() if m>=n)
       vm,cp=profiles[key][n]
       settled=all(abs(vl-vm)/vm*100<=dv and float(abs(cl-cp).sum()*50)<=dc for m,(vl,cl) in profiles[key].items() if m>n)
       good+=agreement and settled
      if good/expected>=fraction:passing.append(n)
     thresholds.append(dict(validation_volume_tolerance_percent=vt,validation_composition_tolerance_pp=ct,incremental_volume_tolerance_percent=dv,incremental_composition_tolerance_pp=dc,required_cell_fraction=fraction,smallest_n=min(passing) if passing else None))
primary=next(r for r in thresholds if (r['validation_volume_tolerance_percent'],r['validation_composition_tolerance_pp'],r['incremental_volume_tolerance_percent'],r['incremental_composition_tolerance_pp'],r['required_cell_fraction'])==(2.,1.,.5,.5,1.))
save('plateau-curves.json',summary);save('plateau-thresholds.json',thresholds);save('plateau-primary.json',primary);save('temporal-drift.json',drift)
with (out/'incremental-cell-comparisons.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(comparisons[0]));w.writeheader();w.writerows(comparisons)
contrasts=readcsv('runtime-contrasts.csv');effects=[]
for n in ns:
 rows=[r for r in contrasts if int(r['n'])==n];item=dict(n=n)
 for prefix in ('','adjusted_'):
  ref=[r for r in rows if r.get(prefix+'reference_distinguishable')=='True']
  item[(prefix or 'raw_')+'reference_resolved']=len(ref)
  item[(prefix or 'raw_')+'unresolved_in_development']=sum(r.get(prefix+'development_distinguishable')!='True' for r in ref)
  item[(prefix or 'raw_')+'sign_disagreements']=sum(r.get(prefix+'sign_agrees')!='True' for r in ref)
 effects.append(item)
save('runtime-interpretation-by-n.json',effects)
print(json.dumps(dict(primary=primary,checkpoints=[r for r in summary if r['n'] in (100,200,300)]),indent=2))
