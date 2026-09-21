package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/files"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)

func main() {
	if !fixture.Begin("shell_config_write") {
		return
	}
	files.Write("/root/.bashrc")
	fmt.Print("CASE_OK shell_config_write\n")
}
