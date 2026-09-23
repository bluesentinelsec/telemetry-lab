#!/usr/bin/env python3
"""Independently check raw primitive counts, native hashes and Linux batch health."""
import argparse,collections,json
from pathlib import Path
from analyze import read,rows
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('bundles',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
counts=collections.Counter();images=set();falco=set();rule_sets=[];primitive_slots=set();container_ids=set()
for host in 'ABC':
 for os in ['linux','windows']:
  bundle=a.bundles/f'telemetry-lab-0.3.0-{os}'
  manifest=read(bundle/'files.sha256.json')
  folder=a.root/host/os/'primitives'
  path=folder/('results.jsonl' if os=='linux' else 'results.json')
  if not path.exists():continue
  for r in rows(path):
   slot=(host,os,r['config'],r['case'],r['repetition']);assert slot not in primitive_slots,slot;primitive_slots.add(slot)
   artifact=f"ttp-primitives/{r['config']}/{r['case']}"+('.exe' if os=='windows' else '')
   assert r['binary_sha256'].lower()==manifest[artifact].lower(),artifact
   data=rows(folder/r['raw']);events=[x for x in data if x.get('record')=='event'];summaries=[x for x in data if x.get('record')=='summary'];meta=[x for x in data if x.get('record')=='meta']
   assert len(summaries)==len(meta)==1,slot
   assert summaries==r['summary'],slot
   assert len(events)==summaries[0]['total_events'],slot
   assert meta[0]['meta']['config']==r['config'],slot
   assert str(meta[0]['meta']['iteration'])==str(r['repetition']),slot
   assert meta[0]['meta']['host']==host,slot
   if os=='linux':
    actual=collections.Counter(x.get('syscall','unknown') if x['kind']=='syscall' else '@'+x['kind'] for x in events)
    assert dict(actual)==r['event_counts'],slot
   counts[os+'_primitive_raw_verified']+=1
 folder=a.root/host/'linux/composites'
 if not (folder/'provenance.json').exists():continue
 provenance=read(folder/'provenance.json');images.add(provenance['image_id']);falco.add(provenance['falco']['sha256']);rule_sets.append(provenance['rules_sha256'])
 native_manifest=read(a.bundles/'telemetry-lab-0.3.0-linux/files.sha256.json')
 for line in provenance['binaries'].splitlines():
  digest,path=line.split(maxsplit=1)
  assert path.startswith('/opt/coverage/'),path
  key='ttp-composite/'+path.removeprefix('/opt/coverage/')
  assert native_manifest[key].lower()==digest.lower(),key
  counts['linux_container_binary_hashes_verified']+=1
 for path in folder.glob('batch-*/health.json'):
  h=read(path);before,after=h['before'],h['after']
  good=before['service']==after['service'] and before['counters'].keys()==after['counters'].keys() and all(after['counters'][k]>=v and ('drops' not in k or after['counters'][k]==v) for k,v in before['counters'].items())
  counts['linux_health_batches']+=1;counts['linux_healthy_batches']+=int(good)
 for i,r in enumerate(rows(folder/'results.jsonl')):
  assert r['container_id'] not in container_ids;container_ids.add(r['container_id'])
  dest=folder/r['batch']/f"{i:05d}-{r['config']}-{r['case']}"
  assert read(dest/'result.json')==r,(host,i)
  counts['linux_composite_records_verified']+=1
assert len(images)<=1,'Container images differ across hosts'
assert len(falco)<=1,'Falco binaries differ across hosts'
assert not rule_sets or all(x==rule_sets[0] for x in rule_sets),'Linux rules differ across hosts'
result=dict(counts=counts,image_ids=sorted(images),falco_sha256=sorted(falco),linux_rules_sha256=rule_sets[0] if rule_sets else {},primitive_slots=len(primitive_slots),unique_composite_containers=len(container_ids))
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['counts']))
