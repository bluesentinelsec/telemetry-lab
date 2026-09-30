package main
import (
"fmt"
"os/exec"
"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)
func main() {
if !fixture.Begin("privileged_debugfs") {return}
cmd := exec.Command("/usr/sbin/debugfs", "-R", "cat /marker", "/tmp/lab/filesystem.img")
data, err := cmd.Output(); fixture.Must(err)
fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
fmt.Print("CASE_OK privileged_debugfs\n")
}
