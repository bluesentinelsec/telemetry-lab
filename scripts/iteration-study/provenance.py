"""Check that hosts and campaigns used identical frozen tooling and rule artifacts."""
import collections,hashlib,json,sys,tarfile
from pathlib import Path
from package_provenance import collection_package_sha
b=Path(sys.argv[1]);r=Path(__file__).resolve().parents[2];records=[json.loads(p.read_text()) for p in (b/'normalized').glob('*-verification.json')]
sets=collections.defaultdict(set);unused_bootstrap_images={};unused_packaging_metadata={}
loaded_rule_names={'falco_rules.yaml','falco-incubating_rules.yaml','falco-sandbox_rules.yaml'}
packaging_metadata={}
if (b/'inputs/support.tgz').exists():
 with tarfile.open(b/'inputs/support.tgz') as tar:
  for member in tar.getmembers():
   if member.isfile() and '/rules/._' in member.name:
    payload=tar.extractfile(member).read();assert payload[:4]==bytes.fromhex('00051607')
    packaging_metadata[Path(member.name).name]=hashlib.sha256(payload).hexdigest()
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
  if x.get('packages_sha256'):sets['linux/installed_packages_at_collection'].add(collection_package_sha(b,x))
  p=x['provenance'];sets['linux/container_image'].add(p['image_id']);sets['linux/falco_binary'].add(p['falco']['sha256'].lower())
  assert loaded_rule_names<=p['rules_sha256'].keys()
  for name,digest in p['rules_sha256'].items():
   if name.startswith('._') and name[2:] in loaded_rule_names:
    assert packaging_metadata.get(name)==digest,'Packaging metadata differs from frozen support archive'
    unused_packaging_metadata.setdefault(x['host'],{})[name]=digest
    continue
   assert name in loaded_rule_names,'Unexpected rule artifact: '+name
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
(b/'analysis/stage-package-inventory-hashes.json').write_text(json.dumps({r['host']:r.get('packages_sha256') for r in records},indent=2)+'\n')
(b/'analysis/provenance-unused-packaging-metadata.json').write_text(json.dumps(unused_packaging_metadata,indent=2)+'\n')
(b/'analysis/provenance-unused-bootstrap-images.json').write_text(json.dumps(unused_bootstrap_images,indent=2)+'\n')
(b/'analysis/provenance-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
