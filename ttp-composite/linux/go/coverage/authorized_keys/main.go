package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("authorized_keys") {
		return
	}
	files.Write("/root/.ssh/authorized_keys")
	fmt.Print("CASE_OK authorized_keys\n")
}
