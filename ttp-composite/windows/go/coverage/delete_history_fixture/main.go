//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
)

func main() {
	fmt.Println("COMPOSITE_CASE delete_history_fixture")
	if !fixture.Begin("delete_history_fixture") {
		return
	}
	path := "C:\\lab\\windows-coverage\\work\\PSReadLine\\ConsoleHost_history.txt"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_history_fixture")
}
