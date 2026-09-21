#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OUT="${1:?Usage: build.sh OUTPUT_DIRECTORY (with CGO_ENABLED=0 or 1)}"
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
# SSM sessions need explicit cache/module paths when HOME is absent.
export GOCACHE="${GOCACHE:-$OUT/go-cache}"
export GOPATH="${GOPATH:-$OUT/go-path}"
case "${CGO_ENABLED:?Set CGO_ENABLED=0 or 1}" in
  0) runtime=go-static ;;
  1) runtime=go-cgo ;;
  *) echo "CGO_ENABLED must be 0 or 1" >&2; exit 1 ;;
esac
cd "$HERE/.."
# Fresh staging: no stale dispatcher or binaries from another configuration.
rm -rf "$OUT/coverage"
mkdir -p "$OUT/coverage"
for program in "$HERE"/*/main.go; do
  case_name=$(basename "$(dirname "$program")")
  GOOS=linux GOARCH=amd64 go build -trimpath -o "$OUT/coverage/$case_name" "./coverage/$case_name"
done
python3 "$HERE/../../coverage/verify_programs.py" "$OUT/coverage" "$runtime"
