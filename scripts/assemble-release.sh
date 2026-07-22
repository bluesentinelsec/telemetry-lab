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
  for cfg in $configs; do
    local cdst="$root/ttp-composite/$cfg"
    mkdir -p "$cdst"
    # Tolerate a missing composite-<config> artifact: the Windows composite CI
    # jobs are non-blocking (go-backs), so a bundle stays valid with its Linux
    # composites even if a Windows composite build did not produce an artifact.
    if [ -d "$COMP/composite-$cfg" ]; then
      find "$COMP/composite-$cfg" -type f \( "${compnameargs[@]}" -name '*.dll' \) -exec cp {} "$cdst/" \;
      if [ "$os" = linux ]; then chmod +x "$cdst"/* 2>/dev/null || true; fi
    else
      echo "::warning::composite artifacts absent for $cfg -- skipped"
    fi
  done

  # Manifest.
  local cfgjson primjson compjson
  cfgjson=$(printf '"%s",' $configs); cfgjson="[${cfgjson%,}]"
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
  "configs": ${cfgjson}
}
EOF
  cp scripts/release-README.txt "$root/README.txt"

  # Archive (idiomatic per OS).
  if [ "$os" = linux ]; then
    tar -C "$OUT" -czf "${OUT}/${name}.tar.gz" "$name"
  else
    (cd "$OUT" && zip -qr "${name}.zip" "$name")
  fi
  echo "assembled ${name}"
}

mkdir -p "$OUT"
assemble linux "$LINUX_CONFIGS"
assemble windows "$WIN_CONFIGS"
