# Falco 0.45.0 partial-entry pairing fix

Falco 0.45.0/libsinsp 0.26.0 can report a missing syscall-entry pair even when the entry event was delivered. The retained C/musl `read_sensitive_file` and `clear_log` pilot programs reproduce this: they exit successfully and trigger their expected rules, but `n_retrieve_evts_drops` increases by one. The strict collector-health gate correctly rejects those attempts.

## Cause and change

At syscall entry, an eBPF pathname read can fail if the user-memory page has not yet been faulted in. Flags and mode remain present in the event. By syscall exit the kernel has accessed the pathname and the exit event carries it. The [libsinsp entry parser](https://github.com/falcosecurity/libs/blob/8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3/userspace/libsinsp/parsers.cpp) assumes an empty first parameter means all parameters are empty and discards this partially populated entry. The exit parser then counts its missing saved entry as a retrieval failure.

`preserve-partial-enter.patch` skips an entry only when **all** its parameters are empty, preserving the existing treatment of converted legacy placeholders. Partial live entries are saved for pairing. The existing exit parser already falls back to the exit pathname when the entry pathname is absent. Usable entry pathnames retain precedence, and genuinely missing entries still increment the failure counter. No TTP program, rule, or collector-health threshold changes.

The four parser regressions cover partial `open` and `creat` entries, a genuinely missing entry, and entry-pathname precedence. CI builds the pinned sources, requires all four tests to pass, reverses the patch to prove the two partial-entry tests fail, then reapplies it and verifies success.

## Lab installation and provenance

`../setup-detector.sh` selects this build when the packaged detector reports exactly 0.45.0. The original `/usr/bin/falco` stays installed. Other versions are not patched automatically; their strict collection gate still applies. For explicit before/after diagnostics, set `FALCO_BIN` to the detector executable when running setup.

On the disposable Debian 13 x86-64 host, `install.sh` installs build dependencies and builds:

- Falco commit `05d5b3e363d5196c68c8ccea842ca57a2ef05562` (0.45.0).
- libs commit `8fc2f1fbfc90f8ce7f68e00cdfa692cc7a9983a3` (0.26.0), with only this parser patch.
- Version labels `0.45.0+telemetry-lab.1` and `0.26.0+telemetry-lab.1`.

The default installation is `/opt/telemetry-lab/falco-0.45.0-healthfix.1`. Its `receipt.json` records source commits, patch/test/installer hashes, binary hash, and version metadata. `packages.txt` records installed package versions. The runner and host inventory record the running detector, rather than the untouched distribution executable. A cached build is reused only when its inputs and binary hash match the receipt. Initial builds take several minutes and require network access. `FALCO_BUILD_ROOT`, `FALCO_HEALTH_PREFIX`, and `FALCO_BUILD_JOBS` override build location, installation location, and concurrency.

This is a lab-maintained collector patch, not an upstream Falco release. Keep its identity in experiment provenance and revalidate before changing the collector version.

## Minimal reproducer

Run only on the disposable Linux lab host with the detector collecting and its metrics enabled:

```sh
gcc -O2 -Wall -Wextra reproduce.c -o /tmp/health-repro
printf '/etc/shadow\0' > /tmp/falco-health-path
sudo /tmp/health-repro cold
sudo /tmp/health-repro warm
```

Both modes issue the same direct `SYS_open` against `/etc/shadow`. Cold mode leaves the pathname mapping untouched; warm mode reads its first byte before the syscall. On the affected collector, cold mode increases the retrieval-failure counter and warm mode does not. With the patch, neither increases it. Compare settled metrics snapshots around each execution; Falco exports them once per second in this lab. A syscall-entry/exit bpftrace observer can independently confirm that the cold entry pathname is unreadable and the exit pathname is available. The diagnostic is not part of the TTP test binaries and does not warm their memory.
