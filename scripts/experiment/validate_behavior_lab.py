#!/usr/bin/env python3
"""Inject genuine native failures on disposable hosts; keep separate from study data.

Linux removes a fixture only inside a new disposable container. Windows hides
cmd.exe from one child process's environment. Binaries and rules are unchanged.
"""
import argparse
import json
import os
from pathlib import Path
from engine import campaign, write_json
from primitives import Primitives
from composites import LinuxComposites
from run import host_lock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--image', default='lab-falco-coverage:local')
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    windows = json.loads((bundle/'manifest.json').read_text())['os'] == 'windows'
    config = 'windows-c-ucrt' if windows else 'linux-c-glibc'
    slot = dict(cohort='primitives' if windows else 'composites',
                os='windows' if windows else 'linux', config=config,
                case='spawn' if windows else 'sensitive_read',
                mode='primitive' if windows else 'active', repetition=1)

    class WindowsFault(Primitives):
        remaining = 1
        def execute(self, slot, folder):
            if not self.remaining:
                return super().execute(slot, folder)
            self.remaining -= 1
            saved = {key: os.environ.get(key) for key in ('COMSPEC', 'PATH')}
            write_json(folder/'injected-fault.json', dict(type='Hide shell in native child environment'))
            try:
                os.environ['COMSPEC'] = str(output/'nonexistent-cmd.exe')
                os.environ['PATH'] = str(output/'nonexistent-directory')
                result = super().execute(slot, folder)
            finally:
                for key, value in saved.items():
                    if value is None: os.environ.pop(key, None)
                    else: os.environ[key] = value
            assert result['status'] == 'behavior-failure', result
            assert result['summary']['target_exit_code'] != 0, result
            return result

    class LinuxFault(LinuxComposites):
        remaining = 1
        def execute(self, slot, folder):
            original = self.cov.prepare_container
            injected = False
            def prepare(cid, config, case):
                nonlocal injected
                original(cid, config, case)
                if self.remaining:
                    self.remaining -= 1
                    injected = True
                    self.cov.command(['docker', 'exec', cid, 'rm', '/etc/shadow'])
                    write_json(folder/'injected-fault.json', dict(type='Remove required fixture inside disposable container', container=cid))
            self.cov.prepare_container = prepare
            try:
                result = super().execute(slot, folder)
            finally:
                self.cov.prepare_container = original
            if injected:
                assert result['status'] == 'behavior-failure', result
                execution = json.loads((folder/'measurement/execution.json').read_text())
                assert execution['returncode'] != 0, execution
            return result

    reports = {}
    with host_lock():
        for name, retries, faults, count in [('replace', 3, 1, 2), ('disabled', 0, 1, 1), ('exhaust', 3, 4, 4)]:
            adapter = (WindowsFault(bundle, 'windows', 'native-failure-validation', lambda slot: None)
                       if windows else LinuxFault(bundle/'ttp-composite/coverage', args.image, lambda slot: None))
            adapter.remaining = faults
            result = campaign(output/name, [slot], adapter, max_retries=retries, retry_delay=0)
            assert result['complete'] == (name == 'replace'), result
            assert result['total_attempts'] == count, result
            rows = [json.loads(line) for line in (output/name/'attempts.jsonl').read_text().splitlines()]
            assert rows[0]['status'] == 'behavior-failure', rows
            assert all((output/name/row['evidence']/'attempt.json').exists() for row in rows)
            if name == 'replace':
                assert rows[1]['replaces_attempt'] == rows[0]['attempt_id'], rows
            reports[name] = result
    write_json(output/'validation.json', dict(passed=True, scenarios=reports))
    print('NATIVE_FAILURE_RETRY_VALIDATED')


if __name__ == '__main__':
    main()
