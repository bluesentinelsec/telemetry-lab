"""Audit staged artifacts and retain independent Sysmon image-hash observations."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[1]);rows=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for campaign in sorted(root.iterdir()):
 if not (campaign/'qualification.json').exists():continue
 build=read(campaign/'build-manifest.json');events=read(campaign/'events.json')
 attempts=read(campaign/'attempts.json') if (campaign/'attempts.json').exists() else []
 if isinstance(attempts,dict):attempts=[attempts]
 outcomes=read(campaign/'qualification.json')['attempts']
 programs={p['case_id']:p for p in build['programs']}
 for attempt,outcome in zip(attempts,outcomes):
  binary=programs[attempt['case_id']]
  starts=[e for e in events if e['event_id']==1 and str(e['fields'].get('ProcessId'))==str(attempt['process']['pid']) and e['fields'].get('ProcessGuid') in outcome['process_guids']]
  guids={e['fields']['ProcessGuid'] for e in starts}
  loads=[e for e in events if e['event_id']==7 and e['fields'].get('ProcessGuid') in guids]
  ucrt=[e['record_id'] for e in loads if e['fields'].get('ImageLoaded','').lower().endswith('\\ucrtbase.dll')]
  expected_cgo='1' if build['runtime']=='go-cgo' else '0'
  present='staged_sha256' in attempt
  linkage=(attempt['sha256']==binary['sha256'] and binary['go_build_settings']['CGO_ENABLED']==expected_cgo and (bool(ucrt) or expected_cgo=='0'))
  verified=present and attempt['staged_sha256']==binary['sha256'] and len(starts)==1 and linkage
  observed=[]
  for e in starts:
   match=re.search(r'(?:^|,)SHA256=([0-9a-fA-F]{64})(?:,|$)',e['fields'].get('Hashes',''))
   if match:observed.append(match[1].lower())
  rows.append({'campaign':campaign.name,'case_id':attempt['case_id'],'mode':attempt['mode'],'runtime':build['runtime'],'expected_sha256':binary['sha256'],'staged_sha256':attempt.get('staged_sha256'),'prelaunch_hash_recorded':present,'prelaunch_artifact_verified':verified,'linkage_verified':linkage,'start_records':[e['record_id'] for e in starts],'sysmon_sha256':observed,'sysmon_hash_matches':observed==[binary['sha256']],'ucrt_load_records':ucrt})
result={'attempts':len(rows),'prelaunch_hash_recorded':sum(r['prelaunch_hash_recorded'] for r in rows),'prelaunch_artifact_verified':sum(r['prelaunch_artifact_verified'] for r in rows),'linkage_verified':sum(r['linkage_verified'] for r in rows),'sysmon_hash_matches':sum(r['sysmon_hash_matches'] for r in rows),'sysmon_hash_differences':sum(not r['sysmon_hash_matches'] for r in rows),'records':rows}
(root/'runtime-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='records'})
sys.exit(0 if rows and all(r['linkage_verified'] and (r['prelaunch_artifact_verified'] or not r['prelaunch_hash_recorded']) for r in rows) else 1)
