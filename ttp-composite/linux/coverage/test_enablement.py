import json
import unittest
from pathlib import Path
import yaml
from validate_manifest import validate

class EnablementTests(unittest.TestCase):
    def test_profile_only_enables_explicit_stock_rules(self):
        manifest=validate()
        self.assertEqual(manifest['selected_rules'],67)
        self.assertEqual(manifest['enabled_rules'],88)
        rows=yaml.safe_load(Path(__file__).with_name('enablement.yaml').read_text())
        self.assertEqual(len(rows),7)
        self.assertTrue(all(set(r)=={'rule','enabled'} and r['enabled'] is True for r in rows))
        self.assertEqual({r['rule'] for r in rows},set(manifest['enabled_by_profile']))
