//go:build linux

package main

// memory_allocate primitive: allocate, touch, and keep a large buffer.
//
// Memory acquisition underlies staging, unpacking, and injection. The allocation
// is deliberately large (64 MiB) so the Go runtime services it with a fresh mmap
// rather than a small-object arena -- making the acquisition visible as an
// mmap/munmap telemetry pair, mirroring the C malloc-above-mmap-threshold case.
// Each page is touched so the mapping is actually faulted in, not just reserved.
// The runtime allocator underlies this, so the cgo/static substrate split (which
// swaps the C runtime linkage) is the axis; the anchor lives in anchor_cgo.go.
//
// Self-contained; the buffer is kept referenced through the touch loop via a
// package var and runtime.KeepAlive so the compiler cannot elide the allocation.

import (
	"runtime"
)

const (
	allocBytes = 64 << 20 // 64 MiB
	page       = 4096
)

// checksum sinks the touched bytes into observable state so the allocation and
// the write loop cannot be optimized away as dead.
var checksum byte

func main() {
	buf := make([]byte, allocBytes)
	for i := 0; i < allocBytes; i += page {
		buf[i] = byte(i)
		checksum += buf[i]
	}
	runtime.KeepAlive(buf)
}
