// Target rule: Disallowed SSH Connection Non Standard Port
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"os/exec"
)

func main() {
	if !fixture.Begin("ssh_nonstandard") {
		return
	}
	cmd := exec.Command("/usr/bin/ssh", "-F", "/dev/null", "-i", "/tmp/lab/sshkey", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=/tmp/lab/known_hosts", "-p", "4444", "labfixture@198.18.0.1", "/usr/bin/printf SSH_OK")
	data, err := cmd.Output()
	fixture.Must(err)
	fixture.Check(string(data) == "SSH_OK", "utility output")
	fmt.Print("CASE_OK ssh_nonstandard\n")
}
