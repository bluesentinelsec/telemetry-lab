package main

import (
	"testing"

	"github.com/michaellong/telemetry-lab/ttp-primitives/go/internal/primitivetest"
)

func TestFileIOExitsZero(t *testing.T) {
	primitivetest.ExitsZero(t)
}
