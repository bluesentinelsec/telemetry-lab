# Auto-retry validation — September 24, 2026

Application source: `c96675d` (subsequent changes to this document only).
Validated on disposable Debian 13 and Windows Server 2025 lab hosts using the
existing 0.3.0 candidate native binaries. No release was published.

| Check | Linux | Windows |
|---|---|---|
| Primitive smoke collection | 104/104 test/configuration slots accepted | `empty` in all 6 primitive configurations accepted |
| Composite smoke collection | 8/8 slots: sensitive read and reverse shell, C/glibc and Go/static, active/control | 6/6 slots: Run key, TCP 3389, DNS IP lookup, C/UCRT, active/control |
| Injected corrupt primitive telemetry | Failed original quarantined; replacement accepted | Same |
| Retries disabled | One suspect attempt; incomplete campaign | Same |
| Retry exhaustion | Four suspect attempts; incomplete campaign | Same |
| Composite collection failure | Stopped real Falco after native completion; recovered frozen collector and accepted replacement | Corrupted exported event JSON after real execution; preserved original evidence and accepted replacement |
| Configurable repetitions | CLI accepted two requested repetitions | Same |
| Valid detector miss | Go/static reverse-shell miss accepted, zero retries | Covered by contract/attribution tests |

The final Linux collector also retained the journal and native stdout/stderr after
the injected Falco failure. `tap` successfully consumed the accepted-only Linux
primitive directory. Every finalized attempt was audited for unique IDs, correct
accepted/suspect placement, replacement links, and absence of retries of valid or
behavior-failure outcomes.

Tests: 14 experiment contract/CLI tests on Linux; 14 on Windows with the two POSIX
fixture tests skipped; 10 Linux collector tests; 15 Windows attribution tests;
release-validation and assembly regression tests. Windows PowerShell collectors
were parsed and exercised on Windows. Fault-injection results are validation data,
not dissertation observations.

Raw archives, SHA-256 receipts, source/support snapshots, SSM commands/output,
campaign audit, and teardown receipts are retained locally under:

`/Users/michaellong/telemetry-lab-data/auto-retry-validation-2026-09-24/`

The two validation hosts and their volumes are destroyed after evidence archival.
The unrelated Windows SBOM lab remains untouched. Refer to `cleanup/complete.json`
for the teardown receipt.

This validates retry behavior and representative native integrations; it is not a
new full repetition study. The experiment runner checks composites individually,
so pilot timings that amortized collector overhead across batches do not directly
apply to this runner.
