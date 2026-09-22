#!/usr/bin/env python3
"""Bundle the actual MSYS2 DLL dependency closure beside each Windows binary."""
import argparse
import shutil
import sys
from pathlib import Path
from verify_programs import pe_imports


def bundle(directory, runtime_bin, objdump='objdump'):
    for folder in sorted({p.parent for p in directory.rglob('*.exe')}):
        queue=list(folder.glob('*.exe'));seen=set()
        while queue:
            binary=queue.pop()
            for name in pe_imports(binary,objdump):
                key=name.lower()
                if key in seen:continue
                seen.add(key)
                source=runtime_bin/name
                # Windows system DLLs are supplied by the OS; only ship MSYS2 DLLs.
                if source.is_file():
                    dest=folder/name;shutil.copy2(source,dest);queue.append(dest)
                    print(f'{folder.name}: {name}')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path)
    p.add_argument('--runtime-bin',type=Path,default=Path(sys.executable).parent)
    p.add_argument('--objdump',default='objdump');a=p.parse_args()
    bundle(a.directory,a.runtime_bin,a.objdump)
