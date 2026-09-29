"""Retained pilot programs: execution/collection validation, not qualified positives."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from batch_composites import LinuxBatch
from composites import WindowsComposites
from engine import IntegrityError,MeasurementError,write_json

class LinuxLegacy(LinuxBatch):
    def __init__(self,coverage,image,verify):
        super().__init__(coverage,image,verify)
        m=json.loads((self.coverage.parent.parent/'manifest.json').read_text())
        self.cases={name:dict(id=name) for name in m['composites']}
        paths=[f'/opt/coverage/{cfg}/{name}' for cfg in m['configs'] for name in self.cases]
        inventory=self.cov.command(['docker','run','--rm','--network','none',self.image,'sha256sum',*paths])
        for line in inventory.splitlines():
            digest,name=line.split(maxsplit=1)
            if hashlib.sha256((self.coverage.parent/name.removeprefix('/opt/coverage/')).read_bytes()).hexdigest()!=digest:
                raise IntegrityError('Legacy image/bundle bytes differ')
        self.binary_inventory+='\n'+inventory
    def score_slot(self,slot,case,run,alerts,healthy,selected):
        behavior=run.returncode==0
        return dict(behavior_ok=behavior,collection_ok=healthy,valid=behavior and healthy,
                    qualification=False,matched_rules=sorted({a['rule'] for a in alerts}))
    def execute(self,slot,folder):
        batch=folder.parent.parent/'batches'/('single-'+folder.name);batch.mkdir(parents=True)
        return self.execute_batch([slot],[folder],batch)[0]

class WindowsLegacy(WindowsComposites):
    def batch_key(self,slot):return slot['repetition']
    def prepare_batch(self,slots,folders,batch):
        for s in slots:self.verify(s)
        self.prepare(slots[0],folders[0]);write_json(batch/'slots.json',slots)
    def execute(self,slot,folder):
        batch=folder.parent.parent/'batches'/('single-'+folder.name);batch.mkdir(parents=True)
        return self.execute_batch([slot],[folder],batch)[0]
    def execute_batch(self,slots,folders,batch):
        script=Path(__file__).with_name('legacy-windows.ps1')
        if not script.exists():script=Path(__file__).parent.parent/'e2e/legacy-windows.ps1'
        dest=batch/'measurement';plan=batch/'native-plan.json';write_json(plan,slots)
        cmd=['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script),
             '-Bundle',str(self.bundle),'-Output',str(dest),'-PlanFile',str(plan)]
        with (batch/'stdout').open('w') as out,(batch/'stderr').open('w') as err:
            execution=subprocess.run(cmd,stdout=out,stderr=err,timeout=1200)
        if (dest/'cleanup-error.txt').exists():raise IntegrityError('Legacy cleanup failed; inspect evidence')
        a=self.analyzer
        native=a.as_list(a.read_json(dest/'attempts.json')) if (dest/'attempts.json').exists() else []
        wanted={(s['config'],s['case']) for s in slots}
        if len(native)!=len(slots) or {(r['config'],r['case']) for r in native}!=wanted:
            raise IntegrityError('Legacy harness did not record the exact native plan')
        healthy=False;events=[];alerts=[];error=None
        try:
            h=a.read_json(dest/'health.json');events=a.as_list(a.read_json(dest/'events.json'))
            with (dest/'alerts.csv').open(encoding='utf-8-sig',newline='') as f:alerts=list(csv.DictReader(f))
            healthy=(not h['log_overwritten'] and h['sysmon_service']=='Running' and not a.as_list(h['error_events'])
                     and (dest/'detector-exit.txt').read_text(encoding='utf-8-sig').strip()=='0')
        except (OSError,ValueError,KeyError,TypeError) as exc:error=repr(exc)
        by_key={(r['config'],r['case']):r for r in native};results=[]
        for slot,folder in zip(slots,folders):
            n=by_key[(slot['config'],slot['case'])];ok=n['exit_code']==0 and not n['timed_out']
            attempt=dict(case_id=slot['case'],runtime=slot['config'],mode='active',rule_id='legacy-no-target',
                         executable=n['executable'],behavior_ok=ok,process=n)
            row=a.evaluate(attempt,events,alerts,healthy)
            guids=set(row['process_guids']);owned=[e for e in events if e['fields'].get('ProcessGuid') in guids]
            ids={str(e['record_id']) for e in owned};matches=[e for e in alerts if e.get('RecordID') in ids]
            row.update(qualification=False,matched_rule_ids=sorted({e['RuleID'] for e in matches}))
            d=folder/'measurement';d.mkdir();write_json(d/'native.json',n);write_json(d/'events.json',owned);write_json(d/'alerts.json',matches)
            write_json(d/'capture.json',dict(batch=str(batch.relative_to(folder.parent.parent)),healthy=healthy,error=error,harness_exit=execution.returncode))
            status='behavior-failure' if not ok else 'valid' if row['valid'] and not execution.returncode else 'measurement-failure'
            result=dict(status=status,reason=None if status=='valid' else error or status,measurement=row)
            self.verify(slot);write_json(d/'result.json',result);results.append(result)
        return results
