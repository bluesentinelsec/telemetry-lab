# Windows C++ detection composites

This directory implements the same 24 standalone cases and exact target rule IDs as the [Windows C reference suite](../../coverage). Each directory builds one executable; `--control` skips its measured behavior. The five-second post-I/O hold is also applied to TCP controls. There is no multi-case dispatcher.

## Runtime comparison

Clang, UCRT, optimization and behavior contracts are held constant. The two configurations dynamically link GNU libstdc++ or LLVM libc++, including their required exception/thread dependencies. All programs use C++ standard I/O and strings. File-copy cases use binary `std::ifstream`/`std::ofstream`, flush/close, and readback. Windows-specific operations (registry, sockets, timestamps, process creation, named pipes and module loading) use the same native APIs as C because C++17 does not provide equivalent facilities.

This varies the C++ library configuration, including necessary dependency DLLs; it does not isolate a single DLL or claim every native operation is implemented by the standard library. Both configurations must import UCRT and their selected C++ library. CI rejects mixed libraries, absent case markers, duplicate executable hashes, or missing runtime dependencies. The manifest records compiler identity, imports and hashes of programs and dependent DLLs.

The runner stages verified DLLs beside the neutral `probe.exe` and the Public-folder probe, then removes them after the campaign. It refuses pre-existing DLLs at those paths. It does not rely on a developer machine's library search path.

## Behavioral equivalence

The shared [selection](../../coverage/selection.json) and runner define the rule mapping for C and C++. Destination paths, registry values, payload bytes, helper result, resolver names/answer, TCP ports and request bytes are unchanged. Controls use the same executable as each active case. Fixtures are prepared outside the measured process. For live comparison, stage one fixed set of C helper/module/server binaries for both C++ configurations and retain their hashes.

A positive alert requires independently successful behavior and an exact rule ID linked through its event record to the measured process GUID (or the explicitly allowed child). A target miss or attribution failure is retained, not replaced by another rule or credited by PID alone.

`dns_onion` retains the inherited successful-resolution contract. Windows rejected that lookup in the C reference, even with a working local responder; it remains an implemented, unqualified candidate. The qualified reference scope is 23 target rules out of 2,269 enabled Sysmon rules in Hayabusa 4.1.0. The 24th program is not counted as qualified coverage.

## Build and run

Use MSYS2 UCRT64 with Clang, GCC/libstdc++, libc++, CMake, Ninja and native Python:

```sh
cmake -S ttp-composite/windows/cpp -B build-windows-cpp -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=toolchains/windows-libstdcxx.cmake
cmake --build build-windows-cpp
cmake --install build-windows-cpp --prefix composite-dist/windows-cpp-libstdcxx
python ttp-composite/windows/coverage/bundle_runtime.py composite-dist/windows-cpp-libstdcxx
python ttp-composite/windows/coverage/verify_programs.py \
  composite-dist/windows-cpp-libstdcxx/coverage libstdcxx --compiler clang++
```

Repeat with `windows-libcxx.cmake`, a separate build/output directory and `libcxx` verifier argument. Shared `run.ps1`, `run-local-tcp.ps1` and `run-local-dns.ps1 -Cases dns_ip_lookup` accept either verified coverage directory. See the [reference procedure](../../coverage/implementation.md) for fixed fixtures, pinned detection tools, attribution and archiving. CI behavior checks do not establish alert qualification; live evidence is recorded separately.
