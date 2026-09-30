package main
import("fmt";"os";"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture")
func main(){if !fixture.Begin("executable_chmod"){return};
fixture.Must(os.Chmod("/tmp/lab/executable-mode",0700)); st,e:=os.Stat("/tmp/lab/executable-mode"); fixture.Must(e); fixture.Check(st.Mode().Perm()==0700,"mode")
fmt.Println("CASE_OK executable_chmod")
}
