# validate-windows.ps1 — post-deploy validation for the Windows Server 2025 host.
#
# Two jobs, matching the study's rigor model (consume latest, record exactly what
# ran):
#   1. Provenance: capture the installed Sysmon + Hayabusa versions, their SHA-256s,
#      the Sysmon config hash and bundled-ruleset fingerprint, into a JSON manifest
#      (printed, saved, and uploaded to S3).
#   2. Fire test: generate benign ATT&CK-flavoured activity, let Sysmon log it,
#      export the Sysmon EVTX, run Hayabusa's Sigma ruleset over it, and require at
#      least one detection — proving the Sysmon -> EVTX -> Hayabusa/Sigma pipeline.
#
# Usage:  powershell -ExecutionPolicy Bypass -File validate-windows.ps1 [-Bucket <name>]
# Exits 0 only if Hayabusa produced >= 1 detection.
param([string]$Bucket = "")

$ErrorActionPreference = "Continue"
$lab = "C:\lab"
$manifest = "$lab\provision-windows.json"
function Section($t) { Write-Host "`n=== $t ===" }

# ---------------------------------------------------------------- provenance ---
Section "PROVENANCE"
$sysmonExe = "$lab\sysmon\Sysmon64.exe"
$sysmonCfg = "$lab\sysmon\config.xml"
$hbExe     = "$lab\hayabusa\hayabusa.exe"

$sysmonVer = (Get-Item $sysmonExe -EA SilentlyContinue).VersionInfo.FileVersion
$sysmonSha = (Get-FileHash $sysmonExe -Algorithm SHA256 -EA SilentlyContinue).Hash
$cfgSha    = (Get-FileHash $sysmonCfg -Algorithm SHA256 -EA SilentlyContinue).Hash
$hbSha     = (Get-FileHash $hbExe -Algorithm SHA256 -EA SilentlyContinue).Hash
$hbVer     = (& $hbExe help 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+' | Select-Object -First 1).Matches.Value
$sysmonSvc = (Get-Service -Name Sysmon64 -EA SilentlyContinue).Status
$osBuild   = (Get-CimInstance Win32_OperatingSystem).Caption + " " + [System.Environment]::OSVersion.Version

# Bundled Sigma ruleset fingerprint: count + a stable hash over sorted rule hashes.
$rulesDir = Get-ChildItem "$lab\hayabusa" -Recurse -Directory -Filter "rules" -EA SilentlyContinue | Select-Object -First 1
$ruleCount = 0; $rulesFp = ""
if ($rulesDir) {
  $rf = Get-ChildItem $rulesDir.FullName -Recurse -Include *.yml,*.yaml -EA SilentlyContinue
  $ruleCount = ($rf | Measure-Object).Count
  $acc = ($rf | Sort-Object FullName | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash }) -join ""
  if ($acc) {
    $sha = [Security.Cryptography.SHA256]::Create()
    $rulesFp = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::ASCII.GetBytes($acc))) -replace '-','')
  }
}

Write-Host "sysmon:   $sysmonVer  sha=$sysmonSha  svc=$sysmonSvc"
Write-Host "config:   sha=$cfgSha"
Write-Host "hayabusa: $hbVer  sha=$hbSha"
Write-Host "rules:    count=$ruleCount fp=$rulesFp"
Write-Host "os:       $osBuild"

# ------------------------------------------------------------------ firetest ---
Section "FIRE TEST"
# Benign but detection-flagged activity: recon + a Run-key persistence write.
cmd.exe /c "whoami" | Out-Null
cmd.exe /c "net user" | Out-Null
cmd.exe /c "systeminfo" | Out-Null
reg.exe add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v LabFiretest /t REG_SZ /d "calc.exe" /f | Out-Null
Start-Sleep -Seconds 6   # let Sysmon flush events to its channel

$evtx = "$lab\sysmon-firetest.evtx"
Remove-Item $evtx -EA SilentlyContinue
wevtutil epl "Microsoft-Windows-Sysmon/Operational" $evtx 2>$null

$csv = "$lab\hayabusa-firetest.csv"
Remove-Item $csv -EA SilentlyContinue
$rulesArg = @(); if ($rulesDir) { $rulesArg = @("-r", $rulesDir.FullName) }
# csv-timeline over the single EVTX; -m low = include low+ severity; --no-wizard
# scans all rules non-interactively (-w is its alias, so don't pass both); -C
# overwrites the output. Run from the hayabusa dir so relative rules resolve.
Push-Location "$lab\hayabusa"
& $hbExe csv-timeline -f $evtx -o $csv @rulesArg -m low --no-wizard -C 2>&1 | Tee-Object -Variable hbOut | Out-Null
Pop-Location
Write-Host ($hbOut | Select-Object -Last 25 | Out-String)

$detections = 0
if (Test-Path $csv) { $detections = (@(Import-Csv $csv -EA SilentlyContinue)).Count }
# Fallback: parse the "Total detections" summary line if the CSV was empty.
if ($detections -eq 0 -and $hbOut) {
  $m = ($hbOut | Select-String -Pattern "Total detections:\s*([\d,]+)" | Select-Object -First 1)
  if ($m) { $detections = [int](($m.Matches[0].Groups[1].Value) -replace ',','') }
}
Write-Host "hayabusa_detections=$detections"

reg.exe delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v LabFiretest /f 2>$null | Out-Null

$result = if ($detections -ge 1 -and $sysmonSvc -eq "Running") { "pass" } else { "fail" }

# ------------------------------------------------------------------ manifest ---
$obj = [ordered]@{
  host                 = "windows"
  sysmon_version       = $sysmonVer
  sysmon_sha256        = $sysmonSha
  sysmon_config_sha256 = $cfgSha
  sysmon_service       = "$sysmonSvc"
  hayabusa_version     = $hbVer
  hayabusa_sha256      = $hbSha
  sigma_rule_count     = $ruleCount
  sigma_rules_fp       = $rulesFp
  os                   = "$osBuild"
  firetest_detections  = $detections
  result               = $result
}
$json = $obj | ConvertTo-Json -Depth 4
$json | Set-Content -Path $manifest -Encoding ascii
Write-Host $json

if ($Bucket -ne "") {
  & aws s3 cp $manifest "s3://$Bucket/provenance/windows-provision.json" --only-show-errors
  Write-Host "uploaded to s3://$Bucket/provenance/windows-provision.json"
}

Section "RESULT: $result"
if ($result -ne "pass") { exit 1 }
