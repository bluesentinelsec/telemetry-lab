package main
import (
"fmt"
"os/exec"
"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
"os"
)
func main() {
if !fixture.Begin("netcat_exec") {return}
cmd := exec.Command("/usr/bin/ncat", "--exec", "/usr/bin/printf NETCAT_OK", "198.18.0.1", "4444")
data, err := cmd.Output(); fixture.Must(err)
fixture.Check(string(data) == "", "utility output")
got, err := os.ReadFile("/tmp/lab/received"); fixture.Must(err); fixture.Check(string(got) == "NETCAT_OK", "fixture bytes")
fmt.Print("CASE_OK netcat_exec\n")
}
