#!/usr/bin/env python3
"""Enter real application ancestry while preserving native output and status."""
import os,subprocess,sys,urllib.request
case,config,mode=sys.argv[1:4]
if case=='npm_network_tool':
    env=dict(os.environ,npm_config_cache='/tmp/npm-cache',npm_config_logs_dir='/tmp/npm-logs',npm_config_update_notifier='false')
    r=subprocess.run(['/usr/bin/npm','install','--offline','--no-audit','--no-fund','--package-lock=false','--foreground-scripts'],cwd='/tmp/lab/npm',env=env)
    sys.exit(r.returncode)
if case in {'protected_shell','web_shell','web_child','web_reverse_shell'}:
    response=urllib.request.urlopen('http://127.0.0.1:18082/measured'+('?--control' if mode=='control' else ''),timeout=15)
    data=response.read().decode();sys.stdout.write(data)
    # Apache reports CGI exit failures as HTTP errors or missing native markers.
    marker=('CONTROL_OK ' if mode=='control' else 'CASE_OK ')+case
    sys.exit(0 if marker in data.splitlines() else 1)
raise ValueError('Not an application-ancestry case')
