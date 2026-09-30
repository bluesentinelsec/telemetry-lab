#!/usr/bin/env python3
"""Enter real application ancestry while preserving native output and status."""
import os,json,sys,time,urllib.request
from pathlib import Path
case,config,mode=sys.argv[1:4]
if case=='npm_network_tool':
    p=Path('/tmp/lab')
    with (p/'native-trigger').open('wb',buffering=0) as gate:gate.write(b'1')
    for _ in range(250):
        if (p/'npm-result.json').exists():break
        time.sleep(.05)
    else:raise RuntimeError('npm lifecycle did not complete')
    sys.stdout.write((p/'npm.stdout').read_text());sys.stderr.write((p/'npm.stderr').read_text())
    sys.exit(json.loads((p/'npm-result.json').read_text())['returncode'])
if case in {'protected_shell','web_shell','web_child','web_reverse_shell'}:
    response=urllib.request.urlopen('http://127.0.0.1:18082/measured'+('?--control' if mode=='control' else ''),timeout=15)
    data=response.read().decode();sys.stdout.write(data)
    # Apache reports CGI exit failures as HTTP errors or missing native markers.
    marker=('CONTROL_OK ' if mode=='control' else 'CASE_OK ')+case
    if marker not in data.splitlines():
        error=Path('/tmp/lab/apache-error')
        if error.exists():sys.stderr.write(error.read_text())
        sys.exit(1)
    sys.exit(0)
raise ValueError('Not an application-ancestry case')
