#!/usr/bin/env python3
"""Fault-injection validation ONLY on a disposable lab, never study data.

Run after staging the ordinary collectors and immutable native bundle. Preserves
all real raw evidence alongside injected faults and asserts retry accounting.
"""
import argparse
import json
import shutil
from pathlib import Path
from engine import campaign, write_json
from primitives import Primitives, classify
from composites import LinuxComposites, WindowsComposites


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    m=json.loads((a.bundle/'manifest.json').read_text());windows=m['os']=='windows'
    cfg='windows-c-ucrt' if windows else 'linux-c-glibc'
    plan=[dict(cohort='primitives',os=m['os'],config=cfg,case='empty',repetition=1,mode='primitive')]
    reports={}
    class CorruptPrimitive(Primitives):
        remaining=1
        def execute(self,slot,folder):
            result=super().execute(slot,folder)
            if self.remaining and result['status']=='valid':
                self.remaining-=1
                raw=folder/'telemetry.jsonl';shutil.copy2(raw,folder/'telemetry-before-injection.txt')
                with raw.open('a') as f:f.write('{INJECTED-TRUNCATION\n')
                write_json(folder/'injected-fault.json',dict(type='truncated JSONL after real collection'))
                return classify(raw,0)
            return result
    for name,retries,faults in [('replace',3,1),('disabled',0,1),('exhaust',3,99)]:
        adapter=CorruptPrimitive(a.bundle,m['os'],'validation',lambda slot:None);adapter.remaining=faults
        result=campaign(a.output/('primitive-'+name),plan,adapter,max_retries=retries,retry_delay=0)
        assert result['complete']==(name=='replace'),result
        assert result['total_attempts']=={'replace':2,'disabled':1,'exhaust':4}[name],result
        reports['primitive-'+name]=result
    coverage=a.bundle/'ttp-composite/coverage'
    case='registry_run_key' if windows else 'sensitive_read'
    composite_plan=[dict(cohort='composites',os=m['os'],config=cfg,case=case,repetition=1,mode='active')]
    if windows:
        class FaultComposite(WindowsComposites):
            remaining=1
            def execute(self,slot,folder):
                result=super().execute(slot,folder)
                if self.remaining and result['status']=='valid':
                    self.remaining-=1
                    raw=folder/'measurement/events.json';shutil.copy2(raw,folder/'events-before-injection.json')
                    raw.write_text('{INJECTED-TRUNCATION')
                    write_json(folder/'injected-fault.json',dict(type='corrupted exported event JSON after real collection'))
                    # Exercise the real analyzer's inability to read damaged evidence.
                    try:self.analyzer.analyze(folder/'measurement')
                    except ValueError:return dict(status='measurement-failure',reason='Injected exported-event corruption')
                    raise AssertionError('Analyzer accepted corrupt data')
                return result
        adapter=FaultComposite(a.bundle,coverage,lambda slot:None)
    else:
        class FaultComposite(LinuxComposites):
            remaining=1
            def execute(self,slot,folder):
                original=self.cov.detector_state
                def state():
                    if self.remaining and (folder/'measurement/execution.json').exists():
                        self.remaining-=1
                        self.cov.command(['systemctl','stop',self.cov.SERVICE])
                        write_json(folder/'injected-fault.json',dict(type='stopped actual Falco after native completion'))
                    return original()
                self.cov.detector_state=state
                try:return super().execute(slot,folder)
                finally:self.cov.detector_state=original
        adapter=FaultComposite(coverage,'lab-falco-coverage:pilot',lambda slot:None)
    result=campaign(a.output/'composite-replace',composite_plan,adapter,retry_delay=0)
    assert result['complete'] and result['retries']>=1,result
    reports['composite-replace']=result
    write_json(a.output/'validation.json',reports)
    print('FAULT_INJECTION_VALIDATION_PASSED')

if __name__=='__main__':main()
