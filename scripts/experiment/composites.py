"""One independently attributed active/control execution per logical run."""
import importlib.util
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
from pathlib import Path
from engine import IntegrityError, MeasurementError, write_json


def load(path, name):
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class LinuxComposites:
    def __init__(self, coverage, image, verify):
        self.coverage=Path(coverage);self.verify=verify
        self.cov=load(self.coverage/'run.py','linux_coverage')
        self.image=self.cov.command(['docker','image','inspect',image,'--format','{{.Id}}'])
        self.expected=self.cov.detector_provenance()
        self.cases={c['id']:c for c in self.cov.validate()['cases']}
        self.cases['negative']={'id':'negative'}
        manifest=self.cov.validate()
        paths=['/opt/coverage/'+cfg+'/coverage/'+name for cfg in manifest['configs']
               for name in list(self.cases)+['fixture_prepare']]
        self.binary_inventory=self.cov.command(['docker','run','--rm','--network','none',self.image,'sha256sum',*paths])
        for line in self.binary_inventory.splitlines():
            digest,name=line.split(maxsplit=1)
            relative=name.removeprefix('/opt/coverage/')
            if relative==name:raise IntegrityError('Unexpected image inventory path')
            local=self.coverage.parent/relative
            if hashlib.sha256(local.read_bytes()).hexdigest()!=digest:
                raise IntegrityError('Container program differs from frozen bundle: '+relative)

    def prepare(self, slot, folder, retry=False):
        self.verify(slot)
        try:
            before=self.cov.detector_state()
        except Exception as error:
            before={'error':repr(error)}
        write_json(folder/'recovery.json',dict(before=before,retry=retry,expected=self.expected))
        if retry or 'error' in before:
            # Restart only the exact pinned binary; never install or rebuild it here.
            try:
                result=subprocess.run(['env','FALCO_BIN='+self.expected['path'],'bash',str(self.coverage/'setup-detector.sh')],capture_output=True,text=True,timeout=120)
            except (OSError,subprocess.SubprocessError) as error:
                raise MeasurementError(f'Frozen Falco recovery failed: {error}') from error
            (folder/'recovery.stdout').write_text(result.stdout);(folder/'recovery.stderr').write_text(result.stderr)
            if result.returncode:
                raise MeasurementError('Frozen Falco recovery failed')
        try:
            actual=self.cov.detector_provenance()
            before=self.cov.detector_state();time.sleep(2);after=self.cov.detector_state()
        except Exception as error:
            raise MeasurementError(f'Collector readiness failed: {error}') from error
        write_json(folder/'recovery.json',dict(before=before,after=after,retry=retry,expected=self.expected,actual=actual))
        if actual!=self.expected:
            raise IntegrityError('Collector provenance changed')
        if not self.cov.health_ok(before,after):
            raise MeasurementError('Collector is not stable after recovery/readiness check')

    def execute(self, slot, folder):
        case=dict(self.cases[slot['case']],control=slot['mode']=='control')
        dest=folder/'measurement'
        try:
            row=self.cov.execute(case,slot['config'],dest,self.image)
        except RuntimeError as error:
            if not str(error).startswith(('Falco is not healthy:', 'No kernel-drop counters')):
                raise
            return self.failed_collection(dest,case,error)
        except subprocess.TimeoutExpired as error:
            if error.cmd[:2]==['docker','exec'] and case['id'] in str(error.cmd):
                return dict(status='behavior-failure',reason='Native execution timed out; requires investigation')
            raise MeasurementError(f'Infrastructure command timed out: {error}') from error
        except (subprocess.SubprocessError, OSError, urllib.error.URLError) as error:
            return self.failed_collection(dest,case,error)
        self.verify(slot)
        if not row['behavior_ok']:
            status='behavior-failure';reason='Program exit or behavior marker failed'
        elif not row['collection_ok']:
            status='measurement-failure';reason='Collector health failed'
        else:
            status='valid';reason=None
        return dict(status=status,reason=reason,measurement=row)

    def failed_collection(self,dest,case,error):
        # Native completion is written before querying Falco. Behavior failures
        # remain terminal even when collection also failed.
        if (dest/'execution.json').exists():
            e=json.loads((dest/'execution.json').read_text())
            execution=subprocess.CompletedProcess([],e['returncode'],e['stdout'],e['stderr'])
            if not self.cov.score(case,execution,[],False,set())['behavior_ok']:
                return dict(status='behavior-failure',reason='Behavior failed before collector error',error=repr(error))
        raise MeasurementError(f'Collection/infrastructure failed: {error}') from error


class WindowsComposites:
    def __init__(self, bundle, coverage, verify):
        self.bundle=Path(bundle);self.coverage=Path(coverage);self.verify=verify
        self.analyzer=load(self.coverage/'analyze.py','windows_coverage')

    def prepare(self, slot, folder, retry=False):
        self.verify(slot)
        # An existing process is never replaced; only restart a stopped Sysmon
        # service, preserving its installed binary/configuration.
        command="if ((Get-Service Sysmon64).Status -ne 'Running') { Start-Service Sysmon64 }; if ((Get-Service Sysmon64).Status -ne 'Running') { throw 'Sysmon not ready' }"
        result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"$ErrorActionPreference='Stop'; "+command],capture_output=True,text=True,timeout=60)
        write_json(folder/'recovery.json',dict(retry=retry,stdout=result.stdout,stderr=result.stderr,exit_code=result.returncode))
        if result.returncode:raise MeasurementError('Sysmon readiness/recovery failed')

    def execute(self, slot, folder):
        case=slot['case'];dest=folder/'measurement'
        script='run.ps1';extra=[]
        fixtures=self.bundle/'ttp-composite/windows-c-ucrt/coverage/fixtures'
        if case.startswith('tcp_connect_'):
            script='run-local-tcp.ps1';extra=['-EchoServer',str(fixtures/'windows_echo_server.exe')]
        elif case.startswith('dns_'):
            script='run-local-dns.ps1';extra=['-DnsServer',str(fixtures/'windows_dns_server.exe')]
        cmd=['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(self.coverage/script),
             '-Programs',str(self.bundle/'ttp-composite'/slot['config']/'coverage'),'-Output',str(dest),
             '-Cases',case,'-Modes',slot['mode'],*extra]
        with (folder/'harness.stdout').open('w') as stdout,(folder/'harness.stderr').open('w') as stderr:
            result=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=420)
        native=self.analyzer.as_list(self.analyzer.read_json(dest/'attempts.json')) if (dest/'attempts.json').exists() else []
        if any(not r['behavior_ok'] for r in native):
            return dict(status='behavior-failure',reason='Native behavior failed',harness_exit_code=result.returncode)
        if (dest/'cleanup-error.txt').exists() or (dest/'execution-error.txt').exists():
            raise IntegrityError('Unsafe harness/fixture state; inspect error logs before continuing')
        if not native:
            # Unknown fixture/provenance failure is not safe to retry blindly.
            raise IntegrityError('No native attempt recorded; inspect harness logs before continuing')
        try:
            qualification=self.analyzer.analyze(dest)
        except (OSError,ValueError,KeyError,TypeError) as error:
            raise MeasurementError(f'Incomplete collector evidence: {error}') from error
        if result.returncode or not qualification['healthy'] or not all(r['valid'] for r in qualification['attempts']):
            return dict(status='measurement-failure',reason='Sysmon/Hayabusa collection or attribution failed',measurement=qualification)
        self.verify(slot)
        # Both valid misses and control alerts are accepted research outcomes.
        return dict(status='valid',measurement=qualification)
