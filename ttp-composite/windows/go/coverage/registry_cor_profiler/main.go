//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_cor_profiler")
	if !fixture.Begin("registry_cor_profiler") {
		return
	}
	regops.SetRegistry("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}")
	fixture.Success("registry_cor_profiler")
}
