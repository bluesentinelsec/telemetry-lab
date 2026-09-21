#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OUT="${1:?Usage: build.sh OUTPUT_DIRECTORY gnu|musl}"
RUNTIME="${2:?Set gnu or musl}"
case "$RUNTIME" in
  gnu) TARGET=x86_64-unknown-linux-gnu ;;
  musl) TARGET=x86_64-unknown-linux-musl ;;
  *) echo 'Expected gnu or musl' >&2; exit 1 ;;
esac
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
# Both target libraries are static. The Rust compiler is held constant.
export RUSTFLAGS='-C target-feature=+crt-static'
unset CARGO_ENCODED_RUSTFLAGS
cd "$HERE/.."
cargo build --locked --release --target "$TARGET" -p coverage_suite --bins
rm -rf "$OUT/coverage"
mkdir -p "$OUT/coverage"
for program in "$HERE"/*/main.rs; do
  name=$(basename "$(dirname "$program")")
  cp "${CARGO_TARGET_DIR:-target}/$TARGET/release/coverage_$name" "$OUT/coverage/$name"
done
python3 "$HERE/../../coverage/verify_programs.py" "$OUT/coverage" "rust-$RUNTIME"
