package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("binary_write") {
		return
	}
	files.Write("/usr/bin/lab_fixture")
	fmt.Print("CASE_OK binary_write\n")
}
