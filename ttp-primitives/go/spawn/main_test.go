package main

import (
	"testing"

	"github.com/michaellong/telemetry-lab/ttp-primitives/go/internal/primitivetest"
)

func TestSpawnExitsZero(t *testing.T) {
	primitivetest.ExitsZero(t)
}
