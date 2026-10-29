// Target rule: ADS Zone.Identifier Deleted By Uncommon Application
// Sigma rule ID: 2090f94a-7ba3-61c7-e843-f3864b2d3947
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_zone_identifier_ads_uncommon.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os"
)

func main() {
	fmt.Printf("COMPOSITE_CASE delete_zone_identifier\n")
	if !fixture.Begin("delete_zone_identifier") {
		return
	}
	path := "C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier"
	before, err := os.ReadFile(path)
	fixture.Must(err)
	fixture.Check(len(before) > 0 && before[0] == '[', "invalid stream fixture")
	fixture.Must(os.Remove(path))
	_, err = os.Open(path)
	fixture.Check(os.IsNotExist(err), "stream still exists")
	_, err = os.Stat("C:\\lab\\windows-coverage\\work\\download.txt")
	fixture.Must(err)
	fixture.Success("delete_zone_identifier")
}
