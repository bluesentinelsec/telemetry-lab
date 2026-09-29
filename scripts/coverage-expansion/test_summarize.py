import json
import tempfile
import unittest
from pathlib import Path
from summarize import summarize

class EvidenceSummaryTests(unittest.TestCase):
    def test_batch_and_replacement_formats_preserve_misses_and_control_alerts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            slots=[dict(config='windows-c-ucrt',case='example',mode=m,repetition=1) for m in ('active','control')]
            records=[]
            for slot,outcome in zip(slots,('valid-miss','control-failed')):
                row=dict(case_id='example',mode=slot['mode'],valid=True,outcome=outcome)
                measurement=row if slot['mode']=='control' else dict(healthy=True,attempts=[row])
                records.append(dict(**slot,os='windows',status='valid',measurement=measurement))
            (root/'plan.json').write_text(json.dumps(dict(slots=slots)))
            (root/'summary.json').write_text('{}')
            (root/'accepted.jsonl').write_text('\n'.join(map(json.dumps,records)))
            result=summarize(root)
            self.assertTrue(result['complete'])
            self.assertEqual(result['outcomes'],{'valid-miss':1,'control-alert':1})
            # An original and replacement cannot both count toward the same slot.
            with (root/'accepted.jsonl').open('a') as f:f.write('\n'+json.dumps(records[0]))
            with self.assertRaisesRegex(AssertionError,'Duplicate'):summarize(root)

if __name__=='__main__':unittest.main()
