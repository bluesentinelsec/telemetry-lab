package main
import (
"fmt"
"os/exec"
"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
"os"
)
func main() {
if !fixture.Begin("bulk_clear") {return}
cmd := exec.Command("/usr/bin/shred", "-n", "0", "-z", "-s", "64", "/tmp/lab/shred-target")
data, err := cmd.Output(); fixture.Must(err)
fixture.Check(string(data) == "", "utility output")
got, err := os.ReadFile("/tmp/lab/shred-target"); fixture.Must(err); fixture.Check(string(got) == "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000", "fixture bytes")
fmt.Print("CASE_OK bulk_clear\n")
}
