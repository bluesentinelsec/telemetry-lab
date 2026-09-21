package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("dev_file") {
		return
	}
	files.Write("/dev/lab_fixture")
	fmt.Print("CASE_OK dev_file\n")
}
