package main
import("fmt";"os";"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture")
func main(){if !fixture.Begin("executable_create"){return};
f,e:=os.OpenFile("/tmp/lab/executable-new",os.O_CREATE|os.O_EXCL|os.O_WRONLY,0700); fixture.Must(e); fixture.Must(f.Close()); st,e:=os.Stat("/tmp/lab/executable-new"); fixture.Must(e); fixture.Check(st.Mode().Perm()==0700,"mode")
fmt.Println("CASE_OK executable_create")
}
