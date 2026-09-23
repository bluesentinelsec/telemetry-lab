#!/usr/bin/env python3
"""Analyze preserved pilot executions; never turn collection failures into misses.

Requires numpy and scipy. Planning intervals/counts are pointwise, run-level
estimates. Host summaries and variance components expose the clustering limit.
"""
import argparse, collections, contextlib, csv, importlib.util, io, json, math
from pathlib import Path
import numpy as np
from scipy.stats import t, norm, beta, chi2


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rows(path):
    if path.suffix == '.jsonl':
        return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    value=read(path)
    return value if isinstance(value,list) else [value]


def need(sd, margin, alpha=.05, power=None):
    """Planning count from pilot SD, two-sided t margin; optional 90% power."""
    if margin <= 0: return None
    if sd == 0: return 2
    extra=norm.ppf(power) if power else 0
    def sufficient(n):
        return (t.ppf(1-alpha/2,n-1)+extra)*sd/math.sqrt(n)<=margin
    low,high=2,2
    while not sufficient(high):high*=2
    while low<high:
        mid=(low+high)//2
        if sufficient(mid):high=mid
        else:low=mid+1
    return low



def metrics(values, hosts):
    x=np.asarray(values,dtype=float);n=len(x);mean=float(x.mean())
    sd=float(x.std(ddof=1)) if n>1 else 0.
    half=float(t.ppf(.975,n-1)*sd/math.sqrt(n)) if n>1 else None
    groups={h:x[np.array(hosts)==h] for h in sorted(set(hosts))}
    within_ss=sum(float(((v-v.mean())**2).sum()) for v in groups.values())
    df=n-len(groups);msw=within_ss/df if df else 0.
    # Standard unbalanced one-way random-effects method-of-moments estimate.
    if len(groups)>1:
        msb=sum(len(v)*(float(v.mean())-mean)**2 for v in groups.values())/(len(groups)-1)
        n0=(n-sum(len(v)**2 for v in groups.values())/n)/(len(groups)-1)
        host_var=max(0.,(msb-msw)/n0)
        host_means=[float(v.mean()) for v in groups.values()]
        host_half=float(t.ppf(.975,len(groups)-1)*np.std(host_means,ddof=1)/math.sqrt(len(groups)))
    else:host_var=None;host_half=None
    return dict(n=n,mean=mean,sd=sd,cv=sd/mean if mean>0 else None,ci95_half=half,
                relative_half=half/mean if mean>0 and half is not None else None,
                min=float(x.min()),max=float(x.max()),within_host_sd=math.sqrt(msw),
                between_host_sd=math.sqrt(host_var) if host_var is not None else None,
                host_mean_ci95_half=host_half,
                hosts={h:dict(n=len(v),mean=float(v.mean()),sd=float(v.std(ddof=1)) if len(v)>1 else 0.) for h,v in groups.items()})


def binomial(k,n):
    if not n:return dict(n=0,alerts=0,rate=None,lower=None,upper=None,opposite_upper_onesided=None)
    return dict(n=n,alerts=k,rate=k/n,
       lower=float(beta.ppf(.025,k,n-k+1)) if k else 0.,
       upper=float(beta.ppf(.975,k+1,n-k)) if k<n else 1.,
       opposite_upper_onesided=1-.05**(1/n) if k in (0,n) else None)


def primitive_rows(root):
    answer=[]
    for host in 'ABC':
        for os in ('linux','windows'):
            folder=root/host/os/'primitives'
            path=folder/('results.jsonl' if os=='linux' else 'results.json')
            if not path.exists():continue
            for original in rows(path):
                r=dict(original);r['os']=os;r['host']=host
                if 'event_counts' not in r and r.get('valid'):
                    counts=collections.Counter()
                    for line in (folder/r['raw']).read_text(encoding='utf-8-sig').splitlines():
                        e=json.loads(line)
                        if e.get('record')=='event':counts[e.get('syscall','unknown') if e['kind']=='syscall' else '@'+e['kind']]+=1
                    r['event_counts']=dict(counts);r['raw_events']=sum(counts.values())
                answer.append(r)
    return answer


def analyze_primitives(data):
    groups=collections.defaultdict(list)
    for r in data:groups[(r['os'],r['case'],r['config'])].append(r)
    cells=[];compositions=[];lookup={}
    for key,attempts in sorted(groups.items()):
        valid=[r for r in attempts if r['valid']]
        if not valid:continue
        lookup[key]=valid
        counts=[sum(r['event_counts'].values()) for r in valid]
        if any(n!=r['summary'][0]['total_events'] for n,r in zip(counts,valid)):
            raise ValueError(f'Raw/summary event count mismatch: {key}')
        stats=metrics(counts,[r['host'] for r in valid]);margin=.05*stats['mean']
        entry=dict(os=key[0],case=key[1],config=key[2],attempts=len(attempts),invalid=len(attempts)-len(valid),**stats)
        entry['volume_n']=need(stats['sd'],margin)
        # Show SD-estimation uncertainty, rather than treating the pilot SD as known.
        entry['volume_n_sd_upper95']=need(stats['sd']*math.sqrt((len(valid)-1)/chi2.ppf(.05,len(valid)-1)),margin) if len(valid)>1 else None
        worst=None
        types=sorted(set().union(*(r['event_counts'].keys() for r in valid)))
        for event in types:
            x=[r['event_counts'].get(event,0)/n for r,n in zip(valid,counts)]
            st=metrics(x,[r['host'] for r in valid]);n=need(st['sd'],.05)
            comp=dict(os=key[0],case=key[1],config=key[2],event=event,occurrences=sum(r['event_counts'].get(event,0)>0 for r in valid),required_n=n,**st)
            compositions.append(comp)
            if worst is None or comp['ci95_half']>worst['ci95_half']:worst=comp
        entry['composition_n']=max(c['required_n'] for c in compositions if (c['os'],c['case'],c['config'])==key)
        entry['worst_composition_event']=worst['event'];entry['composition_ci95_half_max']=worst['ci95_half']
        cells.append(entry)
    contrasts=[]
    pairgroups=collections.defaultdict(list)
    for key in lookup:pairgroups[(key[0],key[1],key[2].split('-')[1])].append(key[2])
    for (os,case,language),configs in sorted(pairgroups.items()):
        configs=sorted(set(configs))
        if len(configs)!=2:continue
        left,right=configs
        def mapping(config,name):
            return {(r['host'],r['repetition']):sum(r['event_counts'].values()) for r in lookup.get((os,name,config),[])}
        a,b=mapping(left,case),mapping(right,case);shared=sorted(a.keys()&b.keys())
        if len(shared)<2:continue
        delta=[b[k]-a[k] for k in shared];st=metrics(delta,[k[0] for k in shared]);baseline=float(np.mean([(a[k]+b[k])/2 for k in shared]))
        c=dict(os=os,case=case,language=language,left=left,right=right,scale_mean=baseline,raw=st,
               power90_n_10pct=need(st['sd'],.10*baseline,power=.90),precision_n_5pct=need(st['sd'],.05*baseline))
        ea,eb=mapping(left,'empty'),mapping(right,'empty');common=sorted(set(shared)&ea.keys()&eb.keys())
        if case!='empty' and len(common)>1:
            v=[(b[k]-eb[k])-(a[k]-ea[k]) for k in common]
            c['empty_adjusted']=metrics(v,[k[0] for k in common])
            c['adjusted_power90_n_10pct_raw_scale']=need(c['empty_adjusted']['sd'],.10*baseline,power=.90)
        contrasts.append(c)
    return cells,compositions,contrasts


def composite_rows(root):
    spec=importlib.util.spec_from_file_location('windows_analysis',Path(__file__).resolve().parents[2]/'ttp-composite/windows/coverage/analyze.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    answer=[];campaigns=[]
    for host in 'ABC':
        folder=root/host/'linux/composites';path=folder/'results.jsonl'
        if path.exists():
            for x in rows(path):
                r=dict(x);r['host']=host;r['os']='linux';r['mode']='negative' if r['case']=='negative' else 'control' if r['control'] else 'active'
                # For controls preserve both target-rule firing and any selected-rule firing.
                r['fired']=r['target_fired'] if r['mode']=='active' else bool(r.get('target_rule') and r['target_rule'] in r.get('matched_rules',[]))
                r['any_selected_control_alert']=r['mode']!='active' and r.get('negative_control_ok') is False
                answer.append(r)
        original_campaigns={}
        campaign_log=root/host/'windows/composites/campaigns.json'
        failed_originals={r['campaign'] for r in rows(campaign_log) if r.get('error')} if campaign_log.exists() else set()
        folders=[(p,'initial') for p in sorted((root/host/'windows/composites').glob('*-windows-*')) if p.is_dir()]
        folders += [(p,'replacement') for p in sorted((root/host/'windows/composites-replacements').glob('*-windows-*')) if p.is_dir()]
        for folder,role in folders:
            if not (folder/'health.json').exists():
                campaigns.append(dict(host=host,campaign=folder.name,error='incomplete: no health.json'));continue
            try:
                with contextlib.redirect_stdout(io.StringIO()):result=module.analyze(folder)
            except Exception as e:
                campaigns.append(dict(host=host,campaign=folder.name,error=str(e)));continue
            if role=='initial':original_campaigns[folder.name]=result
            else:
                original=original_campaigns.get(folder.name)
                if folder.name not in failed_originals or (original is not None and (original['healthy'] or any(r['valid'] for r in original['attempts']))):
                    raise ValueError(f'Replacement would repeat interpretable original outcomes: {host}/{folder.name}')
            campaigns.append(dict(host=host,campaign=folder.name,attempt_role=role,**{k:result[k] for k in ('healthy','complete','expected_attempts','recorded_attempts','counts')}))
            rep,cfg=folder.name.split('-',1)
            for x in result['attempts']:
                r=dict(x,os='windows',host=host,case=x['case_id'],config=cfg,repetition=int(rep),fired=bool(x['target_record_ids']),evidence_path=str(folder.relative_to(root)),attempt_role=role)
                answer.append(r)
    return answer,campaigns


def analyze_composites(data):
    groups=collections.defaultdict(list)
    for r in data:groups[(r['os'],r['case'],r['config'],r['mode'])].append(r)
    output=[]
    for key,attempts in sorted(groups.items()):
        valid=[r for r in attempts if r['valid']]
        output.append(dict(os=key[0],case=key[1],config=key[2],mode=key[3],attempts=len(attempts),invalid=len(attempts)-len(valid),
            **binomial(sum(r['fired'] for r in valid),len(valid)),
            hosts={h:binomial(sum(r['fired'] for r in valid if r['host']==h),sum(r['host']==h for r in valid)) for h in sorted({r['host'] for r in attempts})},
            any_selected_control_alerts=sum(r.get('any_selected_control_alert',False) for r in valid)))
    return output


def effective_slots(data):
    """Use explicitly identified replacements for matrix coverage, retain all data elsewhere."""
    def slot(r):return (r['os'],r['host'],r['case'],r['config'],r['repetition'],r['mode'])
    replacements={slot(r) for r in data if r.get('attempt_role')=='replacement'}
    for r in data:
        if r.get('attempt_role')!='replacement' and slot(r) in replacements:
            if r['valid']:raise ValueError('Cannot replace a valid observation')
            continue
        yield r


def matrix_audit(data, expected, modes=None):
    """Expected includes explicit OS/case/config cells, never inferred from successes."""
    observed=collections.Counter((r['os'],r['case'],r['config'],r.get('mode') if modes else None,r['host'],r['repetition']) for r in data)
    planned={(os,case,cfg,mode,host,rep) for os,case,cfg in expected
             for mode in (modes or [None]) for host in 'ABC' for rep in range(1,11)}
    return dict(expected_attempts=len(planned),recorded_attempts=len(data),
                missing=sorted(planned-observed.keys()),unexpected=sorted(observed.keys()-planned),
                duplicates=[dict(slot=k,count=n) for k,n in observed.items() if n>1])


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);p.add_argument('--bundles',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    primitives=primitive_rows(a.root);pc,composition,contrasts=analyze_primitives(primitives)
    repeated_cells,_,_=analyze_primitives([r for r in primitives if r['repetition']>1])
    composites,campaigns=composite_rows(a.root);cc=analyze_composites(composites)
    result=dict(primitive_attempts=len(primitives),primitive_valid=sum(r['valid'] for r in primitives),
      composite_attempts=len(composites),composite_valid=sum(r['valid'] for r in composites),
      primitive_cells=pc,post_first_primitive_cells=repeated_cells,composite_cells=cc,contrasts=contrasts,
      invalid_composite_attempts=[r for r in composites if not r['valid']],windows_campaigns=campaigns,
      windows_initial_batch_errors=[dict(r,host=h) for h in 'ABC' if (a.root/h/'windows/composites/campaigns.json').exists() for r in rows(a.root/h/'windows/composites/campaigns.json') if r.get('error')],
      expected=dict(primitive_cells=122,composite_active_cells=424,primitive_executions=3660,composite_executions=25680),
      limitations=['Pointwise run-level intervals and counts; not simultaneous suite-wide coverage.',
                  'Hosts are clusters. Three hosts cannot establish broad between-host precision.',
                  'Counts are planning estimates from exploratory data, not confirmatory conclusions.'])
    if a.bundles:
        expected_p=[];expected_c=[]
        for os in ('linux','windows'):
            manifest=read(a.bundles/f'telemetry-lab-0.3.0-{os}'/'manifest.json')
            expected_p.extend((os,case,cfg) for case in manifest['primitives'] for cfg in manifest['configs'])
            if os=='linux':cases=[r['id'] for r in read(Path(__file__).resolve().parents[2]/'ttp-composite/linux/coverage/manifest.json')['cases']]
            else:cases=[r['case_id'] for r in read(Path(__file__).resolve().parents[2]/'ttp-composite/windows/coverage/selection.json')['candidates'] if r['case_id']!='dns_onion']
            expected_c.extend((os,case,cfg) for case in cases for cfg in manifest['composite_configs'])
        result['matrix_audit']={'primitives':matrix_audit(primitives,expected_p),
             'composites':matrix_audit([r for r in effective_slots(composites) if r['mode']!='negative'],expected_c,['active','control']),
             'negative':matrix_audit([r for r in composites if r['mode']=='negative'],[('linux','negative',cfg) for cfg in read(a.bundles/'telemetry-lab-0.3.0-linux/manifest.json')['configs']],['negative'])}
    (a.output/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    (a.output/'primitive-event-composition.json').write_text(json.dumps(composition,indent=2)+'\n')
    for name,data in [('primitive-cells',pc),('composite-cells',cc),('runtime-contrasts',contrasts)]:
        if not data:continue
        fields=list(dict.fromkeys(k for r in data for k,v in r.items() if not isinstance(v,(dict,list))))
        with (a.output/f'{name}.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data)
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}))
    if pc:
        print('Volume precision counts:',[(r['os'],r['case'],r['config'],r['n'],round(r['cv'],4),r['volume_n']) for r in sorted(pc,key=lambda r:r['volume_n'],reverse=True)[:12]])
    print('Mixed composite cells:',[(r['os'],r['case'],r['config'],r['mode'],r['alerts'],r['n']) for r in cc if 0<r['alerts']<r['n']])

if __name__=='__main__':main()
