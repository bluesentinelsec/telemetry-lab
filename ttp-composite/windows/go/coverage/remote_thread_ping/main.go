//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/processfixture"
)

func main() {
	fmt.Println("COMPOSITE_CASE remote_thread_ping")
	if !fixture.Begin("remote_thread_ping") {
		return
	}
	processfixture.Run(true)
	fixture.Success("remote_thread_ping")
}
