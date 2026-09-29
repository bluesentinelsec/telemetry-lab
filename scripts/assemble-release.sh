#!/usr/bin/env bash
# Assemble the per-OS release bundles from downloaded CI component artifacts.
#
# Usage: assemble-release.sh <version> <components-dir> <out-dir>
#
# <components-dir> holds the artifacts of the latest green main runs of the build
# workflows (each artifact in a subdir named after it): the primitive bundles
# (one per config, named by config), plus tmon-linux, tmon-windows, and tap.
# Produces telemetry-lab-<version>-linux.tar.gz and -windows.zip with the
# repo-mirroring layout (tmon/, tap/, ttp-primitives/<config>/).
set -euo pipefail

VERSION="$1"
COMP="$2"
OUT="$3"
GIT_SHA="${GITHUB_SHA:-unknown}"
BUILD_TIME="${BUILD_TIME:-unknown}"

LINUX_CONFIGS="linux-c-glibc linux-c-musl linux-cpp-libstdcxx linux-cpp-libcxx linux-go-cgo linux-go-static linux-rust-gnu linux-rust-musl"
WIN_CONFIGS="windows-c-ucrt windows-c-msvcrt windows-cpp-libstdcxx windows-cpp-libcxx windows-go-cgo windows-go-static"

# Primitive rosters differ by OS: the 10 process/threading/network/memory/IPC
# primitives are Linux-first (issue #44 tracks Windows parity), so Windows still
# ships only the three cross-platform primitives. The names drive both the copy
# glob and the manifest, so a new primitive is added in exactly one place here.
LINUX_PRIMS="empty file_io spawn process_exec process_enumeration thread_create directory_enumeration memory_allocate pipe_ipc tcp_client tcp_server dns_lookup http_client"
WIN_PRIMS="empty file_io spawn"

# Composite rosters (multi-step ATT&CK techniques) also differ by OS. Like the
# primitive rosters, these names drive both the copy glob and the manifest, so a
# new composite is added in exactly one place. Composite artifacts arrive under
# COMP as composite-<config>/ (built by build-composites.yml); they carry no
# substrate-verification record, so nothing is copied into substrate/ for them.
LINUX_COMPS="reverse_shell imds read_sensitive_file symlink_sensitive clear_log mkdir_bin ptrace_antidebug"
WIN_COMPS="reverse_shell imds registry_run_key startup_folder"

# find1 <dir> <find-args...> -> first matching file path (fails loudly if none).
find1() {
  local dir="$1"; shift
  local hit
  hit=$(find "$dir" -type f "$@" 2>/dev/null | head -1)
  [ -n "$hit" ] || { echo "::error::not found under $dir: $*" >&2; exit 1; }
  echo "$hit"
}

assemble() {
  local os="$1" configs="$2"
  local prims comps
  if [ "$os" = linux ]; then prims="$LINUX_PRIMS"; comps="$LINUX_COMPS"
  else prims="$WIN_PRIMS"; comps="$WIN_COMPS"; fi
  local name="telemetry-lab-${VERSION}-${os}"
  local root="${OUT}/${name}"
  rm -rf "$root"
  mkdir -p "$root/tmon" "$root/tap" "$root/ttp-primitives" "$root/ttp-composite" "$root/substrate"

  # Tools.
  if [ "$os" = linux ]; then
    cp "$(find1 "$COMP/tmon-linux" -name tmon)"          "$root/tmon/tmon"
    cp "$(find1 "$COMP/tap" -path '*/linux/tap')"        "$root/tap/tap"
    chmod +x "$root/tmon/tmon" "$root/tap/tap"
  else
    # Windows tmon is a self-contained folder (tmon.exe + native TraceEvent DLLs
    # + the .NET runtime), so copy the whole publish directory.
    local tmondir
    tmondir=$(dirname "$(find1 "$COMP/tmon-windows" -name tmon.exe)")
    cp -r "$tmondir/." "$root/tmon/"
    cp "$(find1 "$COMP/tap" -path '*/windows/tap.exe')"  "$root/tap/tap.exe"
  fi

  # Primitives, per config, plus the substrate-verification records. The -name
  # predicate is built from the OS roster ($prims), so a primitive absent on a
  # given config (e.g. a Linux-only one under a Windows config) simply never
  # matches -- no per-config special-casing needed.
  local nameargs=()
  for p in $prims; do
    nameargs+=( -name "$p" -o )
    [ "$os" = windows ] && nameargs+=( -name "$p.exe" -o )
  done
  for cfg in $configs; do
    local dst="$root/ttp-primitives/$cfg"
    mkdir -p "$dst"
    find "$COMP/$cfg" -type f \( "${nameargs[@]}" -name '*.dll' \) -exec cp {} "$dst/" \;
    if [ "$os" = linux ]; then chmod +x "$dst"/* 2>/dev/null || true; fi
    find "$COMP/$cfg" -name 'substrate-*.json' -exec cp {} "$root/substrate/" \; 2>/dev/null || true
  done

  # Composites, per config, mirroring the primitive staging. Their artifacts
  # live under COMP as composite-<config>/, and the -name predicate is built from
  # the OS composite roster ($comps). The C++ Windows configs bundle their stdlib
  # DLL beside the exe, so *.dll is copied too. No substrate records exist for
  # composites, so none are collected.
  local compnameargs=()
  for c in $comps; do
    compnameargs+=( -name "$c" -o )
    [ "$os" = windows ] && compnameargs+=( -name "$c.exe" -o )
  done
  if [ "$os" = linux ]; then
    compnameargs+=( -name falco_helper -o )
    mkdir -p "$root/ttp-composite/coverage"
    cp ttp-composite/linux/coverage/manifest.json "$root/ttp-composite/coverage/"
    cp ttp-composite/linux/coverage/run.py ttp-composite/linux/coverage/validate_manifest.py ttp-composite/linux/coverage/setup-detector.sh ttp-composite/linux/coverage/Dockerfile "$root/ttp-composite/coverage/"
    cp -R ttp-composite/linux/coverage/falco-health-fix "$root/ttp-composite/coverage/"
    cp -R ttp-composite/linux/coverage/rules "$root/ttp-composite/coverage/"
  fi
  if [ "$os" = windows ]; then
    mkdir -p "$root/ttp-composite/coverage"
    for support in selection.json rule-inventory.csv RULE-LICENSE.md run.ps1 run-local-tcp.ps1 run-local-dns.ps1 analyze.py verify_programs.py; do
      cp "ttp-composite/windows/coverage/$support" "$root/ttp-composite/coverage/"
    done
  fi
  local composite_configs="$configs"
  if [ "$os" = windows ]; then composite_configs="$composite_configs windows-rust-msvc-dynamic windows-rust-msvc-static"; fi
  for cfg in $composite_configs; do
    local cdst="$root/ttp-composite/$cfg"
    mkdir -p "$cdst"
    if [ -d "$COMP/composite-$cfg" ]; then
      find "$COMP/composite-$cfg" -path '*/coverage' -prune -o -type f \( "${compnameargs[@]}" -name '*.dll' \) -exec cp {} "$cdst/" \;
      if [ "$os" = windows ] && [ -d "$COMP/composite-$cfg/coverage" ]; then
        cp -R "$COMP/composite-$cfg/coverage" "$cdst/coverage"
      fi
      if [ "$os" = linux ]; then
        chmod +x "$cdst"/* 2>/dev/null || true
        if [ -d "$COMP/composite-$cfg/coverage" ]; then
          cp -R "$COMP/composite-$cfg/coverage" "$cdst/coverage"
          chmod +x "$cdst/coverage/"*
        fi
      fi
    else
      echo "::error::composite artifacts absent for $cfg" >&2; exit 1
    fi
  done

  # Manifest.
  local cfgjson primjson compjson compcfgjson
  cfgjson=$(printf '"%s",' $configs); cfgjson="[${cfgjson%,}]"
  compcfgjson=$(printf '"%s",' $composite_configs); compcfgjson="[${compcfgjson%,}]"
  primjson=$(printf '"%s",' $prims); primjson="[${primjson%,}]"
  compjson=$(printf '"%s",' $comps); compjson="[${compjson%,}]"
  cat > "$root/manifest.json" <<EOF
{
  "name": "telemetry-lab",
  "version": "${VERSION}",
  "os": "${os}",
  "commit": "${GIT_SHA}",
  "built": "${BUILD_TIME}",
  "tools": ["tmon", "tap"],
  "primitives": ${primjson},
  "composites": ${compjson},
  "configs": ${cfgjson},
  "composite_configs": ${compcfgjson}
}
EOF
  cp scripts/release-README.txt "$root/README.txt"
  mkdir -p "$root/experiment"
  cp scripts/e2e/legacy-windows.ps1 "$root/experiment/"
  cp scripts/experiment/{run.py,engine.py,primitives.py,composites.py,batch_composites.py,legacy.py,README.md} "$root/experiment/"

  # Reject incomplete matrices and record the exact bytes being released.
  python3 scripts/validate-release.py "$root" --write

  # Archive (idiomatic per OS).
  if [ "$os" = linux ]; then
    local tar_flags=()
    if [ "$(uname -s)" = Darwin ]; then tar_flags=(--no-mac-metadata --no-xattrs); fi
    COPYFILE_DISABLE=1 tar "${tar_flags[@]}" -C "$OUT" -czf "${OUT}/${name}.tar.gz" "$name"
  else
    rm -f "${OUT}/${name}.zip"
    (cd "$OUT" && zip -qr "${name}.zip" "$name")
  fi
  echo "assembled ${name}"
}

mkdir -p "$OUT"
assemble linux "$LINUX_CONFIGS"
assemble windows "$WIN_CONFIGS"
