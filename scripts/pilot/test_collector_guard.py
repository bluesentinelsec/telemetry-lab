import importlib.util,tempfile,unittest,json
from pathlib import Path
from unittest.mock import Mock,patch
spec=importlib.util.spec_from_file_location('guard',Path(__file__).with_name('collector_guard.py'));g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class CollectorGuardTests(unittest.TestCase):
 def test_unavailable_snapshots_never_certify_health(self):
  c=Mock();c.detector_state.side_effect=RuntimeError('down');s=g.snapshot(c)
  self.assertFalse(g.healthy(c,s,s));c.health_ok.assert_not_called()
 def test_recovery_keeps_evidence_and_requires_identical_binary(self):
  c=Mock();c.SERVICE='test';c.__file__='/frozen/run.py';c.detector_state.side_effect=[RuntimeError('down'),dict(service='active',counters={'drops':0})];c.detector_provenance.return_value={'sha':'changed'}
  with tempfile.TemporaryDirectory() as d,patch.object(g.time,'sleep'):
   with self.assertRaisesRegex(RuntimeError,'provenance changed'):g.ensure_ready(c,{'sha':'frozen','path':'/frozen/falco'},d,16)
   r=json.loads((Path(d)/'collector-restart-000016.json').read_text());self.assertEqual(r['actual_provenance'],{'sha':'changed'});self.assertIn('error',r['before'])
 def test_ready_collector_not_restarted(self):
  c=Mock();c.detector_state.return_value={'service':'active','counters':{'drops':0}}
  with tempfile.TemporaryDirectory() as d:g.ensure_ready(c,{'sha':'frozen'},d,0)
  c.command.assert_not_called()
 def test_attempt_replacement_is_complete_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'attempt.json';g.write_json(p,{'state':'starting'});g.write_json(p,{'state':'completed','exit':0});self.assertEqual(json.loads(p.read_text()),{'state':'completed','exit':0});self.assertFalse(p.with_suffix('.json.tmp').exists())
if __name__=='__main__':unittest.main()
