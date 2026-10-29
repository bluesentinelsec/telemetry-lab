// Target rule: EventLog EVTX File Deleted
// Sigma rule ID: 956a26a6-af21-94d6-9fb7-0abbe37e3c7d
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_delete_event_log_files.yml
//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/internal/fixture"
	"os"
)

func main() {
	fmt.Printf("COMPOSITE_CASE delete_eventlog_fixture\n")
	if !fixture.Begin("delete_eventlog_fixture") {
		return
	}
	path := "C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_eventlog_fixture")
}
