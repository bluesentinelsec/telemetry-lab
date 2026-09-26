"""Bounded replacements of invalid measurements, with immutable attempt evidence."""
import datetime
import json
import os
import time
import traceback
from pathlib import Path


class MeasurementError(Exception):
    """Known collection/infrastructure failure; eligible for bounded replacement."""


class IntegrityError(Exception):
    """Changed inputs or unsafe state: stop the campaign, never silently retry."""


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)


def append(path, value):
    with Path(path).open('a', encoding='utf-8') as f:
        f.write(json.dumps(value, allow_nan=False) + '\n'); f.flush(); os.fsync(f.fileno())


def campaign(output, plan, adapter, max_retries=3, retry_delay=1, provenance=None, inventory=None, batch_size=1):
    """Adapter returns valid/behavior-failure/measurement-failure, never selects alerts.

    Output must not exist. No implicit resume: interrupted evidence requires review.
    The accepted index contains one measurement per slot; all attempts are audited.
    """
    if max_retries < 0 or retry_delay < 0 or batch_size < 1 or not plan:
        raise ValueError('Nonempty plan and nonnegative retry limits required')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name in ('accepted', 'suspect', 'in-progress'):
        (output / name).mkdir()
    if provenance is not None:
        write_json(output/'provenance.json', provenance)
    if inventory is not None:
        write_json(output/'accepted/inventory.json', inventory)
    slots = [dict(item, run_id=f'run-{i:07d}') for i, item in enumerate(plan, 1)]
    write_json(output/'plan.json', dict(max_retries=max_retries, retry_delay=retry_delay,
                                      planned_runs=len(slots), batch_size=batch_size, slots=slots))
    accepted = []; unresolved = []; attempts = []; aborted = None
    # Retries are singleton collections. First attempts may share a drained
    # capture, but every logical slot has durable metadata before execution.
    from collections import deque
    pending = deque((slot, 1, None) for slot in slots)
    try:
        while pending:
            group = [pending.popleft()]
            if batch_size > 1 and group[0][1] == 1:
                key = adapter.batch_key(group[0][0])
                while (pending and len(group) < batch_size and pending[0][1] == 1
                       and adapter.batch_key(pending[0][0]) == key):
                    group.append(pending.popleft())
            records = []; folders = []
            for slot, number, previous in group:
                aid = f"{slot['run_id']}-attempt-{number:02d}"
                folder = output/'in-progress'/aid; folder.mkdir()
                record = dict(slot, attempt_id=aid, attempt_number=number,
                              replaces_attempt=previous,
                              started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              state='running', measurement_invoked=False)
                write_json(folder/'attempt.json', record)
                records.append(record); folders.append(folder)
            try:
                if len(group) > 1:
                    batch = output/'batches'/records[0]['attempt_id']
                    batch.mkdir(parents=True)
                    adapter.prepare_batch([g[0] for g in group], folders, batch)
                    for record, folder in zip(records, folders):
                        record['measurement_invoked'] = True
                        write_json(folder/'attempt.json', record)
                    results = adapter.execute_batch([g[0] for g in group], folders, batch)
                else:
                    slot, number, _ = group[0]
                    adapter.prepare(slot, folders[0], retry=number > 1)
                    records[0]['measurement_invoked'] = True
                    write_json(folders[0]/'attempt.json', records[0])
                    results = [adapter.execute(slot, folders[0])]
                if (len(results) != len(group) or any(r.get('status') not in
                        ('valid','measurement-failure','behavior-failure') for r in results)):
                    raise IntegrityError('Adapter did not classify every measurement')
            except MeasurementError as error:
                for folder in folders:(folder/'traceback.txt').write_text(traceback.format_exc())
                results = [dict(status='measurement-failure',reason=str(error)) for _ in group]
            except BaseException as error:
                for folder in folders:(folder/'traceback.txt').write_text(traceback.format_exc())
                aborted = f'{type(error).__name__}: {error}'
                results = [dict(status='fatal',reason=aborted) for _ in group]
            replacements = []
            for (slot, number, previous), record, folder, result in zip(group,records,folders,results):
                record.update(result)
                record.update(state='finished', ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                good = record['status'] == 'valid'
                aid = record['attempt_id']
                destination = output/('accepted' if good else 'suspect')/aid
                record['evidence'] = str(destination.relative_to(output))
                write_json(folder/'attempt.json', record); folder.rename(destination)
                append(output/'attempts.jsonl', record); attempts.append(record)
                print(json.dumps({k: record[k] for k in ('run_id','attempt_id','status','evidence')}), flush=True)
                if good:
                    accepted.append(record); append(output/'accepted.jsonl', record)
                elif aborted or record['status']=='behavior-failure' or number==max_retries+1:
                    unresolved.append(dict(slot,last_attempt=aid,status=record['status'],reason=record.get('reason')))
                else:
                    replacements.append((slot, number+1, aid))
            if aborted:break
            if replacements:
                pending.extendleft(reversed(replacements)); time.sleep(retry_delay)
    except BaseException as error:
        aborted=f'{type(error).__name__}: {error}'
        resolved={r['run_id'] for r in accepted+unresolved}
        for slot in slots:
            prior=[r for r in attempts if r['run_id']==slot['run_id']]
            if prior and slot['run_id'] not in resolved:
                unresolved.append(dict(slot,last_attempt=prior[-1]['attempt_id'],status='interrupted',reason=aborted))
    finally:
        # A batch may have queued replacements when another replacement aborts.
        # Those slots were attempted, so they must not be labelled unstarted.
        resolved={r['run_id'] for r in accepted+unresolved}
        latest={r['run_id']:r for r in attempts}
        for slot in slots:
            if slot['run_id'] in latest and slot['run_id'] not in resolved:
                prior=latest[slot['run_id']]
                unresolved.append(dict(slot,last_attempt=prior['attempt_id'],status='interrupted',reason=aborted or 'Replacement not completed'))
        by_cell = {}
        for row in attempts:
            key = '|'.join(str(row.get(k, '')) for k in ('cohort','config','case','mode'))
            counts = by_cell.setdefault(key, dict(attempts=0, accepted=0, suspect=0, retries=0))
            counts['attempts'] += 1; counts['accepted'] += row['status'] == 'valid'
            counts['suspect'] += row['status'] != 'valid'; counts['retries'] += row['attempt_number'] > 1
        summary = dict(planned_runs=len(slots), accepted=len(accepted), suspect=len(attempts)-len(accepted),
                       total_attempts=len(attempts), retries=sum(r['attempt_number'] > 1 for r in attempts),
                       unresolved=unresolved, unstarted_runs=len(slots)-len(accepted)-len(unresolved),
                       complete=len(accepted)==len(slots) and aborted is None, aborted=aborted, by_cell=by_cell)
        write_json(output/'summary.json', summary)
    return summary
