import copy
import unittest
import json
import tempfile
import subprocess
import sys
from pathlib import Path
from analyze import evaluate, analyze

class AttributionTests(unittest.TestCase):
    def setUp(self):
        self.attempt=dict(case_id='case',mode='active',runtime='ucrt',rule_id='target',executable=r'C:\lab\probe.exe',behavior_ok=True,process=dict(pid=100,start_utc='2026-09-22T12:00:00Z',end_utc='2026-09-22T12:00:01Z'))
        self.events=[dict(record_id=1,event_id=1,time_utc='2026-09-22T12:00:00.100Z',fields=dict(ProcessId='100',Image=r'C:\lab\probe.exe',ProcessGuid='probe')),dict(record_id=2,event_id=3,time_utc='2026-09-22T12:00:00.500Z',fields=dict(ProcessGuid='probe'))]
    def test_exact_id_and_process_required(self):
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='other',RecordID='2')])['outcome'],'valid-miss')
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='target',RecordID='999')])['outcome'],'valid-miss')
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='target',RecordID='2')])['outcome'],'alert')
    def test_helper_or_cleanup_alert_not_attributed(self):
        events=self.events+[dict(record_id=3,event_id=3,time_utc='2026-09-22T12:00:00Z',fields=dict(ProcessGuid='harness'))]
        self.assertEqual(evaluate(self.attempt,events,[dict(RuleID='target',RecordID='3')])['outcome'],'valid-miss')
    def test_descendant_supported(self):
        events=self.events+[dict(record_id=3,event_id=1,time_utc='2026-09-22T12:00:00.700Z',fields=dict(ProcessGuid='child',ParentProcessGuid='probe'))]
        self.assertEqual(evaluate(self.attempt,events,[dict(RuleID='target',RecordID='3')])['outcome'],'alert')
    def test_bad_behavior_or_capture_not_a_miss(self):
        self.assertEqual(evaluate(self.attempt,self.events,[],False)['outcome'],'invalid')
        self.attempt['behavior_ok']=False
        self.assertEqual(evaluate(self.attempt,self.events,[])['outcome'],'invalid')
    def test_pid_reuse_does_not_join(self):
        events=copy.deepcopy(self.events);events[0]['time_utc']='2026-09-22T11:00:00Z'
        self.assertEqual(evaluate(self.attempt,events,[])['outcome'],'invalid')
    def test_control_alert_is_failure(self):
        self.attempt['mode']='control'
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='target',RecordID='2')])['outcome'],'control-failed')
    def test_zero_guid_alert_is_not_a_valid_miss(self):
        events=copy.deepcopy(self.events)
        events[1]['fields']=dict(ProcessGuid='{00000000-0000-0000-0000-000000000000}',ProcessId='100',UtcTime='2026-09-22 12:00:00.500')
        events[1]['time_utc']='2026-09-22T12:00:03Z'
        result=evaluate(self.attempt,events,[dict(RuleID='target',RecordID='2')])
        self.assertEqual(result['outcome'],'attribution-incomplete')
        self.assertFalse(result['valid'])
        self.assertEqual(result['unattributed_target_record_ids'],['2'])
    def test_stale_nonzero_guid_during_probe_is_incomplete(self):
        events=copy.deepcopy(self.events)
        events[1]['fields']=dict(ProcessGuid='old-conhost-guid',ProcessId='100',Image=r'C:\Windows\System32\conhost.exe')
        result=evaluate(self.attempt,events,[dict(RuleID='target',RecordID='2')])
        self.assertEqual(result['outcome'],'attribution-incomplete')
        self.assertEqual(result['conflicting_guid_record_ids'],['2'])
        self.assertEqual(result['target_record_ids'],[])
        self.assertEqual(result['unattributed_target_record_ids'],['2'])
    def test_later_pid_reuse_does_not_invalidate_probe(self):
        events=copy.deepcopy(self.events)
        events.append(dict(record_id=3,event_id=3,time_utc='2026-09-22T12:00:20Z',fields=dict(ProcessGuid='later-process',ProcessId='100')))
        result=evaluate(self.attempt,events,[dict(RuleID='target',RecordID='2')])
        self.assertEqual(result['outcome'],'alert')
    def test_missing_start_is_invalid(self):
        self.assertEqual(evaluate(self.attempt,self.events[1:],[])['outcome'],'invalid')

    def test_staged_binary_must_match_manifest(self):
        self.attempt.update(sha256='expected',staged_sha256='different')
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='target',RecordID='2')])['outcome'],'invalid')
        self.attempt['staged_sha256']='expected'
        self.events[0]['fields']['Hashes']='SHA256=previous-case'
        self.assertEqual(evaluate(self.attempt,self.events,[dict(RuleID='target',RecordID='2')])['outcome'],'alert')

    def test_campaign_aborted_before_first_attempt_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,value in {'events.json':[], 'health.json':{'log_overwritten':False,'sysmon_service':'Running','error_events':[]},
                               'run-plan.json':{'cases':['registry_run_key'],'expected_attempts':2}}.items():
                (root/name).write_text(json.dumps(value))
            (root/'alerts.csv').write_text('RuleID,RecordID\n')
            (root/'detector-exit.txt').write_text('0')
            (root/'execution-error.txt').write_text('Fixture precondition failed')
            result=analyze(root)
            self.assertFalse(result['healthy']);self.assertFalse(result['complete'])
            self.assertEqual(result['recorded_attempts'],0)
            command=subprocess.run([sys.executable,str(Path(__file__).with_name('analyze.py')),str(root)],capture_output=True)
            self.assertEqual(command.returncode,1)

if __name__=='__main__':unittest.main()
