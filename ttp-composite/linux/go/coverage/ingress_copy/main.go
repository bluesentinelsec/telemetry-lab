package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("ingress_copy") {
		return
	}
	cmd := exec.Command("/usr/bin/curl", "-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture", "-o", "/tmp/lab/downloaded")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "", "utility output")
	got, err := os.ReadFile("/tmp/lab/downloaded")
	fixture.Must(err)
	fixture.Check(string(got) == "telemetry-lab-fixture\n", "fixture bytes")
	fmt.Print("CASE_OK ingress_copy\n")
}
