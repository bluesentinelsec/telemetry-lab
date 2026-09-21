package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("etc_write") {
		return
	}
	files.Write("/etc/lab_fixture")
	fmt.Print("CASE_OK etc_write\n")
}
