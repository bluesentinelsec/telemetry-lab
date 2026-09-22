#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OUT="${1:?Usage: build.sh OUTPUT_DIRECTORY (CGO_ENABLED=0 or 1)}"
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
case "${CGO_ENABLED:?Set CGO_ENABLED=0 or 1}" in
  0) runtime=go-static; flags=() ;;
  1) runtime=go-cgo; flags=(-ldflags=-linkmode=external) ;;
  *) echo "CGO_ENABLED must be 0 or 1" >&2; exit 1 ;;
esac
cd "$HERE/.."
# Fresh stage: preserve legacy programs, never reuse another coverage build.
rm -rf "$OUT/coverage"
mkdir -p "$OUT/coverage/fixtures"
for program in "$HERE"/*/main.go; do
  name=$(basename "$(dirname "$program")")
  GOOS=windows GOARCH=amd64 go build -trimpath "${flags[@]}" -o "$OUT/coverage/$name.exe" "./coverage/$name"
done
# Fixed C support programs are outside the measured Go process. Live campaigns
# stage the archived C reference fixtures identically for both configurations.
gcc ../c/coverage/helper.c -o "$OUT/coverage/fixtures/windows_fixture_helper.exe"
gcc -shared ../c/coverage/module.c -o "$OUT/coverage/fixtures/fixture.node"
for server in echo dns; do
  gcc -O2 -Wall -Wextra -Werror "../c/coverage/${server}_server.c" -lws2_32 -o "$OUT/coverage/fixtures/windows_${server}_server.exe"
done
python ../coverage/bundle_runtime.py "$OUT"
python ../coverage/verify_programs.py "$OUT/coverage" "$runtime" --compiler gcc
