"""Observed sample-size curves and detector agreement, without hypothetical rates."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('--recommended',type=int);a=p.parse_args();out=a.base/'analysis'
def read(name):return json.loads((out/name).read_text())
curves=read('primitive-curves.json');composites=read('composite-curves.json');ns=[r['n'] for r in curves]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(14,8));grid=fig.add_gridspec(2,2,height_ratios=[3.6,1],hspace=.52,bottom=.15,top=.86,left=.08,right=.96,wspace=.25)
for col,metric,title,ylabel in [(0,'volume_error_percent','Mean telemetry volume','Difference from validation mean (%)'),(1,'composition_tv_pp','Event composition','Total variation distance (percentage points)')]:
 ax=fig.add_subplot(grid[0,col])
 for stat,label,color in [('max','Worst test/configuration','#466262'),('p95','95th percentile across test/configurations','#9c8e66')]:ax.plot(ns,[r[metric][stat] for r in curves],marker='o',label=label,color=color,linewidth=2)
 if a.recommended:ax.axvline(a.recommended,color='#7c5d70',linestyle='--',alpha=.7,label=f'{a.recommended}-run primitive choice')
 ax.set(xlabel='Development executions per test/configuration',ylabel=ylabel,xticks=ns,ylim=(0,None),title=title);ax.grid(alpha=.18);ax.legend(fontsize=9)
ax=fig.add_subplot(grid[1,:]);ax.axis('off');rows=[];labels=[]
for os in ('linux','windows'):
 selected={r['n']:r for r in composites if r['os']==os and r['mode']=='active'}
 if not selected:continue
 labels.append(os.capitalize());rows.append([f"{selected[n]['class_agreement']}/{selected[n]['cells']}" if n in selected else 'Pending' for n in ns])
if rows:
 table=ax.table(cellText=rows,rowLabels=labels,colLabels=[str(n) for n in ns],loc='center',cellLoc='center');table.auto_set_font_size(False);table.set_fontsize(11);table.scale(1,1.7)
 for (r,c),cell in table.get_celld().items():
  cell.set_edgecolor('#dce2df')
  if r==0:cell.set_facecolor('#eaf0ed')
 ax.set_title('Active composite cells matching the validation alert classification',fontsize=12,pad=14)
fig.suptitle('Repetition count: observed stability',fontsize=22,fontweight='bold',y=.96)
fig.text(.5,.90,'10, 20, …, 100 development executions compared with 100 separate validation executions',ha='center',fontsize=12,color='#5c6661')
fig.text(.08,.065,'Balanced across ten hosts per platform. Validation is a sample, not ground truth.\nAlert classifications use valid observations; unknown outcomes and denominators are reported separately.',fontsize=10,color='#5c6661')
for ext in ('png','pdf','svg'):fig.savefig(out/f'observed-iteration-stability.{ext}',dpi=180)
