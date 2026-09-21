#!/usr/bin/env python3
"""Verify the fixed rule corpus and the complete case-to-rule mapping."""
import hashlib
import json
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent

def validate():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    rules = {}
    for spec in manifest['rule_files']:
        path = HERE / 'rules' / spec['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['sha256'], path
        entries = [x for x in yaml.safe_load(path.read_text()) if 'rule' in x]
        assert len(entries) == spec['rules']
        for rule in entries:
            assert rule['rule'] not in rules, rule['rule']
            rules[rule['rule']] = rule
    assert len(rules) == manifest['provided_rules'] == 95
    assert sum(r.get('enabled', True) for r in rules.values()) == 81
    cases = manifest['cases']
    assert len(cases) == len({c['id'] for c in cases}) == 30
    assert len({c['rule'] for c in cases}) == 30
    assert len({c['executable'] for c in cases}) == 30
    for case in cases:
        assert case['executable'] == 'coverage/' + case['id']
        assert rules[case['rule']].get('enabled', True)
    return manifest

if __name__ == '__main__':
    validate()
    print('Verified: 30 cases / 30 selected rules / 95 provided / 81 stock-enabled')
