package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/network"
)

func main() {
	if !fixture.Begin("reverse_shell") {
		return
	}
	network.ReverseShell()
	fmt.Print("CASE_OK reverse_shell\n")
}
