import json
import tempfile
import unittest
from pathlib import Path
from engine import campaign, MeasurementError, IntegrityError
from primitives import classify


class Adapter:
    def __init__(self, results):self.results=iter(results);self.prepares=[]
    def prepare(self, slot, folder, retry=False):self.prepares.append(retry)
    def execute(self, slot, folder):
        (folder/'raw.txt').write_text(str(len(self.prepares)))
        result=next(self.results)
        if isinstance(result,BaseException):raise result
        return result


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)/'campaign'
        self.plan=[dict(cohort='composites',config='runtime',case='probe',mode='active',repetition=1)]

    def run_campaign(self,results,**kw):
        adapter=Adapter(results)
        summary=campaign(self.out,self.plan,adapter,retry_delay=0,**kw)
        rows=[json.loads(line) for line in (self.out/'attempts.jsonl').read_text().splitlines()]
        return summary,rows,adapter

    def test_replacement_retains_raw_evidence_and_link(self):
        s,rows,a=self.run_campaign([MeasurementError('lost events'),dict(status='valid',target_fired=False)])
        self.assertTrue(s['complete']);self.assertEqual((s['accepted'],s['suspect'],s['retries']),(1,1,1))
        self.assertEqual(a.prepares,[False,True]);self.assertEqual(rows[1]['replaces_attempt'],rows[0]['attempt_id'])
        self.assertEqual(rows[0]['run_id'],rows[1]['run_id'])
        self.assertEqual((self.out/rows[0]['evidence']/'raw.txt').read_text(),'1')
        self.assertEqual(len(list((self.out/'accepted').iterdir())),1)
        self.assertEqual(len(list((self.out/'suspect').iterdir())),1)

    def test_miss_and_control_alert_are_not_retried(self):
        self.plan.append(dict(self.plan[0],mode='control'))
        s,rows,a=self.run_campaign([dict(status='valid',target_fired=False),dict(status='valid',control_alert=True)])
        self.assertTrue(s['complete']);self.assertEqual(s['retries'],0);self.assertEqual(len(rows),2)

    def test_default_exhaustion_is_four_attempts(self):
        s,rows,a=self.run_campaign([MeasurementError('down')]*4)
        self.assertFalse(s['complete']);self.assertEqual(s['total_attempts'],4);self.assertEqual(len(s['unresolved']),1)
        self.assertEqual(len(list((self.out/'accepted').iterdir())),0)

    def test_disabled_retry(self):
        s,rows,a=self.run_campaign([MeasurementError('down')],max_retries=0)
        self.assertEqual(s['total_attempts'],1);self.assertFalse(s['complete'])

    def test_behavior_failure_is_not_retried(self):
        s,rows,a=self.run_campaign([dict(status='behavior-failure',reason='crash')])
        self.assertEqual(s['total_attempts'],1);self.assertFalse(s['complete'])

    def test_changed_artifacts_abort_remaining_plan(self):
        self.plan.append(dict(self.plan[0],repetition=2))
        s,rows,a=self.run_campaign([IntegrityError('changed')])
        self.assertEqual(s['unstarted_runs'],1);self.assertTrue(s['aborted']);self.assertEqual(s['retries'],0)

    def test_interruption_is_quarantined(self):
        s,rows,a=self.run_campaign([KeyboardInterrupt()])
        self.assertFalse(s['complete']);self.assertEqual(rows[0]['status'],'fatal')
        self.assertFalse(list((self.out/'in-progress').iterdir()))

    def test_existing_evidence_is_never_reused(self):
        self.run_campaign([dict(status='valid')])
        with self.assertRaises(FileExistsError):campaign(self.out,self.plan,Adapter([]))

    def test_failed_recovery_does_not_launch_measurement(self):
        class RecoveryFailure(Adapter):
            def prepare(self,*args,**kw):raise MeasurementError('recovery failed')
        s=campaign(self.out,self.plan,RecoveryFailure([]),retry_delay=0)
        self.assertEqual(s['total_attempts'],4);self.assertFalse(s['complete'])

    def test_primitive_loss_corruption_and_behavior(self):
        raw=Path(self.temp.name)/'raw.jsonl'
        def data(summary):raw.write_text(json.dumps({'record':'event'})+'\n'+json.dumps(dict(record='summary',**summary))+'\n')
        data(dict(target_exit_code=0,total_events=1,dropped=0));self.assertEqual(classify(raw,0)['status'],'valid')
        data(dict(target_exit_code=0,total_events=1,lost=1));self.assertEqual(classify(raw,0)['status'],'measurement-failure')
        data(dict(target_exit_code=2,total_events=1,dropped=0));self.assertEqual(classify(raw,2)['status'],'behavior-failure')
        raw.write_text('{bad json');self.assertEqual(classify(raw,0)['status'],'measurement-failure')

if __name__=='__main__':unittest.main()
