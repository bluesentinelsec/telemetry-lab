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
    overrides = yaml.safe_load((HERE / manifest['enablement_file']).read_text())
    assert len(overrides) == len({r['rule'] for r in overrides})
    assert all(set(r) == {'rule', 'enabled'} and r['enabled'] is True for r in overrides)
    enabled = {r['rule'] for r in overrides}
    assert enabled == set(manifest['enabled_by_profile'])
    assert all(name in rules and not rules[name].get('enabled', True) for name in enabled)
    assert sum(r.get('enabled', True) or name in enabled for name, r in rules.items()) == manifest['enabled_rules']
    cases = manifest['cases']
    assert len(cases) == len({c['id'] for c in cases}) == manifest['selected_rules']
    assert len({c['rule'] for c in cases}) == manifest['selected_rules']
    assert len({c['executable'] for c in cases}) == manifest['selected_rules']
    for case in cases:
        assert case['executable'] == 'coverage/' + case['id']
        assert rules[case['rule']].get('enabled', True) or case['rule'] in enabled
    return manifest

if __name__ == '__main__':
    validate()
    print('Verified case mapping and pinned Falco corpus')
