# Seed only a newly created, detached fixed VHD; mount it read-only.
# Never open a write handle against a physical disk device.
function New-OwnedRawDisk([string]$Evidence) {
 $image=Join-Path $Evidence 'owned-raw-read.vhd'
 if(Test-Path -LiteralPath $image){throw 'Raw-read fixture already exists'}
 $script=Join-Path $Evidence 'create-vhd.txt'
 @("create vdisk file=`"$image`" maximum=16 type=fixed",'exit') | Set-Content $script -Encoding ASCII
 & diskpart.exe /s $script | Out-File (Join-Path $Evidence 'diskpart.log')
 if($LASTEXITCODE -or !(Test-Path -LiteralPath $image)){throw 'VHD creation failed'}
 try {
  $bytes=[byte[]](0..511 | ForEach-Object {$_ % 251})
  $stream=[IO.File]::Open($image,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
  try {$stream.Write($bytes,0,$bytes.Length);$stream.Flush()} finally {$stream.Dispose()}
  $hash=(Get-FileHash -LiteralPath $image).Hash
  $mounted=Mount-DiskImage -ImagePath $image -Access ReadOnly -NoDriveLetter -PassThru
  $disk=$mounted | Get-Disk
  if($disk.IsBoot -or $disk.IsSystem -or !$disk.IsReadOnly){throw 'Unexpected VHD disk properties'}
  $device=(Get-DiskImage -ImagePath $image).DevicePath
  if($device -notmatch '^\\\\\.\\PhysicalDrive[0-9]+$' -or $device -ne "\\.\PhysicalDrive$($disk.Number)"){throw 'Ambiguous owned disk mapping'}
  @{image=$image;device=$device;disk_number=$disk.Number;read_only=$disk.IsReadOnly;sha256=$hash;expected_bytes=512;pattern='byte[i] = i % 251'} | ConvertTo-Json | Set-Content (Join-Path $Evidence 'raw-disk.json')
  $env:TELEMETRY_LAB_RAW_DEVICE=$device
  return $image
 } catch {
  Dismount-DiskImage -ImagePath $image -ErrorAction SilentlyContinue | Out-Null
  throw
 }
}
function Remove-OwnedRawDisk([string]$Image) {
 Remove-Item Env:TELEMETRY_LAB_RAW_DEVICE -ErrorAction SilentlyContinue
 Dismount-DiskImage -ImagePath $Image -ErrorAction Stop | Out-Null
 if((Get-DiskImage -ImagePath $Image).Attached){throw 'Owned VHD still attached'}
 $expected=Get-Content (Join-Path (Split-Path $Image) 'raw-disk.json') -Raw | ConvertFrom-Json
 if((Get-FileHash -LiteralPath $Image).Hash -ne $expected.sha256){throw 'Read-only fixture bytes changed'}
 Remove-Item -LiteralPath $Image -Force
 if(Test-Path -LiteralPath $Image){throw 'Owned VHD cleanup failed'}
 @{detached=$true;removed=$true;sha256_unchanged=$true} | ConvertTo-Json | Set-Content (Join-Path (Split-Path $Image) 'raw-disk-cleanup.json')
}
