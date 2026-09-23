import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('release',Path(__file__).parents[1]/'validate-release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        manifest=dict(os='linux',configs=['linux-c-glibc'],composite_configs=['linux-c-glibc'],primitives=['empty'],composites=['reverse_shell'])
        (self.root/'manifest.json').write_text(json.dumps(manifest))
        for name in ['tmon/tmon','tap/tap','ttp-primitives/linux-c-glibc/empty','ttp-composite/linux-c-glibc/reverse_shell','ttp-composite/linux-c-glibc/coverage/target','ttp-composite/linux-c-glibc/coverage/negative','ttp-composite/linux-c-glibc/coverage/fixture_prepare']:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'program')
        p=self.root/'ttp-composite/coverage/manifest.json';p.parent.mkdir();p.write_text(json.dumps(dict(cases=[dict(id='target')])))

    def test_complete_bundle_and_tampering(self):
        original=release.validate(self.root)
        (self.root/'tmon/tmon').write_bytes(b'changed monitor')
        self.assertNotEqual(original,release.validate(self.root))

    def test_missing_primitive(self):
        (self.root/'ttp-primitives/linux-c-glibc/empty').unlink()
        with self.assertRaisesRegex(ValueError,'empty'):release.validate(self.root)

    def test_missing_composite(self):
        (self.root/'ttp-composite/linux-c-glibc/coverage/target').unlink()
        with self.assertRaisesRegex(ValueError,'coverage/target'):release.validate(self.root)

    def test_empty_monitor(self):
        (self.root/'tmon/tmon').write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'tmon/tmon'):release.validate(self.root)

if __name__=='__main__':unittest.main()
