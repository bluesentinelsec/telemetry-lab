// Target rule: Prefetch File Deleted
// Sigma rule ID: 1e50ff2d-08cc-b108-b8c8-3327cf39794f
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_delete_prefetch.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os"
)

func main() {
	fmt.Printf("COMPOSITE_CASE delete_prefetch_fixture\n")
	if !fixture.Begin("delete_prefetch_fixture") {
		return
	}
	path := "C:\\Windows\\Prefetch\\TELEMETRYLABFIXTURE.pf"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_prefetch_fixture")
}
