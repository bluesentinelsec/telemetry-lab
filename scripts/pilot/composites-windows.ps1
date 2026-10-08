[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Bundle,[Parameter(Mandatory=$true)][string]$Output,[int]$Repetitions=10,[int]$Seed=1,[string]$HostId='pilot',[string]$ReplaceFailedFrom='',[string]$ResumeMissingFrom='')
$ErrorActionPreference='Stop'
if(Test-Path $Output){throw 'Output exists'}
New-Item -ItemType Directory $Output | Out-Null
$coverage="$Bundle\ttp-composite\coverage"
$manifest=Get-Content "$Bundle\manifest.json" -Raw | ConvertFrom-Json
$selection=Get-Content "$coverage\selection.json" -Raw | ConvertFrom-Json
$cases=@($selection.candidates | Where-Object case_id -ne 'dns_onion' | ForEach-Object case_id)
if($cases.Count -ne 23){throw 'Qualified scope changed'}
$fixture="$Bundle\ttp-composite\windows-c-ucrt\coverage\fixtures"
$ports=@(88,2525,9389,49152);$processes=@();$policy=$null
$rng=[Random]::new($Seed);$plan=@()
for($rep=1;$rep -le $Repetitions;$rep++) {
 $configs=@($manifest.composite_configs)
 for($i=$configs.Count-1;$i -gt 0;$i--){$j=$rng.Next($i+1);$tmp=$configs[$i];$configs[$i]=$configs[$j];$configs[$j]=$tmp}
 foreach($config in $configs){$plan+=[pscustomobject]@{host=$HostId;config=$config;repetition=$rep;seed=$rng.Next(1,2147483647)}}
}
if($ReplaceFailedFrom -and $ResumeMissingFrom){throw 'Choose one recovery mode'}
if($ResumeMissingFrom) {
 $original=Get-Content "$ResumeMissingFrom\campaigns.json" -Raw | ConvertFrom-Json
 $originalPlan=Get-Content "$ResumeMissingFrom\plan.json" -Raw | ConvertFrom-Json
 if($original.Count -ne $originalPlan.plan.Count){throw 'Original campaign has not finished'}
 $plan=@()
 foreach($cell in $originalPlan.plan) {
  $name=('{0:D2}-{1}' -f $cell.repetition,$cell.config)
  $prior=Get-Content "$ResumeMissingFrom\$name\attempts.json" -Raw | ConvertFrom-Json
  $seen=@{}
  foreach($attempt in @($prior)) {
   if($null -eq $attempt){continue}
   if($attempt.case_id -notin $cases -or $attempt.mode -notin @('active','control')){throw 'Invalid prior slot'}
   $key="$($attempt.case_id)|$($attempt.mode)"
   if($seen.ContainsKey($key)){throw 'Duplicate prior slot'}
   $seen[$key]=$true
  }
  if($seen.Count -lt 2*$cases.Count){$plan+=$cell}
 }
 if(!$plan.Count){throw 'No unexecuted slots to resume'}
}
if($ReplaceFailedFrom) {
 $original=Get-Content "$ReplaceFailedFrom\campaigns.json" -Raw | ConvertFrom-Json
 $originalPlan=Get-Content "$ReplaceFailedFrom\plan.json" -Raw | ConvertFrom-Json
 if($original.Count -ne $originalPlan.plan.Count){throw 'Original campaign has not finished'}
 $failed=@($original | Where-Object {$_.error} | ForEach-Object campaign)
 $plan=@($originalPlan.plan | Where-Object {('{0:D2}-{1}' -f $_.repetition,$_.config) -in $failed})
 if(!$plan.Count -or $plan.Count -ne $failed.Count){throw 'No unambiguous failed batches to replace'}
}
@{seed=$Seed;host=$HostId;cases=$cases;plan=$plan;replaces_failed_from=$ReplaceFailedFrom;resumes_missing_from=$ResumeMissingFrom} | ConvertTo-Json -Depth 6 | Set-Content "$Output\plan.json" -Encoding UTF8
if(!(Get-NetTCPConnection -State Listen -LocalPort 3389 -ErrorAction SilentlyContinue)){throw 'Existing RDP listener required'}
if(Get-NetUDPEndpoint -LocalPort 53 -ErrorAction SilentlyContinue){throw 'UDP 53 occupied'}
foreach($rule in @(Get-DnsClientNrptRule)){foreach($name in $rule.Namespace){if($name -in @('.','api.ipify.org','.ipify.org','.org')){throw 'Overlapping DNS policy'}}}
try {
 foreach($port in $ports){
  if(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue){throw "Port $port occupied"}
  $processes+=Start-Process "$fixture\windows_echo_server.exe" -ArgumentList $port -PassThru -RedirectStandardOutput "$Output\echo-$port.log" -RedirectStandardError "$Output\echo-$port.stderr"
 }
 $dns=Start-Process "$fixture\windows_dns_server.exe" -PassThru -RedirectStandardOutput "$Output\dns.log" -RedirectStandardError "$Output\dns.stderr";$processes+=$dns
 Start-Sleep -Seconds 1
 foreach($process in $processes){if($process.HasExited){throw 'Fixture exited'}}
 $policy=Add-DnsClientNrptRule -Namespace 'api.ipify.org' -NameServers '127.0.0.1' -Comment 'Telemetry lab pilot exact-name fixture' -PassThru
 Get-DnsClientNrptPolicy -Effective | Export-Clixml "$Output\nrpt-effective.xml"
 @{ports=$ports;dns_policy=$policy.Name;dns_answer='127.0.0.42';server_sha256=(Get-FileHash "$fixture\windows_dns_server.exe").Hash;echo_sha256=(Get-FileHash "$fixture\windows_echo_server.exe").Hash;rdp=@(Get-NetTCPConnection -State Listen -LocalPort 3389 | Select-Object LocalAddress,LocalPort,OwningProcess)} | ConvertTo-Json -Depth 4 | Set-Content "$Output\fixtures.json" -Encoding UTF8
 $rows=@()
 foreach($cell in $plan){
  $name=('{0:D2}-{1}' -f $cell.repetition,$cell.config);$errorText=$null
  try {
   if($ResumeMissingFrom){& "$coverage\resume-run.ps1" -Programs "$Bundle\ttp-composite\$($cell.config)\coverage" -Output "$Output\$name" -Cases $cases -IncludeNetwork -Seed $cell.seed -SkipAttemptsFrom "$ResumeMissingFrom\$name\attempts.json"}
   else {& "$coverage\run.ps1" -Programs "$Bundle\ttp-composite\$($cell.config)\coverage" -Output "$Output\$name" -Cases $cases -IncludeNetwork -Seed $cell.seed}
  }
  catch {$errorText=$_ | Out-String; $errorText | Set-Content "$Output\$name-error.txt"}
  $rows+=[pscustomobject]@{host=$HostId;config=$cell.config;repetition=$cell.repetition;campaign=$name;error=$errorText}
  $rows | ConvertTo-Json -Depth 5 | Set-Content "$Output\campaigns.json" -Encoding UTF8
  Write-Output "PILOT_PROGRESS $HostId campaigns=$($rows.Count)/$($plan.Count) error=$([bool]$errorText)"
 }
 if(!(Get-Content "$Output\dns.log" -Raw).Contains('DNS_QUERY api.ipify.org type=1 answer=127.0.0.42')){throw 'No resolver-side evidence'}
} finally {
 if($policy){Remove-DnsClientNrptRule -Name $policy.Name -Force}
 Clear-DnsClientCache
 foreach($process in $processes){if(!$process.HasExited){Stop-Process -Id $process.Id -Force};$process.Dispose()}
 @(Get-DnsClientNrptRule) | Export-Clixml "$Output\nrpt-after.xml"
}
