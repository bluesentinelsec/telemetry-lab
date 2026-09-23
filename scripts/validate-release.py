#!/usr/bin/env python3
"""Reject incomplete release bundles and write a verifiable file inventory."""
import argparse
import hashlib
import json
from pathlib import Path


def validate(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    windows = manifest['os'] == 'windows'
    suffix = '.exe' if windows else ''
    required = ['tmon/tmon' + suffix, 'tap/tap' + suffix]
    for config in manifest['configs']:
        required += [f'ttp-primitives/{config}/{name}{suffix}' for name in manifest['primitives']]
    coverage = root / 'ttp-composite/coverage'
    if windows:
        cases = [c['case_id'] for c in json.loads((coverage / 'selection.json').read_text())['candidates']]
    else:
        cases = [c['id'] for c in json.loads((coverage / 'manifest.json').read_text())['cases']]
        cases += ['negative', 'fixture_prepare']
        required += [f'ttp-composite/coverage/falco-health-fix/{name}' for name in
                     ('install.sh', 'preserve-partial-enter.patch', 'regression.cpp')]
    for config in manifest['composite_configs']:
        prefix = f'ttp-composite/{config}'
        required += [f'{prefix}/coverage/{name}{suffix}' for name in cases]
        # Windows Rust was introduced after the legacy pilot suite.
        if not config.startswith('windows-rust-'):
            required += [f'{prefix}/{name}{suffix}' for name in manifest['composites']]
        if windows:
            required.append(f'{prefix}/coverage/build-manifest.json')
            build = json.loads((root / required[-1]).read_text())
            for program in build['programs']:
                # Program entries name standalone case executables.
                path = root / prefix / 'coverage' / (program['case_id'] + '.exe')
                if hashlib.sha256(path.read_bytes()).hexdigest() != program['sha256']:
                    raise ValueError(f'Build-manifest hash mismatch: {path}')
            for dll in build.get('dependent_dlls', []):
                path = root / prefix / 'coverage' / dll['name']
                if hashlib.sha256(path.read_bytes()).hexdigest() != dll['sha256']:
                    raise ValueError(f'Dependency hash mismatch: {path}')
    missing = [p for p in required if not (root / p).is_file() or not (root / p).stat().st_size]
    if missing:
        raise ValueError('Missing release files: ' + ', '.join(missing))
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'files.sha256.json'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    hashes = validate(args.bundle)
    target = args.bundle / 'files.sha256.json'
    if args.write:
        target.write_text(json.dumps(hashes, indent=2) + '\n')
    elif json.loads(target.read_text()) != hashes:
        raise SystemExit('Bundle differs from its file inventory')
    print(f'Validated {len(hashes)} files in {args.bundle.name}')
