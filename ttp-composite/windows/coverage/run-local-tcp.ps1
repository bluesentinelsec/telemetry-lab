# Harness-only local echo fixture. No application protocols or remote hosts.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Programs,
  [Parameter(Mandatory=$true)][string]$Output,
  [Parameter(Mandatory=$true)][string]$EchoServer,
  [string]$Hayabusa='C:\lab\hayabusa\hayabusa.exe'
)
$ErrorActionPreference='Stop'
# 3389 is deliberately not claimed here: its existing RDP listener is a pending user decision.
$ports=@(88,2525,9389,49152)
$cases=@('tcp_connect_88','tcp_connect_2525','tcp_connect_9389','tcp_connect_public_path')
$fixtureOutput="$Output-fixtures"
if(Test-Path $fixtureOutput){throw 'Fixture evidence exists; choose a new output directory'}
New-Item -ItemType Directory $fixtureOutput -Force | Out-Null
$fixtureOutput=(Resolve-Path $fixtureOutput).Path
$processes=@()
try {
 foreach($port in $ports) {
  if(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue){throw "Port $port is occupied; do not change services automatically"}
  $process=Start-Process $EchoServer -ArgumentList $port -PassThru -RedirectStandardOutput "$fixtureOutput\echo-$port.log" -RedirectStandardError "$fixtureOutput\echo-$port.stderr"
  $processes+=$process
 }
 Start-Sleep -Seconds 1
 foreach($p in $processes){if($p.HasExited){throw 'Echo fixture failed to start'}}
 @{server_sha256=(Get-FileHash $EchoServer).Hash;ports=$ports;bind_address='127.0.0.1';process_ids=@($processes.Id)} | ConvertTo-Json | Set-Content "$fixtureOutput\fixture.json" -Encoding UTF8
 & "$PSScriptRoot\run.ps1" -Programs $Programs -Output $Output -Cases $cases -IncludeNetwork -Hayabusa $Hayabusa
} finally {
 foreach($p in $processes){if(!$p.HasExited){Stop-Process -Id $p.Id -Force};$p.Dispose()}
}
