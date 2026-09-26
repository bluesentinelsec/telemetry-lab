# Native Windows regression: an image mapping must be released before deletion.
param([string]$Runner = "$PSScriptRoot\..\..\ttp-composite\windows\coverage\run.ps1")
$ErrorActionPreference='Stop'
$tokens=$null;$parseErrors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Resolve-Path $Runner),[ref]$tokens,[ref]$parseErrors)
if($parseErrors.Count){throw 'Runner parse failed'}
$definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Remove-OwnedFile'},$true)
if(!$definition){throw 'Cleanup function absent'}
. ([ScriptBlock]::Create($definition.Extent.Text))
$Output=Join-Path $env:TEMP ('telemetry-cleanup-test-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $Output | Out-Null
$exe=Join-Path $Output 'held.exe';$proc=$null;$release=$null
try {
  Copy-Item "$env:WINDIR\System32\ping.exe" $exe
  $proc=Start-Process $exe -ArgumentList '-t 127.0.0.1' -PassThru -WindowStyle Hidden -RedirectStandardOutput "$Output\ping.txt"
  Start-Sleep -Milliseconds 200
  if($proc.HasExited){throw 'Image-lock fixture exited early'}
  $release=Start-Job -ArgumentList $proc.Id -ScriptBlock {param($ownedPid) Start-Sleep -Milliseconds 700;Stop-Process -Id $ownedPid -Force -ErrorAction Stop}
  Remove-OwnedFile $exe
  $release | Wait-Job | Receive-Job -ErrorAction Stop
  if(Test-Path $exe){throw 'Owned image was not removed after its lock was released'}
  $rows=@(Get-Content "$Output\cleanup-retries.jsonl" | ForEach-Object {$_ | ConvertFrom-Json})
  if(!$rows.Count -or !$rows[-1].removed -or $rows[-1].retries -lt 1){throw 'Transient image lock was not recorded'}
  $proc.Dispose();$proc=$null
  # A persistent mapping must remain a failure, not be silently accepted.
  Copy-Item "$env:WINDIR\System32\ping.exe" $exe
  $proc=Start-Process $exe -ArgumentList '-t 127.0.0.1' -PassThru -WindowStyle Hidden -RedirectStandardOutput "$Output\ping-persistent.txt"
  Start-Sleep -Milliseconds 200
  $failed=$false;$timer=[Diagnostics.Stopwatch]::StartNew()
  try {Remove-OwnedFile $exe} catch [System.IO.IOException], [System.UnauthorizedAccessException] {$failed=$true}
  $timer.Stop()
  if(!$failed -or !(Test-Path $exe) -or $timer.Elapsed.TotalSeconds -lt 4.5 -or $timer.Elapsed.TotalSeconds -gt 10){throw 'Persistent lock did not produce a bounded failure'}
  'WINDOWS_CLEANUP_REGRESSION_PASSED'
} finally {
  if($proc){if(!$proc.HasExited){Stop-Process -Id $proc.Id -Force};$proc.WaitForExit();$proc.Dispose()}
  if($release){$release | Wait-Job | Out-Null;Remove-Job $release -Force}
  if(Test-Path $exe){Remove-OwnedFile $exe}
  Remove-Item $Output -Recurse -Force
}
