"""Publication-ready SVG/PDF/PNG figures from actual study metrics."""
import json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1])/'analysis'
def read(name):return json.loads((p/name).read_text())
c=read('primitive-curves.json');s=read('order-sensitivity.json');r=read('binary-sensitivity.json')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(13,8.2),layout='constrained');ns=[x['n'] for x in c]
for ax,metric,label,smetric in [(axes[0,0],'volume_error_percent','Mean event-count error (%)','random_order_max_volume_p95'),(axes[0,1],'composition_tv_pp','Event-composition distance\n(percentage points)','random_order_max_tv_p95')]:
 for stat,color in [('max','#466262'),('p95','#9c8e66'),('median','#8ba290')]:ax.plot(ns,[x[metric][stat] for x in c],marker='o',color=color,label={'max':'Worst cell','p95':'95th percentile cell','median':'Median cell'}[stat])
 ax.plot(ns[:-1],[x[smetric] for x in s[:-1]],color='#7c5d70',linestyle='--',label='Worst cell: order sensitivity (95th percentile; n < 100)')
 ax.set(xlabel='Development repetitions per test/configuration',ylabel=label,xticks=ns);ax.grid(alpha=.2);ax.legend(fontsize=8)
ax=axes[1,0]
for rate,color in [(.01,'#9c8e66'),(.02,'#8ba290'),(.05,'#466262'),(.1,'#7c5d70')]:ax.plot([x['n'] for x in r],[x['chance_observe_at_least_one'][str(rate)]*100 for x in r],label=f'{rate:.0%} hypothetical opposite-outcome rate',color=color)
ax.set(xlabel='Independent repetitions',ylabel='Chance of observing an opposite outcome (%)',xticks=ns,ylim=(0,102));ax.grid(alpha=.2);ax.legend(fontsize=8);ax.set_title('Binary-outcome sensitivity (model, not observed miss rates)',fontsize=10)
ax=axes[1,1];cold=sorted(read('first-launch.json'),key=lambda x:abs(x['first_excess_percent'] or 0),reverse=True)[:6]
ax.barh(range(len(cold)),[x['first_excess_percent'] for x in cold],color='#466262');ax.set_yticks(range(len(cold)),[x['config']+' / '+x['case'] for x in cold],fontsize=8);ax.invert_yaxis();ax.set_xlabel('First-launch excess over validation mean (%)');ax.set_title('First launches are a separate condition',fontsize=10);ax.grid(axis='x',alpha=.2)
fig.suptitle('Iteration count and measurement stability',fontsize=18,fontweight='bold')
for ext in ('png','svg','pdf'):fig.savefig(p/f'iteration-study.{ext}',dpi=180,bbox_inches='tight')
