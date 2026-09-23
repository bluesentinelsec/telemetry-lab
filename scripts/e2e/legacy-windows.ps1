# Exercise retained pilot programs. Report execution and attributed alerts;
# these programs do not have the independent contracts of the qualified suite.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Bundle,[Parameter(Mandatory=$true)][string]$Output)
$ErrorActionPreference='Stop'
if(Test-Path $Output){throw 'Evidence directory already exists'}
New-Item -ItemType Directory $Output -Force | Out-Null
$channel='Microsoft-Windows-Sysmon/Operational'
$manifest=Get-Content "$Bundle\manifest.json" -Raw | ConvertFrom-Json
$rows=[Collections.Generic.List[object]]::new()
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
 foreach($config in $manifest.configs) {
  foreach($case in $manifest.composites) {
   $exe="$Bundle\ttp-composite\$config\$case.exe"
   $dest="$Output\$config-$case";New-Item -ItemType Directory $dest | Out-Null
   $started=[DateTime]::UtcNow
   $process=Start-Process $exe -PassThru -NoNewWindow -RedirectStandardOutput "$dest\stdout.txt" -RedirectStandardError "$dest\stderr.txt"
   $probePid=$process.Id
   $finished=$process.WaitForExit(30000)
   if(!$finished){Stop-Process -Id $probePid -Force}
   $process.WaitForExit()
   $row=[pscustomobject]@{config=$config;case=$case;executable=$exe;sha256=(Get-FileHash $exe).Hash.ToLower();pid=$probePid;start_utc=$started.ToString('o');end_utc=[DateTime]::UtcNow.ToString('o');exit_code=$process.ExitCode;timed_out=(!$finished)}
   $rows.Add($row);$process.Dispose()
   $rows | ConvertTo-Json -Depth 5 | Set-Content "$Output\attempts.json" -Encoding UTF8
   $row | ConvertTo-Json -Compress | Write-Output
  }
 }
} finally {
 $key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($keyPath,$true)
 if($key){$key.DeleteValue('lab_test',$false);$key.Close()}
 if(!$keyExisted){[Microsoft.Win32.Registry]::CurrentUser.DeleteSubKey($keyPath,$false)}
 Remove-Item "$startup\lab_test.lnk" -Force -ErrorAction SilentlyContinue
 if(!$startupExisted){Remove-Item $startup -ErrorAction Stop}
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
Push-Location C:\lab\hayabusa
try {& .\hayabusa.exe dfir-timeline -f "$Output\events.evtx" -o "$Output\alerts.csv" -r .\rules -m low --no-wizard -p all-field-info -C *> "$Output\detector.log"; $code=$LASTEXITCODE} finally {Pop-Location}
$code | Set-Content "$Output\detector-exit.txt"
if($code -or @($rows | Where-Object {$_.exit_code -ne 0 -or $_.timed_out}).Count){throw 'Legacy execution failed; preserve evidence'}
