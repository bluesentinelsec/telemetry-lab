//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/processfixture"
)

func main() {
	fmt.Printf("COMPOSITE_CASE remote_thread_ping\n")
	if !fixture.Begin("remote_thread_ping") {
		return
	}
	processfixture.Run(true)
	fixture.Success("remote_thread_ping")
}
