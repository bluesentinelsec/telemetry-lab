# Shared drain/evaluation only; native programs execute serially in explicit order.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Programs,
 [Parameter(Mandatory=$true)][string]$Output,
 [Parameter(Mandatory=$true)][string]$Fixtures,
 [Parameter(Mandatory=$true)][string]$PlanFile
)
$ErrorActionPreference='Stop'
$plan=(Get-Content $PlanFile -Raw | ConvertFrom-Json)
$cases=@($plan.case_id | Select-Object -Unique)
$tcp=@($cases | Where-Object {$_ -like 'tcp_connect_*'})
$dns=@($cases | Where-Object {$_ -like 'dns_*'})
$fixtureOutput="$Output-fixtures"
if(Test-Path $fixtureOutput){throw 'Fixture evidence already exists'}
New-Item -ItemType Directory $fixtureOutput -Force | Out-Null
$processes=@();$policy=$null;$runError=$null
try {
 if($tcp.Count) {
  if(!(Get-NetTCPConnection -State Listen -LocalPort 3389 -ErrorAction SilentlyContinue)){throw 'Existing RDP listener required'}
  foreach($port in @(88,2525,9389,49152)) {
   if(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue){throw "Port $port occupied"}
   $processes+=Start-Process "$Fixtures\windows_echo_server.exe" -ArgumentList $port -PassThru -RedirectStandardOutput "$fixtureOutput\echo-$port.log" -RedirectStandardError "$fixtureOutput\echo-$port.stderr"
  }
 }
 if($dns.Count) {
  if(Get-NetUDPEndpoint -LocalPort 53 -ErrorAction SilentlyContinue){throw 'UDP 53 occupied'}
  foreach($r in @(Get-DnsClientNrptRule)){foreach($n in $r.Namespace){if($n -in @('.','lab.onion','.onion','api.ipify.org','.ipify.org','.org')){throw 'Overlapping DNS policy'}}}
  $processes+=Start-Process "$Fixtures\windows_dns_server.exe" -PassThru -RedirectStandardOutput "$fixtureOutput\dns.log" -RedirectStandardError "$fixtureOutput\dns.stderr"
  $names=@($dns | ForEach-Object {if($_ -eq 'dns_onion'){'lab.onion'}else{'api.ipify.org'}})
  $policy=Add-DnsClientNrptRule -Namespace $names -NameServers '127.0.0.1' -Comment 'Telemetry lab exact-name batch fixture' -PassThru
  Clear-DnsClientCache
  Get-DnsClientNrptPolicy -Effective | Export-Clixml "$fixtureOutput\nrpt-effective.xml"
 }
 Start-Sleep -Seconds 1
 foreach($p in $processes){if($p.HasExited){throw 'Fixture exited before measurement'}}
 @{process_ids=@($processes.Id);dns_policy=$policy;dns_answer='127.0.0.42';bind_address='127.0.0.1';dns_sha256=(Get-FileHash "$Fixtures\windows_dns_server.exe").Hash;echo_sha256=(Get-FileHash "$Fixtures\windows_echo_server.exe").Hash} | ConvertTo-Json -Depth 6 | Set-Content "$fixtureOutput\fixture.json" -Encoding UTF8
 try {
  & "$PSScriptRoot\run.ps1" -Programs $Programs -Output $Output -Cases $cases -IncludeNetwork -PlanFile $PlanFile -ReturnBehaviorFailures
 } catch {
  # The adapter distinguishes persisted native/cleanup faults from export or
  # evaluator failure. A collector failure does not imply unsafe fixtures.
  $runError=$_
  if(Test-Path $Output){$_ | Out-String | Set-Content "$Output\collector-error.txt"}
 }
 foreach($p in $processes){if($p.HasExited){throw 'Fixture exited during capture'}}
 if(@($plan | Where-Object {$_.case_id -eq 'dns_ip_lookup' -and $_.mode -eq 'active'}).Count) {
  if(!(Get-Content "$fixtureOutput\dns.log" -Raw).Contains('DNS_QUERY api.ipify.org type=1 answer=127.0.0.42')){throw 'Missing responder evidence for ordinary DNS lookup'}
 }
} catch {
 if(Test-Path $Output){$_ | Out-String | Set-Content "$Output\fixture-error.txt"}
 throw
} finally {
 if($policy){Remove-DnsClientNrptRule -Name $policy.Name -Force}
 if($dns.Count){Clear-DnsClientCache}
 foreach($p in $processes){if(!$p.HasExited){Stop-Process -Id $p.Id -Force};$p.Dispose()}
 @(Get-DnsClientNrptRule) | Export-Clixml "$fixtureOutput\nrpt-after.xml"
 if($policy -and (Get-DnsClientNrptRule | Where-Object Name -eq $policy.Name)){throw 'DNS policy cleanup failed'}
}

if($runError){throw $runError}
