// Target rule: Launch Package Management Process in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("package_manager_query") {
		return
	}
	cmd := exec.Command("/usr/bin/dpkg", "--print-architecture")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "amd64\n", "utility output")
	fmt.Printf("CASE_OK package_manager_query\n")
}
