"""Account for every planned slot, including invalid observations and missing executions."""
import os,collections,json,sys
from pathlib import Path
b=Path(sys.argv[1]);root=Path(__file__).resolve().parents[2]
bundles=Path(os.environ.get('TELEMETRY_STUDY_BUNDLES','/Users/michaellong/telemetry-lab-data/release-0.3.0-2026-09-22/release'))
expected=set();actual=collections.Counter();invalid=collections.Counter();unique_containers=set();container_duplicates=[]
for os in ('linux','windows'):
 m=json.loads((bundles/f'telemetry-lab-0.3.0-{os}/manifest.json').read_text())
 if os=='linux':
  selection=json.loads((root/'ttp-composite/linux/coverage/manifest.json').read_text());cases=[x['id'] for x in selection['cases']];configs=selection['configs']
 else:
  selection=json.loads((root/'ttp-composite/windows/coverage/selection.json').read_text());cases=[x['case_id'] for x in selection['candidates'] if x['case_id']!='dns_onion'];configs=m['composite_configs']
 for h in range(1,11):
  host=f'H{h:02}'
  for rep in range(1,22):
   for cfg in m['configs']:
    for case in m['primitives']:expected.add((host,os,'primitives',cfg,case,'primitive',rep))
   for cfg in configs:
    for case in cases:
     for mode in ('active','control'):expected.add((host,os,'composites',cfg,case,mode,rep))
    if os=='linux':expected.add((host,os,'composites',cfg,'negative','negative',rep))
 for cohort in ('primitives','composites'):
  for p in (b/'normalized').glob(f'*-{os}-{cohort}.jsonl'):
   for line in p.read_text().splitlines():
    r=json.loads(line);slot=(r['host'],os,cohort,r['config'],r['case'],r.get('mode','primitive'),r['repetition']);actual[slot]+=1
    if not r['valid']:invalid[(os,cohort,r.get('outcome','invalid'))]+=1
    if r.get('container_id'):
     if r['container_id'] in unique_containers:container_duplicates.append(r['container_id'])
     unique_containers.add(r['container_id'])
result=dict(expected_slots=len(expected),physical_records=sum(actual.values()),unique_recorded_slots=len(actual),missing=sorted(expected-actual.keys()),unexpected=sorted(actual.keys()-expected),duplicates=[dict(slot=k,count=v) for k,v in actual.items() if v>1],invalid=[dict(os=k[0],cohort=k[1],reason=k[2],count=v) for k,v in invalid.items()],unique_container_ids=len(unique_containers),duplicate_container_ids=container_duplicates)
(b/'analysis/slot-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in result.items()},indent=2))
if result['unexpected'] or result['duplicates'] or container_duplicates:raise SystemExit('Unexpected or duplicate slots')
