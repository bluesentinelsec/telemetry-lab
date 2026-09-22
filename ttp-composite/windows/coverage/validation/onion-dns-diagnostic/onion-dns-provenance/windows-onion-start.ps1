$aws='C:\Program Files\Amazon\AWSCLIV2\aws.exe'
foreach($name in @('support','ucrt','msvcrt')) {
 & $aws s3 cp "s3://windowscvalidation-labdata46f5603f-ygr1wqpnawd0/stage/$name.zip" "C:\lab\followup-$name.zip" --only-show-errors
 if($LASTEXITCODE){throw 'Artifact download failed'}
 Expand-Archive "C:\lab\followup-$name.zip" "C:\lab\followup-$name" -Force
}
New-Item -ItemType Directory C:\lab\windows-coverage\fixtures -Force | Out-Null
Copy-Item C:\lab\followup-ucrt\coverage\fixtures\windows_fixture_helper.exe C:\lab\windows-coverage\fixtures\helper.exe -Force
Copy-Item C:\lab\followup-ucrt\coverage\fixtures\fixture.node C:\lab\windows-coverage\fixtures\fixture.node -Force
wevtutil sl Microsoft-Windows-Sysmon/Operational /ms:1073741824
Get-Service Sysmon64
Get-NetTCPConnection -State Listen -LocalPort 3389
Get-FileHash C:\lab\hayabusa\hayabusa.exe

$ErrorActionPreference='Stop'
$out='C:\lab\qualification\onion-diagnostic-01'
if(Test-Path $out){throw 'Evidence exists'}
New-Item -ItemType Directory $out -Force | Out-Null
$startRecord=(Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 1).RecordId
$server='C:\lab\followup-ucrt\coverage\fixtures\windows_dns_server.exe'
if(Get-NetUDPEndpoint -LocalPort 53 -ErrorAction SilentlyContinue){throw 'UDP 53 occupied'}
$env:TELEMETRY_LAB_FIXTURE='1'
$results=[Collections.Generic.List[object]]::new()
$policy=$null;$p=$null
function Probe([string]$phase,[string]$crt,[string]$name) {
 Clear-DnsClientCache
 $i=[Diagnostics.ProcessStartInfo]::new();$i.FileName="C:\lab\followup-$crt\coverage\$name.exe";$i.UseShellExecute=$false;$i.RedirectStandardOutput=$true;$i.RedirectStandardError=$true
 $r=[Diagnostics.Process]::new();$r.StartInfo=$i
 $start=[DateTime]::UtcNow
 if(!$r.Start()){throw 'Probe launch failed'}
 $id=$r.Id;$ot=$r.StandardOutput.ReadToEndAsync();$et=$r.StandardError.ReadToEndAsync()
 if(!$r.WaitForExit(15000)){$r.Kill();$r.WaitForExit()}
 $entry=@{phase=$phase;crt=$crt;case=$name;pid=$id;start=$start.ToString('o');end=[DateTime]::UtcNow.ToString('o');exit_code=$r.ExitCode;stdout=$ot.Result;stderr=$et.Result}
 $results.Add($entry);$entry | ConvertTo-Json -Compress | Write-Host;$r.Dispose()
}
try {
 $p=Start-Process $server -PassThru -RedirectStandardOutput "$out\dns.log" -RedirectStandardError "$out\dns.stderr"
 Start-Sleep -Seconds 1
 if($p.HasExited){throw 'DNS fixture failed'}
 # Direct UDP request bypasses client resolution and validates the server's fixed A record.
 foreach($name in @('lab.onion','api.ipify.org')) {
  $q=[Collections.Generic.List[byte]]::new();$q.AddRange([byte[]]@(0x12,0x34,1,0,0,1,0,0,0,0,0,0))
  foreach($label in $name.Split('.')){$q.Add([byte]$label.Length);$q.AddRange([Text.Encoding]::ASCII.GetBytes($label))}
  $q.AddRange([byte[]]@(0,0,1,0,1))
  $udp=[Net.Sockets.UdpClient]::new();$udp.Client.ReceiveTimeout=3000
  try {
   $udp.Connect('127.0.0.1',53);[void]$udp.Send($q.ToArray(),$q.Count)
   $remote=[Net.IPEndPoint]::new([Net.IPAddress]::Any,0);$reply=$udp.Receive([ref]$remote)
   [IO.File]::WriteAllBytes("$out\$name-response.bin",$reply)
   if($reply.Length -lt 16 -or $reply[7] -ne 1 -or (($reply[($reply.Length-4)..($reply.Length-1)] -join '.') -ne '127.0.0.42')){throw 'Incorrect direct DNS response'}
   Write-Host "DIRECT_SERVER_OK $name 127.0.0.42"
  } finally {$udp.Dispose()}
 }
 @(Get-DnsClientNrptRule) | Export-Clixml "$out\nrpt-before.xml"
 $policy=Add-DnsClientNrptRule -Namespace @('lab.onion','api.ipify.org') -NameServers '127.0.0.1' -Comment 'Telemetry lab diagnostic' -PassThru
 foreach($crt in @('ucrt','msvcrt')){foreach($name in @('dns_onion','dns_ip_lookup')){Probe 'immediate' $crt $name}}
 Start-Sleep -Seconds 10
 Get-DnsClientNrptPolicy -Effective | Export-Clixml "$out\nrpt-effective.xml"
 foreach($crt in @('msvcrt','ucrt')){foreach($name in @('dns_onion','dns_ip_lookup')){Probe 'settled' $crt $name}}
 foreach($name in @('lab.onion','api.ipify.org')) {
  try {Resolve-DnsName -Name $name -Type A -Server 127.0.0.1 -DnsOnly -NoHostsFile -ErrorAction Stop | ConvertTo-Json -Depth 5 | Set-Content "$out\$name-explicit-server.json"}
  catch {$_ | Out-String | Set-Content "$out\$name-explicit-server-error.txt"}
 }
} finally {
 if($policy){Remove-DnsClientNrptRule -Name $policy.Name -Force}
 Clear-DnsClientCache
 if($p){if(!$p.HasExited){Stop-Process -Id $p.Id -Force};$p.Dispose()}
 $results.ToArray() | ConvertTo-Json -Depth 6 | Set-Content "$out\results.json" -Encoding UTF8
 @(Get-DnsClientNrptRule) | Export-Clixml "$out\nrpt-after.xml"
 Get-FileHash $server | ConvertTo-Json | Set-Content "$out\server-hash.json"
}

Start-Sleep -Seconds 30
$endRecord=(Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 1).RecordId
$q="*[System[EventRecordID > $startRecord and EventRecordID <= $endRecord]]"
& wevtutil epl Microsoft-Windows-Sysmon/Operational "$out\events.evtx" "/q:$q" /ow:true
if($LASTEXITCODE){throw 'Diagnostic EVTX export failed'}
@{start_record=$startRecord;end_record=$endRecord} | ConvertTo-Json | Set-Content "$out\capture.json"

& 'C:\Program Files\Amazon\AWSCLIV2\aws.exe' s3 sync C:\lab\qualification s3://windowscvalidation-labdata46f5603f-ygr1wqpnawd0/evidence --only-show-errors
if($LASTEXITCODE){throw 'Evidence upload failed'}
