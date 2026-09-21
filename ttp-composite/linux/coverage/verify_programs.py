#!/usr/bin/env python3
"""Check actual ELF artifacts: distinct single-case binaries, correct libc loader."""
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
        loader='ld-linux' if libc=='glibc' else 'ld-musl'
        if loader not in header:raise ValueError(f'{name} has the wrong runtime loader')
        markers={case for case in ids if any(('CASE_OK '+case+end).encode() in data for end in ('\n','\0'))}
        if markers != ({name} if name in ids else set()):
            raise ValueError(f'{name} bundles unrelated case markers: {markers}')
    print(f'Verified {len(ids)-1} distinct standalone cases, baseline, and setup ({libc})')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('libc',choices=['glibc','musl'])
    args=parser.parse_args();verify(args.directory,args.libc)
