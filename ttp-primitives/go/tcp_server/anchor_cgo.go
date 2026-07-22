//go:build cgo && linux

package main

// DESIGN CONCESSION (Go cgo axis) -- cross-platform.
//
// The Go substrate axis is CGO_ENABLED=1 (links the platform C runtime
// dynamically) vs CGO_ENABLED=0 (pure-Go static binary). That axis only
// manifests if the program actually pulls in the cgo runtime. A bare no-op
// main() compiles to a static binary with no C runtime under BOTH settings, so
// the two configurations would be indistinguishable for this primitive.
//
// This file is compiled ONLY when cgo is enabled: the `cgo` build tag above is
// set automatically by the toolchain when CGO_ENABLED=1. Importing "C" forces
// the cgo runtime to be linked, so under CGO_ENABLED=1 the binary dynamically
// links the platform C runtime (glibc on Linux, UCRT on Windows); under
// CGO_ENABLED=0 this file is excluded and the binary stays pure-Go static. The
// C symbol is never called, so runtime behaviour is unchanged and the primitive
// still exits 0 with no output.
//
// This replaces an earlier `import _ "net"` hack that only worked on Linux -- on
// Windows the net package does not use cgo, so it produced no split (confirmed
// on windows-2025). It is a deliberate deviation from the minimal-primitive
// principle, needed only for pure-compute primitives like `empty`; primitives
// that do real I/O pull in the cgo runtime naturally. See tools/substrate.toml
// ({linux,windows}-go-*) and record as a dissertation limitation.

/*
#include <stddef.h>
*/
import "C"

var _ = C.size_t(0)
