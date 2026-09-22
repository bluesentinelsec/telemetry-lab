//go:build windows

package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/fixture"
	"github.com/michaellong/telemetry-lab/ttp-composite/windows/go/coverage/internal/netio"
	"os"
	"strings"
)

func main() {
	fmt.Print("COMPOSITE_CASE tcp_connect_public_path\n")
	if !fixture.Begin("tcp_connect_public_path") {
		fixture.Hold()
		return
	}
	image, err := os.Executable()
	fixture.Must(err)
	fixture.Check(strings.EqualFold(image, `C:\Users\Public\telemetry-lab\probe.exe`), "wrong executable path")
	netio.Exchange("49152")
	fixture.Hold()
	fixture.Success("tcp_connect_public_path")
}
