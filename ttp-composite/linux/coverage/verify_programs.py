#!/usr/bin/env python3
"""Check actual ELF artifacts: distinct single-case binaries, declared runtime configuration."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def verify(directory, libc):
    manifest=json.loads(Path(__file__).with_name('manifest.json').read_text())
    ids=[case['id'] for case in manifest['cases']]+['negative']
    expected=set(ids+['fixture_prepare'])
    actual={p.name for p in directory.iterdir() if p.is_file()}
    if actual != expected:
        raise ValueError(f'Executable roster differs: missing={expected-actual}, extra={actual-expected}')
    hashes=set()
    for name in expected:
        p=directory/name
        data=p.read_bytes()
        if not data.startswith(b'\x7fELF'):
            raise ValueError(f'{name} is not a standalone ELF program')
        digest=hashlib.sha256(data).hexdigest()
        if digest in hashes:raise ValueError(f'{name} duplicates another executable')
        hashes.add(digest)
        header=subprocess.check_output(['readelf','-l',str(p)],text=True)
        if libc in ('rust-gnu', 'rust-musl'):
            dynamic=subprocess.check_output(['readelf','-d',str(p)],text=True)
            if 'INTERP' in header or 'NEEDED' in dynamic:
                raise ValueError(f'{name} is not a static Rust program')
            env=libc.removeprefix('rust-')
            marker=('RUNTIME_TARGET x86_64-unknown-linux-'+env+'\0').encode()
            if marker not in data:
                raise ValueError(f'{name} has the wrong Rust target')
            symbols=subprocess.check_output(['nm','--defined-only',str(p)],text=True)
            required,forbidden = (('__libc_early_init','__init_libc') if env=='gnu'
                                  else ('__init_libc','__libc_early_init'))
            names={line.split()[-1] for line in symbols.splitlines() if line.split()}
            if required not in names or forbidden in names:
                raise ValueError(f'{name} has the wrong statically linked libc')
        elif libc in ('go-cgo','go-static'):
            dynamic=subprocess.check_output(['readelf','-d',str(p)],text=True)
            info=subprocess.check_output(['go','version','-m',str(p)],text=True)
            cgo='1' if libc=='go-cgo' else '0'
            if not all(setting in info for setting in ('CGO_ENABLED='+cgo,'GOARCH=amd64','GOOS=linux')):
                raise ValueError(f'{name} has the wrong Go build configuration')
            if libc=='go-static':
                if 'INTERP' in header or 'NEEDED' in dynamic:
                    raise ValueError(f'{name} is not a static Go program')
            elif 'ld-linux' not in header or '[libc.so.6]' not in dynamic:
                raise ValueError(f'{name} does not link the cgo/glibc runtime')
        else:
            loader='ld-musl' if libc=='musl' else 'ld-linux'
            if loader not in header:raise ValueError(f'{name} has the wrong runtime loader')
        if libc in ('libstdcxx', 'libcxx'):
            dynamic=subprocess.check_output(['readelf','-d',str(p)],text=True)
            symbols=subprocess.check_output(['readelf','--dyn-syms','--wide',str(p)],text=True)
            required,forbidden,symbol = (('libstdc++.so.6','libc++.so.1','GLIBCXX_')
                if libc == 'libstdcxx' else ('libc++.so.1','libstdc++.so.6','_ZNSt3__1'))
            if f'[{required}]' not in dynamic or f'[{forbidden}]' in dynamic:
                raise ValueError(f'{name} has the wrong C++ standard library')
            if not any(' UND ' in line and symbol in line for line in symbols.splitlines()):
                raise ValueError(f'{name} does not use the selected C++ standard library')
        markers={case for case in ids if any(('CASE_OK '+case+end).encode() in data for end in ('\n','\0'))}
        if markers != ({name} if name in ids else set()):
            raise ValueError(f'{name} bundles unrelated case markers: {markers}')
    print(f'Verified {len(ids)-1} distinct standalone cases, baseline, and setup ({libc})')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('libc',choices=['glibc','musl','libstdcxx','libcxx','go-cgo','go-static','rust-gnu','rust-musl'])
    args=parser.parse_args();verify(args.directory,args.libc)
