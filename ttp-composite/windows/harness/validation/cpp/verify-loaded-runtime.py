import json,sys
from pathlib import Path, PureWindowsPath
root=Path(sys.argv[1]);rows=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for campaign in sorted(root.iterdir()):
 if not (campaign/'qualification.json').exists():continue
 build=read(campaign/'build-manifest.json');events=read(campaign/'events.json')
 attempts=read(campaign/'attempts.json');qualified=read(campaign/'qualification.json')['attempts']
 manifests={p['case_id']:p for p in build['programs']}
 dlls={d['name'].lower():d for d in build['dependent_dlls']}
 for attempt,outcome in zip(attempts,qualified):
  # Only the measured root; fixed child/helper modules are not C++ variants.
  starts=[e for e in events if e['event_id']==1 and str(e['fields'].get('ProcessId'))==str(attempt['process']['pid']) and e['fields'].get('ProcessGuid') in outcome['process_guids']]
  guids={e['fields']['ProcessGuid'] for e in starts}
  loads=[e for e in events if e['event_id']==7 and e['fields'].get('ProcessGuid') in guids]
  needed=set();queue=list(manifests[attempt['case_id']]['imports'])
  while queue:
   n=queue.pop().lower()
   if n in dlls and n not in needed:
    needed.add(n);queue.extend(dlls[n]['imports'])
  details=[]
  for n in sorted(needed):
   expected=str(PureWindowsPath(attempt['executable']).parent/n).lower()
   matching=[e for e in loads if e['fields'].get('ImageLoaded','').lower()==expected and ('SHA256='+dlls[n]['sha256']).lower() in e['fields'].get('Hashes','').lower()]
   details.append({'dll':n,'sha256':dlls[n]['sha256'],'record_ids':[e['record_id'] for e in matching],'verified':bool(matching)})
  other='libc++.dll' if build['runtime']=='libstdcxx' else 'libstdc++-6.dll'
  mixed=[e['record_id'] for e in loads if PureWindowsPath(e['fields'].get('ImageLoaded','')).name.lower()==other]
  rows.append({'campaign':campaign.name,'case_id':attempt['case_id'],'mode':attempt['mode'],'runtime':build['runtime'],'dependencies':details,'mixed_library_records':mixed,'verified':bool(needed) and len(starts)==1 and all(d['verified'] for d in details) and not mixed})
result={'attempts':len(rows),'verified':sum(r['verified'] for r in rows),'records':rows}
(root/'loaded-runtime-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='records'})
for r in rows:
 if not r['verified']:print(r)
sys.exit(0 if rows and all(r['verified'] for r in rows) else 1)
