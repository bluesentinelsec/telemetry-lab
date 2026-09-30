package main
import("fmt";"net";"io";"time";"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture")
func main(){if !fixture.Begin("unexpected_inbound"){return}
ln,err:=net.Listen("tcp4","198.18.0.1:4447"); fixture.Must(err); defer ln.Close()
cli,err:=net.DialTimeout("tcp4",ln.Addr().String(),3*time.Second); fixture.Must(err); defer cli.Close()
srv,err:=ln.Accept(); fixture.Must(err); defer srv.Close()
fixture.Must(cli.SetDeadline(time.Now().Add(3*time.Second))); fixture.Must(srv.SetDeadline(time.Now().Add(3*time.Second)))
_,err=io.WriteString(cli,fixture.Payload); fixture.Must(err); b:=make([]byte,len(fixture.Payload)); _,err=io.ReadFull(srv,b); fixture.Must(err); fixture.Check(string(b)==fixture.Payload,"peer bytes")
_,err=srv.Write(b); fixture.Must(err); _,err=io.ReadFull(cli,b); fixture.Must(err); fixture.Check(string(b)==fixture.Payload,"echo bytes")
fmt.Println("CASE_OK unexpected_inbound")
}
