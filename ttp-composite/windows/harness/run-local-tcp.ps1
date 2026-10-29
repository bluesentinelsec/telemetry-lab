# Harness-only local echo fixture. No application protocols or remote hosts.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Programs,
  [Parameter(Mandatory=$true)][string]$Output,
  [Parameter(Mandatory=$true)][string]$EchoServer,
  [ValidateSet('active','control')][string[]]$Modes=@('control','active'),
  [ValidateSet('tcp_connect_3389','tcp_connect_88','tcp_connect_2525','tcp_connect_9389','tcp_connect_public_path')][string[]]$Cases=@('tcp_connect_3389','tcp_connect_88','tcp_connect_2525','tcp_connect_9389','tcp_connect_public_path'),
  [string]$Hayabusa='C:\lab\hayabusa\hayabusa.exe'
)
$ErrorActionPreference='Stop'
# Use the existing RDP service; never replace it with an echo server.
if (!(Get-NetTCPConnection -State Listen -LocalPort 3389 -ErrorAction SilentlyContinue)) {throw 'Existing RDP listener is required'}
$ports=@(88,2525,9389,49152)
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
 @{server_sha256=(Get-FileHash $EchoServer).Hash;ports=$ports;rdp_listener=@(Get-NetTCPConnection -State Listen -LocalPort 3389 | Select-Object LocalAddress,LocalPort,OwningProcess);bind_address='127.0.0.1';process_ids=@($processes.Id)} | ConvertTo-Json -Depth 4 | Set-Content "$fixtureOutput\fixture.json" -Encoding UTF8
 & "$PSScriptRoot\run.ps1" -Programs $Programs -Output $Output -Cases $cases -IncludeNetwork -Hayabusa $Hayabusa -Modes $Modes
} finally {
 foreach($p in $processes){if(!$p.HasExited){Stop-Process -Id $p.Id -Force};$p.Dispose()}
}
