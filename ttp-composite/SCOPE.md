# TTP composite scope

The selected composite suites exercise **30 Linux target rules** and **23 qualified Windows target rules**, with C, C++, Go and Rust implementations. These are different platform-specific rule selections, not 53 portable behaviors or 53 independent attack mechanisms. Every case is a standalone program with a same-binary no-behavior control. Legacy pilot programs remain separate and do not expand these counts.

| Platform | Detector and subject corpus | Implemented candidates per language | Qualified target selection | Runtime configurations |
| --- | --- | ---: | ---: | ---: |
| Linux | Falco 0.45.0; pinned 95-rule syscall corpus, 81 stock-enabled | 30 | 30 | 8 |
| Windows | Sysmon and Hayabusa 4.1.0; 4,987 supplied rules, 2,269 enabled for the Sysmon input | 23 | 23 | 8 |

The Windows `.onion` candidate was removed from the programs and experiment scope after local DNS and hosts-file fixtures failed to satisfy its successful-resolution requirement. The ordinary DNS and TCP fixtures require no external endpoints, authentication or application-protocol libraries.

## Implemented runtime matrix

| Language | Linux configurations | Windows configurations |
| --- | --- | --- |
| C | GCC: glibc / musl | GCC: UCRT / MSVCRT |
| C++ | Clang: libstdc++ / libc++, both on glibc | Clang: libstdc++ / libc++, both on UCRT |
| Go | cgo / pure Go | cgo with UCRT / pure Go |
| Rust | Rust 1.98.1: static GNU/glibc / static musl | Rust 1.98.1 MSVC target: dynamic CRT / static CRT |

The comparison axes differ by language and OS. Windows Rust holds its compiler, target ABI and standard-library version constant while changing CRT linkage. Linux Rust changes target-specific standard libraries and libc together. Go's cgo toggle changes linkage/startup and does not imply that all Go operations use libc. These distinctions limit causal interpretation.

## Qualification is evidence, not a requirement to force every alert

Linux C, C++ and Rust have positive-alert and clean-control evidence for all 30 selected targets in both configurations. Both Go configurations demonstrate 29: the reverse-shell behavior succeeds but its pipe-relay implementation misses the socket-duplication rule. The C reference demonstrates that target; the Go miss remains a measured outcome. See [Linux scope](linux/coverage/README.md), [Go evidence](linux/coverage/validation/go/README.md), and [Rust evidence](linux/coverage/validation/rust/README.md).

Windows C, C++, Go and Rust demonstrate the same 23 targets with clean controls in all eight configurations. The Rust dynamic/static CRT comparison produced no target-rule or attributable all-rule alert-count differences in its complete qualification runs; see [Rust evidence](windows/coverage/validation/rust/README.md). See [Windows rule selection](windows/coverage/README.md) and the per-language validation directories. Attribution failures, sensor metadata discrepancies, unsuccessful behavior and incomplete captures remain visible alongside valid outcomes.

Identical alerts do not imply identical telemetry. Qualification establishes that the fixtures and detection mapping are usable; it does not supply the dissertation's balanced repeated experiment or paired tmon event-volume/composition dataset. Final configuration freeze, orchestration, collector-health policy and confirmatory collection remain [#54](https://github.com/bluesentinelsec/telemetry-lab/issues/54). The broader executable/attribution audit remains [#55](https://github.com/bluesentinelsec/telemetry-lab/issues/55).

This scope covers composites only. Windows Rust primitive coverage is a separate task; release manifests list primitive and composite configurations separately.
