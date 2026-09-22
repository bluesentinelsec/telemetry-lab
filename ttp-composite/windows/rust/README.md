# Windows Rust detection composites

All 24 C/C++/Go candidates have a separate Rust `src/bin/<case>.rs` executable. Each program has one fixed behavior and same-binary `--control`; there is no runtime dispatcher. The shared selection JSON, neutral program paths, fixture bytes and exact target rule IDs are unchanged. The `.onion` candidate retains its successful-resolution requirement and remains unqualified unless that behavior succeeds.

## Runtime configurations

Both builds pin Rust 1.98.1, windows-sys 0.59.0 (locked dependencies), and `x86_64-pc-windows-msvc`. `windows-rust-msvc-dynamic` uses `-C target-feature=-crt-static`; `windows-rust-msvc-static` uses `+crt-static`. This varies **CRT linkage**, not the Rust compiler, standard-library version or target ABI. Rust's standard library is statically linked in both builds; Windows system DLLs remain required. This is a different comparison from Linux Rust's GNU/musl axis. See the [Rust linkage reference](https://doc.rust-lang.org/reference/linkage.html#static-and-dynamic-c-runtimes).

The build records compiler, linker, SDK, target and actual compiler cfg. Each binary retains its build-time target/CRT marker. The shared verifier checks those markers, the sole case marker, unique hashes and PE import tables: dynamic builds require UCRT and VCRUNTIME; static builds reject direct CRT runtime DLL imports. Required redistributable DLLs are bundled and hashed. System DLLs indirectly loaded by Windows APIs do not establish that a static program was built with dynamic CRT linkage.

This adds composite configurations only. Windows Rust primitives are not implemented or advertised by this change; the release manifest lists composite configurations separately.

## Equivalent operations

File cases use Rust File reads/writes with a 4,096-byte buffer, close, and independent byte readback. Registry operations use Windows bindings and verify the values or deletion. Process creation uses Rust Command and checks the fixed helper's exit code. Timestamp, pipe and module-load cases use Windows bindings with the same date, byte exchange, and function result as the reference.

TCP uses Rust TcpStream, identical IPv4 loopback addresses, ports, echo/RDP payloads and a five-second post-I/O lifetime for both actives and controls. DNS uses ordinary Rust ToSocketAddrs and requires the same fixture answer, 127.0.0.42. Rust's resolver may request both address families whereas the C implementation uses an AF_INET hint; resulting telemetry is retained as an implementation difference, not suppressed with a custom resolver. No protocol authentication or third-party network client is introduced.

CI compiles support fixtures for behavior checks. Live qualification uses the archived C helper/module/server bytes unchanged in every configuration, so fixture compilers do not become an experimental variable. Registry and file setup/cleanup remains in the shared harness, outside measured actions. Alert attribution uses measured process GUIDs and exact rule IDs; starting a program alone must leave its target control clean.

## Build

From a Visual Studio x64 development shell with the pinned Rust toolchain and Python available:

```powershell
./ttp-composite/windows/rust/build.ps1 -Output composite-dist/windows-rust-msvc-dynamic -Crt dynamic
./ttp-composite/windows/rust/build.ps1 -Output composite-dist/windows-rust-msvc-static -Crt static
```

CI requires both builds and 17 non-network behavior/control pairs per build. Use the shared run.ps1, run-local-tcp.ps1 and run-local-dns.ps1 for live qualification. Build/behavior checks alone do not demonstrate detector outcomes. Full repetitions and paired tmon collection remain the experiment phase.
