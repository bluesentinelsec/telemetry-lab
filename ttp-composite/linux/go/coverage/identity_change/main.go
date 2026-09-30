package main
import("fmt";"os";"syscall";"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture")
func main(){if !fixture.Begin("identity_change"){return}
fixture.Check(os.Getuid()==0,"initial UID"); fixture.Must(syscall.Setuid(2000)); fixture.Check(os.Getuid()==2000 && os.Geteuid()==2000,"resulting UID")
fmt.Println("CASE_OK identity_change")
}
