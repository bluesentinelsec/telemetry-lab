package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/process"
)

func main() {
	if !fixture.Begin("memfd_execute") {
		return
	}
	process.ExecuteHelper("", true)
	fmt.Print("CASE_OK memfd_execute\n")
}
