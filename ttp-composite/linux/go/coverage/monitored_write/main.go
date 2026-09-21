package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("monitored_write") {
		return
	}
	files.Write("/boot/lab_fixture")
	fmt.Print("CASE_OK monitored_write\n")
}
