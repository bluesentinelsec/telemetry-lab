# Exercise the smoke runner on Windows PowerShell, where Start-Process can
# return a Process whose ExitCode is null. Mock only the external tool binaries.
$ErrorActionPreference='Stop'
$root=Join-Path $env:TEMP ("release runner test " + [guid]::NewGuid().ToString('N'))
try {
 $bundle=Join-Path $root bundle
 foreach($d in @('tmon','tap','ttp-primitives\windows-c-ucrt')){New-Item -ItemType Directory (Join-Path $bundle $d) -Force | Out-Null}
 Add-Type -TypeDefinition @'
using System;
using System.IO;
public class FakeMonitor {
 public static int Main(string[] args) {
  string output=args[Array.IndexOf(args,"-o")+1];
  string target=args[args.Length-1];
  int lost=target.EndsWith("loss.exe")?3:0;
  File.WriteAllText(output,"{\"record\":\"summary\",\"target_exit_code\":0,\"lost\":"+lost+",\"total_events\":1}\n");
  Console.Out.WriteLine("stdout drained"); Console.Error.WriteLine("stderr drained");
  return target.EndsWith("monitor_failure.exe")?7:0;
 }
}
'@ -OutputAssembly "$bundle\tmon\tmon.exe" -OutputType ConsoleApplication
 Add-Type -TypeDefinition 'public class FakeTap { public static int Main(string[] args) { return 0; } }' -OutputAssembly "$bundle\tap\tap.exe" -OutputType ConsoleApplication
 foreach($case in @('valid','monitor_failure','loss')){[IO.File]::WriteAllText("$bundle\ttp-primitives\windows-c-ucrt\$case.exe",'fixture')}
 @{version='test';configs=@('windows-c-ucrt');primitives=@('valid','monitor_failure','loss')} | ConvertTo-Json | Set-Content "$bundle\manifest.json"
 @{telemetry_lab_release='test'} | ConvertTo-Json | Set-Content "$root\inventory.json"
 $rejected=$false
 try {& "$PSScriptRoot\..\e2e\primitives.ps1" -Bundle $bundle -Output "$root\results" -Inventory "$root\inventory.json"}
 catch {if($_.Exception.Message -notlike 'Primitive validation failed*'){throw};$rejected=$true}
 if(!$rejected){throw 'Runner accepted monitor failure and lost events'}
 $rows=Get-Content "$root\results\results.json" -Raw | ConvertFrom-Json
 if($rows.Count -ne 3){throw 'Runner did not exercise every case'}
 $good=$rows | Where-Object case -eq valid
 $bad=$rows | Where-Object case -eq monitor_failure
 $loss=$rows | Where-Object case -eq loss
 if(!$good.valid -or $good.exit_code -ne 0){throw 'Successful process exit code was lost'}
 if($bad.valid -or $bad.exit_code -ne 7){throw 'Monitor failure was not preserved'}
 if($loss.valid -or $loss.summary[0].lost -ne 3){throw 'Collection loss was not rejected'}
 if((Get-Content "$root\results\raw\windows-c-ucrt-valid.jsonl.stderr" -Raw).Trim() -ne 'stderr drained'){throw 'Standard error was not drained'}
 'Windows primitive runner process/health regression checks passed'
} finally {Remove-Item $root -Recurse -Force -ErrorAction SilentlyContinue}
