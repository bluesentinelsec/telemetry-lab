//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"os"
)

func main() {
	fmt.Println("COMPOSITE_CASE delete_zone_identifier")
	if !fixture.Begin("delete_zone_identifier") {
		return
	}
	path := "C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier"
	fixture.Must(os.Remove(path))
	_, err := os.Stat(path)
	fixture.Check(os.IsNotExist(err), "fixture still exists")
	fixture.Success("delete_zone_identifier")
}
