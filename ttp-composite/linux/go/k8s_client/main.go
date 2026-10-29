// Target rule: Kubernetes Client Tool Launched in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
	"strings"
)

func main() {
	if !fixture.Begin("k8s_client") {
		return
	}
	cmd := exec.Command("/usr/bin/docker", "--version")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(strings.HasPrefix(string(data), "Docker version "), "utility output")
	fmt.Print("CASE_OK k8s_client\n")
}
