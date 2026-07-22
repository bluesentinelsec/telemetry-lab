//go:build linux

package main

// dns_lookup primitive: resolve a hostname to addresses.
//
// Name resolution is a precursor to most network activity. Resolving "localhost"
// keeps the primitive offline and deterministic (served from /etc/hosts /
// nsswitch, no DNS packet) while still exercising the resolver telemetry path.
//
// The resolver is where Go's cgo/pure-Go split diverges most: under CGO_ENABLED=1
// the net package can use the libc resolver (getaddrinfo, NSS modules), while the
// pure-Go static build uses Go's own resolver. That makes this a strong substrate
// discriminator; the cgo linkage anchor lives in anchor_cgo.go. Exits 0 when
// resolution yields at least one address.
//
// Linux-only for this pass (getaddrinfo via ws2tcpip on Windows -- issue #44).

import (
	"context"
	"net"
	"os"
)

func main() {
	addrs, err := net.DefaultResolver.LookupHost(context.Background(), "localhost")
	if err != nil || len(addrs) < 1 {
		os.Exit(1)
	}
}
