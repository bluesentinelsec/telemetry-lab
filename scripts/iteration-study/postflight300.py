"""Verify host packages, kernel, rules, binary, and image after collection."""
import concurrent.futures,json
from orchestrate300 import BASE,ssm,write
from package_provenance import collection_package_sha

assert (BASE/'ANALYSIS300_READY').exists()
fleet=json.loads((BASE/'fleet.json').read_text())
script='''python3 - <<'END'
import hashlib,json,platform,subprocess
from pathlib import Path
p=Path('/opt/pilot/evidence');inventory=json.loads((p/'inventory.json').read_text())
provenance=json.loads((p/'composites/provenance.json').read_text())
packages=subprocess.check_output(['dpkg-query','-W'])
initial=(p/'packages.txt').read_bytes()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
rules=Path('/opt/pilot/telemetry-lab-0.3.0-linux/ttp-composite/coverage/rules')
observed_rules={name:sha(rules/name) for name in provenance['rules_sha256']}
image=subprocess.check_output(['docker','image','inspect','lab-falco-coverage:pilot','--format','{{.Id}}'],text=True).strip()
result=dict(kernel=platform.release(),kernel_unchanged=platform.release()==inventory['kernel'],
 packages_sha256=hashlib.sha256(packages).hexdigest(),packages_match_stage_snapshot=packages==initial,
 falco_binary_sha256=sha(provenance['falco']['path']),
 falco_binary_unchanged=sha(provenance['falco']['path'])==provenance['falco']['sha256'],
 rules_sha256=observed_rules,rules_unchanged=observed_rules==provenance['rules_sha256'],
 image_id=image,image_unchanged=image==provenance['image_id'])
print(json.dumps(result))
END'''

def one(x):
 state=ssm(x['host'],'linux',x['instance'],x['bucket'],'postcollection-provenance',script)
 result=json.loads(state['StandardOutputContent']);result['host']=x['host']
 expected=json.loads((BASE/'normalized'/f"{x['host']}-linux-verification.json").read_text())
 result['packages_match_collection_inventory']=result['packages_sha256']==collection_package_sha(BASE,expected)
 write(BASE/'cleanup'/f"{x['host']}-postcollection-provenance.json",result)
 assert all(result[k] for k in ('kernel_unchanged','packages_match_collection_inventory','falco_binary_unchanged','rules_unchanged','image_unchanged')),result
 return result

with concurrent.futures.ThreadPoolExecutor(20) as pool:results=list(pool.map(one,fleet))
write(BASE/'analysis/postcollection-provenance.json',dict(hosts=len(results),all_measured_components_unchanged=True,records=results))
print('ALL_20_HOSTS_POSTCOLLECTION_PROVENANCE_VERIFIED',flush=True)
