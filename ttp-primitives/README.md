# Primitive implementation scope

Release builds contain 13 Linux cases across eight configurations and 12 Windows cases across six configurations. This gives 104 Linux and 72 Windows test/configuration combinations. Windows configurations cover C (UCRT/MSVCRT), C++ (libstdc++/libc++ on UCRT), and Go (cgo/pure Go). Windows Rust primitives are not included in release bundles.

Both platforms build `empty`, `file_io`, `spawn`, `process_enumeration`, `thread_create`, `directory_enumeration`, `memory_allocate`, `pipe_ipc`, `tcp_client`, `tcp_server`, `dns_lookup`, and `http_client`. Linux additionally builds `process_exec`, which replaces the process image with `execve`.

CI verifies native execution and runtime linkage. Existing archived experiment campaigns used only `empty`, `file_io`, and `spawn` on Windows: 18 Windows combinations and 122 total combinations. Adding source and CI coverage does not retroactively expand those datasets. The nine added Windows cases require collector-level lab qualification before inclusion in a new experiment.

Composite scope is separate: see [TTP composite scope](../ttp-composite/SCOPE.md). Research protocols under `scripts/pilot` and `scripts/iteration-study` retain the scope and allocation of their original campaigns.
