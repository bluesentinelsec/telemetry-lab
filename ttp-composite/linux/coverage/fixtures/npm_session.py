#!/usr/bin/env python3
"""Start the real offline npm lifecycle before capture and preserve completion."""
import json,os,subprocess
from pathlib import Path
p=Path('/tmp/lab')
env=dict(os.environ,npm_config_cache='/tmp/npm-cache',npm_config_logs_dir='/tmp/npm-logs',npm_config_update_notifier='false')
with (p/'npm.stdout').open('w') as out,(p/'npm.stderr').open('w') as err:
    r=subprocess.run(['/usr/bin/npm','install','--offline','--no-audit','--no-fund','--package-lock=false','--foreground-scripts'],cwd=p/'npm',env=env,stdout=out,stderr=err)
(p/'npm-result.json').write_text(json.dumps({'returncode':r.returncode}))
