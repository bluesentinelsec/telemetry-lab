#!/usr/bin/env python3
"""Produce standalone scientific figures from the pilot's analyzed data."""
import argparse,csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
p=argparse.ArgumentParser();p.add_argument('analysis',type=Path);a=p.parse_args()
r=json.loads((a.analysis/'analysis.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
colors=['#476566','#9e906d']
fig,ax=plt.subplots(figsize=(10,6));fig.subplots_adjust(top=.78,bottom=.18,left=.12,right=.96)
for i,os in enumerate(['linux','windows']):
 values=sorted(100*x['relative_half'] for x in r['primitive_cells'] if x['os']==os)
 ax.scatter(np.linspace(i-.20,i+.20,len(values)),values,color=colors[i],s=35,alpha=.8,zorder=3)
 ax.text(i, max(values)+.13,f'Maximum ±{max(values):.2f}%',ha='center',fontsize=12,fontweight='bold',bbox=dict(facecolor='white',edgecolor='none',pad=2))
 ax.text(i,-.68,f'{len(values)} test/configuration combinations',ha='center',fontsize=10,color='#5e6762')
ax.axhline(5,color='#934e46',ls='--',lw=1.5,label='±5% precision target')
ax.set(xticks=[0,1],xticklabels=['Linux','Windows'],xlim=(-.55,1.55),ylim=(-.12,5.8),ylabel='95% interval half-width (% of mean event volume)')
ax.grid(axis='y',color='#e0e5e2');ax.legend(loc='upper left',frameon=False)
fig.suptitle('Primitive precision at 30 repetitions',x=.12,ha='left',fontsize=22,fontweight='bold',y=.96)
fig.text(.12,.865,'3,660 valid executions across three independently provisioned host pairs',color='#5e6762')
fig.text(.12,.04,'Pointwise t intervals; first launches retained. Host sensitivity is reported separately.',fontsize=10,color='#5e6762')
for ext in ['png','svg','pdf']:fig.savefig(a.analysis/f'primitive-precision.{ext}',dpi=200,facecolor='white')
plt.close(fig)
rows=list(csv.DictReader((a.analysis/'first-launch-diagnostic.csv').open()))
fig,ax=plt.subplots(figsize=(10,5.5));fig.subplots_adjust(left=.12,right=.96,top=.75,bottom=.20)
sel=[x for x in rows if x['config']=='windows-cpp-libcxx' and x['case']=='empty']
x=np.arange(3);width=.34
ax.bar(x-width/2,[float(z['first_volume']) for z in sel],width,color=colors[1],label='First measured launch')
ax.bar(x+width/2,[float(z['later_mean']) for z in sel],width,color=colors[0],label='Mean of next nine launches')
for xx,z in zip(x,sel):
 for delta,key in [(-width/2,'first_volume'),(width/2,'later_mean')]:ax.text(xx+delta,float(z[key])+12,f"{float(z[key]):,.0f}",ha='center',fontsize=11)
ax.set(xticks=x,xticklabels=['Host '+z['host'] for z in sel],ylabel='Events per program execution',ylim=(0,1250))
ax.grid(axis='y',color='#e0e5e2');ax.set_axisbelow(True);ax.legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.01),ncol=2,fontsize=10)
fig.suptitle('First launch is a separate condition',x=.12,ha='left',fontsize=22,fontweight='bold',y=.95)
fig.text(.12,.84,'Windows empty C++/libc++ program: about 45% more events on the first launch',color='#5e6762')
fig.text(.12,.065,'Exploratory diagnostic. All observations remain in the primary pilot analysis.',fontsize=10,color='#5e6762')
for ext in ['png','svg','pdf']:fig.savefig(a.analysis/f'windows-first-launch.{ext}',dpi=200,facecolor='white')
print('Saved primitive precision and first-launch figures (PNG, SVG, PDF).')
