package main
import("fmt";"os";"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture")
func main(){if !fixture.Begin("shell_config_read"){return};
b,e:=os.ReadFile("/root/.bashrc"); fixture.Must(e); fixture.Check(string(b)==fixture.Payload,"bytes")
fmt.Println("CASE_OK shell_config_read")
}
