#!/usr/bin/env python3
"""Recheck collector-invalid attempts without replacing the original campaign.

Only successful behavior with failed collection health is eligible. Valid misses
are never retried. Each recheck is retained even if it is invalid again.
"""
import argparse
import json
import sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('bundle',type=Path);p.add_argument('campaign',type=Path);p.add_argument('output',type=Path)
p.add_argument('--image',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(a.bundle/'ttp-composite/coverage'))
import run as coverage
original=json.loads((a.campaign/'summary.json').read_text())['records']
image_id=coverage.command(['docker','image','inspect',a.image,'--format','{{.Id}}'])
if image_id != json.loads((a.campaign/'provenance.json').read_text())['image_id']:
    raise SystemExit('Rechecks must use the original immutable image')
cases={c['id']:c for c in coverage.validate()['cases']};cases['negative']={'id':'negative'}
failed=[r for r in original if not r['valid']]
if any(not r.get('behavior_ok') or r.get('collection_ok') is not False for r in failed):
    raise SystemExit('A failure needs diagnosis beyond collector health; no automatic recheck')
rows=[]
for index,r in enumerate(failed):
    case={**cases[r['case']]}
    if r.get('control'):case['control']=True
    dest=a.output/f"{index:04d}-{r['config']}-{r['case']}"
    result=coverage.execute(case,r['config'],dest,image_id)
    result['original_campaign']=str(a.campaign)
    result['original_container_id']=r['container_id']
    (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    rows.append(result);print(json.dumps(result),flush=True)
    (a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(0 if all(r['valid'] for r in rows) else 1)
