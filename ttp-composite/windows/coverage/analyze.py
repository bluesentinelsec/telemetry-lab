#!/usr/bin/env python3
"""Join exact Hayabusa rule IDs to Sysmon records and measured process GUIDs."""
import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def as_list(value):
    if value is None:return []
    return value if isinstance(value,list) else [value]


def timestamp(value):
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def evaluate(attempt, events, alerts, healthy=True, selected_rule_ids=None):
    process=attempt['process'];start=timestamp(process['start_utc']);end=timestamp(process['end_utc'])
    starts=[e for e in events if e['event_id']==1
            and str(e['fields'].get('ProcessId'))==str(process['pid'])
            and e['fields'].get('Image','').lower()==attempt['executable'].lower()
            and start-timedelta(milliseconds=100)<=timestamp(e['time_utc'])<=end+timedelta(seconds=1)]
    staged_ok=('staged_sha256' not in attempt or attempt['staged_sha256']==attempt.get('sha256'))
    valid=healthy and attempt['behavior_ok'] and len(starts)==1 and staged_ok
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
    # A zero GUID is a loss of attribution, not proof that this program had no alert.
    # PID and event arrival within the bounded drain window only flag ambiguity;
    # they never award a positive result. EventData.UtcTime can precede process
    # creation in these asynchronous Sysmon network records.
    missing_guid={'',None,'{00000000-0000-0000-0000-000000000000}'}
    ambiguous={str(e['record_id']) for e in events
               if e['fields'].get('ProcessGuid') in missing_guid
               and str(e['fields'].get('ProcessId'))==str(process['pid'])
               and start-timedelta(seconds=1)<=timestamp(e['time_utc'])<=end+timedelta(seconds=30)}
    # Network and DNS records can arrive after process exit carrying a stale
    # nonzero GUID (including an old svchost GUID). Treat them as ambiguous,
    # not a detector miss. A positively observed later process start can prove
    # legitimate PID reuse; event arrival time alone cannot do so.
    def later_pid_reuse(event):
        return any(e['event_id']==1
                   and e['fields'].get('ProcessGuid')==event['fields'].get('ProcessGuid')
                   and str(e['fields'].get('ProcessId'))==str(process['pid'])
                   and end<timestamp(e['time_utc'])<=timestamp(event['time_utc'])
                   for e in events)
    conflicting={str(e['record_id']) for e in events
                 if e['event_id'] in (3,22) and e['fields'].get('ProcessGuid') not in guids|missing_guid
                 and str(e['fields'].get('ProcessId'))==str(process['pid'])
                 and start-timedelta(seconds=1)<=timestamp(e['time_utc'])<=end+timedelta(seconds=30)
                 and not later_pid_reuse(e)}
    # A stale GUID can also equal this *earlier* probe's GUID after its PID has
    # been reused. Do not award that delayed network/DNS event to the old probe:
    # an intervening observed process start makes its ownership ambiguous even
    # when the GUID string matches. This applies equally to active and control
    # outcomes and never depends on whether the event produced an alert.
    owned_starts={e['fields'].get('ProcessGuid'):e for e in events
                  if e['event_id']==1 and e['fields'].get('ProcessGuid') in guids}
    def owner_pid_reused(event):
        owner=owned_starts.get(event['fields'].get('ProcessGuid'))
        if not owner:return False
        pid=owner['fields'].get('ProcessId')
        if pid is None:return False
        return any(e['event_id']==1 and str(e['fields'].get('ProcessId'))==str(pid)
                   and e['fields'].get('ProcessGuid')!=owner['fields'].get('ProcessGuid')
                   and timestamp(owner['time_utc'])<timestamp(e['time_utc'])<=timestamp(event['time_utc'])
                   for e in events)
    reused_owner={str(e['record_id']) for e in events if e['event_id'] in (3,22)
                  and e['fields'].get('ProcessGuid') in guids and owner_pid_reused(e)}
    ambiguous |= conflicting | reused_owner
    ambiguous_alerts=[a for a in alerts if a.get('RuleID','').lower()==attempt['rule_id'].lower()
                      and str(a.get('RecordID','')) in ambiguous]
    control_matches=[a for a in alerts if a.get('RuleID','').lower() in (selected_rule_ids or {attempt['rule_id'].lower()})
                     and str(a.get('RecordID','')) in attributable]
    fired=bool(control_matches if attempt['mode']=='control' else matches)
    outcome=('invalid' if not valid else 'control-failed' if attempt['mode']=='control' and fired
             else 'control-pass' if attempt['mode']=='control' else 'alert' if fired else 'valid-miss')
    if valid and ambiguous:
        valid=False;outcome='attribution-incomplete'
    return dict(case_id=attempt['case_id'],runtime=attempt['runtime'],mode=attempt['mode'],
                rule_id=attempt['rule_id'],valid=valid,outcome=outcome,
                behavior_ok=attempt['behavior_ok'],process_start_matches=len(starts),
                matched_selected_rule_ids=sorted({a['RuleID'] for a in control_matches}),
                ambiguous_record_ids=sorted(ambiguous),conflicting_guid_record_ids=sorted(conflicting),reused_owner_record_ids=sorted(reused_owner),unattributed_target_record_ids=sorted({a['RecordID'] for a in ambiguous_alerts}),
                process_guids=sorted(guids),target_record_ids=sorted({a['RecordID'] for a in matches}),
                attributable_event_ids=sorted({e['event_id'] for e in events if str(e['record_id']) in attributable}))


def analyze(directory, write_result=True):
    attempts=as_list(read_json(directory/'attempts.json')) if (directory/'attempts.json').exists() else []
    events=as_list(read_json(directory/'events.json'))
    health=read_json(directory/'health.json')
    with (directory/'alerts.csv').open(encoding='utf-8-sig',newline='') as f:alerts=list(csv.DictReader(f))
    plan=read_json(directory/'run-plan.json')
    wanted=({(s['case_id'],s['mode']) for s in plan['slots']} if 'slots' in plan else
            {(c,m) for c in plan['cases'] for m in plan.get('modes', ('active','control'))})
    complete=(len(attempts)==plan['expected_attempts']==len(wanted) and {(a['case_id'],a['mode']) for a in attempts}==wanted)
    detector_ok=(directory/'detector-exit.txt').read_text().strip()=='0'
    healthy=(complete and not (directory/'execution-error.txt').exists() and detector_ok and not health['log_overwritten'] and health['sysmon_service']=='Running'
             and not as_list(health['error_events']))
    catalog=read_json(Path(__file__).with_name('selection.json'))
    selected={c['rule_id'].lower() for c in catalog['candidates']}
    rows=[evaluate(a,events,alerts,healthy,selected) for a in attempts]
    rules={c['rule_id']:c for c in catalog['candidates']}
    for row in rows:
        rule=rules[row['rule_id']]
        row['rule_authors']=rule.get('authors','')
        row['rule_source_url']=rule.get('source_url','')
    result=dict(healthy=healthy,complete=complete,expected_attempts=plan['expected_attempts'],recorded_attempts=len(attempts),attempts=rows,
                counts={key:sum(r['outcome']==key for r in rows) for key in ['alert','valid-miss','control-pass','control-failed','attribution-incomplete','invalid']})
    if write_result:(directory/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts']))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    args=parser.parse_args();result=analyze(args.directory)
    # Qualification requires target alerts; valid misses are still retained as data.
    raise SystemExit(0 if result['healthy'] and result['attempts'] and all(r['outcome'] in ('alert','control-pass') for r in result['attempts']) else 1)
