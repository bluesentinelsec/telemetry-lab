package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("privileged_mount") {
		return
	}
	cmd := exec.Command("/usr/bin/mount", "--bind", "/tmp/lab/mount-source", "/tmp/lab/mount-target")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "", "utility output")
	got, err := os.ReadFile("/tmp/lab/mount-target/payload")
	fixture.Must(err)
	fixture.Check(string(got) == "telemetry-lab-fixture\n", "fixture bytes")
	fmt.Print("CASE_OK privileged_mount\n")
}
