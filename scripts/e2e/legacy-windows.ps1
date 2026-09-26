# Exercise retained pilot programs. Report execution and attributed alerts;
# these programs do not have the independent contracts of the qualified suite.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Bundle,[Parameter(Mandatory=$true)][string]$Output,[string]$PlanFile='')
$ErrorActionPreference='Stop'
if(Test-Path $Output){throw 'Evidence directory already exists'}
New-Item -ItemType Directory $Output -Force | Out-Null
$channel='Microsoft-Windows-Sysmon/Operational'
$manifest=Get-Content "$Bundle\manifest.json" -Raw | ConvertFrom-Json
$rows=[Collections.Generic.List[object]]::new()
$plan=@()
if($PlanFile){$plan=(Get-Content $PlanFile -Raw | ConvertFrom-Json)}
else{foreach($config in $manifest.configs){foreach($case in $manifest.composites){$plan+=@{config=$config;case=$case}}}}
foreach($slot in $plan){if($slot.config -notin $manifest.configs -or $slot.case -notin $manifest.composites){throw 'Unknown legacy slot'}}

$selection=Get-Content "$Bundle\ttp-composite\coverage\selection.json" -Raw | ConvertFrom-Json
$hayabusa='C:\lab\hayabusa\hayabusa.exe'
if((Get-FileHash $hayabusa).Hash.ToLower() -ne $selection.provenance.executable_sha256){throw 'Hayabusa differs from frozen selection'}
$rules='C:\lab\hayabusa\rules'
foreach($p in $selection.provenance.config_sha256.PSObject.Properties){
 if((Get-FileHash (Join-Path "$rules\config" $p.Name)).Hash.ToLower() -ne $p.Value){throw 'Rule configuration changed'}
}
foreach($r in (Import-Csv "$Bundle\ttp-composite\coverage\rule-inventory.csv")){
 if((Get-FileHash (Join-Path $rules $r.path)).Hash.ToLower() -ne $r.sha256){throw 'Rule corpus changed'}
}
$startRecord=(Get-WinEvent -LogName $channel -MaxEvents 1).RecordId
$keyPath='Software\Microsoft\Windows\CurrentVersion\Run'
$key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($keyPath,$true)
$keyExisted=$null -ne $key
if(!$key){$key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($keyPath)}
if('lab_test' -in $key.GetValueNames()){$key.Close();throw 'Pilot registry fixture already exists'}
$key.Close()
$startup="$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$startupExisted=Test-Path $startup
if(Test-Path "$startup\lab_test.lnk"){throw 'Pilot startup fixture already exists'}
New-Item -ItemType Directory $startup -Force | Out-Null
try {
 foreach($slot in $plan) {
  $config=$slot.config
  foreach($case in @($slot.case)) {
   $exe="$Bundle\ttp-composite\$config\$case.exe"
   $dest="$Output\$config-$case";New-Item -ItemType Directory $dest | Out-Null
   $started=[DateTime]::UtcNow
   $info=[Diagnostics.ProcessStartInfo]::new()
   $info.FileName=$exe;$info.UseShellExecute=$false
   $info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
   $process=[Diagnostics.Process]::new();$process.StartInfo=$info
   if(!$process.Start()){throw 'Cannot launch pilot program'}
   $stdoutTask=$process.StandardOutput.ReadToEndAsync();$stderrTask=$process.StandardError.ReadToEndAsync()
   $probePid=$process.Id
   $finished=$process.WaitForExit(30000)
   if(!$finished){$process.Kill()}
   $process.WaitForExit()
   [IO.File]::WriteAllText("$dest\stdout.txt",$stdoutTask.Result)
   [IO.File]::WriteAllText("$dest\stderr.txt",$stderrTask.Result)
   $row=[pscustomobject]@{config=$config;case=$case;executable=$exe;sha256=(Get-FileHash $exe).Hash.ToLower();pid=$probePid;start_utc=$started.ToString('o');end_utc=[DateTime]::UtcNow.ToString('o');exit_code=$process.ExitCode;timed_out=(!$finished)}
   $rows.Add($row);$process.Dispose()
   $rows | ConvertTo-Json -Depth 5 | Set-Content "$Output\attempts.json" -Encoding UTF8
   $row | ConvertTo-Json -Compress | Write-Output
  }
 }
} finally {
 try {
 $key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($keyPath,$true)
 if($key){$key.DeleteValue('lab_test',$false);$key.Close()}
 if(!$keyExisted){[Microsoft.Win32.Registry]::CurrentUser.DeleteSubKey($keyPath,$false)}
 Remove-Item "$startup\lab_test.lnk" -Force -ErrorAction SilentlyContinue
 if(!$startupExisted){Remove-Item $startup -ErrorAction Stop}
 } catch {$_ | Out-String | Set-Content "$Output\cleanup-error.txt";throw}
}
Start-Sleep -Seconds 20
$endRecord=(Get-WinEvent -LogName $channel -MaxEvents 1).RecordId
$query="*[System[(EventRecordID > $startRecord) and (EventRecordID <= $endRecord)]]"
& wevtutil epl $channel "$Output\events.evtx" "/q:$query" /ow:true
if($LASTEXITCODE){throw 'EVTX export failed'}
$events=@(Get-WinEvent -Path "$Output\events.evtx" -Oldest | ForEach-Object {
 $xml=[xml]$_.ToXml();$fields=@{}
 foreach($field in $xml.Event.EventData.Data){$fields[[string]$field.Name]=[string]$field.'#text'}
 [pscustomobject]@{record_id=$_.RecordId;event_id=$_.Id;time_utc=$_.TimeCreated.ToUniversalTime().ToString('o');fields=$fields}
})
$events | ConvertTo-Json -Depth 7 | Set-Content "$Output\events.json" -Encoding UTF8
$oldest=(Get-WinEvent -LogName $channel -Oldest -MaxEvents 1).RecordId
@{start_record=$startRecord;end_record=$endRecord;log_overwritten=($oldest -gt ($startRecord+1));sysmon_service=(Get-Service Sysmon64).Status.ToString();error_events=@($events | Where-Object event_id -in @(4,16,255))} | ConvertTo-Json -Depth 7 | Set-Content "$Output\health.json" -Encoding UTF8
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName='C:\lab\hayabusa\hayabusa.exe';$info.WorkingDirectory='C:\lab\hayabusa';$info.UseShellExecute=$false
$info.Arguments="dfir-timeline -f `"$Output\events.evtx`" -o `"$Output\alerts.csv`" -r .\rules -m low --no-wizard -p all-field-info -C"
$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
$detector=[Diagnostics.Process]::new();$detector.StartInfo=$info
if(!$detector.Start()){throw 'Cannot launch Hayabusa'}
$stdoutTask=$detector.StandardOutput.ReadToEndAsync();$stderrTask=$detector.StandardError.ReadToEndAsync()
if(!$detector.WaitForExit(120000)){$detector.Kill();throw 'Hayabusa timed out'}
$detector.WaitForExit();$code=$detector.ExitCode
[IO.File]::WriteAllText("$Output\detector.log",$stdoutTask.Result)
[IO.File]::WriteAllText("$Output\detector.stderr",$stderrTask.Result)
$detector.Dispose()
$code | Set-Content "$Output\detector-exit.txt"
if($code -or @($rows | Where-Object {$_.exit_code -ne 0 -or $_.timed_out}).Count){throw 'Legacy execution failed; preserve evidence'}
