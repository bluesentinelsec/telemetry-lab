import json,time
from orchestrate import BASE,aws,write
fleet=json.loads((BASE/'fleet.json').read_text());online={x['InstanceId'] for x in json.loads(aws('ssm','describe-instance-information'))['InstanceInformationList'] if x['PingStatus']=='Online'}
commands=[]
for os in ('linux','windows'):
 selected=[x for x in fleet if x['os']==os and x['instance'] in online]
 if not selected:continue
 if os=='linux':script="""python3 - <<'END'
import json,pathlib
p=pathlib.Path('/opt/pilot/evidence');out={}
for cohort in ('primitives','composites'):
 f=p/cohort/'results.jsonl'
 if f.exists():
  lines=f.read_text().splitlines();rows=[]
  for line in lines:
   try:rows.append(json.loads(line))
   except ValueError:pass
  out[cohort]={'count':len(rows),'invalid':sum(not r['valid'] for r in rows),'last_rep':rows[-1]['repetition'] if rows else None}
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
 for x in selected:
  v=json.loads(aws('ssm','get-command-invocation','--command-id',cmd,'--instance-id',x['instance']));row=dict(host=x['host'],os=x['os'],status=v['Status'],output=v.get('StandardOutputContent',''),error=v.get('StandardErrorContent',''));result.append(row);print(json.dumps(row),flush=True)
with (BASE/'progress.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),hosts=result))+'\n')
