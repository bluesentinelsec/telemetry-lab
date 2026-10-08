"""Check selection/holdout separation, host uncertainty and unknown alert accounting."""
import csv,json,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).parent
class StudyAnalysisTests(unittest.TestCase):
 def test_control_alerts_include_non_target_selected_rules(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('normalizer',HERE/'normalize.py');normalizer=importlib.util.module_from_spec(spec);spec.loader.exec_module(normalizer)
  self.assertTrue(normalizer.linux_alert_outcome(dict(mode='control',target_rule='A',matched_rules=['B'],target_fired=None,negative_control_ok=False)))
  self.assertTrue(normalizer.linux_alert_outcome(dict(mode='negative',target_rule=None,matched_rules=['B'],target_fired=None,negative_control_ok=False)))
  self.assertFalse(normalizer.linux_alert_outcome(dict(mode='control',target_fired=None,negative_control_ok=True)))
  self.assertFalse(normalizer.linux_alert_outcome(dict(mode='active',target_fired=False,negative_control_ok=None)))
 def test_independent_blocks_cold_exclusion_and_missing_alerts(self):
  allocation=json.loads((HERE/'allocation.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'allocation.json').write_text(json.dumps(allocation));(p/'normalized').mkdir()
   primitive=[];composite=[]
   for hi,(host,phases) in enumerate(allocation.items()):
    self.assertFalse(set(phases['development'])&set(phases['validation']))
    for rep in range(1,22):
     for cfg,offset in [('linux-c-glibc',0),('linux-c-musl',50)]:
      volume=100+hi+offset if rep!=1 else 10000
      primitive.append(dict(os='linux',host=host,case='empty',config=cfg,repetition=rep,valid=True,event_counts={'write':volume}))
      primitive.append(dict(os='linux',host=host,case='file_io',config=cfg,repetition=rep,valid=True,event_counts={'write':volume+10+(20 if offset else 0)}))
     composite.append(dict(os='linux',host=host,case='example',config='linux-c-glibc',mode='active',repetition=rep,valid=not(host=='H01' and rep in phases['development']),fired=True))
   for name,rs in [('synthetic-primitives.jsonl',primitive),('synthetic-composites.jsonl',composite)]:(p/'normalized'/name).write_text(''.join(json.dumps(r)+'\n' for r in rs))
   subprocess.run([sys.executable,str(HERE/'analyze.py'),str(p),'--resamples','20'],check=True,stdout=subprocess.DEVNULL)
   curves=json.loads((p/'analysis/primitive-curves.json').read_text())
   self.assertEqual(len(curves),10)
   self.assertTrue(all(r['volume_error_percent']['max']==0 for r in curves))
   first=json.loads((p/'analysis/first-launch.json').read_text())
   self.assertTrue(all(r['first_excess_percent']>5000 for r in first))
   self.assertTrue(all(r['host_mean_ci95_half_percent']>0 for r in first))
   with (p/'analysis/runtime-contrasts.csv').open() as f:contrasts=list(csv.DictReader(f))
   self.assertTrue(all(float(r['reference_delta'])==(50 if r['case']=='empty' else 70) for r in contrasts))
   self.assertTrue(all(float(r['adjusted_reference_delta'])==20 for r in contrasts if r['case']=='file_io'))
   self.assertTrue(all(float(r['jaccard_error_pp'])==0 for r in contrasts))
   with (p/'analysis/composite-cells.csv').open() as f:cells=list(csv.DictReader(f))
   self.assertEqual(cells[0]['development_valid'],'9');self.assertEqual(cells[-1]['development_valid'],'90')
   self.assertTrue(all(r['development_class']=='always' and float(r['alert_rate_error_pp'])==0 for r in cells))
   subprocess.run([sys.executable,str(HERE/'composite_diagnostics.py'),str(p)],check=True,stdout=subprocess.DEVNULL)
   discovery=json.loads((p/'analysis/composite-discovery.json').read_text())
   self.assertEqual(discovery[0]['subsequent_unknown'],10)
   self.assertIsNone(discovery[0]['first_development_n_with_mixed_outcomes'])
   sensitivity=json.loads((p/'analysis/composite-order-and-unknown-sensitivity.json').read_text())
   self.assertTrue(all(r['minimum_order_class_agreement']==1 for r in sensitivity))
   self.assertTrue(all(abs(r['maximum_unknown_rate_bound_width_pp']-10)<1e-8 for r in sensitivity))
   # A genuine late opposite outcome must be retained and discovered at n=100.
   late=allocation['H02']['development'][-1]
   for r in composite:
    if r['host']=='H02' and r['repetition']==late:r['fired']=False
   (p/'normalized/synthetic-composites.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in composite))
   subprocess.run([sys.executable,str(HERE/'composite_diagnostics.py'),str(p)],check=True,stdout=subprocess.DEVNULL)
   discovery=json.loads((p/'analysis/composite-discovery.json').read_text())
   self.assertEqual(discovery[0]['first_development_n_with_mixed_outcomes'],100)
   self.assertEqual(discovery[0]['subsequent_alerts'],189)
   self.assertEqual(discovery[0]['subsequent_unknown'],10)
 def test_twenty_hosts_three_hundred_observations_and_late_miss(self):
  allocation={f'H{i:02}':dict(first_launch=[1],development=list(range(2,32,2)),validation=list(range(3,32,2))) for i in range(1,21)}
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'allocation.json').write_text(json.dumps(allocation));(p/'normalized').mkdir()
   primitive=[];composite=[]
   for hi,(host,phases) in enumerate(allocation.items()):
    for rep in range(1,32):
     primitive.append(dict(os='linux',host=host,case='empty',config='linux-c-glibc',repetition=rep,valid=True,event_counts={'write':100+hi if rep!=1 else 10000}))
     composite.append(dict(os='linux',host=host,case='example',config='linux-c-glibc',mode='active',repetition=rep,valid=not(host=='H01' and rep in phases['development']),fired=not(host=='H02' and rep==30)))
   for name,rs in [('synthetic-primitives.jsonl',primitive),('synthetic-composites.jsonl',composite)]:(p/'normalized'/name).write_text(''.join(json.dumps(r)+'\n' for r in rs))
   subprocess.run([sys.executable,str(HERE/'analyze.py'),str(p),'--resamples','20'],check=True,stdout=subprocess.DEVNULL)
   curves=json.loads((p/'analysis/primitive-curves.json').read_text())
   self.assertEqual([r['n'] for r in curves],list(range(20,301,20)))
   subprocess.run([sys.executable,str(HERE/'plateau.py'),str(p)],check=True,stdout=subprocess.DEVNULL)
   plateau=json.loads((p/'analysis/plateau-primary.json').read_text());self.assertEqual(plateau['smallest_n'],20)
   endpoint=json.loads((p/'analysis/plateau-curves.json').read_text())[-1]
   self.assertFalse(endpoint['eligible_for_plateau_claim']);self.assertIsNone(endpoint['worst_later_volume_change_percent'])
   self.assertTrue(all(r['volume_error_percent']['max']==0 for r in curves))
   with (p/'analysis/composite-cells.csv').open() as f:cells=list(csv.DictReader(f))
   self.assertTrue(all(r['validation_valid']=='300' for r in cells))
   self.assertEqual(cells[-1]['development_valid'],'285');self.assertEqual(cells[-1]['development_class'],'mixed')
   subprocess.run([sys.executable,str(HERE/'composite_diagnostics.py'),str(p)],check=True,stdout=subprocess.DEVNULL)
   discovery=json.loads((p/'analysis/composite-discovery.json').read_text())
   self.assertEqual(discovery[0]['first_development_n_with_mixed_outcomes'],300)
   self.assertEqual(discovery[0]['subsequent_unknown'],15)
   for script in ('diagnostics.py','dependence300.py','report300.py'):
    subprocess.run([sys.executable,str(HERE/script),str(p)],check=True,stdout=subprocess.DEVNULL)
   self.assertIn('300', (p/'report.md').read_text())
if __name__=='__main__':unittest.main()
