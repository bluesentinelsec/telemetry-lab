[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Bundle,[Parameter(Mandatory=$true)][string]$Output)
$ErrorActionPreference='Stop'
if(Test-Path $Output){throw 'Evidence directory already exists'}
New-Item -ItemType Directory "$Output\raw" -Force | Out-Null
$manifest=Get-Content "$Bundle\manifest.json" -Raw | ConvertFrom-Json
$rows=[Collections.Generic.List[object]]::new()
foreach($config in $manifest.configs) {
 foreach($case in $manifest.primitives) {
  $exe="$Bundle\ttp-primitives\$config\$case.exe"
  $raw="$Output\raw\$config-$case.jsonl"
  $argsList=@('--format','json','-o',$raw,'--meta','os=windows','--meta',"config=$config",'--meta',"primitive=$case",'--meta','iteration=1','--meta',"host=$env:COMPUTERNAME",'--meta',"language=$($config.Split('-')[1])",'--meta',"runtime=$($config.Split('-')[2..($config.Split('-').Length-1)] -join '-')",'--',$exe)
  $process=Start-Process "$Bundle\tmon\tmon.exe" -ArgumentList $argsList -PassThru -NoNewWindow -RedirectStandardOutput "$raw.stdout" -RedirectStandardError "$raw.stderr"
  $finished=$process.WaitForExit(180000)
  if(!$finished){Stop-Process -Id $process.Id -Force}
  $process.WaitForExit()
  $code=$process.ExitCode
  $summaries=@()
  if(Test-Path $raw){$summaries=@(Get-Content $raw | ForEach-Object {ConvertFrom-Json $_} | Where-Object record -eq 'summary')}
  $valid=$finished -and $code -eq 0 -and $summaries.Count -eq 1 -and $summaries[0].target_exit_code -eq 0 -and $summaries[0].lost -eq 0 -and $summaries[0].total_events -gt 0
  $row=[pscustomobject]@{config=$config;case=$case;exit_code=$code;timed_out=(!$finished);valid=$valid;binary_sha256=(Get-FileHash $exe).Hash.ToLower();summary=$summaries}
  $rows.Add($row)
  $rows | ConvertTo-Json -Depth 8 | Set-Content "$Output\results.json" -Encoding UTF8
  $row | ConvertTo-Json -Depth 5 -Compress | Write-Output
  $process.Dispose()
 }
}
& "$Bundle\tap\tap.exe" run "$Output\raw" -o "$Output\tap" *> "$Output\tap.log"
if($LASTEXITCODE -or @($rows | Where-Object {!$_.valid}).Count){throw 'Primitive validation failed; retain all evidence'}
