package main

import (
	"testing"

	"github.com/michaellong/telemetry-lab/ttp-primitives/go/internal/primitivetest"
)

func TestEmptyExitsZero(t *testing.T) {
	primitivetest.ExitsZero(t)
}
