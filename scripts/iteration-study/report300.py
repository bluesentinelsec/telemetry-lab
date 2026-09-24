"""Render observed results; keep planning choices separate from measured findings."""
import collections,csv,json,statistics,sys
from pathlib import Path

b=Path(sys.argv[1]);out=b/'analysis'
def read(n,default=None):
 p=out/n;return json.loads(p.read_text()) if p.exists() else default
def csvrows(n):
 with (out/n).open() as f:return list(csv.DictReader(f))
def table(headers,rows):
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |',*['| '+' | '.join(map(str,r))+' |' for r in rows]])
def fmt(x):return 'Not established' if x is None else f'{x:.3f}'
counts=read('counts.json');curves=read('primitive-curves.json');plateau=read('plateau-curves.json');primary=read('plateau-primary.json')
cells=csvrows('primitive-cells.csv');increments=csvrows('incremental-cell-comparisons.csv');composites=read('composite-discovery.json',[])
parts=['# Linux repetition study through 300','This study compares 20–300 development repetitions with 300 separate validation repetitions per test/configuration. Both sets are balanced across the same 20 fresh Linux hosts; validation is another sample, not ground truth. First launches are retained separately.']
choice=primary['smallest_n']
parts+=['## Prespecified decision rule',
 'For every primitive test/configuration, require agreement with validation within **2% in mean volume** and **1 percentage point in event composition**. Additional runs must change mean volume by no more than **0.5%** and composition by no more than **0.5 percentage points** at any later tested count. Require at least 100 further observations to assess those gains. These tolerances are explicit planning choices; they are not discovered statistical constants.',
 f"The earliest count satisfying that rule is **{choice} repetitions**." if choice is not None else 'The all-cell decision rule **did not establish a plateau by the eligible 200-repetition checkpoint**. The 300-run endpoint cannot establish whether later repetitions would provide negligible benefit.']
parts+=['## Observed primitive results',table(['Repetitions','Worst volume difference from validation (%)','Worst composition difference (pp)','Worst volume change at any later tested n (%)','Worst composition change at any later tested n (pp)'],[[r['n'],fmt(r['worst_validation_volume_percent']),fmt(r['worst_validation_composition_pp']),fmt(r['worst_later_volume_change_percent']),fmt(r['worst_later_composition_change_pp'])] for r in plateau if r['n'] in (100,200,300)])]
parts.append('The validation differences compare sample means and average event proportions. They do not mean that one execution emitted that percentage more telemetry. “Not established” in the endpoint row means no later count was measured.')
direct=[]
for lo,hi in ((100,200),(200,300),(100,300)):
 rs=[r for r in increments if int(r['n'])==lo and int(r['later_n'])==hi]
 v=max(rs,key=lambda r:float(r['volume_change_percent']));c=max(rs,key=lambda r:float(r['composition_change_pp']))
 direct.append([f'{lo} → {hi}',fmt(float(v['volume_change_percent'])),v['case']+' / '+v['config'],fmt(float(c['composition_change_pp'])),c['case']+' / '+c['config']])
parts += [table(['Comparison','Worst mean-volume change (%)','Volume cell','Worst composition change (pp)','Composition cell'],direct)]
se=[]
for n in (100,200,300):
 rs=[r for r in cells if int(r['n'])==n];worst=max(rs,key=lambda r:float(r['development_host_half_percent']))
 se.append([n,fmt(float(worst['development_host_half_percent'])),worst['case']+' / '+worst['config'],fmt(float(worst['development_host_se_percent'])),fmt(float(worst['development_iid_se_percent']))])
parts += ['### Uncertainty and run variability',table(['n','Largest host-based 95% interval half-width (%)','Cell','Host-based standard error (%)','IID run-level standard error for same cell (%)'],se),
 'Host-based uncertainty uses the 20 host means and retains within-host dependence. The IID calculation is a comparison, not an assumption that all native executions are independent. Intervals are pointwise, not simultaneous guarantees over every cell. Repeated-measurement dependence can invalidate the usual independent-observation uncertainty calculation ([NIST](https://www.nist.gov/publications/calculation-uncertainty-mean-autocorrelated-measurements?pub_id=151800)).']
ranges=read('subsequent-run-ranges.json',[])
if ranges:
 worst=max(ranges,key=lambda r:r['cv_percent']);constant=sum(r['min']==r['max'] for r in ranges)
 parts += [f"Across all 600 subsequent executions per cell, **{constant}/{len(ranges)} cells had identical total event counts**. This does not imply identical raw event content. The largest run-level coefficient of variation was {worst['cv_percent']:.3f}% for `{worst['case']}` / `{worst['config']}`: {worst['min']}–{worst['max']} events, mean {worst['mean']:.3f}."]
rare=read('rare-validation-only-events.json',[])
parts += [f"Event-type discovery: **{len(rare)} cell/event combinations** appeared in validation but not in the complete 300-run development sample; frequencies are retained in `analysis/rare-validation-only-events.json`."]
drift=read('temporal-drift.json',[])
if drift:
 d=max(drift,key=lambda r:abs(r['relative_change_percent']));c=max(drift,key=lambda r:r['composition_tv_pp'])
 parts += [f"Early/late diagnostic: the largest mean-volume shift between the first and last 15 subsequent chronological blocks was {d['relative_change_percent']:.3f}% (`{d['case']}` / `{d['config']}`). The largest composition shift was {c['composition_tv_pp']:.3f} pp (`{c['case']}` / `{c['config']}`). These comparisons describe drift; they do not identify its cause."]
order=read('order-sensitivity.json',[])
parts += ['### Order sensitivity',table(['n','95th percentile worst volume disagreement (%)','95th percentile worst composition disagreement (pp)','Subset samples meeting both primary agreement targets (%)'],[[r['n'],fmt(r['random_order_max_volume_p95']),fmt(r['random_order_max_tv_p95']),fmt(100*r['primary_joint_pass_fraction'])] for r in order if r['n'] in (100,200,300)]),'These 500 within-host reorderings/subsets reuse the measured development observations. They test sensitivity to which runs enter the sample; they are not 500 new experiments.']
effects=read('runtime-interpretation-by-n.json',[])
parts += ['### Runtime comparisons',table(['n','Raw validation-resolved contrasts unresolved in development','Raw sign disagreements','Empty-adjusted validation-resolved contrasts unresolved in development','Empty-adjusted sign disagreements'],[[r['n'],r['raw_unresolved_in_development'],r['raw_sign_disagreements'],r['adjusted_unresolved_in_development'],r['adjusted_sign_disagreements']] for r in effects if r['n'] in (100,200,300)]),
 '“Resolved” means the pointwise host-based interval excludes zero; it is not an effect-size requirement or a reason to choose the repetition count. Full contrast magnitudes, intervals, and event-set overlap are in `analysis/runtime-contrasts.csv`.']
replication=read('cross-study-replication.json')
if replication:
 rs=replication['cells'];v=max(rs,key=lambda r:abs(r['mean_change_percent']));c=max(rs,key=lambda r:r['composition_tv_pp'])
 parts += ['## Replication against the earlier Linux fleet',f"The largest mean-volume change between the previous 200 subsequent observations per cell and this fleet’s 600 was {v['mean_change_percent']:.3f}% (`{v['case']}` / `{v['config']}`). The largest composition difference was {c['composition_tv_pp']:.3f} pp (`{c['case']}` / `{c['config']}`). These involve different fleets and collection times, so they cannot be attributed to repetition count. The studies are not pooled."]
parts += ['## Composite detection outcomes']
if composites:
 cc=read('composite-curves.json');parts += [table(['n','Mode','Cells matching validation classification','Valid development outcomes','Unknown development outcomes'],[[r['n'],r['mode'],f"{r['class_agreement']}/{r['cells']}",r['valid'],r['unknown_or_missing']] for r in cc if r['n'] in (100,200,300)])]
 mixed=[r for r in composites if r['development_class']=='mixed' or r['validation_class']=='mixed']
 silent=[r for r in composites if r['mode']=='active' and r['development_class']==r['validation_class']=='never']
 control_alerts=[r for r in composites if r['mode']!='active' and r['subsequent_alerts']]
 parts += [f"**{len(mixed)} cells had mixed valid outcomes; {len(silent)} active cells consistently lacked the target alert; {len(control_alerts)} control cells triggered a selected rule.**",'Active outcomes refer to each composite’s target rule. Controls and negative programs are checked against all selected rules, including rules other than the paired target. Unknown outcomes never count as valid misses.']
 quality=read('composite-order-and-unknown-sensitivity.json',[])
 parts += [table(['Mode at 300 attempted repetitions','Smallest valid count per cell','Largest unknown count per cell','Largest unknown-outcome rate range (pp)'],[[r['mode'],r['minimum_valid_n'],r['maximum_unknown_n'],fmt(r['maximum_unknown_rate_bound_width_pp'])] for r in quality if r['n']==300])]
 if silent:parts += [table(['Consistently silent active composite','Configuration','Valid subsequent outcomes'],[[r['case'],r['config'],r['subsequent_valid']] for r in silent])]
 if mixed:parts += [table(['Mixed composite','Configuration','Mode','First development n showing both outcomes'],[[r['case'],r['config'],r['mode'],r['first_development_n_with_mixed_outcomes']] for r in mixed])]
 parts += ['Unchanging observed alerts do not establish a zero probability of a rare opposite outcome. Under independent Bernoulli trials, zero opposite outcomes in 100, 200, and 300 **valid** trials give one-sided 95% upper bounds of approximately 2.95%, 1.49%, and 0.99%, respectively. These are per-cell model-based bounds, not guarantees across hosts or all rules; the actual valid denominators and unknown-outcome bounds are reported separately ([NIST exact binomial bounds](https://www.itl.nist.gov/div898/handbook/prc/section2/old.prc271.htm)).']
else:parts+=['Composite collection/analysis is still in progress. No final repetition recommendation is made from this primitive-only snapshot.']
parts += ['## Quality and scope',f"Normalized records: {counts['primitive_attempts']:,} primitive attempts ({counts['primitive_invalid']:,} invalid); {counts['composite_attempts']:,} composite attempts ({counts['composite_invalid']:,} invalid). Complete primitive cells: {counts['complete_primitive_cells']}/104.",
 'The planned scope is 13 primitives × 8 configurations, plus 30 composites × 8 configurations in active and control modes and 8 negative-control cells. Every cell has 300 development, 300 validation, and 20 initial-launch observations. Planned total: 367,040 native test executions. Helpers and fixture processes are not counted.',
 'Programs, Falco binary/rules, and measured container image are frozen from the prior study. First launches are not claimed to be cold operating-system starts. Repetition reduces sampling uncertainty under these conditions; it cannot remove collector bias, establish correctness of attribution by itself, or generalize to untested platforms/rules.',
 'This is a Linux precision/stability pilot, not a power calculation for Chapter 3’s multiplicity-adjusted confirmatory comparisons. No minimum effect size was specified for that calculation. Fix the eventual repetition count before confirmatory collection, keep pilot observations out of that dataset, and evaluate Windows separately.',
 'The initial us-west-2a provisioning attempt failed for lack of capacity before any measurements. The successful fleet used the same AMI and instance type across us-west-2b and us-west-2c. This is recorded in `study-deviations.json`.',
 'Alternative precision targets and all-cell versus 95%-of-cell criteria are reported in `analysis/plateau-thresholds.json`. The prior 100-run study is not pooled into this experiment. Release publication remains deferred.']
timings=read('collection-durations.json',[])
if timings:
 pt=[r['primitive_wall_seconds'] for r in timings];ct=[r['composite_wall_seconds_including_fixture_and_evaluation'] for r in timings if 'composite_wall_seconds_including_fixture_and_evaluation' in r and not r['collector_interruption']]
 parts += ['## Measured collection time',f"Median primitive collection duration per host: {statistics.median(pt)/60:.1f} minutes for 3,224 attempts."]
 if ct:parts += [f"Median uninterrupted composite collection duration per host: {statistics.median(ct)/3600:.2f} hours for 15,128 attempts ({len(ct)} hosts with no recorded collector interruption). These times include harness/fixture/drain overhead. Full timing records include interrupted hosts as well."]
parts += ['## All measured checkpoints',table(['n','Worst volume disagreement (%)','Worst composition disagreement (pp)','Worst later volume change (%)','Worst later composition change (pp)'],[[r['n'],fmt(r['worst_validation_volume_percent']),fmt(r['worst_validation_composition_pp']),fmt(r['worst_later_volume_change_percent']),fmt(r['worst_later_composition_change_pp'])] for r in plateau]),
 '## Evidence','Raw compressed per-host archives, SHA-256 receipts, normalized rows, protocol/allocation, source snapshots, SSM commands/output, and analysis tables are retained under this study directory. Exact slot, provenance, early/final trace, and infrastructure-cleanup checks are separate machine-readable artifacts.']
(b/'report.md').write_text('\n\n'.join(parts)+'\n')
print(b/'report.md')
