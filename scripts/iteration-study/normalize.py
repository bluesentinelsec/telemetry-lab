#!/usr/bin/env python3
"""Verify and normalize one host archive at a time, preserving compressed raw evidence."""
import os,collections,contextlib,fcntl,hashlib,importlib.util,io,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/Users/michaellong/telemetry-lab-data/iteration-study-2026-09-23')
BUNDLES=Path(os.environ.get('TELEMETRY_STUDY_BUNDLES','/Users/michaellong/telemetry-lab-data/release-0.3.0-2026-09-22/release'))
spec=importlib.util.spec_from_file_location('wc',ROOT/'ttp-composite/windows/coverage/analyze.py');wc=importlib.util.module_from_spec(spec);spec.loader.exec_module(wc)

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rows(p):
 if p.suffix=='.jsonl':return [json.loads(x) for x in p.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
 x=read(p);return x if isinstance(x,list) else [x]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write_rows(p,rs):p.write_text(''.join(json.dumps(r)+'\n' for r in rs))

def normalize(folder,host,os,out):
 manifest=read(BUNDLES/f'telemetry-lab-0.3.0-{os}/files.sha256.json')
 prim=[];comp=[];campaigns=[];check=collections.Counter();provenance={};invalid_health_batches=[]
 path=folder/'primitives'/('results.jsonl' if os=='linux' else 'results.json')
 if path.exists():
  for row in rows(path):
   raw=rows(folder/'primitives'/row['raw']);ev=[e for e in raw if e.get('record')=='event'];su=[e for e in raw if e.get('record')=='summary'];meta=[e for e in raw if e.get('record')=='meta']
   key=f"ttp-primitives/{row['config']}/{row['case']}"+('.exe' if os=='windows' else '')
   assert manifest[key].lower()==row['binary_sha256'].lower(),key
   assert len(meta)==1 and meta[0]['meta']['host']==host and meta[0]['meta']['config']==row['config']
   assert str(meta[0]['meta']['iteration'])==str(row['repetition'])
   assert su==row['summary'] and len(su)==1 and len(ev)==su[0]['total_events'],row
   counts=dict(collections.Counter(e.get('syscall','unknown') if e['kind']=='syscall' else '@'+e['kind'] for e in ev))
   if os=='linux':assert counts==row['event_counts']
   row.update(host=host,os=os,event_counts=counts,raw_events=len(ev),raw_sha256=sha(folder/'primitives'/row['raw']))
   prim.append(row);check['primitive_raw_verified']+=1
 if os=='linux' and (folder/'composites/results.jsonl').exists():
  cp=folder/'composites';provenance=read(cp/'provenance.json')
  for line in provenance['binaries'].splitlines():
   digest,p=line.split(maxsplit=1);key='ttp-composite/'+p.removeprefix('/opt/coverage/');assert manifest[key].lower()==digest.lower(),key
   check['container_binary_hashes_verified']+=1
  health={}
  for p in cp.glob('batch-*/health.json'):
   h=read(p);b,a=h['before'],h['after'];good=b['service']==a['service'] and b['counters'].keys()==a['counters'].keys() and all(a['counters'][k]>=v and ('drops' not in k or a['counters'][k]==v) for k,v in b['counters'].items());health[p.parent.name]=good
   check['health_batches']+=1;check['healthy_batches']+=int(good)
   if not good:invalid_health_batches.append(dict(batch=p.parent.name,service_before=b['service'],service_after=a['service'],counter_changes={k:[b['counters'].get(k),a['counters'].get(k)] for k in b['counters'].keys()|a['counters'].keys() if k not in b['counters'] or k not in a['counters'] or a['counters'][k]<b['counters'][k] or ('drops' in k and a['counters'][k]!=b['counters'][k])}))
  for i,row in enumerate(rows(cp/'results.jsonl')):
   p=cp/row['batch']/f"{i:05d}-{row['config']}-{row['case']}";assert read(p/'result.json')==row
   assert not row['valid'] or health[row['batch']]
   row.update(host=host,os=os,mode='negative' if row['case']=='negative' else 'control' if row['control'] else 'active')
   row['fired']=row['target_fired'] if row['mode']=='active' else bool(row.get('target_rule') and row['target_rule'] in row.get('matched_rules',[]))
   row['any_selected_control_alert']=row['mode']!='active' and row.get('negative_control_ok') is False
   row['seconds']=(row['ended_ns']-row['started_ns'])/1e9 if 'ended_ns' in row and 'started_ns' in row else None
   comp.append(row);check['composite_rows_verified']+=1
 elif os=='windows':
  for cp in sorted([*(folder/'composites').glob('*-windows-*'),*(folder/'composites-resumed').glob('*-windows-*')]):
   if not cp.is_dir():continue
   rep,cfg=cp.name.split('-',1)
   if cp.parent.name=='composites-resumed':
    assert (cp/'prior-attempts.json').read_bytes()==(folder/'composites'/cp.name/'attempts.json').read_bytes(),'Resumption did not preserve original attempts'
   if not (cp/'health.json').exists():campaigns.append(dict(campaign=cp.name,error='No health.json'));continue
   with contextlib.redirect_stdout(io.StringIO()):result=wc.analyze(cp)
   original=rows(cp/'attempts.json');omap={(x['case_id'],x['mode']):x for x in original}
   for x in original:
    key=f"ttp-composite/{cfg}/coverage/{x['case_id']}.exe"
    assert x['sha256'].lower()==manifest[key].lower(),key
    assert x.get('staged_sha256','').lower()==x['sha256'].lower(),key
    check['native_composite_hashes_verified']+=1
   campaigns.append(dict(campaign=cp.name,segment=cp.parent.name,**{k:result[k] for k in ('healthy','complete','expected_attempts','recorded_attempts','counts')}))
   for r in result['attempts']:
    x=omap[(r['case_id'],r['mode'])]
    r.update(host=host,os=os,config=cfg,case=r['case_id'],repetition=int(rep),fired=bool(r['target_record_ids']),segment=cp.parent.name,started_epoch=wc.timestamp(x['process']['start_utc']).timestamp(),seconds=(wc.timestamp(x['process']['end_utc'])-wc.timestamp(x['process']['start_utc'])).total_seconds())
    comp.append(r);check['composite_rows_verified']+=1
  provenance={'inventories':[read(p) for p in [*(folder/'composites').glob('*/inventory.json'),*(folder/'composites-resumed').glob('*/inventory.json')]]}
 slots=[(r['case'],r['config'],r['repetition']) for r in prim];assert len(set(slots))==len(slots)
 slots=[(r['case'],r['config'],r['mode'],r['repetition']) for r in comp];assert len(set(slots))==len(slots)
 write_rows(out/f'{host}-{os}-primitives.jsonl',prim);write_rows(out/f'{host}-{os}-composites.jsonl',comp)
 result=dict(host=host,os=os,counts=dict(check),primitive_count=len(prim),composite_count=len(comp),primitive_invalid=sum(not r['valid'] for r in prim),composite_invalid=sum(not r['valid'] for r in comp),campaigns=campaigns,provenance=provenance,inventory=read(folder/'inventory.json'),collection_started=(folder/'collection-started.txt').read_text(encoding='utf-8-sig').strip() if (folder/'collection-started.txt').exists() else None,collection_ended=(folder/'collection-ended.txt').read_text(encoding='utf-8-sig').strip() if (folder/'collection-ended.txt').exists() else None)
 result['invalid_health_batches']=invalid_health_batches
 result['collection_exit_codes']={p.name:p.read_text(encoding='utf-8-sig').strip() for p in folder.glob('*.exit')}
 campaigns_file=folder/'composites/campaigns.json'
 result['campaign_execution_errors']=[r for r in rows(campaigns_file) if r.get('error')] if campaigns_file.exists() else []
 interruption=folder/'composites/interruption-reconciliation.json'
 result['interruption_reconciliation']=read(interruption) if interruption.exists() else None
 for name in ('cleanup-catch-fix','windows-resumption-complete','residual-probe-cleanup','residual-carrier-cleanup'):
  path=folder/(name+'.json')
  if path.exists():result[name.replace('-','_')]=read(path)
 (out/f'{host}-{os}-verification.json').write_text(json.dumps(result,indent=2))
 print(host,os,'normalized',len(prim),len(comp),result['composite_invalid'],flush=True)

if __name__=='__main__':
 with (BASE/'.normalization.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  out=BASE/'normalized';out.mkdir(exist_ok=True)
  for archive in sorted((BASE/'archives').glob('H??-*.tar.gz')):
   host,os=archive.name.removesuffix('.tar.gz').split('-')
   if (out/f'{host}-{os}-verification.json').exists():continue
   receipt=read(archive.with_name(archive.name.removesuffix('.tar.gz')+'-verified.json'));assert sha(archive)==receipt['sha256']
   with tempfile.TemporaryDirectory(prefix='iteration-study-',dir=BASE) as tmp:
    subprocess.run(['tar','-xzf',str(archive),'-C',tmp],check=True)
    normalize(Path(tmp),host,os,out)
