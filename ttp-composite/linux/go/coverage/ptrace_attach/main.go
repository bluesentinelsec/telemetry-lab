package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/process"
)

func main() {
	if !fixture.Begin("ptrace_attach") {
		return
	}
	process.Attach()
	fmt.Print("CASE_OK ptrace_attach\n")
}
