import json
import subprocess
import unittest
from run import attributed_alerts, health_ok, score
from validate_manifest import validate


class EvidenceTests(unittest.TestCase):
    def test_only_matching_container_alerts_are_scored(self):
        def event(cid, rule):
            return json.dumps({'rule':rule,'output_fields':{'container.id':cid}})
        log='\n'.join(['not json', event('abc','short'), event('b'*12,'unrelated'),
                       event('a'*12,'target'), json.dumps({'rule':'missing container'})])
        self.assertEqual([a['rule'] for a in attributed_alerts(log,'a'*64)], ['target'])

    def test_wrong_rule_does_not_satisfy_target(self):
        run=subprocess.CompletedProcess([],0,'CASE_OK example\n','')
        result=score({'id':'example','rule':'target'},run,[{'rule':'other'}],True,{'target'})
        self.assertTrue(result['valid'])
        self.assertFalse(result['target_fired'])

    def test_failed_behavior_is_invalid_even_if_target_alerts(self):
        run=subprocess.CompletedProcess([],1,'','failure')
        result=score({'id':'example','rule':'target'},run,[{'rule':'target'}],True,{'target'})
        self.assertFalse(result['valid'])

    def test_marker_and_collection_health_are_required(self):
        for text,healthy in [('',True),('CASE_OK wrong\n',True),('CASE_OK example\n',False)]:
            run=subprocess.CompletedProcess([],0,text,'')
            self.assertFalse(score({'id':'example','rule':'target'},run,[],healthy,{'target'})['valid'])

    def test_drops_and_detector_restart_invalidate_collection(self):
        before={'service':'pid=10','counters':{'n_drops':0,'n_evts':10}}
        self.assertTrue(health_ok(before,{'service':'pid=10','counters':{'n_drops':0,'n_evts':20}}))
        self.assertFalse(health_ok(before,{'service':'pid=10','counters':{'n_drops':1,'n_evts':20}}))
        self.assertFalse(health_ok(before,{'service':'pid=11','counters':{'n_drops':0,'n_evts':20}}))
        self.assertFalse(health_ok(before,{'service':'pid=10','counters':{'n_drops':0,'n_evts':5}}))

    def test_negative_control_detects_selected_rule_contamination(self):
        run=subprocess.CompletedProcess([],0,'CASE_OK negative\n','')
        result=score({'id':'negative'},run,[{'rule':'target'}],True,{'target'})
        self.assertFalse(result['negative_control_ok'])

    def test_same_binary_control_requires_control_marker_and_no_selected_alerts(self):
        case={'id':'example','rule':'target','control':True}
        run=subprocess.CompletedProcess([],0,'CONTROL_OK example\n','')
        result=score(case,run,[],True,{'target'})
        self.assertTrue(result['valid'])
        self.assertTrue(result['negative_control_ok'])
        self.assertIsNone(result['target_fired'])
        contaminated=score(case,run,[{'rule':'target'}],True,{'target'})
        self.assertFalse(contaminated['negative_control_ok'])
        wrong=subprocess.CompletedProcess([],0,'CASE_OK example\n','')
        self.assertFalse(score(case,wrong,[],True,{'target'})['valid'])

    def test_snapshot_and_mapping_integrity(self):
        self.assertEqual(len(validate()['cases']),30)


if __name__=='__main__':
    unittest.main()
