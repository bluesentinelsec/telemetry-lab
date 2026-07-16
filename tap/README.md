# tap

`tap` (telemetry analysis pipeline) is the third tool in the telemetry-lab study,
after the two `tmon` monitors. It turns the raw JSONL that `tmon` emits — eBPF on
Linux, ETW on Windows — into the normalized common schema and, in later stages,
the cross-runtime comparisons that answer the dissertation's research questions.

It implements the "Telemetry Processor" from dissertation Chapter 3: a
self-contained Go binary (pure Go, no cgo, cross-compiles Linux + Windows,
deterministic). See issue #25 for the full design.

## Status

- **v0.1:** `normalize` + `inspect` — raw tmon JSONL → common schema.
- **v0.2 (this build):** `analyze` — the six Chapter 3 techniques: per-family
  volume + ratios, Jaccard symbol-set similarity (within-OS), stable features
  (per OS), substrate-specific features, `empty`-baseline subtraction, and
  Mann-Whitney U significance with Benjamini-Hochberg correction.
- Planned: `render` (figures), `report` (by-RQ narrative), `run` (end-to-end),
  and cross-OS comparison at the semantic-family layer.

```
tap analyze normalized.jsonl [-o analysis.json] [--primitive spawn]
```

## Usage

```
tap normalize <raw-dir|file> [-o normalized.jsonl]   # raw tmon JSONL -> common schema
tap inspect   <file.jsonl>                           # human summary of one artifact
tap version
```

Inputs are **self-describing**: provenance (`os`, `language`, `compiler`,
`runtime`, `primitive`, `iteration`, `host`) is read from each tmon file's `meta`
record — the `--meta` values the experiment controller passes to `tmon` — so you
point `tap` at a directory and it organizes itself. No rigid folder layout.

```
$ tap normalize ./raw -o normalized.jsonl
tap normalize: 6720 executions · 14 configs · 16 primitives
  4213890 normalized events → normalized.jsonl
  by family: file=... library=... network=... process=... registry=... syscall=...
  excluded 15 run(s):
    linux-c-musl/spawn/7 — 42 dropped events (incomplete telemetry)
```

## Common schema

One normalized event per line (`internal/model.Event`):

```json
{"os":"linux","language":"c","compiler":"gcc","runtime":"glibc","primitive":"read_file",
 "iteration":1,"config":"linux-c-glibc","run_id":"linux-c-glibc/read_file/1",
 "time_ns":1000,"pid":100,"tid":100,"comm":"cat",
 "family":"file","name":"open","attrs":{"path":"/etc/hostname","ret":3}}
```

`family` ∈ {`syscall`, `process`, `file`, `network`, `library`, `registry`};
provenance is denormalized onto every event so the dataset is self-describing.

## Reconciling the two monitors

Windows `tmon` emits first-class `file`/`network`/`registry`/`image` events;
Linux `tmon` is syscall-centric with decoded paths and sockaddrs. `normalize`
keeps every syscall as the `syscall` family **and synthesizes** the semantic
family events on Linux from the decoded syscalls (a `.so` open → `library`; a
path-bearing syscall → `file`; a socket syscall → `network`; `fork`/`exec`/`exit`
→ `process`). This gives one comparable per-family model on both platforms:
within-OS comparison uses the syscall symbol sets; cross-OS uses the semantic
families.

Runs that did not complete (no summary) or lost telemetry (`dropped`/`lost` > 0)
are excluded from the output and reported, per the Ch. 3 preprocessing.

## Building

```sh
cd tap
go test ./...
go build ./cmd/tap
# cross-compile for the lab hosts:
GOOS=linux   GOARCH=amd64 go build ./cmd/tap
GOOS=windows GOARCH=amd64 go build ./cmd/tap
```

Scope note: the *user-mode API calls* telemetry family is out of scope — it is
not observable via kernel-native instrumentation (eBPF / the ETW kernel session).
