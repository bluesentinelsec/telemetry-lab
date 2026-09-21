package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/process"
)

func main() {
	if !fixture.Begin("exec_shm") {
		return
	}
	process.ExecuteHelper("/dev/shm/lab-helper", false)
	fmt.Print("CASE_OK exec_shm\n")
}
