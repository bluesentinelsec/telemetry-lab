// Target rule: Remote Thread Creation In Uncommon Target Image
// Sigma rule ID: 43e75355-271c-2069-4eca-cc2e117f8510
// Ruleset path: sigma/sysmon/create_remote_thread/create_remote_thread_win_susp_uncommon_target_image.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/processfixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE remote_thread_ping\n")
	if !fixture.Begin("remote_thread_ping") {
		return
	}
	processfixture.Run(true)
	fixture.Success("remote_thread_ping")
}
