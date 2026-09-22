#!/usr/bin/env python3
"""Join exact Hayabusa rule IDs to Sysmon records and measured process GUIDs."""
import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def as_list(value):
    if value is None:return []
    return value if isinstance(value,list) else [value]


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def evaluate(attempt, events, alerts, healthy=True):
    process=attempt['process'];start=timestamp(process['start_utc']);end=timestamp(process['end_utc'])
    starts=[e for e in events if e['event_id']==1
            and str(e['fields'].get('ProcessId'))==str(process['pid'])
            and e['fields'].get('Image','').lower()==attempt['executable'].lower()
            and start-timedelta(milliseconds=100)<=timestamp(e['time_utc'])<=end+timedelta(seconds=1)]
    valid=healthy and attempt['behavior_ok'] and len(starts)==1
    guids={e['fields'].get('ProcessGuid') for e in starts}
    guids.discard(None)
    # Include only descendants of the uniquely identified measured process.
    if len(starts)==1:
        changed=True
        while changed:
            before=set(guids)
            for e in events:
                if e['event_id']==1 and e['fields'].get('ParentProcessGuid') in guids:
                    guid=e['fields'].get('ProcessGuid')
                    if guid:guids.add(guid)
            changed=before!=guids
    attributable={str(e['record_id']) for e in events if e['fields'].get('ProcessGuid') in guids}
    matches=[a for a in alerts if a.get('RuleID','').lower()==attempt['rule_id'].lower()
             and str(a.get('RecordID','')) in attributable]
    fired=bool(matches)
    outcome=('invalid' if not valid else 'control-failed' if attempt['mode']=='control' and fired
             else 'control-pass' if attempt['mode']=='control' else 'alert' if fired else 'valid-miss')
    return dict(case_id=attempt['case_id'],runtime=attempt['runtime'],mode=attempt['mode'],
                rule_id=attempt['rule_id'],valid=valid,outcome=outcome,
                behavior_ok=attempt['behavior_ok'],process_start_matches=len(starts),
                process_guids=sorted(guids),target_record_ids=sorted({a['RecordID'] for a in matches}),
                attributable_event_ids=sorted({e['event_id'] for e in events if str(e['record_id']) in attributable}))


def analyze(directory):
    attempts=as_list(read_json(directory/'attempts.json'))
    events=as_list(read_json(directory/'events.json'))
    health=read_json(directory/'health.json')
    with (directory/'alerts.csv').open(encoding='utf-8-sig',newline='') as f:alerts=list(csv.DictReader(f))
    detector_ok=(directory/'detector-exit.txt').read_text().strip()=='0'
    healthy=(detector_ok and not health['log_overwritten'] and health['sysmon_service']=='Running'
             and not as_list(health['error_events']))
    rows=[evaluate(a,events,alerts,healthy) for a in attempts]
    result=dict(healthy=healthy,attempts=rows,
                counts={key:sum(r['outcome']==key for r in rows) for key in ['alert','valid-miss','control-pass','control-failed','invalid']})
    (directory/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts']))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    args=parser.parse_args();result=analyze(args.directory)
    # Qualification requires target alerts; valid misses are still retained as data.
    raise SystemExit(0 if all(r['outcome'] in ('alert','control-pass') for r in result['attempts']) else 1)
