#!/usr/bin/env python3
"""Inspect actual PE binaries, their CRT imports, and the standalone roster."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def pe_imports(path,objdump='objdump'):
    report=subprocess.check_output([objdump,'-p',str(path)],text=True)
    return re.findall(r'DLL Name:\s*(\S+)',report)


def verify_imports(imports,runtime,label):
    names={n.lower() for n in imports}
    ucrt=any(n.startswith(('api-ms-win-crt-','ucrtbase')) for n in names)
    msvcrt='msvcrt.dll' in names
    if runtime in ('ucrt','libstdcxx','libcxx') and (not ucrt or msvcrt):
        raise ValueError(f'{label}: wrong CRT {imports}')
    if runtime=='msvcrt' and (not msvcrt or ucrt):
        raise ValueError(f'{label}: wrong CRT {imports}')
    required={'libstdcxx':'libstdc++-6.dll','libcxx':'libc++.dll'}.get(runtime)
    if required:
        other='libc++.dll' if runtime=='libstdcxx' else 'libstdc++-6.dll'
        if required not in names or other in names:
            raise ValueError(f'{label}: missing or mixed C++ library {imports}')


def verify(directory, runtime, objdump='objdump', compiler='gcc'):
    spec=json.loads(Path(__file__).with_name('selection.json').read_text())
    cases=[c['case_id'] for c in spec['candidates']]
    actual={p.stem for p in directory.glob('*.exe')}
    if actual != set(cases):
        raise ValueError(f'Roster differs: missing={set(cases)-actual}, extra={actual-set(cases)}')
    programs=[]
    for case in cases:
        p=directory/(case+'.exe');data=p.read_bytes()
        if data[:2]!=b'MZ':raise ValueError(f'{case}: not a PE executable')
        imports=pe_imports(p,objdump)
        verify_imports(imports,runtime,case)
        # Each executable embeds its sole fixed case ID; no unrelated case IDs.
        markers={c for c in cases if ('COMPOSITE_CASE '+c+'\0').encode() in data}
        if markers != {case}:raise ValueError(f'{case}: incorrect case markers {markers}')
        programs.append(dict(case_id=case,sha256=hashlib.sha256(data).hexdigest(),imports=imports))
    if len({p['sha256'] for p in programs})!=len(programs):raise ValueError('Duplicate binary')
    version_flag='-dumpversion' if runtime in ('libstdcxx','libcxx') else '-dumpfullversion'
    compiler_version=subprocess.check_output([compiler,version_flag],text=True).strip()
    identity=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    dlls=[]
    for dll in sorted(directory.glob('*.dll')):
        imports=pe_imports(dll,objdump)
        names={n.lower() for n in imports}
        if runtime in ('libstdcxx','libcxx'):
            forbidden='libc++.dll' if runtime=='libstdcxx' else 'libstdc++-6.dll'
            if 'msvcrt.dll' in names or forbidden in names:
                raise ValueError(f'{dll.name}: dependency mixes runtime configurations')
        dlls.append(dict(name=dll.name,sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),imports=imports))
    # Every non-system dependency in the selected MSYS2 family must be present,
    # including indirect exception/unwind/thread libraries.
    bundled={d['name'].lower() for d in dlls}
    for entry in programs+dlls:
        for name in entry['imports']:
            if name.lower().startswith(('libstdc++','libc++','libgcc','libunwind','libwinpthread','libatomic')) and name.lower() not in bundled:
                raise ValueError(f'Missing bundled runtime dependency: {name}')
    result=dict(runtime=runtime,language='cpp' if runtime in ('libstdcxx','libcxx') else 'c',compiler_version=compiler_version,compiler_identity=identity,programs=programs,dependent_dlls=dlls)
    (directory/'build-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Validated {len(programs)} separate Windows programs and {runtime} imports ({identity})')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    parser.add_argument('runtime',choices=['ucrt','msvcrt','libstdcxx','libcxx']);parser.add_argument('--objdump',default='objdump')
    parser.add_argument('--compiler',default='gcc')
    a=parser.parse_args();verify(a.directory,a.runtime,a.objdump,a.compiler)
