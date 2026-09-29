import json
import tempfile
import unittest
from pathlib import Path
from engine import campaign,MeasurementError,IntegrityError

class Batch:
    def __init__(self,results):self.results=results;self.singles=[]
    def batch_key(self,s):return s['config']
    def prepare_batch(self,slots,folders,batch):
        self.slots=slots
        for s,f in zip(slots,folders):
            assert json.loads((f/'attempt.json').read_text())['run_id']==s['run_id']
    def execute_batch(self,slots,folders,batch):
        (batch/'raw').write_text('shared capture')
        if isinstance(self.results,Exception):raise self.results
        return self.results
    def prepare(self,s,f,retry=False):self.singles.append((s['run_id'],retry))
    def execute(self,s,f):return dict(status='valid',target_fired=False)

class BatchTests(unittest.TestCase):
    def run_case(self,results,**kw):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out';adapter=Batch(results)
            plan=[dict(cohort='composites',config='cfg',case=f'c{i}',mode='active',repetition=1) for i in range(3)]
            summary=campaign(out,plan,adapter,batch_size=3,retry_delay=0,**kw)
            rows=[json.loads(x) for x in (out/'attempts.jsonl').read_text().splitlines()]
            for row in rows:self.assertTrue((out/row['evidence']/'attempt.json').exists())
            return summary,rows,adapter
    def test_retry_only_invalid_member_retains_valid_miss(self):
        s,rows,a=self.run_case([dict(status='valid',target_fired=False),dict(status='measurement-failure'),dict(status='valid')])
        self.assertTrue(s['complete']);self.assertEqual(s['retries'],1)
        self.assertEqual(a.singles,[('run-0000002',True)])
        self.assertEqual(rows[-1]['replaces_attempt'],'run-0000002-attempt-01')
    def test_shared_failure_replaces_all_individually(self):
        s,rows,a=self.run_case(MeasurementError('capture loss'))
        self.assertTrue(s['complete']);self.assertEqual((s['suspect'],s['retries']),(3,3))
        self.assertTrue(all(retry for _,retry in a.singles))
    def test_behavior_failure_never_auto_replaced(self):
        s,rows,a=self.run_case([dict(status='behavior-failure'),dict(status='valid'),dict(status='valid')])
        self.assertFalse(s['complete']);self.assertEqual(s['accepted'],2);self.assertFalse(a.singles)
    def test_shared_failure_no_retry(self):
        s,rows,a=self.run_case(MeasurementError('capture loss'),max_retries=0)
        self.assertFalse(s['complete']);self.assertEqual(len(s['unresolved']),3);self.assertFalse(a.singles)
    def test_abort_accounts_for_other_pending_replacements(self):
        class AbortReplacement(Batch):
            def execute(self,s,f):raise IntegrityError('Frozen input changed')
        with tempfile.TemporaryDirectory() as t:
            plan=[dict(config='cfg',case=str(i)) for i in range(3)]
            adapter=AbortReplacement([dict(status='measurement-failure') for _ in plan])
            summary=campaign(Path(t)/'out',plan,adapter,batch_size=3,retry_delay=0)
            self.assertEqual(len(summary['unresolved']),3)
            self.assertEqual(summary['unstarted_runs'],0)
            self.assertEqual(summary['total_attempts'],4)

    def test_missing_batch_results_fatal(self):
        s,rows,a=self.run_case([dict(status='valid')])
        self.assertTrue(s['aborted']);self.assertEqual(s['accepted'],0);self.assertFalse(a.singles)

if __name__=='__main__':unittest.main()
