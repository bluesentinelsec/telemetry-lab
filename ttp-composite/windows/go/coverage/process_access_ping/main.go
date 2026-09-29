//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/processfixture"
)

func main() {
	fmt.Println("COMPOSITE_CASE process_access_ping")
	if !fixture.Begin("process_access_ping") {
		return
	}
	processfixture.Run(false)
	fixture.Success("process_access_ping")
}
