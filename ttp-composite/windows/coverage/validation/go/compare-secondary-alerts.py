import json,csv,collections,sys
from pathlib import Path
root=Path(sys.argv[1]);matrix={};titles={}
for d in root.glob('*-02'):
 if not (d/'qualification.json').exists() or 'onion' in d.name:continue
 q=json.loads((d/'qualification.json').read_text());events=json.loads((d/'events.json').read_text(encoding='utf-8-sig'))
 alerts=list(csv.DictReader((d/'alerts.csv').open(encoding='utf-8-sig',newline='')))
 for a in alerts:titles[a['RuleID']]=a.get('RuleTitle','')
 for row in q['attempts']:
  ids={str(e['record_id']) for e in events if e['fields'].get('ProcessGuid') in row['process_guids']}
  counts=collections.Counter(a['RuleID'] for a in alerts if a.get('RecordID') in ids)
  matrix[(row['case_id'],row['mode'],row['runtime'])]=counts
rows=[]
for case,mode,_ in sorted(matrix):
 if (case,mode,'go-cgo') not in matrix or (case,mode,'go-static') not in matrix:continue
 key=(case,mode)
 if any((r['case_id'],r['mode'])==key for r in rows):continue
 left=matrix[(case,mode,'go-cgo')];right=matrix[(case,mode,'go-static')]
 if left!=right:rows.append({'case_id':case,'mode':mode,'go_cgo':dict(left),'go_static':dict(right)})
result={'scope':'Exploratory all-rule alert counts attributable to the measured process/allowed descendants in complete -02 campaigns; not causal runtime attribution.','paired_case_modes':len(matrix)//2,'differences':rows,'titles':{k:titles[k] for r in rows for side in ['go_cgo','go_static'] for k in r[side]}}
(root/'secondary-alert-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
