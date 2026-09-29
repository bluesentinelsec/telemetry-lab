//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
)

func main() {
	fmt.Println("COMPOSITE_CASE delete_eventlog_fixture")
	if !fixture.Begin("delete_eventlog_fixture") {
		return
	}
	path := "C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_eventlog_fixture")
}
