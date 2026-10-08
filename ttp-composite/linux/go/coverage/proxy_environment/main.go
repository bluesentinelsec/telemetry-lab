package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"os"
	"os/exec"
)

func main() {
	if !fixture.Begin("proxy_environment") {
		return
	}
	cmd := exec.Command("/usr/bin/curl", "-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture")
	cmd.Env = append(os.Environ(), "HTTP_PROXY=http://198.18.0.1:18081")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
	fmt.Print("CASE_OK proxy_environment\n")
}
