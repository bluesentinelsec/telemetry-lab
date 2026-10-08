package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("interactive_recon") {
		return
	}
	cmd := exec.Command("/usr/bin/script", "-q", "-e", "-c", "exec /usr/bin/id -u", "/dev/null")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "0\r\n", "utility output")
	fmt.Print("CASE_OK interactive_recon\n")
}
