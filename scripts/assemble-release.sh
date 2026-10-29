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

# Primitive rosters differ by OS by exactly one entry:
# process_exec is the only Linux-only primitive (execve has no Windows analogue,
# issue #44); every other primitive is built on both OSes. The names drive both the copy
# glob and the manifest, so a new primitive is added in exactly one place here.
LINUX_PRIMS="empty file_io spawn process_exec process_enumeration thread_create directory_enumeration memory_allocate pipe_ipc tcp_client tcp_server dns_lookup http_client"
WIN_PRIMS="empty file_io spawn process_enumeration thread_create directory_enumeration memory_allocate pipe_ipc tcp_client tcp_server dns_lookup http_client"

# Composite rosters come from the exact-rule catalogs; pilots are no longer shipped.
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
  local prims
  if [ "$os" = linux ]; then prims="$LINUX_PRIMS"
  else prims="$WIN_PRIMS"; fi
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

  # Fixed support plus the independently rule-mapped composite artifacts.
  if [ "$os" = linux ]; then
    mkdir -p "$root/ttp-composite/coverage"
    cp ttp-composite/linux/harness/manifest.json "$root/ttp-composite/coverage/"
    cp ttp-composite/linux/harness/run.py ttp-composite/linux/harness/validate_manifest.py ttp-composite/linux/harness/setup-detector.sh ttp-composite/linux/harness/Dockerfile "$root/ttp-composite/coverage/"
    cp -R ttp-composite/linux/harness/falco-health-fix "$root/ttp-composite/coverage/"
    cp ttp-composite/linux/harness/enablement.yaml "$root/ttp-composite/coverage/"
    cp -R ttp-composite/linux/harness/fixtures "$root/ttp-composite/coverage/"
    cp -R ttp-composite/linux/harness/rules "$root/ttp-composite/coverage/"
  fi
  if [ "$os" = windows ]; then
    mkdir -p "$root/ttp-composite/coverage"
    for support in selection.json rule-inventory.csv RULE-LICENSE.md raw-disk-fixture.ps1 run.ps1 run-batch.ps1 run-local-tcp.ps1 run-local-dns.ps1 analyze.py verify_programs.py; do
      cp "ttp-composite/windows/harness/$support" "$root/ttp-composite/coverage/"
    done
  fi
  local composite_configs="$configs"
  if [ "$os" = windows ]; then composite_configs="$composite_configs windows-rust-msvc-dynamic windows-rust-msvc-static"; fi
  for cfg in $composite_configs; do
    local cdst="$root/ttp-composite/$cfg"
    mkdir -p "$cdst"
    if [ -d "$COMP/composite-$cfg" ]; then
      if [ "$os" = linux ]; then cp "$COMP/composite-$cfg/falco_helper" "$cdst/"; fi
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
  compjson=$(python3 -c 'import json,sys; p=sys.argv[1]; d=json.load(open("ttp-composite/"+p+"/harness/"+("manifest.json" if p=="linux" else "selection.json"))); print(json.dumps([c["id" if p=="linux" else "case_id"] for c in d["cases" if p=="linux" else "candidates"]]))' "$os")
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
  cp scripts/experiment/{run.py,engine.py,primitives.py,composites.py,batch_composites.py,README.md} "$root/experiment/"

  # Python caches from local verification are not release inputs. The runner
  # deliberately ignores runtime-generated caches in its integrity comparison.
  find "$root" -type d -name __pycache__ -prune -exec rm -rf {} +

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
