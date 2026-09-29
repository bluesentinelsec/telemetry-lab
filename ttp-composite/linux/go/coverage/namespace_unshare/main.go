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
	if !fixture.Begin("namespace_unshare") {
		return
	}
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	before, err := os.Stat("/proc/thread-self/ns/user")
	fixture.Must(err)
	fixture.Must(unix.Unshare(unix.CLONE_NEWUSER))
	after, err := os.Stat("/proc/thread-self/ns/user")
	fixture.Must(err)
	fixture.Check(after.Sys().(*syscall.Stat_t).Ino != before.Sys().(*syscall.Stat_t).Ino, "namespace unchanged")
	fmt.Println("CASE_OK namespace_unshare")
}
