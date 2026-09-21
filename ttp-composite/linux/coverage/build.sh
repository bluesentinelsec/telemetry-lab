#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
C_SRC="$HERE/../c"
OUT="${1:?Usage: build.sh OUTPUT_DIRECTORY}"
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
for libc in glibc musl; do
  cmake -S "$C_SRC" -B "$OUT/build-$libc" -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$C_SRC/toolchains/linux-$libc.cmake"
  cmake --build "$OUT/build-$libc" --parallel 2
  cmake --install "$OUT/build-$libc" --prefix "$OUT/image/linux-c-$libc"
  readelf -l "$OUT/image/linux-c-$libc/falco_cases" > "$OUT/elf-$libc.txt"
done
grep -q 'ld-linux' "$OUT/elf-glibc.txt"
grep -q 'ld-musl' "$OUT/elf-musl.txt"
gcc -static -O2 -Wall -Wextra -Werror "$C_SRC/coverage/helper.c" -o "$OUT/image/helper"
cp "$HERE/Dockerfile" "$OUT/image/Dockerfile"
docker build -t lab-falco-coverage:local "$OUT/image"
sha256sum "$OUT"/image/linux-c-*/falco_cases "$OUT/image/helper" > "$OUT/binaries.sha256"
gcc --version > "$OUT/gcc-version.txt"
dpkg-query -W libc6 musl musl-tools > "$OUT/runtime-versions.txt"
