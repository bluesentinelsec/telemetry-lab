// Target rule: Potential Persistence Via AppCompat RegisterAppRestart Layer
// Sigma rule ID: 349ed81d-2f2f-a95f-2d5d-41e5fbeaf784
// Ruleset path: sigma/sysmon/registry/registry_set/registry_set_persistence_app_cpmpat_layer_registerapprestart.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/regops"
)

func main() {
	fmt.Printf("COMPOSITE_CASE registry_appcompat_restart\n")
	if !fixture.Begin("registry_appcompat_restart") {
		return
	}
	regops.SetRegistry("Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers", "C:\\lab\\windows-coverage\\fixtures\\helper.exe", "REGISTERAPPRESTART")
	fixture.Success("registry_appcompat_restart")
}
