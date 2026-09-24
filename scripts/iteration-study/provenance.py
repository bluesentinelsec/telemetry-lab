"""Check that hosts and campaigns used identical frozen tooling and rule artifacts."""
import collections,hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]);r=Path(__file__).resolve().parents[2];records=[json.loads(p.read_text()) for p in (b/'normalized').glob('*-verification.json')]
sets=collections.defaultdict(set);unused_bootstrap_images={}
for x in records:
 os=x['os'];i=x['inventory'];sets[os+'/kernel'].add(i['kernel'])
 for c in i['components']:
  if os=='linux' and c['name']=='lab-substrate-image':
   # Bootstrap builds lab-substrate:13 separately on each host. This study's
   # composites instead load the immutable lab-falco-coverage:pilot archive;
   # primitives execute the verified native bundle directly, outside Docker.
   unused_bootstrap_images[x['host']]=c;continue
  if c.get('sha256'):sets[os+'/'+c['name']].add(c['sha256'].lower())
 if os=='linux':
  if x.get('packages_sha256'):sets['linux/installed_packages'].add(x['packages_sha256'])
  p=x['provenance'];sets['linux/container_image'].add(p['image_id']);sets['linux/falco_binary'].add(p['falco']['sha256'].lower())
  for name,digest in p['rules_sha256'].items():
   assert hashlib.sha256((r/'ttp-composite/linux/coverage/rules'/name).read_bytes()).hexdigest()==digest
   sets['linux/rule/'+name].add(digest)
 else:
  for inv in x['provenance']['inventories']:
   for name,v in inv.items():
    if name.endswith('sha256'):sets['windows/campaign/'+name].add(v.lower())
assert all(len(v)==1 for v in sets.values()),{k:sorted(v) for k,v in sets.items() if len(v)>1}
# Config digest from manifest.json in the frozen, pre-collection image archive.
if 'linux/container_image' in sets:assert sets['linux/container_image']=={'sha256:407332a08409b78e57c974a433749e6fc462e0381b09f67883a0c1b64c6f913e'}
result={k:next(iter(v)) for k,v in sorted(sets.items())}
(b/'analysis/provenance-unused-bootstrap-images.json').write_text(json.dumps(unused_bootstrap_images,indent=2)+'\n')
(b/'analysis/provenance-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
