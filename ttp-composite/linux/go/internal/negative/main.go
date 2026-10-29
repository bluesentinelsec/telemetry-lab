package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
)

func main() {
	if !fixture.Begin("negative") {
		return
	}

	fmt.Print("CASE_OK negative\n")
}
