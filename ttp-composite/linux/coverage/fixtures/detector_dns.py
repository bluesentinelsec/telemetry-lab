#!/usr/bin/env python3
"""Resolve the stock miner-domain lists only to an isolated lab address.

Run on the disposable detector host before Falco starts. No public miner DNS
or network access is required. Original rule predicates remain unchanged.
"""
import hashlib,json
from pathlib import Path
import yaml
here=Path(__file__).resolve().parent.parent
entries=yaml.safe_load((here/'rules/falco-sandbox_rules.yaml').read_text())
names=sorted({name for x in entries if x.get('list') in {'miner_domains','http_miner_domains','https_miner_domains'} for name in x['items']})
assert names and all(all(c.isalnum() or c in '.-' for c in name) for name in names)
begin='# BEGIN TELEMETRY LAB MINER FIXTURES\n';end='# END TELEMETRY LAB MINER FIXTURES\n'
p=Path('/etc/hosts');text=p.read_text()
if begin in text:
    head,tail=text.split(begin,1);_,tail=tail.split(end,1);text=head+tail
block=begin+''.join('198.18.0.1 '+name+'\n' for name in names)+end
p.write_text(text.rstrip()+'\n'+block)
receipt=Path('/var/lib/telemetry-lab');receipt.mkdir(parents=True,exist_ok=True)
(receipt/'miner-dns-fixture.json').write_text(json.dumps({'address':'198.18.0.1','names':names,'block_sha256':hashlib.sha256(block.encode()).hexdigest()},indent=2)+'\n')
