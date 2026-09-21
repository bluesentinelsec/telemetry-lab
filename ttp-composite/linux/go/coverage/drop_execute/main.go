package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/process"
)

func main() {
	if !fixture.Begin("drop_execute") {
		return
	}
	process.ExecuteHelper("/tmp/lab-helper", false)
	fmt.Print("CASE_OK drop_execute\n")
}
