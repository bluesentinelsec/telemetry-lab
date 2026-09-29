#!/usr/bin/env python3
"""Reproduce corpus integrity checks and rule-level expansion disposition tables."""
import argparse,collections,csv,hashlib,json,re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(value):
 if isinstance(value,dict):
  for key,child in value.items():
   if key not in ('condition','timeframe') and not isinstance(child,(dict,list)):
    yield key.split('|')[0]
   elif isinstance(child,list) and all(not isinstance(x,(dict,list)) for x in child):yield key.split('|')[0]
   else:yield from fields(child)
 elif isinstance(value,list):
  for child in value:yield from fields(child)
def event_ids(value):
 if isinstance(value,dict):
  for key,v in value.items():
   if key=='EventID':yield from v if isinstance(v,list) else [v]
   else:yield from event_ids(v)
 elif isinstance(value,list):
  for child in value:yield from event_ids(child)
def write(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('hayabusa_rules',type=Path);p.add_argument('--output',type=Path,default=ROOT/'docs/coverage-expansion');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 new=json.loads((ROOT/'docs/coverage-expansion/windows-plan.json').read_text());selected={x['rule_id'] for x in new};catalog=json.loads((ROOT/'ttp-composite/windows/coverage/selection.json').read_text());existing={x['rule_id'] for x in catalog['candidates']}-selected;deferred={x['rule_id']:x for x in catalog.get('deferred_candidates',[])}
 rows=[]
 for r in csv.DictReader((ROOT/'ttp-composite/windows/coverage/rule-inventory.csv').open()):
  path=a.hayabusa_rules/r['path'];assert sha(path)==r['sha256'],path
  docs=list(yaml.safe_load_all(path.read_text()));det=[d.get('detection',{}) for d in docs if isinstance(d,dict)];fs=set(fields(det));ids=set(event_ids(det))
  if r['rule_id'] in selected:disposition='onboard';reason='Reviewed predicate and fixed cross-language behavior in windows-plan.json'
  elif r['rule_id'] in existing:disposition='existing';reason='Previously qualified selected target'
  elif r['rule_id'] in deferred:disposition='deferred-validation';reason=deferred[r['rule_id']]['decision']
  elif r['rule_id']=='29e2035f-b91f-3c35-9a7a-087b864f6d3b':disposition='excluded';reason='User explicitly removed onion DNS test'
  elif r['static_scope_eligible'].lower()!='true':disposition='outside-current-detector-profile';reason=r['exclusion_reasons'] or 'Not enabled for current Sysmon input'
  else:
   disposition='deferred-triage'
   constraints=[]
   for label,keys in [('process identity/ancestry',{'Image','SourceImage','TargetImage','ParentImage','OriginalFileName','Company'}),('command line',{'CommandLine','ParentCommandLine'}),('network destination policy',{'DestinationIp','DestinationHostname','DestinationPort'}),('runtime stack or memory evidence',{'CallTrace','StartAddress','StartModule','StartFunction','GrantedAccess'}),('file/registry/pipe indicators',{'TargetFilename','TargetObject','Details','PipeName'}),('domain/resolver indicators',{'QueryName','QueryResults'})]:
    if fs&keys:constraints.append(label)
   reason='Separate fixture review required: '+', '.join(constraints or ['event/provider-specific predicates'])+'; not declared infeasible'
  rows.append({**r,'disposition':disposition,'audit_reason':reason,'event_ids':json.dumps(sorted(ids,key=str)),'predicate_fields':';'.join(sorted(fs))})
 assert len(rows)==4987
 write(a.output/'windows-rule-audit.csv',rows)
 linux=json.loads((ROOT/'docs/coverage-expansion/linux-plan.json').read_text());newlinux={x['title']:x for x in linux};rows2=[]
 for r in csv.DictReader((ROOT/'ttp-composite/linux/coverage/rule-inventory.csv').open()):
  if r['rule'] in newlinux:disposition='onboard';reason=newlinux[r['rule']]['behavior']
  elif r['selection']=='selected':disposition='existing';reason='Previously qualified selected target'
  elif r['stock_enabled']=='False':disposition='deferred-disabled';reason='Preserve stock enablement; separate detector profile required'
  else:disposition='deferred';reason=r['reason']+'; separate fixture and behavior contract required'
  rows2.append({**r,'audit_disposition':disposition,'audit_reason':reason})
 write(a.output/'linux-rule-audit.csv',rows2)
 print(json.dumps(dict(windows=collections.Counter(x['disposition'] for x in rows),linux=collections.Counter(x['audit_disposition'] for x in rows2)),indent=2))
if __name__=='__main__':main()
