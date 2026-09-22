#!/usr/bin/env python3
"""Inspect actual PE binaries, their CRT imports, and the standalone roster."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def verify(directory, runtime, objdump='objdump'):
    spec=json.loads(Path(__file__).with_name('selection.json').read_text())
    cases=[c['case_id'] for c in spec['candidates']]
    actual={p.stem for p in directory.glob('*.exe')}
    if actual != set(cases):
        raise ValueError(f'Roster differs: missing={set(cases)-actual}, extra={actual-set(cases)}')
    programs=[]
    for case in cases:
        p=directory/(case+'.exe');data=p.read_bytes()
        if data[:2]!=b'MZ':raise ValueError(f'{case}: not a PE executable')
        report=subprocess.check_output([objdump,'-p',str(p)],text=True)
        imports=re.findall(r'DLL Name:\s*(\S+)',report)
        ucrt=any(x.lower().startswith(('api-ms-win-crt-','ucrtbase')) for x in imports)
        msvcrt=any(x.lower()=='msvcrt.dll' for x in imports)
        if runtime=='ucrt' and (not ucrt or msvcrt):raise ValueError(f'{case}: wrong CRT {imports}')
        if runtime=='msvcrt' and (not msvcrt or ucrt):raise ValueError(f'{case}: wrong CRT {imports}')
        # Each executable embeds its sole fixed case ID; no unrelated case IDs.
        markers={c for c in cases if (c+'\0').encode() in data}
        if markers != {case}:raise ValueError(f'{case}: incorrect case markers {markers}')
        programs.append(dict(case_id=case,sha256=hashlib.sha256(data).hexdigest(),imports=imports))
    if len({p['sha256'] for p in programs})!=len(programs):raise ValueError('Duplicate binary')
    compiler=subprocess.check_output(['gcc','-dumpfullversion'],text=True).strip()
    result=dict(runtime=runtime,compiler_version=compiler,programs=programs)
    (directory/'build-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Validated {len(programs)} separate Windows programs and {runtime} imports (GCC {compiler})')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    parser.add_argument('runtime',choices=['ucrt','msvcrt']);parser.add_argument('--objdump',default='objdump')
    a=parser.parse_args();verify(a.directory,a.runtime,a.objdump)
