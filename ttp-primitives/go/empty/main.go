package main

// DESIGN CONCESSION (Go CGO axis).
//
// The Go Linux substrate axis is CGO_ENABLED=1 (dynamically links the system
// libc) vs CGO_ENABLED=0 (pure-Go static binary). That axis only manifests if
// the program references a cgo-backed standard library package. A bare no-op
// main() compiles to a byte-identical static binary under BOTH settings, so the
// two configurations would be indistinguishable for this primitive.
//
// The blank import of "net" forces the split: under CGO_ENABLED=1 net uses its
// cgo resolver and pulls in libc.so.6 + the glibc loader; under CGO_ENABLED=0
// net falls back to the pure-Go resolver and the binary stays static. net is
// never called, so runtime behavior is unchanged.
//
// This is a deliberate deviation from the "minimal primitive" principle,
// justified because the toolchain otherwise thwarts the research design: it is
// only needed for pure-compute primitives like `empty`. Primitives that
// perform real I/O reference net/os naturally and require no such import.
// See tools/substrate.toml (linux-go-cgo / linux-go-static) and record this as
// a limitation in the dissertation's methodology.
import _ "net"

func main() {}
