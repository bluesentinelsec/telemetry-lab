import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI=Path(__file__).with_name('run.py')

class CLITests(unittest.TestCase):
    def test_negative_retry_budget_rejected(self):
        result=subprocess.run([sys.executable,str(CLI),'unused','unused','--cohort','primitives','--max-retries','-1'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Invalid repetition/retry limits',result.stderr)

    @unittest.skipIf(os.name=='nt','POSIX executable-script collector fixture')
    def test_repetition_quota_and_no_retry_flag_through_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);bundle=root/'bundle';(bundle/'tmon').mkdir(parents=True)
            (bundle/'ttp-primitives/linux-c-glibc').mkdir(parents=True)
            (bundle/'ttp-primitives/linux-c-glibc/empty').write_text('fixture')
            (bundle/'manifest.json').write_text(json.dumps(dict(os=sys.platform if sys.platform=='linux' else 'linux',configs=['linux-c-glibc'],primitives=['empty'])))
            # CLI requires the target OS. On macOS, only test argument handling;
            # native CLI integration runs in Linux CI and on the disposable lab.
            if sys.platform!='linux':self.skipTest('Linux CLI fixture requires Linux')
            tmon=bundle/'tmon/tmon'
            tmon.write_text('#!'+sys.executable+'\n'+'''import sys,json
from pathlib import Path
raw=Path(sys.argv[sys.argv.index('-o')+1])
if 'attempt-01' in str(raw):raw.write_text('{bad')
else:raw.write_text(json.dumps({'record':'event'})+'\\n'+json.dumps({'record':'summary','target_exit_code':0,'total_events':1,'dropped':0})+'\\n')
''');tmon.chmod(0o755)
            base=[sys.executable,str(CLI),str(bundle)]
            result=subprocess.run(base+[str(root/'enabled'),'--cohort','primitives','--repetitions','2','--retry-delay','0'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            s=json.loads((root/'enabled/summary.json').read_text());self.assertEqual((s['accepted'],s['suspect'],s['retries']),(2,2,2))
            result=subprocess.run(base+[str(root/'disabled'),'--cohort','primitives','--repetitions','1','--no-retry'],capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stderr)
            s=json.loads((root/'disabled/summary.json').read_text());self.assertEqual((s['accepted'],s['total_attempts']),(0,1))

if __name__=='__main__':unittest.main()
