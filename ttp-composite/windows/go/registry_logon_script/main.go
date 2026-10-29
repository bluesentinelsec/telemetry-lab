// Target rule: Potential Persistence Via Logon Scripts - Registry
// Sigma rule ID: aadaadd9-d82e-918a-20ca-01a4f35cde1f
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_logon_scripts_userinitmprlogonscript.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_logon_script\n")
	if !fixture.Begin("registry_logon_script") {
		return
	}
	regops.SetRegistry("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe")
	fixture.Success("registry_logon_script")
}
