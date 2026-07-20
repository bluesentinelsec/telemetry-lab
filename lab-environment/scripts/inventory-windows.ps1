# Runs ON the Windows Server lab host at the end of provisioning (invoked from EC2
# user data, before the Defender-removal reboot). Writes C:\lab\inventory.json --
# version + SHA-256 + path for the detectors (Sysmon, Hayabusa), the telemetry-lab
# release and its binaries, and the OS.
#
# tap discovers this file co-located with telemetry data and stamps analysis output
# with it, so every result traces back to exact versions + hashes.
$ErrorActionPreference = "Continue"
$out = "C:\lab\inventory.json"

function Sha($p) { if (Test-Path $p) { (Get-FileHash $p -Algorithm SHA256).Hash } else { $null } }

# telemetry-lab release: version comes from the extracted dir name.
$base = Get-ChildItem "C:\lab\telemetry-lab" -Directory -Filter 'telemetry-lab-*-windows' -EA SilentlyContinue | Select-Object -First 1
$ver = if ($base) { ($base.Name -replace '^telemetry-lab-','' -replace '-windows$','') } else { "" }

$comps = @()
$sm = "C:\lab\sysmon\Sysmon64.exe"
if (Test-Path $sm) {
  $comps += [ordered]@{ name="sysmon"; type="detector"; version=(Get-Item $sm).VersionInfo.FileVersion; sha256=(Sha $sm); path=$sm }
}
$hb = "C:\lab\hayabusa\hayabusa.exe"
if (Test-Path $hb) {
  $hv = (& $hb help 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+' | Select-Object -First 1).Matches.Value
  $comps += [ordered]@{ name="hayabusa"; type="detector"; version=$hv; sha256=(Sha $hb); path=$hb }
}
$zip = "C:\lab\telemetry-lab.zip"
if ((Test-Path $zip) -and $base) {
  $comps += [ordered]@{ name="telemetry-lab"; type="release"; version=$ver; sha256=(Sha $zip); path=$base.FullName }
}
if ($base) {
  foreach ($c in @(,@("tmon","tmon\tmon.exe")) + @(,@("tap","tap\tap.exe"))) {
    $p = Join-Path $base.FullName $c[1]
    if (Test-Path $p) { $comps += [ordered]@{ name=$c[0]; type="project"; version=$ver; sha256=(Sha $p); path=$p } }
  }
  foreach ($d in @("ttp-primitives","ttp-composite")) {
    $p = Join-Path $base.FullName $d
    if (Test-Path $p) { $comps += [ordered]@{ name=($d -replace '-','_'); type="project"; version=$ver; sha256=$null; path=$p } }
  }
}

$doc = [ordered]@{
  generated             = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  host                  = "windows"
  os                    = (Get-CimInstance Win32_OperatingSystem).Caption
  kernel                = [Environment]::OSVersion.Version.ToString()
  telemetry_lab_release = $ver
  components            = $comps
}
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding ascii
Get-Content $out
