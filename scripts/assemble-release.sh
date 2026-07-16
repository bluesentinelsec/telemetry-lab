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
  local name="telemetry-lab-${VERSION}-${os}"
  local root="${OUT}/${name}"
  rm -rf "$root"
  mkdir -p "$root/tmon" "$root/tap" "$root/ttp-primitives" "$root/substrate"

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

  # Primitives, per config, plus the substrate-verification records.
  for cfg in $configs; do
    local dst="$root/ttp-primitives/$cfg"
    mkdir -p "$dst"
    find "$COMP/$cfg" -type f \
      \( -name empty -o -name file_io -o -name spawn \
         -o -name empty.exe -o -name file_io.exe -o -name spawn.exe \
         -o -name '*.dll' \) \
      -exec cp {} "$dst/" \;
    if [ "$os" = linux ]; then chmod +x "$dst"/* 2>/dev/null || true; fi
    find "$COMP/$cfg" -name 'substrate-*.json' -exec cp {} "$root/substrate/" \; 2>/dev/null || true
  done

  # Manifest.
  local cfgjson
  cfgjson=$(printf '"%s",' $configs); cfgjson="[${cfgjson%,}]"
  cat > "$root/manifest.json" <<EOF
{
  "name": "telemetry-lab",
  "version": "${VERSION}",
  "os": "${os}",
  "commit": "${GIT_SHA}",
  "built": "${BUILD_TIME}",
  "tools": ["tmon", "tap"],
  "primitives": ["empty", "file_io", "spawn"],
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
