//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/regops"
)

func main() {
	fmt.Println("COMPOSITE_CASE registry_logon_script")
	if !fixture.Begin("registry_logon_script") {
		return
	}
	regops.SetRegistry("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe")
	fixture.Success("registry_logon_script")
}
