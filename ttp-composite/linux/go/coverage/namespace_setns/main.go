package main

import (
	"fmt"
	"github.com/michaellong/telemetry-lab/ttp-composite/linux/go/coverage/internal/fixture"
	"golang.org/x/sys/unix"
	"os"
	"runtime"
	"syscall"
)

func main() {
	if !fixture.Begin("namespace_setns") {
		return
	}
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	before, err := os.Stat("/proc/thread-self/ns/net")
	fixture.Must(err)
	fd, err := unix.Open("/tmp/lab/netns", unix.O_RDONLY, 0)
	fixture.Must(err)
	defer unix.Close(fd)
	var target unix.Stat_t
	fixture.Must(unix.Fstat(fd, &target))
	fixture.Check(before.Sys().(*syscall.Stat_t).Ino != target.Ino, "namespace already joined")
	fixture.Must(unix.Setns(fd, unix.CLONE_NEWNET))
	after, err := os.Stat("/proc/thread-self/ns/net")
	fixture.Must(err)
	fixture.Check(after.Sys().(*syscall.Stat_t).Ino != before.Sys().(*syscall.Stat_t).Ino, "namespace unchanged")
	fmt.Println("CASE_OK namespace_setns")
}
