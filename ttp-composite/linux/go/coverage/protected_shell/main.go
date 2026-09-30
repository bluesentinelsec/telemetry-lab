package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("protected_shell") {
		return
	}
	cmd := exec.Command("/bin/sh", "-c", "printf 'SHELL_OK\\n'")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "SHELL_OK\n", "utility output")
	fmt.Print("CASE_OK protected_shell\n")
}
