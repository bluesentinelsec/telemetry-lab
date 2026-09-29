$ErrorActionPreference='Stop'
$aws='C:\Program Files\Amazon\AWSCLIV2\aws.exe'
if((Get-WindowsFeature Windows-Defender).Installed -or (Get-Process MsMpEng -ErrorAction SilentlyContinue)){throw 'CDK bootstrap/Defender removal has not finished'}
if(!(Test-Path C:\lab\inventory.json)){throw 'Boot inventory absent'}
$base='C:\lab\coverage-expansion'
New-Item -ItemType Directory "$base\evidence" -Force | Out-Null
& $aws s3 cp s3://@BUCKET@/@PREFIX@/payload.tgz "$base\payload.tgz" --only-show-errors
if($LASTEXITCODE){throw 'Download failed'}
if((Get-FileHash "$base\payload.tgz").Hash.ToLower() -ne '@PAYLOAD_SHA@'){throw 'Payload differs'}
foreach($owned in @('bundle','scripts')){if(Test-Path "$base\$owned"){Remove-Item "$base\$owned" -Recurse -Force}}
& tar.exe -xzf "$base\payload.tgz" -C $base
if($LASTEXITCODE){throw 'Extraction failed'}
$bundle="$base\bundle"
$expected=Get-Content "$bundle\files.sha256.json" -Raw | ConvertFrom-Json
foreach($p in $expected.PSObject.Properties){if((Get-FileHash (Join-Path $bundle $p.Name)).Hash.ToLower() -ne $p.Value){throw "Bundle mismatch $($p.Name)"}}
$selection=Get-Content "$bundle\ttp-composite\coverage\selection.json" -Raw | ConvertFrom-Json
if(!(Test-Path C:\lab\hayabusa\hayabusa.exe) -or (Get-FileHash C:\lab\hayabusa\hayabusa.exe).Hash.ToLower() -ne $selection.provenance.executable_sha256) {
 Invoke-WebRequest $selection.provenance.asset_url -OutFile "$base\hayabusa-pinned.zip" -UseBasicParsing
 if((Get-FileHash "$base\hayabusa-pinned.zip").Hash.ToLower() -ne $selection.provenance.asset_sha256){throw 'Pinned Hayabusa archive mismatch'}
 if(Test-Path C:\lab\hayabusa){Remove-Item C:\lab\hayabusa -Recurse -Force}
 Expand-Archive "$base\hayabusa-pinned.zip" C:\lab\hayabusa
 Move-Item "C:\lab\hayabusa\hayabusa-$($selection.provenance.hayabusa_version)-win-x64.exe" C:\lab\hayabusa\hayabusa.exe
}
$fixture="$bundle\ttp-composite\windows-c-ucrt\coverage\fixtures"
New-Item -ItemType Directory C:\lab\windows-coverage\fixtures -Force | Out-Null
Copy-Item "$fixture\windows_fixture_helper.exe" C:\lab\windows-coverage\fixtures\helper.exe
Copy-Item "$fixture\fixture.node" C:\lab\windows-coverage\fixtures\fixture.node
wevtutil sl Microsoft-Windows-Sysmon/Operational /ms:1073741824
Copy-Item C:\lab\inventory.json "$base\evidence\boot-inventory.json"
# The runner verifies the pinned engine and all 4,987 rule hashes before scoring.
if(!(Test-Path C:\lab\python\python.exe)) {
 Invoke-WebRequest https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip -OutFile C:\lab\python.zip -UseBasicParsing
 Expand-Archive C:\lab\python.zip C:\lab\python -Force
}
$pth='C:\lab\python\python312._pth'
if(!(Get-Content $pth | Where-Object {$_ -eq "$base\scripts\experiment"})){Add-Content $pth "$base\scripts\experiment"}
& $aws s3 sync "$base\evidence" s3://@BUCKET@/results/windows/ --only-show-errors
Get-Service Sysmon64
