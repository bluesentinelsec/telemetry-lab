#!/usr/bin/env python3
"""Separate validation and host-balanced sample-size sensitivity, without claiming a universal optimum."""
import argparse,collections,csv,json,math,sys
from pathlib import Path
import numpy as np
from scipy.stats import t,beta
p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('--resamples',type=int,default=500);a=p.parse_args()
base=a.base;out=base/'analysis';out.mkdir(exist_ok=True)
allocation=json.loads((base/'allocation.json').read_text());hosts=sorted(allocation)
H=len(hosts);D=len(allocation[hosts[0]]['development']);V=len(allocation[hosts[0]]['validation'])
assert all(len(allocation[h]['development'])==D and len(allocation[h]['validation'])==V for h in hosts)
ns=list(range(H,H*D+1,H))

def load(pattern):
 return [json.loads(line) for f in sorted((base/'normalized').glob(pattern)) for line in f.read_text().splitlines() if line.strip()]
def save(name,x):(out/name).write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v)+'\n')
def export(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (out/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)
def summary(v):
 x=np.array(v,float);x=x[np.isfinite(x)]
 return dict(n=len(x),median=float(np.median(x)),p95=float(np.quantile(x,.95)),max=float(x.max())) if len(x) else dict(n=0)
def ci_half_host(means):return float(t.ppf(.975,len(means)-1)*np.std(means,ddof=1)/np.sqrt(len(means)))
def interval(k,n):
 return dict(n=n,k=k,rate=k/n if n else None,lower=float(beta.ppf(.025,k,n-k+1)) if k else 0.,upper=float(beta.ppf(.975,k+1,n-k)) if k<n else 1.)
def classify(rs):
 v=[r['fired'] for r in rs if r['valid']]
 return 'unknown' if not v else 'always' if all(v) else 'never' if not any(v) else 'mixed'
def slots(rs):return {(r['host'],r['repetition']):r for r in rs}
def split(rs,kind,k=None):
 keep={(h,rep) for h in hosts for rep in allocation[h][kind][:k]}
 return [r for r in rs if (r['host'],r['repetition']) in keep]
primitives=load('*-primitives.jsonl');composites=load('*-composites.jsonl')
groups=collections.defaultdict(list)
for r in primitives:groups[(r['os'],r['case'],r['config'])].append(r)
matrices={};first=[];incomplete=[]
for key,rs in sorted(groups.items()):
 lookup=slots([r for r in rs if r['valid']]);types=sorted(set().union(*(r['event_counts'].keys() for r in rs)))
 needed={(h,rep) for h in hosts for rep in allocation[h]['development']+allocation[h]['validation']}
 if needed-lookup.keys():incomplete.append(dict(cell=key,missing_or_invalid=sorted(needed-lookup.keys())));continue
 counts={kind:np.array([[[lookup[h,rep]['event_counts'].get(e,0) for e in types] for rep in allocation[h][kind]] for h in hosts],float) for kind in ('development','validation')}
 m={kind:dict(volume=v.sum(axis=2),composition=v/v.sum(axis=2,keepdims=True),presence=v>0) for kind,v in counts.items()}
 m['types']=types
 matrices[key]=m
 cold=[r for r in split(rs,'first_launch') if r['valid']];cv=np.array([sum(r['event_counts'].values()) for r in cold]);warm=m['validation']['volume'];wm=warm.mean()
 first.append(dict(os=key[0],case=key[1],config=key[2],initial_n=len(cold),initial_mean=float(cv.mean()) if len(cv) else None,subsequent_mean=float(wm),first_excess_percent=float(100*(cv.mean()/wm-1)) if len(cv) else None,subsequent_min=float(warm.min()),subsequent_max=float(warm.max()),subsequent_cv_percent=float(warm.std(ddof=1)/wm*100),host_mean_ci95_half_percent=ci_half_host(warm.mean(axis=1))/wm*100,run_level_ci95_half_percent=float(t.ppf(.975,H*V-1)*warm.std(ddof=1)/np.sqrt(H*V)/wm*100),validation_event_types=types))
# Identical resampling indices across cells preserve block-level dependence.
rng=np.random.default_rng(20260923)
permutations=np.array([[rng.permutation(D) for h in hosts] for b in range(a.resamples)])
bootstrap=rng.integers(0,H,size=(a.resamples,H))
cellcurves=[];curves=[];senscurves=[];contrastcurves=[]
for k in range(1,D+1):
 n=H*k;err=[];tv=[];sensvol=[];senstv=[];bootvol=[];boottv=[]
 for key,m in matrices.items():
  d,v=m['development'],m['validation'];ref=v['volume'].mean();refc=v['composition'].mean(axis=(0,1));x=d['volume'][:,:k];y=d['composition'][:,:k,:]
  ve=abs(x.mean()-ref)/ref*100;ce=abs(y.mean(axis=(0,1))-refc).sum()/2*100
  present=d['presence'][:,:k,:].any(axis=(0,1));validation=v['presence'].any(axis=(0,1));new=validation & ~present
  hdiff=x.mean(axis=1)-v['volume'].mean(axis=1)
  compdiff=y.mean(axis=1)-v['composition'].mean(axis=1)
  bootvol.append(abs(hdiff[bootstrap].mean(axis=1))/ref*100)
  boottv.append(abs(compdiff[bootstrap].mean(axis=1)).sum(axis=1)/2*100)
  ix=permutations[:,:,:k];hidx=np.arange(H)[None,:,None]
  sv=abs(d['volume'][hidx,ix].mean(axis=(1,2))-ref)/ref*100
  sc=abs(d['composition'][hidx,ix].mean(axis=(1,2))-refc).sum(axis=1)/2*100
  sensvol.append(sv);senstv.append(sc);err.append(ve);tv.append(ce)
  cellcurves.append(dict(n=n,os=key[0],case=key[1],config=key[2],relative_volume_error_percent=float(ve),composition_tv_pp=float(ce),development_mean=float(x.mean()),validation_mean=float(ref),validation_host_half_percent=ci_half_host(v['volume'].mean(axis=1))/ref*100,development_host_half_percent=ci_half_host(x.mean(axis=1))/ref*100,new_validation_event_types=int(new.sum()),new_validation_event_max_prevalence=float(v['presence'][:,:,new].mean(axis=(0,1)).max()) if new.any() else 0.,order_error_p95_percent=float(np.quantile(sv,.95)),order_tv_p95_pp=float(np.quantile(sc,.95))))
  cellcurves[-1].update(development_host_se_percent=float(x.mean(axis=1).std(ddof=1)/np.sqrt(H)/x.mean()*100),development_iid_se_percent=float(x.std(ddof=1)/np.sqrt(n)/x.mean()*100))
 if not err:continue
 bv=np.array(bootvol);bc=np.array(boottv);sv=np.array(sensvol);sc=np.array(senstv)
 curves.append(dict(n=n,cells=len(err),volume_error_percent=summary(err),composition_tv_pp=summary(tv),host_bootstrap_max_volume_error_95_interval=np.quantile(bv.max(axis=0),[.025,.975]).tolist(),host_bootstrap_max_tv_95_interval=np.quantile(bc.max(axis=0),[.025,.975]).tolist(),volume_cells_within={str(x):sum(e<=x for e in err) for x in (1,2,5,10)},composition_cells_within={str(x):sum(e<=x for e in tv) for x in (1,2,5)},cells_with_new_validation_types=sum(r['new_validation_event_types']>0 for r in cellcurves if r['n']==n)))
 senscurves.append(dict(n=n,primary_joint_pass_fraction=float(((sv.max(axis=0)<=2)&(sc.max(axis=0)<=1)).mean()),random_order_max_volume_p50=float(np.quantile(sv.max(axis=0),.5)),random_order_max_volume_p95=float(np.quantile(sv.max(axis=0),.95)),random_order_max_tv_p50=float(np.quantile(sc.max(axis=0),.5)),random_order_max_tv_p95=float(np.quantile(sc.max(axis=0),.95)),all_cells_joint_pass_fraction={str(x):float(((sv.max(axis=0)<=x)&(sc.max(axis=0)<=x)).mean()) for x in (1,2,5,10)}))
 # Paired language/runtime comparisons, aligned by host and actual repetition.
 pairs=collections.defaultdict(list)
 for key in matrices:pairs[(key[0],key[1],key[2].split('-')[1])].append(key)
 for (os,case,lang),keys in pairs.items():
  if len(keys)!=2:continue
  left,right=sorted(keys);l,r=matrices[left],matrices[right]
  vd=r['validation']['volume']-l['validation']['volume'];dd=r['development']['volume'][:,:k]-l['development']['volume'][:,:k]
  scale=(r['validation']['volume'].mean()+l['validation']['volume'].mean())/2;reference=vd.mean();half=ci_half_host(vd.mean(axis=1));estimate=dd.mean()
  contrastcurves.append(dict(n=n,os=os,case=case,language=lang,left=left[2],right=right[2],reference_delta=float(reference),estimated_delta=float(estimate),normalized_error_percent=float(abs(estimate-reference)/scale*100),reference_host_ci95_half=float(half),development_host_ci95_half=ci_half_host(dd.mean(axis=1)),reference_effect_percent=float(reference/scale*100),relative_contrast_error_percent=float(abs(estimate-reference)/abs(reference)*100) if abs(reference)>half else None,reference_distinguishable=bool(abs(reference)>half),development_distinguishable=bool(abs(estimate)>ci_half_host(dd.mean(axis=1))),sign_agrees=bool(np.sign(reference)==np.sign(estimate))))
  # Chapter 3's empty-control adjustment, paired within host/repetition.
  el=matrices.get((os,'empty',left[2]));er=matrices.get((os,'empty',right[2]))
  if case!='empty' and el is not None and er is not None:
   av=vd-(er['validation']['volume']-el['validation']['volume'])
   ad=dd-(er['development']['volume'][:,:k]-el['development']['volume'][:,:k])
   ar=av.mean();ah=ci_half_host(av.mean(axis=1));ae=ad.mean()
   contrastcurves[-1].update(adjusted_reference_delta=float(ar),adjusted_estimated_delta=float(ae),adjusted_normalized_error_percent=float(abs(ae-ar)/scale*100),adjusted_reference_host_ci95_half=float(ah),adjusted_reference_distinguishable=bool(abs(ar)>ah),adjusted_development_host_ci95_half=ci_half_host(ad.mean(axis=1)),adjusted_development_distinguishable=bool(abs(ae)>ci_half_host(ad.mean(axis=1))),adjusted_sign_agrees=bool(np.sign(ar)==np.sign(ae)),adjusted_relative_contrast_error_percent=float(abs(ae-ar)/abs(ar)*100) if abs(ar)>ah else None)
  types=sorted(set(l['types'])|set(r['types']))
  def jaccard(kind):
   arrays=[]
   for m in (l,r):
    present=m[kind]['presence'];z=np.zeros((*present.shape[:2],len(types)),bool)
    for i,event in enumerate(m['types']):z[:,:,types.index(event)]=present[:,:,i]
    arrays.append(z)
   intersection=(arrays[0]&arrays[1]).sum(axis=2);union=(arrays[0]|arrays[1]).sum(axis=2)
   return np.divide(intersection,union,out=np.ones_like(intersection,dtype=float),where=union>0)
  jv=jaccard('validation');jd=jaccard('development')[:,:k]
  contrastcurves[-1].update(jaccard_validation_mean=float(jv.mean()),jaccard_development_mean=float(jd.mean()),jaccard_error_pp=float(abs(jd.mean()-jv.mean())*100))

thresholds=[]
for volume in (1,2,5,10):
 for composition in (1,2,5):
  for fraction in (.95,1.):
   rates={n:np.mean([r['relative_volume_error_percent']<=volume and r['composition_tv_pp']<=composition for r in cellcurves if r['n']==n]) for n in ns} if matrices else {}
   sufficient=[n for n in rates if all(rate>=fraction for later,rate in rates.items() if later>=n)]
   thresholds.append(dict(volume_tolerance_percent=volume,composition_tolerance_pp=composition,required_cell_fraction=fraction,smallest_persistent_n=min(sufficient) if sufficient else None))
cgroups=collections.defaultdict(list)
for r in composites:cgroups[(r['os'],r['case'],r['config'],r['mode'])].append(r)
ccells=[];ccurves=[]
for n in ns:
 for key,rs in sorted(cgroups.items()):
  d=split(rs,'development',n//H);v=split(rs,'validation');good=[r for r in d if r['valid']];vgood=[r for r in v if r['valid']]
  ds=interval(sum(r['fired'] for r in good),len(good));vs=interval(sum(r['fired'] for r in vgood),len(vgood));dc=classify(d);vc=classify(v)
  ccells.append(dict(n=n,os=key[0],case=key[1],config=key[2],mode=key[3],development_valid=len(good),development_unknown_or_missing=n-len(good),validation_valid=len(vgood),validation_unknown_or_missing=H*V-len(vgood),development_alerts=ds['k'],validation_alerts=vs['k'],development_class=dc,validation_class=vc,class_agrees=dc==vc,alert_rate_error_pp=abs(ds['rate']-vs['rate'])*100 if good and vgood else None,development_ci95=[ds['lower'],ds['upper']],validation_ci95=[vs['lower'],vs['upper']],hosts={h:dict(valid=sum(r['valid'] for r in d if r['host']==h),alerts=sum(r['valid'] and r['fired'] for r in d if r['host']==h)) for h in hosts}))
 for os in ('linux','windows'):
  for mode in ('active','control','negative'):
   cells=[r for r in ccells if r['n']==n and r['os']==os and r['mode']==mode]
   if not cells:continue
   ccurves.append(dict(n=n,os=os,mode=mode,cells=len(cells),valid=sum(r['development_valid'] for r in cells),unknown_or_missing=sum(r['development_unknown_or_missing'] for r in cells),class_agreement=sum(r['class_agrees'] for r in cells),mixed_development=sum(r['development_class']=='mixed' for r in cells),mixed_validation=sum(r['validation_class']=='mixed' for r in cells),rate_error_pp=summary([r['alert_rate_error_pp'] for r in cells if r['alert_rate_error_pp'] is not None])))
rare=[dict(n=n,opposite_upper95_if_zero=1-.05**(1/n),chance_observe_at_least_one={str(p):1-(1-p)**n for p in (.01,.02,.05,.1)}) for n in ns]
counts=dict(primitive_attempts=len(primitives),primitive_invalid=sum(not r['valid'] for r in primitives),composite_attempts=len(composites),composite_invalid=sum(not r['valid'] for r in composites),complete_primitive_cells=len(matrices),incomplete_primitive_cells=incomplete,composite_unknown_reasons=dict(collections.Counter(r.get('outcome','invalid') for r in composites if not r['valid'])))
save('counts.json',counts);save('primitive-curves.json',curves);save('order-sensitivity.json',senscurves);save('thresholds.json',thresholds);save('first-launch.json',first);save('composite-curves.json',ccurves);save('binary-sensitivity.json',rare)
export('primitive-cells.csv',cellcurves);export('runtime-contrasts.csv',contrastcurves);export('composite-cells.csv',ccells)
print(json.dumps(counts,indent=2));print((out/'primitive-curves.json').read_text())
