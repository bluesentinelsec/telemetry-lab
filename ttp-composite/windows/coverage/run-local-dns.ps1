# Harness-only DNS fixture; route only the two exact test names locally.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Programs,
 [Parameter(Mandatory=$true)][string]$Output,
 [Parameter(Mandatory=$true)][string]$DnsServer,
 [string]$Hayabusa='C:\lab\hayabusa\hayabusa.exe'
)
$ErrorActionPreference='Stop'
$names=@('lab.onion','api.ipify.org')
$fixtureOutput="$Output-fixtures"
if(Test-Path $fixtureOutput){throw 'Fixture evidence exists; choose a new output directory'}
if(Get-NetUDPEndpoint -LocalPort 53 -ErrorAction SilentlyContinue){throw 'UDP 53 is occupied'}
# Refuse overlapping policy rather than modifying another rule.
$before=@(Get-DnsClientNrptRule)
foreach($r in $before){foreach($n in $r.Namespace){if($n -in @('.','lab.onion','.onion','api.ipify.org','.ipify.org','.org')){throw 'Existing NRPT policy overlaps fixture names'}}}
New-Item -ItemType Directory $fixtureOutput -Force | Out-Null
$fixtureOutput=(Resolve-Path $fixtureOutput).Path
$before | Export-Clixml "$fixtureOutput\nrpt-before.xml"
$process=$null;$policy=$null
try {
 $process=Start-Process $DnsServer -PassThru -RedirectStandardOutput "$fixtureOutput\dns.log" -RedirectStandardError "$fixtureOutput\dns.stderr"
 Start-Sleep -Seconds 1
 if($process.HasExited){throw 'DNS fixture failed to start'}
 $policy=Add-DnsClientNrptRule -Namespace $names -NameServers '127.0.0.1' -Comment 'Telemetry lab temporary exact-name fixture' -PassThru
 Clear-DnsClientCache
 @{server_sha256=(Get-FileHash $DnsServer).Hash;process_id=$process.Id;names=$names;address='127.0.0.1';answer='127.0.0.42';policy_name=$policy.Name} | ConvertTo-Json | Set-Content "$fixtureOutput\fixture.json" -Encoding UTF8
 & "$PSScriptRoot\run.ps1" -Programs $Programs -Output $Output -Cases @('dns_onion','dns_ip_lookup') -IncludeNetwork -Hayabusa $Hayabusa
} finally {
 if($policy){Remove-DnsClientNrptRule -Name $policy.Name -Force}
 Clear-DnsClientCache
 if($process){if(!$process.HasExited){Stop-Process -Id $process.Id -Force};$process.Dispose()}
 @(Get-DnsClientNrptRule) | Export-Clixml "$fixtureOutput\nrpt-after.xml"
 if($policy -and (Get-DnsClientNrptRule | Where-Object Name -eq $policy.Name)){throw 'Temporary DNS policy was not removed'}
}
