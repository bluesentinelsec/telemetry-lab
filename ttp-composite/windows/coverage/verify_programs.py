#!/usr/bin/env python3
"""Inspect actual PE binaries, their CRT imports, and the standalone roster."""
import argparse
import hashlib
import json
import re
import subprocess
import struct
from pathlib import Path


def pe_imports(path,objdump=None):
    """Read PE64 import descriptors without objdump's debug-section expansion.

    The optional objdump argument is retained for existing helper callers.
    Format: https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
    """
    data=Path(path).read_bytes()
    def unpack(fmt,offset):
        if offset<0 or offset+struct.calcsize(fmt)>len(data):
            raise ValueError(f'{path}: truncated PE structure')
        return struct.unpack_from(fmt,data,offset)
    if data[:2]!=b'MZ':raise ValueError(f'{path}: missing DOS header')
    pe=unpack('<I',0x3c)[0]
    if data[pe:pe+4]!=b'PE\0\0':raise ValueError(f'{path}: missing PE signature')
    machine,count=unpack('<HH',pe+4);optional_size=unpack('<H',pe+20)[0]
    optional=pe+24
    if machine!=0x8664 or unpack('<H',optional)[0]!=0x20b or optional_size<128:
        raise ValueError(f'{path}: expected x64 PE32+')
    directories=unpack('<I',optional+108)[0]
    if directories<2:raise ValueError(f'{path}: missing import data directory')
    if directories>13 and optional_size>=224 and any(unpack('<II',optional+216)):
        raise ValueError(f'{path}: delay imports require explicit validation')
    rva,size=unpack('<II',optional+120)
    if not rva or not size:raise ValueError(f'{path}: absent import table')
    sections=[unpack('<IIII',optional+optional_size+40*i+8) for i in range(count)]
    def offset(address,length=1):
        matches=[raw+address-va for virtual,va,raw_size,raw in sections
                 if va<=address and address+length<=va+raw_size]
        if len(matches)!=1 or matches[0]+length>len(data):
            raise ValueError(f'{path}: invalid/ambiguous import RVA {address:#x}')
        return matches[0]
    imports=[]
    for position in range(0,size-19,20):
        descriptor=unpack('<IIIII',offset(rva+position,20))
        if not any(descriptor):
            if not imports:raise ValueError(f'{path}: empty import descriptor list')
            return imports
        name_rva=descriptor[3];name=bytearray()
        for i in range(256):
            byte=data[offset(name_rva+i)]
            if not byte:break
            name.append(byte)
        else:raise ValueError(f'{path}: unterminated DLL name')
        try:decoded=name.decode('ascii')
        except UnicodeDecodeError as error:raise ValueError(f'{path}: invalid DLL name') from error
        if not decoded or '/' in decoded or '\\' in decoded:
            raise ValueError(f'{path}: invalid DLL import name')
        imports.append(decoded)
    raise ValueError(f'{path}: unterminated import descriptor table')


def verify_imports(imports,runtime,label):
    names={n.lower() for n in imports}
    ucrt=any(n.startswith(('api-ms-win-crt-','ucrtbase')) for n in names)
    msvcrt='msvcrt.dll' in names
    if runtime in ('ucrt','libstdcxx','libcxx','go-cgo') and (not ucrt or msvcrt):
        raise ValueError(f'{label}: wrong CRT {imports}')
    if runtime=='msvcrt' and (not msvcrt or ucrt):
        raise ValueError(f'{label}: wrong CRT {imports}')
    if runtime=='go-static' and (ucrt or msvcrt):
        raise ValueError(f'{label}: pure-Go binary imports a C runtime')
    if runtime in ('go-cgo','go-static') and names & {'libstdc++-6.dll','libc++.dll'}:
        raise ValueError(f'{label}: unexpected C++ runtime in Go build')
    required={'libstdcxx':'libstdc++-6.dll','libcxx':'libc++.dll'}.get(runtime)
    if required:
        other='libc++.dll' if runtime=='libstdcxx' else 'libstdc++-6.dll'
        if required not in names or other in names:
            raise ValueError(f'{label}: missing or mixed C++ library {imports}')


def verify_go(info, symbols, runtime, label):
    settings=dict(re.findall(r'^\s*build\s+(\S+?)=(.*)$',info,re.MULTILINE))
    expected='1' if runtime=='go-cgo' else '0'
    if any(settings.get(k)!=v for k,v in {'CGO_ENABLED':expected,'GOOS':'windows','GOARCH':'amd64'}.items()):
        raise ValueError(f'{label}: incorrect Go build settings')
    has_cgo=any('runtime/cgo.' in line for line in symbols.splitlines())
    if has_cgo != (runtime=='go-cgo'):
        raise ValueError(f'{label}: cgo metadata does not match actual linked runtime')
    return settings


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
        terminator='\n' if runtime in ('go-cgo','go-static') else '\0'
        markers={c for c in cases if ('COMPOSITE_CASE '+c+terminator).encode() in data}
        if markers != {case}:raise ValueError(f'{case}: incorrect case markers {markers}')
        entry=dict(case_id=case,sha256=hashlib.sha256(data).hexdigest(),imports=imports)
        if runtime in ('go-cgo','go-static'):
            info=subprocess.check_output(['go','version','-m',str(p)],text=True)
            symbols=subprocess.check_output(['go','tool','nm',str(p)],text=True)
            entry['go_build_settings']=verify_go(info,symbols,runtime,case)
            entry['go_build_info']=info
        programs.append(entry)
    if len({p['sha256'] for p in programs})!=len(programs):raise ValueError('Duplicate binary')
    is_go=runtime in ('go-cgo','go-static')
    if is_go:
        identity=subprocess.check_output(['go','version'],text=True).strip()
        compiler_version=subprocess.check_output(['go','env','GOVERSION'],text=True).strip()
    else:
        version_flag='-dumpversion' if runtime in ('libstdcxx','libcxx') else '-dumpfullversion'
        compiler_version=subprocess.check_output([compiler,version_flag],text=True).strip()
        identity=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    dlls=[]
    for dll in sorted(directory.glob('*.dll')):
        imports=pe_imports(dll,objdump)
        names={n.lower() for n in imports}
        if runtime in ('libstdcxx','libcxx','go-cgo'):
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
    result=dict(runtime=runtime,language='go' if is_go else 'cpp' if runtime in ('libstdcxx','libcxx') else 'c',compiler_version=compiler_version,compiler_identity=identity,programs=programs,dependent_dlls=dlls)
    if runtime=='go-cgo':
        result['c_compiler_identity']=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    (directory/'build-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Validated {len(programs)} separate Windows programs and {runtime} imports ({identity})')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    parser.add_argument('runtime',choices=['ucrt','msvcrt','libstdcxx','libcxx','go-cgo','go-static']);parser.add_argument('--objdump',default='objdump')
    parser.add_argument('--compiler',default='gcc')
    a=parser.parse_args();verify(a.directory,a.runtime,a.objdump,a.compiler)
