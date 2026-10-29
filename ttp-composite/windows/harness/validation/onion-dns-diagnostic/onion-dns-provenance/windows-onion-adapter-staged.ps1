# Fallback diagnostic only: use the local DNS server as the adapter resolver,
# restoring the original DHCP/static mode and addresses even on failure.
$ErrorActionPreference='Stop'
$out='C:\lab\qualification\onion-adapter-diagnostic-01'
if(Test-Path $out){throw 'Evidence exists'}
New-Item -ItemType Directory $out -Force | Out-Null
$server='C:\lab\followup-ucrt\coverage\fixtures\windows_dns_server.exe'
$route=Get-NetRoute -AddressFamily IPv4 -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1
$adapter=Get-NetAdapter -InterfaceIndex $route.InterfaceIndex
$dns=Get-DnsClientServerAddress -InterfaceIndex $route.InterfaceIndex -AddressFamily IPv4
$reg="HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\$($adapter.InterfaceGuid)"
$static=(Get-ItemProperty $reg -Name NameServer -ErrorAction SilentlyContinue).NameServer
$savedAddresses=@($dns.ServerAddresses)
$dns | Export-Clixml "$out\dns-before.xml"
@{interface_index=$route.InterfaceIndex;interface_guid=$adapter.InterfaceGuid;static_nameserver=$static} | ConvertTo-Json | Set-Content "$out\mode-before.json"
$env:TELEMETRY_LAB_FIXTURE='1';$p=$null;$changed=$false;$results=@()
try {
 if(Get-NetUDPEndpoint -LocalPort 53 -ErrorAction SilentlyContinue){throw 'UDP 53 occupied'}
 $p=Start-Process $server -PassThru -RedirectStandardOutput "$out\dns.log" -RedirectStandardError "$out\dns.stderr"
 Start-Sleep -Seconds 1
 if($p.HasExited){throw 'DNS fixture failed'}
 $changed=$true
 Set-DnsClientServerAddress -InputObject $dns -ServerAddresses '127.0.0.1'
 Clear-DnsClientCache
 foreach($crt in @('ucrt','msvcrt')) {
  foreach($name in @('dns_onion','dns_ip_lookup')) {
   Clear-DnsClientCache
   $i=[Diagnostics.ProcessStartInfo]::new();$i.FileName="C:\lab\followup-$crt\coverage\$name.exe";$i.UseShellExecute=$false;$i.RedirectStandardOutput=$true;$i.RedirectStandardError=$true
   $r=[Diagnostics.Process]::new();$r.StartInfo=$i
   if(!$r.Start()){throw 'Probe failed to start'}
   $ot=$r.StandardOutput.ReadToEndAsync();$et=$r.StandardError.ReadToEndAsync()
   if(!$r.WaitForExit(15000)){$r.Kill();$r.WaitForExit()}
   $item=@{crt=$crt;case=$name;exit_code=$r.ExitCode;stdout=$ot.Result;stderr=$et.Result};$results+=$item;$item | ConvertTo-Json -Compress | Write-Host;$r.Dispose()
  }
 }
} finally {
 if($changed){
  if([string]::IsNullOrWhiteSpace($static)){Set-DnsClientServerAddress -InputObject $dns -ResetServerAddresses}
  else{Set-DnsClientServerAddress -InputObject $dns -ServerAddresses $savedAddresses}
 }
 Clear-DnsClientCache
 if($p){if(!$p.HasExited){Stop-Process -Id $p.Id -Force};$p.Dispose()}
 Get-DnsClientServerAddress -InterfaceIndex $route.InterfaceIndex -AddressFamily IPv4 | Export-Clixml "$out\dns-after.xml"
 $results | ConvertTo-Json -Depth 5 | Set-Content "$out\results.json" -Encoding UTF8
}

& 'C:\Program Files\Amazon\AWSCLIV2\aws.exe' s3 sync C:\lab\qualification s3://windowscvalidation-labdata46f5603f-ygr1wqpnawd0/evidence --only-show-errors
if($LASTEXITCODE){throw 'Evidence upload failed'}
