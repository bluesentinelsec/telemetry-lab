#!/usr/bin/env python3
"""Start a real Bun npm-package install lifecycle before capture.

Stock Falco lists bun alongside npm. npm install changes its process name to
"npm install", which does not satisfy that unchanged exact-name predicate."""
import json,os,subprocess
from pathlib import Path
p=Path('/tmp/lab')
env=dict(os.environ,BUN_INSTALL_CACHE_DIR='/tmp/package-cache',DO_NOT_TRACK='1')
with (p/'npm.stdout').open('w') as out,(p/'npm.stderr').open('w') as err:
    r=subprocess.run(['/usr/local/bin/bun','install','--no-save','--ignore-optional','--backend=copyfile'],cwd=p/'npm',env=env,stdout=out,stderr=err)
(p/'npm-result.json').write_text(json.dumps({'returncode':r.returncode}))
