"""Fresh tmon process per attempt on Linux or Windows; no detector-based selection."""
import json
import os
import signal
import subprocess
from pathlib import Path
from engine import MeasurementError


def classify(raw, returncode):
    try:
        rows = [json.loads(line) for line in Path(raw).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        summaries = [r for r in rows if r.get('record') == 'summary']
        if len(summaries) != 1:
            raise ValueError('Expected exactly one summary')
        s = summaries[0]
        if s['target_exit_code'] != 0:
            return dict(status='behavior-failure', reason='Target exited unsuccessfully', summary=s)
        loss = s.get('dropped', s.get('lost'))
        if loss is None or loss != 0 or s['total_events'] <= 0 or returncode != 0:
            raise ValueError('Collector exit, loss counter, or event count failed')
        if not any(r.get('record') == 'event' for r in rows):
            raise ValueError('No event records')
        return dict(status='valid', summary=s, raw='telemetry.jsonl')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return dict(status='measurement-failure', reason=f'Invalid telemetry: {error}', raw='telemetry.jsonl')


class Primitives:
    def __init__(self, bundle, os_name, host, verify):
        self.bundle=Path(bundle); self.os=os_name; self.host=host; self.verify=verify

    def prepare(self, slot, folder, retry=False):
        # A new tmon process/session is created for every attempt; frozen files are
        # rechecked before launch. Its summary certifies the new session's health.
        self.verify(slot)

    def execute(self, slot, folder):
        suffix = '.exe' if self.os == 'windows' else ''
        exe = self.bundle/'ttp-primitives'/slot['config']/(slot['case']+suffix)
        cmd = [str(self.bundle/'tmon'/('tmon'+suffix)), '--format','json','-o',str(folder/'telemetry.jsonl')]
        meta = dict(os=self.os, config=slot['config'], primitive=slot['case'], iteration=slot['repetition'],
                    host=self.host, language=slot['config'].split('-')[1], runtime='-'.join(slot['config'].split('-')[2:]))
        for key,value in meta.items(): cmd += ['--meta',f'{key}={value}']
        cmd += ['--', str(exe)]
        # An ambiguous timeout is not automatically attributed to infrastructure.
        # Preserve it as a behavior failure rather than hide a possible runtime hang.
        try:
            with (folder/'stdout.txt').open('w') as stdout, (folder/'stderr.txt').open('w') as stderr:
                process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, start_new_session=os.name!='nt')
                try:
                    code = process.wait(timeout=180)
                except subprocess.TimeoutExpired:
                    if os.name == 'nt':
                        subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=30,check=True)
                    else:
                        os.killpg(process.pid,signal.SIGKILL)
                    process.wait(timeout=30)
                    raise
        except subprocess.TimeoutExpired:
            return dict(status='behavior-failure', reason='Timed out; target/collector cause requires investigation')
        except OSError as error:
            raise MeasurementError(f'Cannot start collector: {error}') from error
        self.verify(slot)
        return dict(classify(folder/'telemetry.jsonl', code), collector_exit_code=code)
