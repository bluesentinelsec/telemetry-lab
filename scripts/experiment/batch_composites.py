"""Optional shared captures; independent native runs, classification and replacement."""
import csv
import datetime
import json
import re
import subprocess
import time
import uuid
from pathlib import Path
from composites import LinuxComposites, WindowsComposites
from engine import IntegrityError, MeasurementError, write_json


def event_ns(event):
    match=re.fullmatch(r'(.*?)(?:\.(\d+))?Z',event['time'])
    if not match:raise ValueError('Unexpected Falco event timestamp')
    return int(datetime.datetime.fromisoformat(match[1]+'+00:00').timestamp())*10**9+int((match[2] or '').ljust(9,'0')[:9])


class LinuxBatch(LinuxComposites):
    def batch_key(self,slot):return slot['repetition']

    def score_slot(self,slot,case,run,alerts,healthy,selected):
        return self.cov.score(case,run,alerts,healthy,selected)

    def prepare_batch(self,slots,folders,batch):
        for slot in slots:self.verify(slot)
        self.prepare(slots[0],folders[0])
        write_json(batch/'slots.json',slots)

    def execute_batch(self,slots,folders,batch):
        c=self.cov;containers=[];pending=[];results=[]
        try:
            before=c.detector_state()
            write_json(batch/'health-before.json',before)
            latest=c.command(['journalctl','-u',c.SERVICE,'-n','1','--show-cursor','--no-pager'])
            cursor=re.search(r'-- cursor: (.+)',latest).group(1)
        except (OSError,RuntimeError,subprocess.SubprocessError) as error:
            raise MeasurementError(f'Capture could not start: {error}') from error
        selected={x['rule'] for x in c.validate()['cases']}
        try:
            for slot,folder in zip(slots,folders):
                self.verify(slot)
                case=dict(self.cases[slot['case']],control=slot['mode']=='control')
                legacy=slot['cohort']=='legacy'
                dest=folder/'measurement';dest.mkdir()
                row=dict(native_started=False,case=case['id'],config=slot['config'],control=case['control'],
                         target_rule=case.get('rule'),container_id=None,batch=str(batch.relative_to(folder.parent.parent)))
                run=None
                try:
                    cid=c.command(['docker','create','--name','full-'+uuid.uuid4().hex[:16],
                        '--network','bridge' if legacy else 'none','--cap-add','SYS_PTRACE','--cap-add','NET_ADMIN',
                        '--security-opt','seccomp=unconfined','--tmpfs','/dev/shm:rw,exec,nosuid,size=16m',self.image])
                    containers.append(cid);row['container_id']=cid
                    c.command(['docker','start',cid])
                    for addr in (() if legacy else ('169.254.169.254/32','198.18.0.1/32')):
                        c.command(['docker','exec',cid,'ip','addr','add',addr,'dev','lo'])
                    c.command(['docker','exec',cid,f"/opt/coverage/{slot['config']}/coverage/fixture_prepare"])
                    # Timestamp boundary excludes fixture activity even if delivered later.
                    exe=f"/opt/coverage/{slot['config']}/"+("" if legacy else "coverage/")+case['id']
                    row.update(started_ns=time.time_ns(),executable=exe,native_started=True)
                    write_json(dest/'execution.json',row)
                    try:
                        run=subprocess.run(['docker','exec',cid,exe]+(['--control'] if case['control'] else []),
                                           capture_output=True,text=True,timeout=20)
                        row.update(returncode=run.returncode,timed_out=False,stdout=run.stdout,stderr=run.stderr)
                    except subprocess.TimeoutExpired as error:
                        def partial(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
                        row.update(returncode=None,timed_out=True,stdout=partial(error.stdout),stderr=partial(error.stderr))
                        run=None
                    row['ended_ns']=time.time_ns()
                    write_json(dest/'execution.json',row)
                    (dest/'stdout.txt').write_text(row['stdout']);(dest/'stderr.txt').write_text(row['stderr'])
                except (OSError,subprocess.SubprocessError) as error:
                    row['infrastructure_error']=repr(error)
                    write_json(dest/'execution.json',row)
                pending.append((slot,case,dest,row,run))
            # Keep containers alive until all asynchronous delivery is drained.
            time.sleep(3);error=None
            try:after=c.detector_state();healthy=c.health_ok(before,after)
            except Exception as exc:after=dict(error=repr(exc));healthy=False;error=repr(exc)
            try:log=c.command(['journalctl','-u',c.SERVICE,'--after-cursor',cursor,'-o','cat','--no-pager'])
            except Exception as exc:log='';healthy=False;error=repr(exc)
            (batch/'journal.jsonl').write_text(log+'\n')
            health=dict(before=before,after=after,healthy=healthy,error=error)
            write_json(batch/'health.json',health)
            for slot,case,dest,row,run in pending:
                alerts=([e for e in c.attributed_alerts(log,row['container_id']) if event_ns(e)>=row.get('started_ns',2**64)]
                        if row['container_id'] else [])
                write_json(dest/'alerts.json',alerts);write_json(dest/'health.json',health)
                if run is None:
                    result=(dict(status='behavior-failure',reason='Native execution timed out; requires investigation') if row.get('timed_out') else
                            dict(status='measurement-failure',reason=row.get('infrastructure_error','Infrastructure failed before native completion')))
                    result['measurement']=row
                else:
                    row.update(self.score_slot(slot,case,run,alerts,healthy,selected))
                    status='behavior-failure' if not row['behavior_ok'] else 'measurement-failure' if not healthy else 'valid'
                    result=dict(status=status,reason=None if status=='valid' else 'Native behavior failed' if status=='behavior-failure' else 'Shared capture health failed',measurement=row)
                self.verify(slot);write_json(dest/'result.json',result);results.append(result)
            return results
        finally:
            errors=[]
            for cid in containers:
                try:
                    clean=subprocess.run(['docker','rm','-f',cid],capture_output=True,text=True,timeout=30)
                    if clean.returncode:errors.append(dict(container=cid,stderr=clean.stderr))
                except Exception as error:errors.append(dict(container=cid,error=repr(error)))
            write_json(batch/'cleanup.json',dict(containers=containers,errors=errors))
            if errors:raise IntegrityError('Container cleanup failed; inspect batch evidence')


class WindowsBatch(WindowsComposites):
    def batch_key(self,slot):return slot['config'],slot['repetition']

    def prepare_batch(self,slots,folders,batch):
        for slot in slots:self.verify(slot)
        self.prepare(slots[0],folders[0])
        write_json(batch/'slots.json',slots)

    def execute_batch(self,slots,folders,batch):
        dest=batch/'measurement';plan=batch/'native-plan.json'
        write_json(plan,[dict(case_id=s['case'],mode=s['mode']) for s in slots])
        cmd=['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(self.coverage/'run-batch.ps1'),
             '-Programs',str(self.bundle/'ttp-composite'/slots[0]['config']/'coverage'),'-Output',str(dest),
             '-Fixtures',str(self.bundle/'ttp-composite/windows-c-ucrt/coverage/fixtures'),'-PlanFile',str(plan)]
        with (batch/'harness.stdout').open('w') as out,(batch/'harness.stderr').open('w') as err:
            completed=subprocess.run(cmd,stdout=out,stderr=err,timeout=1200)
        if any((dest/name).exists() for name in ('cleanup-error.txt','execution-error.txt','fixture-error.txt')):
            raise IntegrityError('Unsafe harness/fixture state; inspect batch logs')
        a=self.analyzer
        native=a.as_list(a.read_json(dest/'attempts.json')) if (dest/'attempts.json').exists() else []
        keys=[(r['case_id'],r['mode']) for r in native]
        wanted=[(s['case'],s['mode']) for s in slots]
        if sorted(keys)!=sorted(wanted):raise IntegrityError('Incomplete or duplicate native batch; inspect preserved attempts')
        # Preserve behavioral failures even if the shared collector also failed.
        error=None;events=[];alerts=[];rows={};healthy=False
        try:
            q=a.analyze(dest);healthy=q['healthy']
            rows={(r['case_id'],r['mode']):r for r in q['attempts']}
            events=a.as_list(a.read_json(dest/'events.json'))
            with (dest/'alerts.csv').open(encoding='utf-8-sig',newline='') as stream:alerts=list(csv.DictReader(stream))
        except (OSError,ValueError,KeyError,TypeError) as exc:error=repr(exc)
        # run.ps1 exits unsuccessfully for behavior failures. They do not taint
        # successful peers if capture health and the exact plan are independently valid.
        unexpected_exit=completed.returncode and all(r['behavior_ok'] for r in native)
        by_key={(r['case_id'],r['mode']):r for r in native};results=[]
        for slot,folder in zip(slots,folders):
            key=(slot['case'],slot['mode']);n=by_key[key];row=rows.get(key,{})
            d=folder/'measurement';d.mkdir()
            write_json(d/'native.json',n)
            write_json(d/'capture.json',dict(batch=str(batch.relative_to(folder.parent.parent)),healthy=healthy,error=error,harness_exit=completed.returncode))
            guids=set(row.get('process_guids',[]))
            owned=[e for e in events if e['fields'].get('ProcessGuid') in guids]
            ids={str(e['record_id']) for e in owned}
            write_json(d/'events.json',owned)
            write_json(d/'alerts.json',[e for e in alerts if e.get('RecordID') in ids])
            status=('behavior-failure' if not n['behavior_ok'] else 'measurement-failure'
                    if error or unexpected_exit or not healthy or not row.get('valid') else 'valid')
            result=dict(status=status,reason=None if status=='valid' else error or row.get('outcome') or status,measurement=row)
            write_json(d/'result.json',result);self.verify(slot);results.append(result)
        return results
