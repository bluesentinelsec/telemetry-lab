#!/usr/bin/env python3
"""Disposable-lab fault injection; never include this evidence in the study cohort."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from batch_composites import LinuxBatch,WindowsBatch
from engine import campaign,write_json

p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('output',type=Path);p.add_argument('--image',default='lab-falco-coverage:pilot')
a=p.parse_args();m=json.loads((a.bundle/'manifest.json').read_text());windows=m['os']=='windows'
cfg='windows-c-ucrt' if windows else 'linux-c-glibc';case='registry_run_key' if windows else 'sensitive_read'
plan=[dict(cohort='composites',os=m['os'],config=cfg,case=case,repetition=1,mode=mode) for mode in ('active','control')]
coverage=a.bundle/'ttp-composite/coverage'
if windows:
    class Fault(WindowsBatch):
        remaining=1
        def execute_batch(self,slots,folders,batch):
            original=self.analyzer.analyze
            def analyze(directory):
                if self.remaining:
                    self.remaining-=1
                    shutil.copy2(directory/'events.json',directory/'events-before-injection.json')
                    (directory/'events.json').write_text('{INJECTED-TRUNCATION')
                    write_json(batch/'injected-fault.json',dict(type='corrupt shared exported JSON after real collection'))
                return original(directory)
            self.analyzer.analyze=analyze
            try:return super().execute_batch(slots,folders,batch)
            finally:self.analyzer.analyze=original
    adapter=Fault(a.bundle,coverage,lambda slot:None)
else:
    class Fault(LinuxBatch):
        remaining=1
        def execute_batch(self,slots,folders,batch):
            original=self.cov.detector_state;calls=0
            def state():
                nonlocal calls
                calls+=1
                if self.remaining and calls==2:
                    self.remaining-=1
                    subprocess.run(['systemctl','stop',self.cov.SERVICE],check=True)
                    write_json(batch/'injected-fault.json',dict(type='stop Falco after real native executions before final health check'))
                return original()
            self.cov.detector_state=state
            try:return super().execute_batch(slots,folders,batch)
            finally:self.cov.detector_state=original
    adapter=Fault(coverage,a.image,lambda slot:None)
s=campaign(a.output,plan,adapter,batch_size=2,retry_delay=0)
assert s['complete'] and s['accepted']==2 and s['suspect']==2 and s['retries']==2,s
write_json(a.output/'validation.json',dict(passed=True,summary=s))
print('BATCH_REPLACEMENT_VALIDATED')
