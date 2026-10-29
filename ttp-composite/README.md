# TTP composites

Each composite is a standalone native program targeting one exact, unmodified
Falco rule (Linux) or Sigma-derived rule (Windows). There are **67 Linux cases**
and **56 Windows cases** in each of C, C++, Go, and Rust, across eight runtime
configurations per platform. Every entry-point source names its tested rule;
Windows sources also include its exact Sigma rule ID and ruleset path.

```
ttp-composite/
  linux/
    c/<case>/main.c
    cpp/<case>/main.cpp
    go/<case>/main.go
    rust/<case>/main.rs
    harness/                 # Falco catalog, rules, runners, qualification
  windows/
    c/<case>/main.c
    cpp/<case>/main.cpp
    go/<case>/main.go
    rust/<case>/main.rs
    harness/                 # Sigma catalog, runners, qualification
```

Case names describe the fixed operation, such as `sensitive_read`,
`registry_run_key`, `unicode_child_arguments`, and `raw_owned_volume_read`.
Every case maps one-to-one to a target in the [Linux manifest](linux/harness/manifest.json)
or [Windows selection](windows/harness/selection.json). The original pilots have
been removed; these directories are the complete measured suites.

Language `internal/` directories hold shared code and fixture helpers. The Linux
`internal/negative` startup baseline and `internal/fixture_prepare` setup are
support programs, not rule-targeted cases. `--control` runs the same measured
executable with its tested operation disabled. Build outputs retain the existing
`<configuration>/coverage/` artifact format consumed by the experiment harness.

The runners independently verify behavior, attribute exact target rules, run
same-binary controls, and gate on collector health. A valid target-rule miss is a
measured outcome. The Go reverse shell still performs the verified exchange but
misses Falco's socket-duplication predicate because it relays through pipes.
Multiple target rules can describe overlapping mechanisms; the 123 cases are not
123 independent attack mechanisms or complete intrusions.

See [scope and configurations](SCOPE.md), [Linux suite](linux/harness/README.md),
[Windows suite](windows/harness/README.md), and [experiment collection](../scripts/experiment/README.md).
