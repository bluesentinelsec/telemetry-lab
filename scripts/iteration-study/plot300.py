"""Publication-quality figures from measured Linux repetition-study results."""
import csv,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

b=Path(sys.argv[1]);out=b/'analysis'
def read(n):return json.loads((out/n).read_text())
curves=read('primitive-curves.json');plateau=read('plateau-curves.json');ns=[r['n'] for r in curves]
with (out/'primitive-cells.csv').open() as f:cells=list(csv.DictReader(f))
colors=['#466262','#9c8e66','#698572']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(14,10))
fig.subplots_adjust(left=.08,right=.97,top=.87,bottom=.14,hspace=.48,wspace=.3)
panels=[('volume_error_percent','relative_volume_error_percent','Mean telemetry volume','Difference from validation mean (%)',2),('composition_tv_pp','composition_tv_pp','Event composition','Total variation distance (percentage points)',1)]
for ax,(metric,field,title,ylabel,tolerance) in zip(axes[0],panels):
 groups={}
 for r in cells:groups.setdefault((r['case'],r['config']),[]).append(r)
 for rs in groups.values():ax.plot([int(r['n']) for r in rs],[float(r[field]) for r in rs],color='#bcc9c3',alpha=.3,lw=.6,zorder=1)
 for stat,label,color in zip(('max','p95','median'),('Worst cell','95th percentile of cells','Median cell'),colors):
  ax.plot(ns,[r[metric][stat] for r in curves],marker='o',ms=3,label=label,color=color,lw=2,zorder=3)
 ax.axhline(tolerance,color='#7c5d70',ls='--',lw=1,label='Prespecified agreement target')
 ax.set(title=title,ylabel=ylabel,xlabel='Development repetitions per test/configuration',ylim=(0,None))
 ax.legend(fontsize=8,loc='upper right')
ax=axes[1,0]
eligible=[r for r in plateau if r['worst_later_volume_change_percent'] is not None]
ax.plot([r['n'] for r in eligible],[r['worst_later_volume_change_percent'] for r in eligible],marker='o',ms=3,color=colors[0],label='Mean-volume change (%)')
ax.plot([r['n'] for r in eligible],[r['worst_later_composition_change_pp'] for r in eligible],marker='o',ms=3,color=colors[1],label='Composition change (percentage points)')
ax.axhline(.5,color='#7c5d70',ls='--',lw=1,label='Prespecified incremental-change target')
ax.axvspan(201,300,color='#e9e9e9',alpha=.5,zorder=0)
ax.set(title='Largest change at any later tested count',ylabel='Worst change across test/configurations',xlabel='Starting repetition count',ylim=(0,None))
ax.legend(fontsize=8)
ax=axes[1,1];composites=read('composite-curves.json')
if composites:
 for mode,color in zip(('active','control','negative'),colors):
  rows=[r for r in composites if r['mode']==mode and r['os']=='linux']
  if rows:ax.plot([r['n'] for r in rows],[100*r['class_agreement']/r['cells'] for r in rows],marker='o',ms=3,color=color,label=f"{mode.capitalize()} ({rows[0]['cells']} cells)")
 ax.set(title='Alert classification agrees with validation',ylabel='Test/configuration cells agreeing (%)',xlabel='Development repetitions per test/configuration',ylim=(0,105))
 ax.legend(fontsize=8)
else:
 ax.axis('off');ax.text(.5,.5,'Composite collection in progress',ha='center',va='center',transform=ax.transAxes)
for ax in axes.flat:
 if ax.axison:ax.set_xticks([20,60,100,140,180,220,260,300]);ax.grid(alpha=.15)
fig.suptitle('Linux repetition study: measured stability',fontsize=22,fontweight='bold',y=.97)
fig.text(.5,.925,'20–300 development repetitions compared with 300 separate validation repetitions per cell',ha='center',fontsize=12,color='#5c6661')
fig.text(.08,.055,'Balanced across 20 hosts. Validation shares hosts and is not ground truth. Invalid observations are reported separately.\nGray region: fewer than 100 later observations available. The 300-run endpoint cannot establish a plateau beyond 300.',fontsize=10,color='#5c6661')
for ext in ('png','pdf','svg'):fig.savefig(out/f'linux-300-stability.{ext}',dpi=180)
