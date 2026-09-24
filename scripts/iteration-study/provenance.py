"""Check that hosts and campaigns used identical frozen tooling and rule artifacts."""
import collections,hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]);r=Path(__file__).resolve().parents[2];records=[json.loads(p.read_text()) for p in (b/'normalized').glob('*-verification.json')]
sets=collections.defaultdict(set)
for x in records:
 os=x['os'];i=x['inventory'];sets[os+'/kernel'].add(i['kernel'])
 for c in i['components']:
  if c.get('sha256'):sets[os+'/'+c['name']].add(c['sha256'].lower())
 if os=='linux':
  p=x['provenance'];sets['linux/container_image'].add(p['image_id']);sets['linux/falco_binary'].add(p['falco']['sha256'].lower())
  for name,digest in p['rules_sha256'].items():
   assert hashlib.sha256((r/'ttp-composite/linux/coverage/rules'/name).read_bytes()).hexdigest()==digest
   sets['linux/rule/'+name].add(digest)
 else:
  for inv in x['provenance']['inventories']:
   for name,v in inv.items():
    if name.endswith('sha256'):sets['windows/campaign/'+name].add(v.lower())
assert all(len(v)==1 for v in sets.values()),{k:sorted(v) for k,v in sets.items() if len(v)>1}
result={k:next(iter(v)) for k,v in sorted(sets.items())}
(b/'analysis/provenance-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
