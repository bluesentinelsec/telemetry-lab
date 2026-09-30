#!/usr/bin/env python3
"""Audit retained Linux 67-rule qualification evidence, including supersession."""
import argparse,collections,csv,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('raw',type=Path);p.add_argument('output',type=Path)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/'ttp-composite/linux/coverage/manifest.json').read_text())
phases=['full-matrix-01','web-recheck-01']
selected=[];summary={};hashes={}
for phase in phases:
 path=a.raw/phase/'attempts.jsonl'
 hashes[str(path.relative_to(a.raw))]=hashlib.sha256(path.read_bytes()).hexdigest()
 rows=[json.loads(x) for x in path.read_text().splitlines()]
 summary[phase]={'attempts':len(rows),'statuses':dict(collections.Counter(x['status'] for x in rows))}
 for row in rows:
  if row['status']!='valid':continue
  if phase=='full-matrix-01' and row['case']=='web_reverse_shell':continue
  assert phase!='web-recheck-01' or row['case']=='web_reverse_shell'
  row['phase']=phase;selected.append(row)
assert len(selected)==1112,len(selected)
assert len({(r['phase'],r['run_id']) for r in selected})==len(selected)
configs=sorted({r['config'] for r in selected});assert len(configs)==8
cases={c['id']:c['rule'] for c in manifest['cases']};assert len(cases)==67
records=[];misses=[];rule_counts=collections.defaultdict(dict)
for config in configs:
 baselines=[r for r in selected if r['config']==config and r['case']=='negative']
 assert len(baselines)==1
 assert baselines[0]['measurement']['negative_control_ok'] is True
 for case,target in cases.items():
  pair=[r for r in selected if r['config']==config and r['case']==case]
  active=[r for r in pair if r['mode']=='active'];controls=[r for r in pair if r['mode']=='control']
  expected=3 if case=='web_reverse_shell' else 1
  assert len(active)==len(controls)==expected,(config,case,len(active),len(controls))
  assert all(r['measurement']['negative_control_ok'] is True and not r['measurement']['matched_rules'] for r in controls),(config,case)
  assert all(r['measurement']['behavior_ok'] and r['measurement']['collection_ok'] for r in pair)
  counts=[]
  for r in active:
   alerts=json.loads((a.raw/r['phase']/r['evidence']/'measurement/alerts.json').read_text())
   counts.append(sum(x['rule']==target for x in alerts))
   assert bool(counts[-1])==r['measurement']['target_fired']
   if not counts[-1]:misses.append({'config':config,'case':case,'phase':r['phase'],'attempt_id':r['attempt_id']})
  rule_counts[case][config]=counts
  records.append({'config':config,'case':case,'target_rule':target,'valid_active':len(active),'target_hits':sum(n>0 for n in counts),'valid_misses':sum(n==0 for n in counts),'clean_controls':len(controls),'target_alert_counts':json.dumps(counts)})
assert sum(r['target_hits']>0 for r in records if r['config']=='linux-c-glibc')==67
assert {(r['config'],r['case']) for r in misses}=={('linux-go-cgo','reverse_shell'),('linux-go-static','reverse_shell')},misses
summary.update(selected_observations=len(selected),case_configuration_pairs=len(records),target_rules=67,supplied_rules=95,coverage_percent=round(6700/95,2),misses=misses,attempt_ledger_sha256=hashes)
summary['count_differences']={case:counts for case,counts in rule_counts.items() if len({tuple(sorted(set(v))) for v in counts.values()})>1}
(a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (a.output/'qualification.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
print(json.dumps(summary,indent=2))
