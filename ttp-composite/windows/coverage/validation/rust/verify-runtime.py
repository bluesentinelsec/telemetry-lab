"""Audit staged executables and loaded runtime DLLs without rewriting Sysmon hashes."""
import json,re,sys
from pathlib import Path, PureWindowsPath
root=Path(sys.argv[1]);rows=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for campaign in sorted(root.iterdir()):
 if not (campaign/'qualification.json').exists():continue
 build=read(campaign/'build-manifest.json');events=read(campaign/'events.json')
 attempts=read(campaign/'attempts.json') if (campaign/'attempts.json').exists() else []
 outcomes=read(campaign/'qualification.json')['attempts']
 programs={p['case_id']:p for p in build['programs']};dlls={d['name'].lower():d for d in build['dependent_dlls']}
 assert len(attempts)==len(outcomes)
 for attempt,outcome in zip(attempts,outcomes):
  binary=programs[attempt['case_id']]
  starts=[e for e in events if e['event_id']==1 and str(e['fields'].get('ProcessId'))==str(attempt['process']['pid']) and e['fields'].get('ProcessGuid') in outcome['process_guids']]
  guids={e['fields']['ProcessGuid'] for e in starts}
  loads=[e for e in events if e['event_id']==7 and e['fields'].get('ProcessGuid') in guids]
  needed=set();queue=list(binary['imports'])
  while queue:
   n=queue.pop().lower()
   if n in dlls and n not in needed:needed.add(n);queue.extend(dlls[n]['imports'])
  details=[]
  for n in sorted(needed):
   path=str(PureWindowsPath(attempt['executable']).parent/n).lower()
   matching=[e for e in loads if e['fields'].get('ImageLoaded','').lower()==path and ('SHA256='+dlls[n]['sha256']).lower() in e['fields'].get('Hashes','').lower()]
   details.append({'dll':n,'sha256':dlls[n]['sha256'],'record_ids':[e['record_id'] for e in matching],'verified':bool(matching)})
  staged=attempt.get('staged_sha256')==binary['sha256']==attempt['sha256']
  observed=[]
  for e in starts:
   match=re.search(r'(?:^|,)SHA256=([0-9a-fA-F]{64})(?:,|$)',e['fields'].get('Hashes',''))
   if match:observed.append(match[1].lower())
  crt_loads=[{'record_id':e['record_id'],'path':e['fields'].get('ImageLoaded',''),'hashes':e['fields'].get('Hashes','')} for e in loads if PureWindowsPath(e['fields'].get('ImageLoaded','')).name.lower().startswith(('ucrtbase','vcruntime','msvcrt'))]
  # Static CRT means no direct dynamic CRT linkage. Windows APIs and fixed
  # fixture modules may independently load system DLLs; report those verbatim.
  rows.append({'campaign':campaign.name,'case_id':attempt['case_id'],'mode':attempt['mode'],'runtime':build['runtime'],'expected_sha256':binary['sha256'],'staged_sha256':attempt.get('staged_sha256'),'staged_verified':staged,'start_records':[e['record_id'] for e in starts],'sysmon_sha256':observed,'sysmon_hash_matches':observed==[binary['sha256']],'dependencies':details,'crt_loads':crt_loads,'verified':staged and len(starts)==1 and all(d['verified'] for d in details)})
result={'attempts':len(rows),'verified':sum(r['verified'] for r in rows),'staged_verified':sum(r['staged_verified'] for r in rows),'sysmon_hash_differences':sum(not r['sysmon_hash_matches'] for r in rows),'records':rows}
(root/'runtime-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='records'})
for r in rows:
 if not r['verified']:print(r)
sys.exit(0 if rows and all(r['verified'] for r in rows) else 1)
