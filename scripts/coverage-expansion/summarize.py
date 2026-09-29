#!/usr/bin/env python3
"""Summarize retained experiment evidence without treating valid misses as faults."""
import argparse,collections,csv,hashlib,json
from pathlib import Path

def summarize(root):
 plan=json.loads((root/'plan.json').read_text());accepted=[json.loads(s) for s in (root/'accepted.jsonl').read_text().splitlines() if s.strip()]
 keys=lambda r:(r['config'],r['case'],r['mode'],r['repetition'])
 wanted={keys(r) for r in plan['slots']};actual=[keys(r) for r in accepted]
 assert len(actual)==len(set(actual)), 'Duplicate accepted logical runs'
 assert set(actual)<=wanted, 'Unplanned accepted logical runs'
 grouped=collections.defaultdict(collections.Counter);matched=collections.defaultdict(set)
 for record in accepted:
  assert record['status']=='valid'
  m=record['measurement'];key=(record['case'],record['config']);mode=record['mode']
  # Single-run Windows replacements retain the entire capture qualification;
  # batch measurements store the one attributed attempt directly.
  if record['os']=='windows' and 'attempts' in m:
   assert m['healthy'] and len(m['attempts'])==1
   m=m['attempts'][0]
  if record['os']=='windows':
   assert m['valid'] and (m['case_id'],m['mode'])==(record['case'],mode)
  if record['os']=='linux':
   outcome=('hit' if m['target_fired'] else 'valid-miss') if mode=='active' else ('control-pass' if m['negative_control_ok'] else 'control-alert')
   matched[key].update(m.get('matched_rules',[]))
  else:
   outcome={'alert':'hit','control-failed':'control-alert'}.get(m['outcome'],m['outcome']);matched[key].update(m.get('matched_selected_rule_ids',[]))
  grouped[key][outcome]+=1
 rows=[dict(case=case,config=cfg,**{k:n[k] for k in ['hit','valid-miss','control-pass','control-alert']},matched_rules=';'.join(sorted(matched[(case,cfg)]))) for (case,cfg),n in sorted(grouped.items())]
 report=dict(campaign=str(root),planned=len(wanted),accepted=len(actual),complete=set(actual)==wanted,
             outcomes=dict(sum(grouped.values(),collections.Counter())),cells=rows,
             campaign_summary=json.loads((root/'summary.json').read_text()),
             plan_sha256=hashlib.sha256((root/'plan.json').read_bytes()).hexdigest(),
             accepted_index_sha256=hashlib.sha256((root/'accepted.jsonl').read_bytes()).hexdigest())
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('campaign',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=summarize(a.campaign);a.output.mkdir(parents=True,exist_ok=True)
 (a.output/'qualification.json').write_text(json.dumps(r,indent=2)+'\n')
 if r['cells']:
  with (a.output/'qualification.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=r['cells'][0]);w.writeheader();w.writerows(r['cells'])
 print(json.dumps({k:r[k] for k in ['planned','accepted','complete','outcomes']},indent=2))
if __name__=='__main__':main()
