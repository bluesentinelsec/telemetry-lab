#!/usr/bin/env bash
# Build a narrowly patched Falco 0.45.0 without replacing the packaged binary.
# Stdout contains only the executable path; build diagnostics go to stderr/logs.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT=${FALCO_BUILD_ROOT:-/opt/telemetry-lab/falco-health-build}
PREFIX=${FALCO_HEALTH_PREFIX:-/opt/telemetry-lab/falco-0.45.0-healthfix.1}
FALCO_COMMIT=05d5b3e363d5196c68c8ccea842ca57a2ef05562
LIBS_COMMIT=8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3

if python3 - "$HERE" "$PREFIX" <<'PY'
import hashlib,json,pathlib,sys
src,out=map(pathlib.Path,sys.argv[1:])
try:
    r=json.loads((out/'receipt.json').read_text())
    assert r['inputs']=={n:hashlib.sha256((src/n).read_bytes()).hexdigest()
                         for n in ('install.sh','preserve-partial-enter.patch','regression.cpp')}
    assert r['binary_sha256']==hashlib.sha256((out/'bin/falco').read_bytes()).hexdigest()
except (OSError,ValueError,KeyError,AssertionError):
    sys.exit(1)
PY
then
    printf '%s\n' "$PREFIX/bin/falco"
    exit 0
fi

[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'Requires Linux x86_64' >&2; exit 1; }
[[ $EUID == 0 ]] || { echo 'Run as root on the disposable Debian lab host' >&2; exit 1; }
mkdir -p "$ROOT/logs" "$PREFIX/bin"
trap 'echo "Falco build failed; see $ROOT/logs" >&2' ERR
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq > "$ROOT/logs/deps.log" 2>&1
apt-get install -y --no-install-recommends build-essential cmake ninja-build git clang llvm \
    pkg-config autoconf automake libtool libelf-dev zlib1g-dev libssl-dev \
    libcurl4-openssl-dev libtbb-dev libjsoncpp-dev libre2-dev libgtest-dev libgmock-dev \
    uthash-dev >> "$ROOT/logs/deps.log" 2>&1

if [[ ! -d "$ROOT/falco-source/.git" ]]; then
    git clone --quiet --depth 1 --branch 0.45.0 https://github.com/falcosecurity/falco.git "$ROOT/falco-source" >&2
fi
if [[ ! -d "$ROOT/libs-source/.git" ]]; then
    git clone --quiet --depth 1 --branch 0.26.0 https://github.com/falcosecurity/libs.git "$ROOT/libs-source" >&2
fi
[[ $(git -C "$ROOT/falco-source" rev-parse HEAD) == "$FALCO_COMMIT" ]]
[[ $(git -C "$ROOT/libs-source" rev-parse HEAD) == "$LIBS_COMMIT" ]]
git -C "$ROOT/libs-source" diff --exit-code -- . ':(exclude)userspace/libsinsp/parsers.cpp' >&2
if git -C "$ROOT/libs-source" apply --check "$HERE/preserve-partial-enter.patch" 2>/dev/null; then
    git -C "$ROOT/libs-source" apply "$HERE/preserve-partial-enter.patch"
else
    git -C "$ROOT/libs-source" apply --reverse --check "$HERE/preserve-partial-enter.patch"
fi
cp "$HERE/regression.cpp" "$ROOT/falco-source/empty-enter-regression.cpp"
python3 - "$ROOT/falco-source" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])/'cmake/modules/falcosecurity-libs.cmake'
s=p.read_text().replace('"0.0.0-local"','"0.26.0+telemetry-lab.1"')
p.write_text(s)
p=Path(sys.argv[1])/'CMakeLists.txt';s=p.read_text()
if 'add_executable(empty-enter-regression' not in s:
    s+='\nfind_package(GTest REQUIRED)\nadd_executable(empty-enter-regression empty-enter-regression.cpp)\ntarget_link_libraries(empty-enter-regression sinsp_test_support GTest::gtest_main)\n'
p.write_text(s)
PY
cmake -S "$ROOT/falco-source" -B "$ROOT/falco-build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DFALCOSECURITY_LIBS_SOURCE_DIR="$ROOT/libs-source" \
    -DFALCO_VERSION=0.45.0+telemetry-lab.1 -DCREATE_TEST_TARGETS=ON -DSCAP_FILES_SUITE_ENABLE=OFF \
    -DBUILD_DRIVER=OFF -DUSE_BUNDLED_DEPS=ON -DUSE_BUNDLED_TBB=OFF \
    -DUSE_BUNDLED_JSONCPP=OFF -DUSE_BUNDLED_RE2=OFF -DUSE_BUNDLED_UTHASH=OFF \
    -DUSE_BUNDLED_CURL=OFF -DUSE_BUNDLED_OPENSSL=OFF -DUSE_BUNDLED_ZLIB=OFF \
    -DUSE_DYNAMIC_LIBELF=ON > "$ROOT/logs/configure.log" 2>&1
cmake --build "$ROOT/falco-build" --target falco empty-enter-regression -j "${FALCO_BUILD_JOBS:-4}" > "$ROOT/logs/build.log" 2>&1
"$ROOT/falco-build/empty-enter-regression" > "$ROOT/logs/regression.log" 2>&1
cat "$ROOT/logs/regression.log" >&2
install -m 0755 "$ROOT/falco-build/userspace/falco/falco" "$PREFIX/bin/falco.new"
mv "$PREFIX/bin/falco.new" "$PREFIX/bin/falco"
cp "$HERE/preserve-partial-enter.patch" "$HERE/regression.cpp" "$PREFIX/"
cp "$ROOT/logs/regression.log" "$PREFIX/"
dpkg-query -W > "$PREFIX/packages.txt"
python3 - "$HERE" "$PREFIX" "$FALCO_COMMIT" "$LIBS_COMMIT" <<'PY'
import datetime,hashlib,json,pathlib,subprocess,sys
src,out=map(pathlib.Path,sys.argv[1:3])
receipt=dict(falco_commit=sys.argv[3],libs_commit=sys.argv[4],
    built=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    inputs={n:hashlib.sha256((src/n).read_bytes()).hexdigest()
            for n in ('install.sh','preserve-partial-enter.patch','regression.cpp')},
    binary_sha256=hashlib.sha256((out/'bin/falco').read_bytes()).hexdigest(),
    version=json.loads(subprocess.check_output([str(out/'bin/falco'),'--version'],text=True)))
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
PY
printf '%s\n' "$PREFIX/bin/falco"
