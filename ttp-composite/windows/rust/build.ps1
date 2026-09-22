param([Parameter(Mandatory=$true)][string]$Output, [Parameter(Mandatory=$true)][ValidateSet('dynamic','static')][string]$Crt)
$ErrorActionPreference='Stop'
$target='x86_64-pc-windows-msvc'
$flag=if($Crt -eq 'static'){'+'}else{'-'}
$env:RUSTFLAGS="-C target-feature=${flag}crt-static"
$env:CARGO_TARGET_DIR=Join-Path $PSScriptRoot "target-$Crt"
New-Item -ItemType Directory -Force $Output | Out-Null
$Output=(Resolve-Path $Output).Path
$coverage=Join-Path $Output 'coverage'
if(Test-Path $coverage){Remove-Item $coverage -Recurse -Force}
New-Item -ItemType Directory -Force "$coverage/fixtures" | Out-Null
Push-Location $PSScriptRoot
try {
 & cargo build --locked --release --target $target --bins
 if($LASTEXITCODE){throw 'Rust build failed'}
 $cfg=& rustc --print cfg --target $target -C "target-feature=${flag}crt-static"
 if($LASTEXITCODE){throw 'Rust cfg query failed'}
 $actualStatic=@($cfg) -contains 'target_feature="crt-static"'
 if($actualStatic -ne ($Crt -eq 'static')){throw 'Rust CRT cfg mismatch'}
 foreach($program in Get-ChildItem src/bin/*.rs){Copy-Item "$env:CARGO_TARGET_DIR/$target/release/$($program.BaseName).exe" $coverage}
 $rustc=(& rustc -vV) -join "`n"
 $linker=(& link.exe /? 2>&1 | Select-Object -First 1) -join "`n"
 @{target=$target;crt=$Crt;rustflags=$env:RUSTFLAGS;cfg=@($cfg);rustc_verbose=$rustc;linker_identity=$linker;vc_tools_version=$env:VCToolsVersion;windows_sdk_version=$env:WindowsSDKVersion} | ConvertTo-Json -Depth 5 | Set-Content "$coverage/rust-build.json" -Encoding utf8
 # CI-only fixture builds. Live qualification reuses the exact archived C fixtures.
 Push-Location "$coverage/fixtures"
 try {
  & cl.exe /nologo /MT /O2 "$PSScriptRoot/../c/coverage/helper.c" /Fewindows_fixture_helper.exe
  if($LASTEXITCODE){throw 'Helper build failed'}
  & cl.exe /nologo /MT /O2 /LD "$PSScriptRoot/../c/coverage/module.c" /link /OUT:fixture.node
  if($LASTEXITCODE){throw 'Module build failed'}
  foreach($server in @('echo','dns')) {
   & cl.exe /nologo /MT /O2 "$PSScriptRoot/../c/coverage/${server}_server.c" "/Fewindows_${server}_server.exe" /link ws2_32.lib
   if($LASTEXITCODE){throw 'Server build failed'}
  }
  Remove-Item *.obj,*.lib,*.exp -ErrorAction SilentlyContinue
 } finally {Pop-Location}
 $redist=Get-ChildItem (Join-Path $env:VCToolsRedistDir 'x64') -Directory | Where-Object {$_.Name -like 'Microsoft.VC*.CRT'} | Select-Object -First 1
 if(!$redist){throw 'MSVC runtime redistribution directory missing'}
 & python ../coverage/bundle_runtime.py $Output --runtime-bin $redist.FullName
 if($LASTEXITCODE){throw 'Runtime bundle failed'}
 & python ../coverage/verify_programs.py $coverage "rust-msvc-$Crt"
 if($LASTEXITCODE){throw 'Rust PE verification failed'}
} finally {Pop-Location}
