// Target rule: Packet socket created in container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/internal/fixture"
	"golang.org/x/sys/unix"
)

func main() {
	if !fixture.Begin("packet_socket") {
		return
	}
	// ETH_P_ALL in network byte order, fixed Linux amd64 lab scope.
	fd, err := unix.Socket(unix.AF_PACKET, unix.SOCK_RAW, 0x0300)
	fixture.Must(err)
	fixture.Must(unix.Close(fd))
	fmt.Print("CASE_OK packet_socket\n")
}
