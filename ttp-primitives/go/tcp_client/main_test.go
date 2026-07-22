//go:build linux

package main

import (
	"testing"

	"github.com/michaellong/telemetry-lab/ttp-primitives/go/internal/primitivetest"
)

func TestTCPClientExitsZero(t *testing.T) {
	primitivetest.ExitsZero(t)
}
