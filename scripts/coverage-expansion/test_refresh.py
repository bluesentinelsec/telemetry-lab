"""Check the generated refresh request without touching AWS or the real lab."""
import contextlib
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

class RefreshTests(unittest.TestCase):
    def test_generated_script_preserves_native_hashes_and_is_valid_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Path(tmp);stage=b/'stage/linux/stage/bundle';stage.mkdir(parents=True)
            (stage/'files.sha256.json').write_text(json.dumps({'ttp-composite/linux-c-glibc/coverage/a':'abc','ttp-composite/coverage/run.py':'old'}))
            outputs=b/'outputs.json';outputs.write_text(json.dumps({'test':{'Region':'us-west-2','DebianInstanceId':'i-test','DataBucketName':'test-bucket'}}))
            requests=[]
            def output(args,**kwargs):
                if args[0]=='git':return 'source-commit\n'
                self.assertEqual(args[:4],['aws','--region','us-west-2','ssm'])
                requests.append(json.loads(args[-1]));return json.dumps({'Command':{'CommandId':'test-command'}})
            def run(args,**kwargs):
                self.assertEqual(args[0],'aws');return subprocess.CompletedProcess(args,0)
            argv=['refresh-linux-fixtures.py','--evidence',str(b),'--outputs',str(outputs),'--stack','test','--phase','fixture-test']
            with patch.object(sys,'argv',argv),patch('subprocess.check_output',side_effect=output),patch('subprocess.run',side_effect=run),contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(Path(__file__).with_name('refresh-linux-fixtures.py')),run_name='__main__')
            req=requests[0];script=req['Parameters']['commands'][0]
            self.assertIn('flock -n 9',script)
            self.assertIn("for name,sha in expected.items():assert",script)
            self.assertEqual(json.loads((b/'fixture-refresh/fixture-test/native-sha256.json').read_text()),{'ttp-composite/linux-c-glibc/coverage/a':'abc'})
            embedded=re.search("python3 - <<'CHECK'\n(.*?)\nCHECK",script,re.S)[1]
            compile(embedded,'generated-refresh','exec')
            subprocess.run(['bash','-n'],input=script,text=True,check=True)
