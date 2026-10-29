// Target rule: Uncommon Process Access Rights For Target Image
// Sigma rule ID: 0d9cc92d-3ed8-beeb-dea9-8447f14fc31e
// Ruleset path: sigma/sysmon/process_access/proc_access_win_susp_all_access_uncommon_target.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/processfixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE process_access_ping\n")
	if !fixture.Begin("process_access_ping") {
		return
	}
	processfixture.Run(false)
	fixture.Success("process_access_ping")
}
