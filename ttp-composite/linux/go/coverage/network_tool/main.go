package main
import (
"fmt"
"os/exec"
"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
)
func main() {
if !fixture.Begin("network_tool") {return}
cmd := exec.Command("/usr/bin/ncat", "--recv-only", "198.18.0.1", "4445")
data, err := cmd.Output(); fixture.Must(err)
fixture.Check(string(data) == "telemetry-lab-fixture\n", "utility output")
fmt.Print("CASE_OK network_tool\n")
}
