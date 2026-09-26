#!/usr/bin/env python3
"""Run a configurable experiment with bounded automatic measurement replacement."""
import argparse
import contextlib
import hashlib
import json
import os
import platform
import random
import sys
import tempfile
from pathlib import Path
from engine import IntegrityError, campaign, write_json
from primitives import Primitives
from composites import LinuxComposites, WindowsComposites
from batch_composites import LinuxBatch, WindowsBatch
from legacy import LinuxLegacy, WindowsLegacy


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


@contextlib.contextmanager
def host_lock():
    if os.name == 'nt':
        import ctypes
        kernel=ctypes.windll.kernel32
        kernel.CreateMutexW.restype=ctypes.c_void_p
        kernel.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_wchar_p]
        kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
        kernel.ReleaseMutex.argtypes=[ctypes.c_void_p]
        kernel.CloseHandle.argtypes=[ctypes.c_void_p]
        handle=kernel.CreateMutexW(None,False,'Global\\TelemetryLabExperiment')
        if not handle:raise RuntimeError('Cannot create host experiment mutex')
        acquired=kernel.WaitForSingleObject(handle,0) in (0,0x80)
        try:
            if not acquired:raise RuntimeError('Another experiment is running on this host')
            yield
        finally:
            if acquired:kernel.ReleaseMutex(handle)
            kernel.CloseHandle(handle)
    else:
        import fcntl
        with open(Path(tempfile.gettempdir())/'telemetry-lab-experiment.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--cohort',choices=('primitives','composites','legacy'),required=True)
    p.add_argument('--repetitions',type=int,default=200,help='Accepted measurements per test/configuration/mode (default: 200)')
    p.add_argument('--batch-size',type=int,default=1,help='Composite capture group size; programs still run serially (default: 1)')
    p.add_argument('--max-retries',type=int,default=3,help='Replacements after the original attempt (default: 3)')
    p.add_argument('--no-retry',action='store_true',help='Disable replacement; retain suspect attempts')
    p.add_argument('--retry-delay',type=float,default=1)
    p.add_argument('--seed',type=int,default=20260924)
    p.add_argument('--host-id',default=platform.node())
    p.add_argument('--case',action='append',dest='cases');p.add_argument('--config',action='append',dest='configs')
    p.add_argument('--image',default='lab-falco-coverage:local')
    p.add_argument('--inventory',type=Path,help='Host inventory copied alongside accepted evidence')
    a=p.parse_args()
    if a.batch_size<1 or a.repetitions<1 or a.max_retries<0 or not (0<=a.retry_delay<=3600):p.error('Invalid repetition/retry limits')
    if a.batch_size>1 and a.cohort=='primitives':p.error('Batch collection is composite-only')
    a.bundle=a.bundle.resolve();a.output=a.output.resolve()
    m=json.loads((a.bundle/'manifest.json').read_text(encoding='utf-8-sig'))
    os_name=m['os']
    if os_name not in ('linux','windows') or platform.system().lower()!=os_name:
        p.error('Run the bundle on its matching operating system')
    coverage=a.bundle/'ttp-composite/coverage'
    if a.cohort=='primitives':
        cases=m['primitives'];configs=m['configs'];modes=['primitive']
    elif a.cohort=='legacy':
        cases=m['composites'];configs=m['configs'];modes=['legacy']
    else:
        catalog=json.loads((coverage/('manifest.json' if os_name=='linux' else 'selection.json')).read_text(encoding='utf-8-sig'))
        cases=([c['id'] for c in catalog['cases']]+['negative']) if os_name=='linux' else [c['case_id'] for c in catalog['candidates']]
        configs=m['composite_configs'];modes=['active','control']
    def choose(values, requested):
        if requested and (len(set(requested))!=len(requested) or not set(requested)<=set(values)):
            p.error('Unknown or duplicate selection: '+str(requested))
        return requested or values
    cases=choose(cases,a.cases);configs=choose(configs,a.configs)
    plan=[];rng=random.Random(a.seed)
    for rep in range(1,a.repetitions+1):
        block=[dict(cohort=a.cohort,os=os_name,host=a.host_id,config=cfg,case=case,mode=mode,repetition=rep)
               for cfg in configs for case in cases for mode in (['negative'] if case=='negative' else modes)]
        rng.shuffle(block)
        if a.batch_size>1 and os_name=='windows' and a.cohort=='composites':
            # One runtime's DLL set per capture, shuffled within every block.
            order=list(configs);rng.shuffle(order)
            block=[s for cfg in order for s in block if s['config']==cfg]
        plan.extend(block)
    # Freeze every released byte once, then verify relevant executables, DLLs,
    # harness and collector artifacts before each attempted measurement.
    expected={path.relative_to(a.bundle).as_posix():sha(path) for path in a.bundle.rglob('*')
              if path.is_file() and '__pycache__' not in path.parts and path.name!='files.sha256.json'}
    inventory_file=a.bundle/'files.sha256.json'
    if inventory_file.exists() and json.loads(inventory_file.read_text())!=expected:
        raise IntegrityError('Bundle differs from its release inventory')
    common=['manifest.json']
    if a.cohort=='primitives':common+=['tmon/tmon'+('.exe' if os_name=='windows' else '')]
    else:common += [name for name in expected if name.startswith('ttp-composite/coverage/') and '/validation/' not in name]
    external={str(f):sha(f) for f in Path(__file__).resolve().parent.glob('*.py')}
    if a.cohort=='legacy' and os_name=='windows':
        script=Path(__file__).with_name('legacy-windows.ps1')
        if not script.exists():script=Path(__file__).parent.parent/'e2e/legacy-windows.ps1'
        external[str(script.resolve())]=sha(script)
    if a.cohort!='primitives':
        system_files=([Path('/etc/falco/falco.yaml')] if os_name=='linux' else
                      [Path('C:/lab/sysmon/Sysmon64.exe'),Path('C:/lab/sysmon/config.xml'),Path('C:/lab/hayabusa/hayabusa.exe'),
                       Path('C:/lab/windows-coverage/fixtures/helper.exe'),Path('C:/lab/windows-coverage/fixtures/fixture.node')])
        external.update({str(f):sha(f) for f in system_files})
        if os_name=='windows':
            common += [name for name in expected if name.startswith('ttp-composite/windows-c-ucrt/coverage/fixtures/')]
    def verify(slot):
        prefix=('ttp-primitives/' if a.cohort=='primitives' else 'ttp-composite/')+slot['config']+'/'
        suffix='.exe' if os_name=='windows' else ''
        subdir='coverage/' if a.cohort=='composites' else ''
        native=prefix+subdir+slot['case']+suffix
        relevant=common+[native]+[name for name in expected if name.startswith(prefix) and (name.endswith('.dll') or name.endswith('build-manifest.json'))]
        for name in relevant:
            if sha(a.bundle/name)!=expected[name]:raise IntegrityError('Frozen artifact changed: '+name)
        for name,digest in external.items():
            if sha(name)!=digest:raise IntegrityError('Collector artifact changed: '+name)
    with host_lock():
        if a.cohort=='primitives':adapter=Primitives(a.bundle,os_name,a.host_id,verify)
        elif a.cohort=='legacy':adapter=LinuxLegacy(coverage,a.image,verify) if os_name=='linux' else WindowsLegacy(a.bundle,coverage,verify)
        elif os_name=='linux':adapter=(LinuxBatch if a.batch_size>1 else LinuxComposites)(coverage,a.image,verify)
        else:adapter=(WindowsBatch if a.batch_size>1 else WindowsComposites)(a.bundle,coverage,verify)
        inventory=None
        if a.inventory:
            inventory=json.loads(a.inventory.read_text(encoding='utf-8-sig'))
            if inventory['telemetry_lab_release']!=m['version']:raise IntegrityError('Host inventory describes another release')
        provenance=dict(bundle=str(a.bundle),files_sha256=expected,external_sha256=external,
                   seed=a.seed,host=a.host_id,python=sys.version,platform=platform.platform(),
                   image_id=getattr(adapter,'image',None),image_binary_inventory=getattr(adapter,'binary_inventory',None),
                   falco=getattr(adapter,'expected',None))
        summary=campaign(a.output,plan,adapter,0 if a.no_retry else a.max_retries,a.retry_delay,
                         provenance=provenance,inventory=inventory,batch_size=a.batch_size)
    print(json.dumps(summary,indent=2))
    return 0 if summary['complete'] else 1


if __name__=='__main__':
    raise SystemExit(main())
