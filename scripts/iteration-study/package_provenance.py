"""Reconcile a documented pre-measurement inventory timing difference explicitly."""
import datetime,hashlib,json

def collection_package_sha(base,record):
 digest=record.get('packages_sha256');path=base/'package-inventory-reconciliation.json'
 if not path.exists():return digest
 r=json.loads(path.read_text())
 if record['host']!=r['host']:return digest
 before=(base/r['initial_packages_file']).read_bytes();after=(base/r['collection_packages_file']).read_bytes()
 assert hashlib.sha256(before).hexdigest()==digest==r['initial_packages_sha256']
 assert hashlib.sha256(after).hexdigest()==r['collection_packages_sha256']
 assert set(after.splitlines())-set(before.splitlines())=={r['sole_added_package_line'].encode()}
 assert not set(before.splitlines())-set(after.splitlines())
 parse=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
 assert parse(r['installation_completed_utc'])<parse(record['collection_started'])==parse(r['collection_started_utc'])
 evidence=json.loads((base/r['timing_evidence']).read_text())['StandardOutputContent']
 stamp=r['installation_completed_utc'].replace('T',' ').removesuffix('Z')
 name,version=r['sole_added_package_line'].split('\t')
 assert f'{stamp} status installed {name}:amd64 {version}' in evidence
 return r['collection_packages_sha256']
