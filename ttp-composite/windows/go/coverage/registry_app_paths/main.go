//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Print("COMPOSITE_CASE registry_app_paths\n")
	if !fixture.Begin("registry_app_paths") {
		return
	}
	regops.SetRegistry(`Software\Microsoft\Windows\CurrentVersion\App Paths\telemetry-lab-fixture.exe`, ``, `C:\Users\Public\telemetry-lab\helper.exe`)
	fixture.Success("registry_app_paths")
}
