//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_hide_files\n")
	if !fixture.Begin("registry_hide_files") {
		return
	}
	regops.SetDword("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden", 0)
	fixture.Success("registry_hide_files")
}
