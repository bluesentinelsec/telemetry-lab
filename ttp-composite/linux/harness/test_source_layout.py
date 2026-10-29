"""Guard the public one-case/one-rule source layout across both platforms."""
import csv
import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class SourceLayoutTests(unittest.TestCase):
    def test_every_public_composite_is_a_cataloged_rule_target(self):
        for platform in ('linux', 'windows'):
            base = ROOT / 'ttp-composite' / platform
            harness = base / 'harness'
            windows = platform == 'windows'
            catalog = json.loads((harness / ('selection.json' if windows else 'manifest.json')).read_text())
            cases = catalog['candidates' if windows else 'cases']
            id_key, rule_key = ('case_id', 'rule_id') if windows else ('id', 'rule')
            ids = {c[id_key] for c in cases}
            self.assertEqual(len(ids), len(cases))
            self.assertEqual(len({c[rule_key] for c in cases}), len(cases))
            with (harness / 'rule-inventory.csv').open() as stream:
                inventory = {r[rule_key]: r for r in csv.DictReader(stream)}
            for case in cases:
                self.assertIn(case[rule_key], inventory)
                if windows:
                    for field in ('path', 'sha256', 'title'):
                        self.assertEqual(case[field], inventory[case[rule_key]][field])
            for language, extension in [('c', 'c'), ('cpp', 'cpp'), ('go', 'go'), ('rust', 'rs')]:
                lang = base / language
                with self.subTest(platform=platform, language=language):
                    self.assertFalse((lang / 'coverage').exists())
                    # No extra pilots or unclassified public case directories.
                    public = {d.name for d in lang.iterdir() if d.is_dir() and d.name not in
                              ('internal', 'toolchains', 'build', 'target', '__pycache__') and not d.name.startswith('target-')}
                    self.assertEqual(public, ids)
                    for case in cases:
                        source = lang / case[id_key] / ('main.' + extension)
                        text = source.read_text()
                        title = case['title' if windows else 'rule']
                        self.assertIn('// Target rule: ' + title + '\n', text)
                        if windows:
                            self.assertIn('// Sigma rule ID: ' + case['rule_id'] + '\n', text)
                            self.assertIn('// Ruleset path: ' + case['path'] + '\n', text)
                        self.assertIn('main(', text)
                        if language in ('c', 'cpp'):
                            for include in re.findall(r'#include \"([^\"]+)\"', text):
                                self.assertTrue((source.parent / include).is_file(), str(source) + ': ' + include)
            # Cargo must build the public entry points, rather than stale src/bin files.
            cargo = tomllib.loads((base / 'rust/Cargo.toml').read_text())
            paths = {b['path'] for b in cargo['bin']}
            expected = {name + '/main.rs' for name in ids}
            if not windows:
                expected |= {'internal/negative/main.rs', 'internal/fixture_prepare/main.rs'}
            self.assertEqual(paths, expected)

    def test_primitive_rust_entry_points_are_in_case_directories(self):
        root = ROOT / 'ttp-primitives/rust'
        workspace = tomllib.loads((root / 'Cargo.toml').read_text())
        for name in workspace['workspace']['members']:
            case = root / name
            with self.subTest(case=name):
                self.assertTrue((case / 'main.rs').is_file())
                self.assertFalse((case / 'src/main.rs').exists())
                package = tomllib.loads((case / 'Cargo.toml').read_text())
                self.assertEqual(package['bin'], [{'name': name, 'path': 'main.rs'}])


if __name__ == '__main__':
    unittest.main()
