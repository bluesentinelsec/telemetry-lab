# Windows Go detection composites

This suite ports all 24 standalone C/C++ cases with the same exact rule IDs and positive behavior contracts. Each directory builds one executable; `--control` skips its measured action. There is no dispatcher. The shared [selection](../../coverage/selection.json) and [runner](../../coverage/run.ps1) determine the targets, fixed paths and process-GUID attribution.

## Runtime comparison

Both configurations use the same Go compiler, source and pinned `golang.org/x/sys` dependency. `CGO_ENABLED=1` enables a build-tagged cgo anchor in the fixture package and external linking through MSYS2 UCRT64 GCC. `CGO_ENABLED=0` omits that anchor and the cgo runtime. The anchor performs no tested operation in C. This compares cgo linkage/startup configurations; it does not claim that the toggle changes every Go library implementation or makes Windows DNS use a C resolver.

The verifier checks each binary's Go build settings and actual `runtime/cgo` symbols, in addition to its single case marker and unique hash. cgo binaries must import UCRT and must not import MSVCRT; pure-Go binaries must not directly import either C runtime. Both still depend on Windows system DLLs: the existing `go-static` configuration name means pure Go here, not a fully static Windows executable. Go may dynamically load system libraries through Windows APIs in either configuration.

Compiler identity, Go build metadata, PE imports, and executable/dependency hashes are retained in the build manifest. The runner also verifies the staged executable hash immediately before launch; Sysmon hashes for reused paths are retained as sensor observations. Any non-system DLL dependencies are bundled and staged using the shared runner. CI requires both Go jobs and exercises 17 non-network cases plus their same-binary controls.

## Behavioral equivalence

- File cases use Go `os` reads/writes, close and independent byte-for-byte readback, with the same source fixtures and destination paths. No helper process performs these writes.
- Registry cases use the pinned Windows registry bindings, with identical keys, REG_SZ values and readback. The RunMRU case deletes the same harness-seeded leaf key and verifies absence.
- TCP cases use Go `net` over IPv4 loopback. Echo payload/reply bytes, ports and the five-second post-I/O hold match C/C++; controls also hold for five seconds. RDP uses the existing listener and the same fixed 11-byte request, without authentication.
- DNS cases use the ordinary Go resolver with an IPv4-only lookup and require the same 127.0.0.42 answer. The local server and temporary exact-name policy are shared fixtures, not custom resolution code in the measured process.
- Process execution verifies the fixed C helper's exit code 42. Timestamp, named-pipe and module-load cases use Windows bindings with the same timestamp, pipe exchange including its terminating zero byte, and fixed module function/result.

Helpers are separated by operation so file-only programs do not import the networking package just to obtain common fixture checks. One fixed archived C helper/module/server set is used across live configurations. The four legacy composites outside `coverage/` are retained but are not part of this 24-case qualification roster.

The `.onion` candidate retains the successful-resolution requirement that Windows rejected in C/C++. It remains unqualified unless the required behavior and attributable alert are both demonstrated. A failed lookup that alerts must not be counted as a positive qualified case.

## Build and qualify

In MSYS2 UCRT64, with Go, GCC and native Python on PATH:

```sh
cd ttp-composite/windows/go
CGO_ENABLED=1 bash coverage/build.sh ../../../composite-dist/windows-go-cgo
CGO_ENABLED=0 bash coverage/build.sh ../../../composite-dist/windows-go-static
```

The build stages the 24 executables, C support fixtures and manifest. Live qualification uses the shared non-network, TCP and DNS runners with fixed reference fixtures; see the [reference procedure](../../coverage/implementation.md). CI behavior checks do not establish alert coverage. Live outcomes, invalid attempts and attribution failures must be retained separately; repeated experiments and paired tmon measurements remain #54.

## Live qualification

Both configurations demonstrated all 23 qualified target rules and clean controls. The full follow-up has 46 attributable alerts and 46 clean controls; no paired rule-count differences were observed. Both `.onion` lookups failed their inherited success requirement. The shared runner now checks staged binary hashes and tolerates bounded post-exit image locks. Initial harness failures and repeated Sysmon image-hash discrepancies are retained in the [qualification report](../../coverage/validation/go/README.md).
