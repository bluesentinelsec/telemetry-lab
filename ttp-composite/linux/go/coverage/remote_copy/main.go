package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("remote_copy") {
		return
	}
	cmd := exec.Command("/usr/bin/rsync", "--port=1873", "rsync://198.18.0.1/fixture/payload", "/tmp/lab/transferred")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "", "utility output")
	got, err := os.ReadFile("/tmp/lab/transferred")
	fixture.Must(err)
	fixture.Check(string(got) == "telemetry-lab-fixture\n", "fixture bytes")
	fmt.Print("CASE_OK remote_copy\n")
}
