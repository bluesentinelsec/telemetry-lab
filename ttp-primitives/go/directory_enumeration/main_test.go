//go:build linux

package main

import (
	"testing"

	"github.com/michaellong/telemetry-lab/ttp-primitives/go/internal/primitivetest"
)

func TestDirectoryEnumerationExitsZero(t *testing.T) {
	primitivetest.ExitsZero(t)
}
