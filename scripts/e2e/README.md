# Release validation

Validate the assembled release bytes on disposable hosts deployed by
`lab-environment`. The Linux container image uses the shipped composite
folders, its bundled `coverage/Dockerfile`, and a single fixed C
`falco_helper` copied as `helper`. Do not rebuild programs on the lab host.

- `primitives.py BUNDLE OUTPUT` runs every shipped Linux primitive once under
  the bundled tmon and passes the raw JSONL to the bundled tap.
- `primitives.ps1 -Bundle BUNDLE -Output OUTPUT` does the same on Windows.
- Use the existing `ttp-composite/coverage/run.py --repetitions 1` on Linux.
  On Windows, run `run.ps1`, `run-local-tcp.ps1`, and `run-local-dns.ps1` for
  each composite configuration. Run `dns_onion` separately: successful
  resolution is not demonstrated, so it must not be counted as qualified.
- `legacy-linux.py BUNDLE OUTPUT --image IMAGE` and
  `legacy-windows.ps1 -Bundle BUNDLE -Output OUTPUT` exercise the retained
  pilot programs and preserve detector evidence. Pilots lack the expanded
  suite's independent behavior contracts; exit success is not qualification.

Run campaigns serially on each host so their collectors and fixtures do not
interfere. Different OS hosts can run concurrently. Preserve every attempt,
including failures; diagnose failures and use new output directories for
rechecks. A valid detector miss is data, not grounds to change the rule or
program to manufacture an alert.

The current release roster contains 122 primitive, 432 expanded composite,
and 80 legacy program/configuration combinations. Expanded runners also
execute 432 same-binary controls and eight Linux negative baselines.

Before publication, retain the component CI run IDs/source commits, hashes,
host inventories, rule inventories, raw telemetry, EVTX/Falco records,
analysis outputs, and a report distinguishing valid misses, invalid attempts,
and rechecks. Verify final asset hashes against the tested binaries. One
iteration is a release smoke test, not the dissertation's repeated experiment.
