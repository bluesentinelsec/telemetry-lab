package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"golang.org/x/sys/unix"
)

func main() {
	if !fixture.Begin("userfaultfd_create") {
		return
	}
	fixture.Must(unix.Setgid(65534))
	fixture.Must(unix.Setuid(65534))
	fixture.Check(unix.Getuid() == 65534, "uid")
	fd, _, err := unix.Syscall(unix.SYS_USERFAULTFD, uintptr(unix.O_CLOEXEC|unix.O_NONBLOCK|1), 0, 0)
	fixture.Check(err == 0, "userfaultfd failed")
	fixture.Must(unix.Close(int(fd)))
	fmt.Printf("CASE_OK userfaultfd_create\n")
}
