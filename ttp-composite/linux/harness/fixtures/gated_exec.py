#!/usr/bin/env python3
"""Wait until capture begins, then replace this fixture process with the native case."""
import os,sys
from pathlib import Path
Path('/tmp/lab/native-ready').touch()
with open('/tmp/lab/native-trigger','rb',buffering=0) as gate:
    if gate.read(1)!=b'1':raise RuntimeError('Missing capture trigger')
os.execv(sys.argv[1],sys.argv[1:])
