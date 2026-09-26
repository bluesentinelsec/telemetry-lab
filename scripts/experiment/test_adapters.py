import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from composites import LinuxComposites
from engine import campaign
from primitives import Primitives


class PrimitiveBoundaryTests(unittest.TestCase):
    def test_actual_subprocess_corruption_is_replaced(self):
        import os,sys
        if os.name=='nt':self.skipTest('Executable script fixture uses POSIX shebang')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'tmon').mkdir();(root/'ttp-primitives/linux-c-glibc').mkdir(parents=True)
            exe=root/'ttp-primitives/linux-c-glibc/empty';exe.write_text('test fixture')
            tmon=root/'tmon/tmon';tmon.write_text('#!'+sys.executable+'\n'+'''import json,sys
from pathlib import Path
raw=Path(sys.argv[sys.argv.index('-o')+1]); state=Path(__file__).with_name('state')
n=int(state.read_text())+1 if state.exists() else 1;state.write_text(str(n))
raw.write_text('{broken' if n==1 else json.dumps({'record':'event'})+'\\n'+json.dumps({'record':'summary','target_exit_code':0,'dropped':0,'total_events':1})+'\\n')
''');tmon.chmod(0o755)
            adapter=Primitives(root,'linux','test',lambda slot:None)
            summary=campaign(root/'out',[dict(config='linux-c-glibc',case='empty',repetition=1)],adapter,retry_delay=0)
            self.assertTrue(summary['complete']);self.assertEqual(summary['retries'],1)

    def test_behavior_failure_survives_simultaneous_falco_error(self):
        class Fake:
            def execute(self,case,config,dest,image):
                dest.mkdir();(dest/'execution.json').write_text(json.dumps(dict(returncode=1,stdout='',stderr='bad')))
                raise OSError('collector crashed')
            def score(self,*args):return dict(behavior_ok=False)
        with tempfile.TemporaryDirectory() as temp:
            adapter=object.__new__(LinuxComposites);adapter.cov=Fake();adapter.image='frozen';adapter.cases={'test':{'id':'test'}}
            result=adapter.execute(dict(case='test',config='cfg',mode='active'),Path(temp))
            self.assertEqual(result['status'],'behavior-failure')

if __name__=='__main__':unittest.main()
