"""Describe opposite-outcome discovery, ordering sensitivity and unknown bounds.

All resamples reuse the measured development executions. These diagnostics do not
turn unobservable outcomes into detector misses or create additional executions.
"""
import collections,json,sys
from pathlib import Path
import numpy as np
b=Path(sys.argv[1]);out=b/'analysis';allocation=json.loads((b/'allocation.json').read_text());hosts=sorted(allocation);H=len(hosts);D=len(allocation[hosts[0]]['development'])
groups=collections.defaultdict(list)
for p in (b/'normalized').glob('*-composites.jsonl'):
 for line in p.read_text().splitlines():
  r=json.loads(line);groups[(r['os'],r['case'],r['config'],r['mode'])].append(r)
def classify(rs):
 values=[bool(r['fired']) for r in rs if r['valid']]
 return 'unknown' if not values else 'always' if all(values) else 'never' if not any(values) else 'mixed'
def save(name,x):(out/name).write_text(json.dumps(x,indent=2)+'\n')
results=[];curves=collections.defaultdict(list)
rng=np.random.default_rng(20260924);orders=np.array([[rng.permutation(D) for _ in hosts] for _ in range(500)])
for key,rs in sorted(groups.items()):
 slots={(r['host'],r['repetition']):r for r in rs}
 development=[r for h in hosts for rep in allocation[h]['development'] if (r:=slots.get((h,rep))) is not None]
 validation=[r for h in hosts for rep in allocation[h]['validation'] if (r:=slots.get((h,rep))) is not None]
 good=[r for r in development+validation if r['valid']];unknown=[r for r in development+validation if not r['valid']]
 first_mixed=None;first_validation_disagreement=None
 valid_matrix=np.zeros((H,D),bool);fired_matrix=np.zeros((H,D),bool)
 for hi,h in enumerate(hosts):
  for j,rep in enumerate(allocation[h]['development']):
   r=slots.get((h,rep));valid_matrix[hi,j]=bool(r and r['valid']);fired_matrix[hi,j]=bool(r and r['valid'] and r['fired'])
 for k in range(1,D+1):
  n=k*H;selected=[r for h in hosts for rep in allocation[h]['development'][:k] if (r:=slots.get((h,rep))) is not None]
  dc=classify(selected);vc=classify(validation)
  if dc=='mixed' and first_mixed is None:first_mixed=n
  if dc!=vc and first_validation_disagreement is None:first_validation_disagreement=n
  hi=np.arange(H)[None,:,None];ix=orders[:,:,:k]
  nv=valid_matrix[hi,ix].sum(axis=(1,2));nf=fired_matrix[hi,ix].sum(axis=(1,2))
  classes=np.where(nv==0,'unknown',np.where(nf==0,'never',np.where(nf==nv,'always','mixed')))
  known=[r for r in selected if r['valid']];alerts=sum(r['fired'] for r in known);missing=n-len(known)
  curves[(n,key[0],key[3])].append(dict(class_agreement=dc==vc,order_class_agreement=float(np.mean(classes==vc)),order_mixed_fraction=float(np.mean(classes=='mixed')),valid=len(known),unknown=missing,lower_rate_if_unknowns_never=alerts/n,upper_rate_if_unknowns_always=(alerts+missing)/n))
 results.append(dict(os=key[0],case=key[1],config=key[2],mode=key[3],development_class=classify(development),validation_class=classify(validation),first_development_n_with_mixed_outcomes=first_mixed,first_development_n_disagreeing_with_validation=first_validation_disagreement,subsequent_valid=len(good),subsequent_alerts=sum(r['fired'] for r in good),subsequent_unknown=len(unknown),unknown_reasons=dict(collections.Counter(r.get('outcome','invalid') for r in unknown)),hosts={h:dict(valid=sum(r['host']==h for r in good),alerts=sum(r['host']==h and r['fired'] for r in good),unknown=sum(r['host']==h for r in unknown)) for h in hosts}))
summary=[]
for (n,os,mode),rs in sorted(curves.items()):
 summary.append(dict(n=n,os=os,mode=mode,cells=len(rs),minimum_valid_n=min(r['valid'] for r in rs),maximum_unknown_n=max(r['unknown'] for r in rs),minimum_order_class_agreement=min(r['order_class_agreement'] for r in rs),cells_ever_mixed_in_resamples=sum(r['order_mixed_fraction']>0 for r in rs),maximum_unknown_rate_bound_width_pp=max((r['upper_rate_if_unknowns_always']-r['lower_rate_if_unknowns_never'])*100 for r in rs)))
save('composite-discovery.json',results);save('composite-order-and-unknown-sensitivity.json',summary)
print(json.dumps(dict(cells=len(results),mixed_cells=sum(r['development_class']=='mixed' or r['validation_class']=='mixed' for r in results),unknown=sum(r['subsequent_unknown'] for r in results))))
