import json,time
from orchestrate300 import BASE,aws,write
fleet=json.loads((BASE/'fleet.json').read_text());online={x['InstanceId'] for x in json.loads(aws('ssm','describe-instance-information'))['InstanceInformationList'] if x['PingStatus']=='Online'}
archived={}
for x in fleet:
 p=BASE/'normalized'/f"{x['host']}-{x['os']}-verification.json"
 if not p.exists():continue
 v=json.loads(p.read_text())
 if v['composite_count']!=(15128 if x['os']=='linux' else 7728):continue
 archived[x['instance']]=dict(primitives=dict(count=v['primitive_count'],invalid=v['primitive_invalid'],last_rep=31),composites=dict(count=v['composite_count'],invalid=v['composite_invalid'],batches=946,collector_restarts=len(v.get('collector_restarts',[])),errors=len(v.get('campaign_execution_errors',[])),last_rep=31),archived=True)
commands=[]
for os in ('linux','windows'):
 selected=[x for x in fleet if x['os']==os and x['instance'] in online and x['instance'] not in archived]
 if not selected:continue
 if os=='linux':script="""python3 - <<'END'
import json,pathlib,collections
p=pathlib.Path('/opt/pilot/evidence');out={}
preflight=list((p/'collector-recovery-preflight').glob('*.json'))
if preflight:
 q=json.loads(preflight[0].read_text());out['collector_recovery_preflight_passed']=q.get('actual_provenance')==q.get('expected_provenance') and 'actual_provenance' in q
for cohort in ('primitives','composites'):
 f=p/cohort/'results.jsonl'
 if f.exists():
  lines=f.read_text().splitlines();rows=[]
  for line in lines:
   try:rows.append(json.loads(line))
   except ValueError:pass
  out[cohort]={'count':len(rows),'invalid':sum(not r['valid'] for r in rows),'last_rep':rows[-1]['repetition'] if rows else None}
  if cohort=='composites':
   out[cohort]['collector_restarts']=len(list((p/cohort).glob('collector-restart-*.json')))
   out[cohort]['invalid_repetitions']=dict(collections.Counter(r['repetition'] for r in rows if not r['valid']))
   out[cohort]['invalid_causes']=dict(collections.Counter('collection' if not r.get('collection_ok') else 'behavior' for r in rows if not r['valid']))
   out[cohort]['native_attempt_states']=dict(collections.Counter(r.get('native_attempt_state','unrecorded') for r in rows))
   out[cohort]['valid_active_misses']=dict(collections.Counter(r['case']+'/'+r['config'] for r in rows if r['valid'] and r['case']!='negative' and not r['control'] and not r['target_fired']))
   out[cohort]['valid_selected_control_alerts']=sum(r['valid'] and (r['case']=='negative' or r['control']) and r.get('negative_control_ok') is False for r in rows)
   failures=[]
   for batch in sorted({r['batch'] for r in rows if not r.get('collection_ok')})[-5:]:
    h=json.loads((p/cohort/batch/'health.json').read_text());b,a=h['before'],h['after']
    failures.append(dict(batch=batch,service_changed=b['service']!=a['service'],counter_decreases={k:[v,a['counters'].get(k)] for k,v in b['counters'].items() if k in a['counters'] and a['counters'][k]<v},drops_changed={k:[v,a['counters'].get(k)] for k,v in b['counters'].items() if 'drops' in k and a['counters'].get(k)!=v},errors=[x.get('error') for x in (b,a) if x.get('error')]))
   out[cohort]['recent_quality_failures']=failures
  if cohort=='composites' and len(rows)<15128 and (p/'composites.exit').exists() and not (p/'composites-resumption-started.txt').exists():out['error']='Composite collector ended before all planned slots; inspect composites.log'
print(json.dumps(out))
END"""
 else:script="""$p='C:\\lab\\pilot\\evidence';$r=@{}
if(Test-Path "$p\\primitives\\results.json"){try{$a=Get-Content "$p\\primitives\\results.json" -Raw | ConvertFrom-Json;$a=@($a);$r.primitives=@{count=$a.Count;invalid=@($a | Where-Object {!$_.valid}).Count;last_rep=$a[-1].repetition}}catch{}}
if(Test-Path "$p\\composites\\campaigns.json"){try{$a=Get-Content "$p\\composites\\campaigns.json" -Raw | ConvertFrom-Json;$a=@($a);$r.composites=@{batches=$a.Count;errors=@($a | Where-Object {$_.error}).Count;last_rep=$a[-1].repetition}}catch{}}
if(Test-Path "$p\\composites-error.txt"){$r.error=Get-Content "$p\\composites-error.txt" -Raw}
$r | ConvertTo-Json -Compress -Depth 4"""
 args=dict(InstanceIds=[x['instance'] for x in selected],DocumentName='AWS-RunPowerShellScript' if os=='windows' else 'AWS-RunShellScript',Parameters={'commands':[script],'executionTimeout':['60']})
 cmd=json.loads(aws('ssm','send-command','--cli-input-json',json.dumps(args)))['Command']['CommandId'];commands.append((cmd,selected))
time.sleep(10);result=[]
for cmd,selected in commands:
 states=json.loads(aws('ssm','list-command-invocations','--command-id',cmd,'--details'))['CommandInvocations']
 by_instance={r['InstanceId']:r for r in states}
 for x in selected:
  v=by_instance.get(x['instance'],{});plugins=v.get('CommandPlugins',[])
  if plugins and '---Output truncated---' in plugins[0].get('Output',''):
   full=json.loads(aws('ssm','get-command-invocation','--command-id',cmd,'--instance-id',x['instance']))
   plugins[0]['Output']=full.get('StandardOutputContent','')
  row=dict(host=x['host'],os=x['os'],status=v.get('Status','Pending'),output=plugins[0].get('Output','') if plugins else '',error='')
  result.append(row);print(json.dumps(row),flush=True)
for x in fleet:
 if x['instance'] in archived:
  row=dict(host=x['host'],os=x['os'],status='Archived',output=json.dumps(archived[x['instance']]),error='');result.append(row);print(json.dumps(row),flush=True)
with (BASE/'progress.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),hosts=result))+'\n')
