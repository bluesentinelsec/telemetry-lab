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
  rm -rf "$OUT/image/linux-c-$libc"
  cmake --install "$OUT/build-$libc" --prefix "$OUT/image/linux-c-$libc"
  : > "$OUT/elf-$libc.txt"
  for program in "$OUT/image/linux-c-$libc/coverage/"*; do
    readelf -l "$program" >> "$OUT/elf-$libc.txt"
  done
  python3 "$HERE/verify_programs.py" "$OUT/image/linux-c-$libc/coverage" "$libc"
done
grep -q 'ld-linux' "$OUT/elf-glibc.txt"
grep -q 'ld-musl' "$OUT/elf-musl.txt"
CPP_SRC="$HERE/../cpp"
for stdlib in libstdcxx libcxx; do
  cmake -S "$CPP_SRC" -B "$OUT/build-$stdlib" -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$CPP_SRC/toolchains/linux-$stdlib.cmake"
  cmake --build "$OUT/build-$stdlib" --parallel 2
  rm -rf "$OUT/image/linux-cpp-$stdlib"
  cmake --install "$OUT/build-$stdlib" --prefix "$OUT/image/linux-cpp-$stdlib"
  python3 "$HERE/verify_programs.py" "$OUT/image/linux-cpp-$stdlib/coverage" "$stdlib"
  for program in "$OUT/image/linux-cpp-$stdlib/coverage/"*; do
    readelf -l -d "$program"
  done > "$OUT/elf-$stdlib.txt"
done
for config in cgo static; do
  cgo=0; if [ "$config" = cgo ]; then cgo=1; fi
  CGO_ENABLED="$cgo" bash "$HERE/../go/coverage/build.sh" "$OUT/image/linux-go-$config"
  for program in "$OUT/image/linux-go-$config/coverage/"*; do
    readelf -l -d "$program"
    go version -m "$program"
  done > "$OUT/elf-go-$config.txt"
done
gcc -static -O2 -Wall -Wextra -Werror "$C_SRC/coverage/helper.c" -o "$OUT/image/helper"
cp "$HERE/Dockerfile" "$OUT/image/Dockerfile"
docker build -t lab-falco-coverage:local "$OUT/image"
sha256sum "$OUT"/image/linux-*/coverage/* "$OUT/image/helper" > "$OUT/binaries.sha256"
go version > "$OUT/go-version.txt"
gcc --version > "$OUT/gcc-version.txt"
clang++ --version > "$OUT/clang-version.txt"
dpkg-query -W libc6 musl musl-tools libstdc++6 libc++1 libc++abi1 clang > "$OUT/runtime-versions.txt"
