# Qualify exact-rule outcomes; setup/cleanup and helpers are outside measured processes.
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Programs,
  [Parameter(Mandatory=$true)][string]$Output,
  [string]$Hayabusa = 'C:\lab\hayabusa\hayabusa.exe',
  [string[]]$Cases = @(),
  [switch]$IncludeNetwork,
  [switch]$BehaviorOnly,
  [string]$PlanFile = '',
  [switch]$ReturnBehaviorFailures,
  [ValidateSet('active','control')][string[]]$Modes = @('control','active'),
  [int]$Seed = -1,
  [string]$SkipAttemptsFrom = ''
)
$lock = [Threading.Mutex]::new($false, 'Global\TelemetryLabWindowsQualification')
if (!$lock.WaitOne(0)) { $lock.Dispose(); throw 'Another Windows qualification run is active' }
try {
$ErrorActionPreference = 'Stop'
$root = 'C:\lab\windows-coverage'
$channel = 'Microsoft-Windows-Sysmon/Operational'
$selection = Get-Content "$PSScriptRoot\selection.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$build = Get-Content "$Programs\build-manifest.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$allCases = @($selection.candidates | Where-Object { (!$Cases.Count -or $_.case_id -in $Cases) -and ($IncludeNetwork -or $_.family -notin @('Network','DNS')) })
if (!$allCases.Count) { throw 'No selected cases' }
# Explicit plans retain their order; seeded pilot runs shuffle cases and modes.
if($PlanFile -and $Seed -ge 0){throw 'PlanFile and Seed are mutually exclusive'}
$rng=$null
if($Seed -ge 0) {
  $rng=[Random]::new($Seed)
  for($i=$allCases.Count-1;$i -gt 0;$i--){$j=$rng.Next($i+1);$tmp=$allCases[$i];$allCases[$i]=$allCases[$j];$allCases[$j]=$tmp}
}
if (!$Modes.Count -or @($Modes | Select-Object -Unique).Count -ne $Modes.Count) { throw 'Select unique nonempty modes' }
$nativePlan=@()
if($PlanFile) {
  $nativePlan=@(foreach($item in (Get-Content $PlanFile -Raw -Encoding UTF8 | ConvertFrom-Json)) {
    [pscustomobject]@{case_id=[string]$item.case_id;mode=[string]$item.mode}
  })
  $keys=@($nativePlan | ForEach-Object {"$($_.case_id)|$($_.mode)"})
  if(!$nativePlan.Count -or @($keys | Select-Object -Unique).Count -ne $keys.Count){throw 'Nonempty unique native plan required'}
  foreach($slot in $nativePlan) {
    if($slot.case_id -notin $allCases.case_id -or $slot.mode -notin @('active','control')){throw 'Unknown native plan slot'}
  }
} else {
  foreach($case in $allCases){
    $caseModes=@($Modes)
    if($rng -and $caseModes.Count -eq 2 -and $rng.Next(2) -eq 1){[array]::Reverse($caseModes)}
    foreach($mode in $caseModes){$nativePlan+=@{case_id=$case.case_id;mode=$mode}}
  }
}

if (Test-Path $Output) { throw 'Evidence directory already exists; retain previous attempts and use a new directory' }
New-Item -ItemType Directory -Path $Output -Force | Out-Null
$Output = (Resolve-Path $Output).Path
$Programs = (Resolve-Path $Programs).Path
$skipAttempts=@{};$priorAttemptsHash=$null
if($SkipAttemptsFrom) {
  $prior=Get-Content -LiteralPath $SkipAttemptsFrom -Raw | ConvertFrom-Json
  foreach($attempt in @($prior)) {
    if($null -eq $attempt){continue}
    if(!@($nativePlan | Where-Object {$_.case_id -eq $attempt.case_id -and $_.mode -eq $attempt.mode}).Count){throw 'Invalid prior attempt identity'}
    $key="$($attempt.case_id)|$($attempt.mode)"
    if($skipAttempts.ContainsKey($key)){throw 'Duplicate prior attempt identity'}
    $skipAttempts[$key]=$true
  }
  $priorAttemptsHash=(Get-FileHash -LiteralPath $SkipAttemptsFrom).Hash.ToLower()
  Copy-Item -LiteralPath $SkipAttemptsFrom -Destination "$Output\prior-attempts.json"
}
$env:TELEMETRY_LAB_FIXTURE = '1'
$attempts = [Collections.Generic.List[object]]::new()
$changes = [Collections.Generic.List[object]]::new()
$stagedDlls = [Collections.Generic.List[string]]::new()
$createdDirs = [Collections.Generic.List[string]]::new()
function Ensure-Directory([string]$path) {
  if (!(Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null; $createdDirs.Add($path) }
}
function Remove-OwnedFile([string]$path) {
  # Verify the cleanup postcondition: a sensor can delay or veto deletion
  # without Remove-Item raising an exception. Only harness-owned paths enter here.
  $lastError='File still exists after deletion request'
  for($retry=0;$retry -le 100;$retry++) {
    if (!(Test-Path -LiteralPath $path)) { return }
    try { Remove-Item -LiteralPath $path -Force -ErrorAction Stop }
    catch [System.IO.IOException], [System.UnauthorizedAccessException] { $lastError=$_.Exception.Message }
    if (!(Test-Path -LiteralPath $path)) {
      if($retry){@{path=$path;retries=$retry;removed=$true} | ConvertTo-Json -Compress | Add-Content "$Output\cleanup-retries.jsonl"}
      return
    }
    if($retry -lt 100){Start-Sleep -Milliseconds 100}
  }
  @{path=$path;retries=100;removed=$false;error=$lastError} | ConvertTo-Json -Compress | Add-Content "$Output\cleanup-retries.jsonl"
  throw [System.IO.IOException]::new("Cleanup postcondition failed for ${path}: $lastError")
}
function Save-RegistryValue([string]$path,[string]$name) {
  $key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($path,$true)
  $keyExisted=$null -ne $key
  if (!$key) { $key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($path) }
  $exists=$name -in $key.GetValueNames()
  $value=$null;$kind=$null
  if ($exists) {$value=$key.GetValue($name,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames);$kind=$key.GetValueKind($name)}
  $changes.Add([pscustomobject]@{Path=$path;Name=$name;KeyExisted=$keyExisted;Exists=$exists;Value=$value;Kind=$kind})
  $key.Close()
}
function Restore-Registry {
  foreach($change in $changes) {
    if (!$change.KeyExisted) { [Microsoft.Win32.Registry]::CurrentUser.DeleteSubKeyTree($change.Path,$false);continue }
    $key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($change.Path)
    if ($change.Exists) {$key.SetValue($change.Name,$change.Value,$change.Kind)} else {$key.DeleteValue($change.Name,$false)}
    $key.Close()
  }
  $changes.Clear()
}
function Invoke-Probe([string]$exe,[string]$mode,[string]$folder) {
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=$exe; $info.UseShellExecute=$false
  $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
  if ($mode -eq 'control') {$info.Arguments='--control'}
  $proc=[Diagnostics.Process]::new();$proc.StartInfo=$info
  $start=[DateTime]::UtcNow
  if (!$proc.Start()) {throw 'Process launch failed'}
  $probePid=$proc.Id
  $stdoutTask=$proc.StandardOutput.ReadToEndAsync();$stderrTask=$proc.StandardError.ReadToEndAsync()
  $finished=$proc.WaitForExit(15000)
  if (!$finished) {$proc.Kill();$proc.WaitForExit()}
  $end=[DateTime]::UtcNow
  $stdout=$stdoutTask.Result;$stderr=$stderrTask.Result
  [IO.File]::WriteAllText("$folder\stdout.txt",$stdout)
  [IO.File]::WriteAllText("$folder\stderr.txt",$stderr)
  $result=[pscustomobject]@{pid=$probePid;start_utc=$start.ToString('o');end_utc=$end.ToString('o');exit_code=$proc.ExitCode;timed_out=(!$finished);stdout=$stdout;stderr=$stderr}
  $proc.Dispose(); return $result
}
function Event-Object($event) {
  $xml=[xml]$event.ToXml();$fields=@{}
  foreach($field in $xml.Event.EventData.Data) {$fields[[string]$field.Name]=[string]$field.'#text'}
  return [pscustomobject]@{record_id=$event.RecordId;event_id=$event.Id;time_utc=$event.TimeCreated.ToUniversalTime().ToString('o');fields=$fields}
}
$files=@{
 startup_file = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\telemetry-lab-fixture.txt"
 powershell_profile = "$env:APPDATA\Microsoft\Windows\PowerShell\Microsoft.PowerShell_profile.ps1"
 public_binary = 'C:\Users\Public\telemetry-lab\fixture.exe'
 double_extension_file = "$root\work\report.pdf.exe"
 double_extension_lnk = "$root\work\report.pdf.lnk"
 office_startup_file = "$env:APPDATA\Microsoft\Word\STARTUP\telemetry-lab-fixture.rtf"
 suspicious_executable_file = "$root\work\lab.sys.exe"
 ads_provenance_contents = "$root\work\provenance.exe:Zone.Identifier"
 ads_executable = "$root\work\carrier.txt:fixture.exe"
 creation_time_change = "$root\work\timestamp.txt"
 double_extension_execute = "$root\work\report.pdf.exe"
}
$registry=@{
 registry_run_key=@('Software\Microsoft\Windows\CurrentVersion\Run','TelemetryLabCoverage')
 registry_app_paths=@('Software\Microsoft\Windows\CurrentVersion\App Paths\telemetry-lab-fixture.exe','')
 registry_active_setup=@('Software\Microsoft\Active Setup\Installed Components\{9B9C8026-806D-41E2-992A-909553D7A52A}','StubPath')
 registry_screensaver=@('Control Panel\Desktop','SCRNSAVE.EXE')
}
foreach($candidate in $selection.candidates) {
  if(!$candidate.expansion){continue}
  $e=$candidate.expansion
  if($e.kind -in @('file','delete')) {$files[$candidate.case_id]=[Environment]::ExpandEnvironmentVariables($e.filename)}
  if($e.kind -eq 'registry') {$registry[$candidate.case_id]=@($e.key,$e.value)}
}
$runmru='Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU'
$latest=$null;$startRecord=0
if (!$BehaviorOnly) {
  if ((Get-Service Sysmon64 -ErrorAction Stop).Status -ne 'Running') {throw 'Sysmon64 not running'}
  $latest=Get-WinEvent -LogName $channel -MaxEvents 1; $startRecord=$latest.RecordId
  # Verify the exact executable and complete inventory, not just selected rules.
  if ((Get-FileHash $Hayabusa).Hash.ToLower() -ne $selection.provenance.executable_sha256) {throw 'Hayabusa artifact differs from selection'}
  $rules=Join-Path (Split-Path $Hayabusa) 'rules'
  foreach($property in $selection.provenance.config_sha256.PSObject.Properties) {
    if((Get-FileHash (Join-Path "$rules\config" $property.Name)).Hash.ToLower() -ne $property.Value){throw "Rule filter configuration differs: $($property.Name)"}
  }
  foreach($entry in (Import-Csv "$PSScriptRoot\rule-inventory.csv")) {
    $path=Join-Path $rules $entry.path
    if ((Get-FileHash $path).Hash.ToLower() -ne $entry.sha256) {throw "Rule hash differs: $($entry.path)"}
  }
}
$runPlan=@{cases=@($allCases.case_id);runtime=$build.runtime;modes=$Modes;seed=$Seed;expected_attempts=$nativePlan.Count-$skipAttempts.Count;slots=@($nativePlan | ForEach-Object {@{case_id=$_.case_id;mode=$_.mode}})}
if($SkipAttemptsFrom){$runPlan.prior_attempts_sha256=$priorAttemptsHash}
$runPlan | ConvertTo-Json -Depth 8 | Set-Content "$Output\run-plan.json" -Encoding UTF8
$executionError=$null
$ownedRawDisk=$null
. "$PSScriptRoot\raw-disk-fixture.ps1"
try {
  if('raw_owned_volume_read' -in $allCases.case_id){$ownedRawDisk=New-OwnedRawDisk $Output}
  if('signed_system_library_load' -in $allCases.case_id) {
    $library='C:\Windows\System32\RstrtMgr.dll'
    $signature=Get-AuthenticodeSignature $library
    if($signature.Status -ne 'Valid'){throw 'System library signature is not valid'}
    @{path=$library;sha256=(Get-FileHash $library).Hash;signature_status=[string]$signature.Status;signer=$signature.SignerCertificate.Subject} | ConvertTo-Json | Set-Content "$Output\system-library.json"
  }
  foreach($dir in @($root,"$root\run","$root\work","$root\fixtures",'C:\Users\Public\telemetry-lab')) {Ensure-Directory $dir}
  # The DLLs are part of the measured runtime configuration. Stage exactly the
  # verified bundle beside neutral/public probe paths; never rely on host PATH.
  foreach($dll in @($build.dependent_dlls)) {
    if(!$dll){continue}
    if([IO.Path]::GetFileName($dll.name) -ne $dll.name -or $dll.name -notmatch '\.dll$'){throw 'Invalid DLL manifest path'}
    $source=Join-Path $Programs $dll.name
    if((Get-FileHash $source).Hash.ToLower() -ne $dll.sha256){throw "DLL hash mismatch: $($dll.name)"}
    foreach($directory in @("$root\run",'C:\Users\Public\telemetry-lab')) {
      $dest=Join-Path $directory $dll.name
      if(Test-Path $dest){throw "Unexpected staged runtime DLL: $dest"}
      Copy-Item $source $dest;$stagedDlls.Add($dest)
    }
  }
  # Fixtures come from one fixed reference build for all configurations. Caller stages them.
  foreach($file in @('helper.exe','fixture.node')) {if (!(Test-Path "$root\fixtures\$file")) {throw "Missing fixed helper $file"}}
  [IO.File]::WriteAllText("$root\fixtures\text.txt","telemetry-lab`n")
  [IO.File]::WriteAllText("$root\fixtures\profile.ps1","# telemetry-lab inert profile fixture`n")
  [IO.File]::WriteAllText("$root\fixtures\document.rtf",'{\rtf1\ansi telemetry-lab}')
  $shell=New-Object -ComObject WScript.Shell
  $shortcut=$shell.CreateShortcut("$root\fixtures\fixture.lnk");$shortcut.TargetPath="$root\fixtures\helper.exe";$shortcut.Save()
  foreach($slot in $nativePlan) {
    $case=@($allCases | Where-Object case_id -eq $slot.case_id)[0]
    $id=$case.case_id
    $source=Join-Path $Programs "$id.exe"
    $manifest=@($build.programs | Where-Object {$_.case_id -eq $id})
    if ($manifest.Count -ne 1 -or (Get-FileHash $source).Hash.ToLower() -ne $manifest[0].sha256) {throw "Artifact mismatch $id"}
    foreach($mode in @($slot.mode)) {
      if($skipAttempts.ContainsKey("${id}|${mode}")){continue}
      $folder=Join-Path $Output "$id-$mode"; New-Item -ItemType Directory $folder | Out-Null
      $targetOwned=$false;$runmruOwned=$false;$zoneCarrierOwned=$false
      $target=$files[$id];$exe="$root\run\probe.exe"
      if ($id -eq 'tcp_connect_public_path') {$exe='C:\Users\Public\telemetry-lab\probe.exe'}
      if (Test-Path $exe) {throw "Unexpected staged executable: $exe"}
      try {
        if($id -in @('delete_zone_identifier','ads_provenance_contents')) {
          $carrier=$target.Split(':',3)[0]+':'+$target.Split(':',3)[1]
          if(Test-Path -LiteralPath $carrier){throw "Unowned ADS carrier already exists: $carrier"}
          [IO.File]::WriteAllText($carrier,'telemetry-lab');$zoneCarrierOwned=$true
        }
        if ($target) {
          if ($id -ne 'ads_executable' -and (Test-Path -LiteralPath $target)) {throw "Fixture already exists: $target"}
          if ($id -eq 'ads_executable' -and (Test-Path "$root\work\carrier.txt")) {throw 'Carrier file already exists'}
          Ensure-Directory (Split-Path $target)
          $targetOwned=$true
        }
        if ($registry.ContainsKey($id)) {Save-RegistryValue $registry[$id][0] $registry[$id][1]}
        if ($id -eq 'registry_runmru_delete') {
          $key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($runmru)
          if ($key) {$key.Close();throw 'RunMRU already exists; do not delete existing history'}
          $runmruOwned=$true
          $key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($runmru);$key.SetValue('a','telemetry-lab');$key.Close()
        }
        if ($id -eq 'creation_time_change') {[IO.File]::WriteAllText($target,'fixture');[IO.File]::SetCreationTimeUtc($target,[DateTime]'2026-01-01T00:00:00Z')}
        if ($id -eq 'double_extension_execute') {Copy-Item "$root\fixtures\helper.exe" $target}
        if ($id -eq 'ads_executable') {[IO.File]::WriteAllText("$root\work\carrier.txt",'fixture')}
        if($case.expansion.kind -eq 'delete') {
          # Only the just-reserved fixture is created/deleted, never real history or logs.
          if($id -eq 'delete_zone_identifier') {
            # Windows PowerShell 5.1/.NET Framework rejects colon stream paths.
            Set-Content -LiteralPath $carrier -Stream Zone.Identifier -Value "[ZoneTransfer]`r`nZoneId=3" -Encoding ASCII
          } else {
            [IO.File]::WriteAllText($target,"telemetry-lab inert deletion fixture`n")
          }
        }
        Copy-Item $source $exe
        # Sysmon may retain an older hash for a reused image path. Independently
        # verify the actual staged file before launch; preserve sensor metadata.
        $stagedHash=(Get-FileHash $exe -Algorithm SHA256).Hash.ToLower()
        if($stagedHash -ne $manifest[0].sha256){throw "Staged artifact mismatch $id"}
        if ($case.family -eq 'DNS') {Clear-DnsClientCache}
        $run=Invoke-Probe $exe $mode $folder
        $prefix=if($mode -eq 'control'){'CONTROL_OK'}else{'BEHAVIOR_OK'}
        $ok=(!$run.timed_out -and $run.exit_code -eq 0 -and $run.stdout.Contains("$prefix $id"))
        if($ok -and $mode -eq 'active' -and $case.expansion.kind -eq 'file' -and !(Test-Path -LiteralPath $target)) {
          throw "Native fixture path differs from manifest: $id"
        }
        $attempt=[ordered]@{case_id=$id;mode=$mode;rule_id=$case.rule_id;runtime=$build.runtime;executable=$exe;sha256=$manifest[0].sha256;staged_sha256=$stagedHash;behavior_ok=$ok;process=$run}
        $attempts.Add([pscustomobject]$attempt)
        $attempt | ConvertTo-Json -Depth 8 | Set-Content "$folder\attempt.json" -Encoding UTF8
        Write-Host "$($build.runtime) $id $mode behavior=$ok"
      } finally {
        # All cleanup is performed by the harness, after the measured process exits.
        if (Test-Path $exe) {Remove-OwnedFile $exe}
        if ($id -notin @('ads_executable','delete_zone_identifier','ads_provenance_contents') -and $targetOwned -and $target -and (Test-Path -LiteralPath $target)) {Remove-OwnedFile $target}
        if ($targetOwned -and $id -eq 'ads_executable') {Remove-Item "$root\work\carrier.txt" -Force -ErrorAction SilentlyContinue}
        if($zoneCarrierOwned){Remove-OwnedFile $carrier}
        if ($runmruOwned) {[Microsoft.Win32.Registry]::CurrentUser.DeleteSubKeyTree($runmru,$false)}
        Restore-Registry
      }
    }
  }
} catch {
  $executionError=$_
  $_ | Out-String | Set-Content "$Output\execution-error.txt"
} finally {
  # Always persist attempts, even if fixture/runtime cleanup fails.
  try {
    if($ownedRawDisk){Remove-OwnedRawDisk $ownedRawDisk}
    foreach($dll in $stagedDlls){Remove-OwnedFile $dll}
    Restore-Registry
  } catch {
    $_ | Out-String | Set-Content "$Output\cleanup-error.txt"
    if(!$executionError){$executionError=$_}
  } finally {
    ConvertTo-Json -InputObject @($attempts.ToArray()) -Depth 10 | Set-Content "$Output\attempts.json" -Encoding UTF8
  }
}
if ($BehaviorOnly) {
  if ($executionError) {throw $executionError}
  if (@($attempts | Where-Object {!$_.behavior_ok}).Count) {throw 'Behavior validation failed'}
  exit 0
}
# Allow asynchronous Sysmon delivery; do not assign events to attempts by arrival order.
Start-Sleep -Seconds 30
$endRecord=(Get-WinEvent -LogName $channel -MaxEvents 1).RecordId
$query="*[System[EventRecordID > $startRecord and EventRecordID <= $endRecord]]"
& wevtutil epl $channel "$Output\events.evtx" "/q:$query" /ow:true
if ($LASTEXITCODE -ne 0) {throw 'EVTX export failed'}
$events=@(Get-WinEvent -Path "$Output\events.evtx" -Oldest | ForEach-Object {Event-Object $_})
$events | ConvertTo-Json -Depth 8 -Compress | Set-Content "$Output\events.json" -Encoding UTF8
$first=(Get-WinEvent -LogName $channel -Oldest -MaxEvents 1).RecordId
$health=[ordered]@{start_record=$startRecord;end_record=$endRecord;oldest_remaining_record=$first;log_overwritten=($first -gt ($startRecord+1));sysmon_service=(Get-Service Sysmon64).Status.ToString();error_events=@($events | Where-Object {$_.event_id -in @(4,16,255)})}
$health | ConvertTo-Json -Depth 8 | Set-Content "$Output\health.json" -Encoding UTF8
Copy-Item "$PSScriptRoot\selection.json" "$Output\selection.json"
Copy-Item "$PSScriptRoot\rule-inventory.csv" "$Output\rule-inventory.csv"
$build | ConvertTo-Json -Depth 8 | Set-Content "$Output\build-manifest.json" -Encoding UTF8
$inventory=[ordered]@{os=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber);sysmon=(Get-Item C:\lab\sysmon\Sysmon64.exe).VersionInfo.FileVersion;sysmon_sha256=(Get-FileHash C:\lab\sysmon\Sysmon64.exe).Hash;sysmon_config_sha256=(Get-FileHash C:\lab\sysmon\config.xml).Hash;hayabusa_sha256=(Get-FileHash $Hayabusa).Hash;fixture_helper_sha256=(Get-FileHash "$root\fixtures\helper.exe").Hash;fixture_module_sha256=(Get-FileHash "$root\fixtures\fixture.node").Hash;identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name;selection_sha256=(Get-FileHash "$PSScriptRoot\selection.json").Hash}
$inventory | ConvertTo-Json -Depth 6 | Set-Content "$Output\inventory.json" -Encoding UTF8
$detector=[Diagnostics.Process]::new()
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName=$Hayabusa; $info.WorkingDirectory=Split-Path $Hayabusa; $info.UseShellExecute=$false
$info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
$info.Arguments="dfir-timeline -f `"$Output\events.evtx`" -o `"$Output\alerts.csv`" -r `"$rules`" -m low --no-wizard -p all-field-info -C"
$detector.StartInfo=$info
if (!$detector.Start()) {throw 'Cannot start Hayabusa'}
$detectorOut=$detector.StandardOutput.ReadToEndAsync();$detectorErr=$detector.StandardError.ReadToEndAsync()
if (!$detector.WaitForExit(180000)) {$detector.Kill();$detector.WaitForExit()}
[IO.File]::WriteAllText("$Output\hayabusa.log",$detectorOut.Result)
[IO.File]::WriteAllText("$Output\hayabusa.stderr",$detectorErr.Result)
$detectorExit=$detector.ExitCode;$detector.Dispose()
[IO.File]::WriteAllText("$Output\detector-exit.txt",[string]$detectorExit)
if ($detectorExit -ne 0) {throw 'Hayabusa evaluation failed; preserve evidence'}
if ($executionError) {throw $executionError}
if (!$ReturnBehaviorFailures -and @($attempts | Where-Object {!$_.behavior_ok}).Count) {throw 'One or more behavior checks failed; preserve evidence'}

} finally { $lock.ReleaseMutex(); $lock.Dispose() }
